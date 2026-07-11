"""Deterministic synthetic end-to-end pipeline and artefact builder."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from closer_to_whom.capacity import implied_capacity
from closer_to_whom.demand import demand_cells_to_frame
from closer_to_whom.equity import equity_summary
from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.mcda import stochastic_acceptability, weighted_sum
from closer_to_whom.metrics import better_worse_summary, compare_to_baseline, scenario_summary
from closer_to_whom.optimisation import solve_location_allocation
from closer_to_whom.provenance import runtime_manifest, write_json
from closer_to_whom.registry import facilities_to_frame
from closer_to_whom.routing import OfflineApproximationEngine, build_route_matrix
from closer_to_whom.simulation import simulate_all
from closer_to_whom.synthetic import synthetic_bundle
from closer_to_whom.validation import validate_results
from closer_to_whom.voi import core_voi, research_value


def _weighted_scenario_matrix(summary: pl.DataFrame) -> tuple[list[str], np.ndarray]:
    labels = [f"{row['scenario_id']}::{row['pathway_id']}" for row in summary.iter_rows(named=True)]
    matrix = summary.select(
        "mean_course_travel_minutes",
        "mean_patient_whanau_cost_nzd",
        "mean_provider_cost_nzd",
        "p90_course_travel_minutes",
    ).to_numpy()
    return labels, matrix.astype(float)


def _optimisation_demo(bundle: dict[str, object]) -> dict[str, Any]:
    demand = demand_cells_to_frame(bundle["demand"])  # type: ignore[arg-type]
    facilities = facilities_to_frame(bundle["facilities"])  # type: ignore[arg-type]
    hospital = facilities.filter(pl.col("facility_type") == "synthetic_hospital")
    routes = build_route_matrix(demand, hospital, OfflineApproximationEngine())
    demand_ids = demand.get_column("demand_cell_id").to_list()
    facility_ids = hospital.get_column("facility_id").to_list()
    pivot = routes.pivot(
        values="one_way_minutes",
        index="demand_cell_id",
        on="facility_id",
        aggregate_function="first",
    ).sort("demand_cell_id")
    pivot = pivot.select("demand_cell_id", *facility_ids)
    costs = pivot.select(facility_ids).to_numpy().astype(float)
    weights_lookup = dict(
        demand.select("demand_cell_id", "expected_courses").iter_rows()
    )
    weights = np.asarray([weights_lookup[item] for item in demand_ids], dtype=float)
    p_median = solve_location_allocation(costs, weights, site_count=4, objective="p_median")
    p_center = solve_location_allocation(costs, weights, site_count=4, objective="p_center")
    return {
        "candidate_facility_ids": facility_ids,
        "p_median": {
            **asdict(p_median),
            "selected_facility_ids": [facility_ids[index] for index in p_median.selected_indices],
        },
        "p_center": {
            **asdict(p_center),
            "selected_facility_ids": [facility_ids[index] for index in p_center.selected_indices],
        },
        "claim_boundary": "Exact enumeration over synthetic facilities; not a service recommendation.",
    }


def _decision_demo(summary: pl.DataFrame, *, seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
    labels, matrix = _weighted_scenario_matrix(summary)
    minimise = np.ones(matrix.shape[1], dtype=bool)
    weights = np.asarray([0.35, 0.30, 0.15, 0.20])
    deterministic = weighted_sum(matrix, weights, minimise=minimise)
    smaa = stochastic_acceptability(
        matrix,
        minimise=minimise,
        draws=4096,
        concentration=np.ones(matrix.shape[1]),
        seed=seed,
    )
    mcda = {
        "alternatives": labels,
        "criteria": [
            "mean_course_travel_minutes",
            "mean_patient_whanau_cost_nzd",
            "mean_provider_cost_nzd",
            "p90_course_travel_minutes",
        ],
        "declared_weights": weights.tolist(),
        "scores": deterministic.scores.tolist(),
        "ranking": deterministic.ranking.tolist(),
        "first_rank_probability": smaa.first_rank_probability.tolist(),
        "expected_rank": smaa.expected_rank.tolist(),
        "normative_warning": "Weights are illustrative viewpoints, not stakeholder-derived preferences.",
    }

    rng = np.random.default_rng(seed)
    draws = 4096
    base_burden = matrix[:, 0] + matrix[:, 1] + matrix[:, 2]
    travel_multiplier = rng.lognormal(mean=0.0, sigma=0.15, size=draws)
    provider_multiplier = rng.lognormal(mean=0.0, sigma=0.20, size=draws)
    net_benefit = np.empty((draws, len(labels)), dtype=float)
    for index in range(len(labels)):
        net_benefit[:, index] = -(
            base_burden[index] * travel_multiplier
            + matrix[index, 2] * provider_multiplier
            + rng.normal(0.0, 1.0, size=draws)
        )
    voi = core_voi(net_benefit)
    # Demonstration EVSI is deliberately bounded by EVPI rather than claimed as an estimated study design.
    illustrative_evsi = voi.evpi_per_decision * 0.35
    microdata = research_value(
        research_id="microdata_study_demo",
        evsi_per_decision=illustrative_evsi,
        annual_affected_decisions=500.0,
        years=5,
        research_cost=250_000.0,
        discount_rate=0.03,
        implementation_delay_years=2,
    )
    voi_payload = {
        "alternatives": labels,
        "current_best_index": voi.current_best_index,
        "expected_net_benefit": voi.expected_net_benefit.tolist(),
        "evpi_per_decision": voi.evpi_per_decision,
        "expected_opportunity_loss": voi.expected_opportunity_loss.tolist(),
        "probability_optimal": voi.probability_optimal.tolist(),
        "illustrative_microdata_research": asdict(microdata),
        "claim_boundary": (
            "Synthetic demonstration. Publication EVSI requires a specified study design and calibrated "
            "likelihood or posterior model."
        ),
    }
    return mcda, voi_payload


def run_demo(output_dir: Path, *, seed: int = 20260711) -> dict[str, Any]:
    """Run and persist a deterministic, aggregate-only nationwide synthetic demonstration."""
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = synthetic_bundle()
    assumptions_fingerprint = "synthetic-demo-v1"
    results = simulate_all(
        demand_cells=bundle["demand"],  # type: ignore[arg-type]
        facilities=bundle["facilities"],  # type: ignore[arg-type]
        pathways=bundle["pathways"],  # type: ignore[arg-type]
        scenarios=bundle["scenarios"],  # type: ignore[arg-type]
        cost_rates=bundle["cost_rates"],  # type: ignore[arg-type]
        assumptions_fingerprint=assumptions_fingerprint,
    )
    summary = scenario_summary(results)
    capacity = implied_capacity(results)
    equity_ethnicity = equity_summary(results, group_column="ethnicity")
    equity_rurality = equity_summary(results, group_column="rurality")

    baseline = "s0_auckland_only_iv"
    compared = compare_to_baseline(results, baseline_scenario_id=baseline)
    better_worse = better_worse_summary(compared)

    digests = {
        "results": write_parquet_deterministic(
            results,
            output_dir / "results.parquet",
            sort_by=("scenario_id", "pathway_id", "demand_cell_id"),
        ),
        "summary": write_parquet_deterministic(
            summary,
            output_dir / "scenario-summary.parquet",
            sort_by=("scenario_id", "pathway_id"),
        ),
        "capacity": write_parquet_deterministic(
            capacity,
            output_dir / "implied-capacity.parquet",
            sort_by=("scenario_id", "pathway_id", "facility_id"),
        ),
        "equity_ethnicity": write_parquet_deterministic(
            equity_ethnicity,
            output_dir / "equity-ethnicity.parquet",
            sort_by=("scenario_id", "pathway_id", "ethnicity"),
        ),
        "equity_rurality": write_parquet_deterministic(
            equity_rurality,
            output_dir / "equity-rurality.parquet",
            sort_by=("scenario_id", "pathway_id", "rurality"),
        ),
        "better_worse": write_parquet_deterministic(
            better_worse,
            output_dir / "better-worse.parquet",
            sort_by=("scenario_id", "pathway_id", "direction"),
        ),
    }
    optimisation = _optimisation_demo(bundle)
    mcda, voi = _decision_demo(summary, seed=seed)
    write_json(output_dir / "optimisation.json", optimisation)
    write_json(output_dir / "mcda.json", mcda)
    write_json(output_dir / "voi.json", voi)
    checks = validate_results(results, output=output_dir / "validation.json")
    manifest = {
        "kind": "synthetic_nationwide_demonstration",
        "seed": seed,
        "assumptions_fingerprint": assumptions_fingerprint,
        "content_digests": digests,
        "row_counts": {
            "results": results.height,
            "summary": summary.height,
            "capacity": capacity.height,
            "equity_ethnicity": equity_ethnicity.height,
            "equity_rurality": equity_rurality.height,
            "better_worse": better_worse.height,
        },
        "validation_passed": all(check.passed or check.severity != "error" for check in checks),
        "runtime": runtime_manifest(Path.cwd(), deterministic=True),
        "claim_boundary": (
            "All inputs are synthetic aggregate fixtures. Outputs demonstrate software behaviour only."
        ),
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def compare_manifests(left: Path, right: Path) -> bool:
    """Compare deterministic content digests from two demo manifests."""
    left_payload = json.loads(left.read_text(encoding="utf-8"))
    right_payload = json.loads(right.read_text(encoding="utf-8"))
    return left_payload["content_digests"] == right_payload["content_digests"]

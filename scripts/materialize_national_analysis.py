#!/usr/bin/env python3
"""Materialise bounded national aggregate decision-analysis outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from closer_to_whom.mcda import stochastic_acceptability, weighted_sum
from closer_to_whom.optimisation import greedy_p_median
from closer_to_whom.voi import core_voi, evppi_quantile_bins

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMAND = ROOT / "data/derived/national-demand-cells.parquet"
DEFAULT_FACILITIES = ROOT / "data/derived/facility-registry.parquet"
DEFAULT_ROUTES = ROOT / "data/derived/route-matrix.parquet"
DEFAULT_SPATIAL_ROUTES = ROOT / "data/derived/route-matrix-spatial-sensitivity.parquet"
DEFAULT_COSTS = ROOT / "reports/travel-cost-parameters.json"
DEFAULT_OUTPUT = ROOT / "artifacts/national-analysis"
SITE_COUNTS = (1, 3, 5, 10, 19)
SEED = 20260727
MCDA_DRAWS = 16_384


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generated_at() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        return datetime.fromtimestamp(int(epoch), UTC).isoformat()
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    order = np.argsort(values, kind="stable")
    sorted_values = values[order]
    cumulative = np.cumsum(weights[order])
    return float(sorted_values[np.searchsorted(cumulative, quantile * cumulative[-1])])


def _load_inputs(
    demand_path: Path,
    facilities_path: Path,
    route_path: Path,
) -> tuple[pl.DataFrame, pl.DataFrame, np.ndarray, np.ndarray]:
    demand = pl.read_parquet(demand_path).sort("demand_cell_id")
    facilities = pl.read_parquet(facilities_path).sort("facility_id")
    routes = pl.read_parquet(route_path)
    if demand.height != 2_313 or facilities.height != 19:
        raise ValueError("National analysis requires 2,313 demand cells and 19 candidate sites")
    if routes.height != demand.height * facilities.height:
        raise ValueError("Baseline route matrix is incomplete")
    if routes["route_is_approximation"].any():
        raise ValueError("National analysis rejects approximate baseline routes")
    route_ids = routes.select("demand_cell_id", "facility_id").unique()
    if route_ids.height != routes.height:
        raise ValueError("Baseline route matrix contains duplicate origin-site pairs")
    ordered = (
        routes.join(
            demand.select("demand_cell_id").with_row_index("demand_index"),
            on="demand_cell_id",
        )
        .join(
            facilities.select("facility_id").with_row_index("facility_index"),
            on="facility_id",
        )
        .sort("demand_index", "facility_index")
    )
    minutes = ordered["one_way_minutes"].to_numpy().reshape(demand.height, facilities.height)
    kilometres = ordered["one_way_km"].to_numpy().reshape(demand.height, facilities.height)
    if not np.isfinite(minutes).all() or not np.isfinite(kilometres).all():
        raise ValueError("National route matrix contains non-finite values")
    return demand, facilities, minutes, kilometres


def _configuration_metrics(
    label: str,
    selected: tuple[int, ...],
    minutes: np.ndarray,
    kilometres: np.ndarray,
    weights: np.ndarray,
    facility_ids: list[str],
    *,
    vehicle_rate: float,
) -> dict[str, Any]:
    local = np.argmin(minutes[:, selected], axis=1)
    assignment = np.asarray(selected)[local]
    selected_minutes = minutes[np.arange(minutes.shape[0]), assignment]
    selected_km = kilometres[np.arange(kilometres.shape[0]), assignment]
    weight_total = float(weights.sum())
    return {
        "configuration_id": label,
        "candidate_site_count": len(selected),
        "candidate_facility_ids": [facility_ids[index] for index in selected],
        "weighted_mean_one_way_minutes": float(np.dot(selected_minutes, weights) / weight_total),
        "weighted_median_one_way_minutes": _weighted_quantile(selected_minutes, weights, 0.5),
        "weighted_p90_one_way_minutes": _weighted_quantile(selected_minutes, weights, 0.9),
        "weighted_p95_one_way_minutes": _weighted_quantile(selected_minutes, weights, 0.95),
        "maximum_one_way_minutes": float(selected_minutes[weights > 0].max()),
        "weighted_mean_one_way_km": float(np.dot(selected_km, weights) / weight_total),
        "expected_annual_round_trip_km": float(np.dot(2.0 * selected_km, weights)),
        "vehicle_resource_cost_nzd": float(np.dot(2.0 * selected_km, weights) * vehicle_rate),
        "share_expected_courses_within_60_minutes": float(
            weights[selected_minutes <= 60.0].sum() / weight_total
        ),
        "_assignment": assignment,
    }


def _spatial_weighted_mean(
    spatial_path: Path,
    demand: pl.DataFrame,
    selected_facility_ids: list[str],
) -> float:
    spatial = pl.read_parquet(spatial_path).filter(
        pl.col("facility_id").is_in(selected_facility_ids)
    )
    if spatial["route_is_approximation"].any():
        raise ValueError("National analysis rejects approximate spatial-sensitivity routes")
    minima = (
        spatial.group_by("geography_code", "routing_point_id", "routing_weight")
        .agg(pl.col("one_way_minutes").min().alias("minimum_minutes"))
        .group_by("geography_code")
        .agg(
            (pl.col("minimum_minutes") * pl.col("routing_weight"))
            .sum()
            .alias("spatial_mean_minutes")
        )
        .join(
            demand.select("geography_code", "expected_courses"),
            on="geography_code",
            how="inner",
        )
    )
    if minima.height != demand.height:
        raise ValueError("Spatial sensitivity does not cover every demand SA2")
    return float(
        (minima["spatial_mean_minutes"] * minima["expected_courses"]).sum()
        / minima["expected_courses"].sum()
    )


def build_outputs(
    demand: pl.DataFrame,
    facilities: pl.DataFrame,
    minutes: np.ndarray,
    kilometres: np.ndarray,
    *,
    spatial_path: Path,
    vehicle_rate: float,
    vehicle_rate_lower: float,
    vehicle_rate_upper: float,
) -> dict[str, dict[str, Any]]:
    weights = demand["expected_courses"].to_numpy()
    facility_ids = facilities["facility_id"].to_list()
    configurations: list[dict[str, Any]] = []
    for count in SITE_COUNTS:
        solution = greedy_p_median(minutes, weights, site_count=count)
        configurations.append(
            _configuration_metrics(
                f"candidate_network_{count:02d}",
                solution.selected_indices,
                minutes,
                kilometres,
                weights,
                facility_ids,
                vehicle_rate=vehicle_rate,
            )
        )

    public_configurations = [
        {key: value for key, value in configuration.items() if not key.startswith("_")}
        for configuration in configurations
    ]
    common = {
        "schema_version": "1.0.0",
        "generated_at": _generated_at(),
        "analysis_population": "aggregate_expected_course_cells",
        "candidate_site_evidence_state": "plausible_not_confirmed_capability",
        "observed_capacity": "unknown",
        "operational_recommendation": False,
    }
    scenario_summary = {
        **common,
        "status": "materialized_source_backed_candidate_network_comparison",
        "configurations": public_configurations,
        "claim_boundary": (
            "Candidate-network travel burdens use modelled aggregate expected courses and verified "
            "OSRM routes. Sites are plausible public-source locations, not confirmed anti-HER2 "
            "services; results do not establish eligibility, capacity, feasibility, or policy."
        ),
    }
    frontier = {
        **common,
        "status": "materialized_deterministic_greedy_frontier",
        "solver": "deterministic-greedy",
        "optimality_claimed": False,
        "objectives": [
            "minimise_candidate_site_count",
            "minimise_weighted_mean_one_way_minutes",
            "minimise_weighted_p95_one_way_minutes",
        ],
        "points": public_configurations,
        "claim_boundary": (
            "This is an exploratory candidate-location frontier, not a service configuration "
            "recommendation. Clinical capability and observed capacity remain hard unknown gates."
        ),
    }

    uncertainty_rows = []
    demand_scale_lower = 3_500.0 / 3_660.0
    for configuration in configurations:
        baseline_mean = configuration["weighted_mean_one_way_minutes"]
        spatial_mean = _spatial_weighted_mean(
            spatial_path,
            demand,
            configuration["candidate_facility_ids"],
        )
        round_trip_km = configuration["expected_annual_round_trip_km"]
        uncertainty_rows.append(
            {
                "configuration_id": configuration["configuration_id"],
                "parameter": "within_sa2_origin_structure",
                "lower_or_baseline": baseline_mean,
                "upper_or_sensitivity": spatial_mean,
                "unit": "weighted_mean_one_way_minutes",
                "uncertainty_type": "spatial_structural",
            }
        )
        uncertainty_rows.append(
            {
                "configuration_id": configuration["configuration_id"],
                "parameter": "annual_registration_calibration",
                "lower_or_baseline": round_trip_km * demand_scale_lower,
                "upper_or_sensitivity": round_trip_km,
                "unit": "expected_annual_round_trip_km",
                "uncertainty_type": "temporal_scenario",
            }
        )
        uncertainty_rows.append(
            {
                "configuration_id": configuration["configuration_id"],
                "parameter": "vehicle_resource_rate",
                "lower_or_baseline": round_trip_km * vehicle_rate_lower,
                "base": round_trip_km * vehicle_rate,
                "upper_or_sensitivity": round_trip_km * vehicle_rate_upper,
                "unit": "NZD_2025_26",
                "uncertainty_type": "deterministic_cost_scenario",
            }
        )
    uncertainty = {
        **common,
        "status": "materialized_separated_uncertainty_scenarios",
        "rows": uncertainty_rows,
        "probabilistic_interval_status": "not_estimated_no_source_backed_probability_distributions",
        "claim_boundary": (
            "Spatial, temporal-demand, and vehicle-rate scenarios are reported separately and are "
            "not pooled into a confidence interval or interpreted as observed variability."
        ),
    }

    criteria = np.asarray(
        [
            [
                item["weighted_mean_one_way_minutes"],
                item["weighted_p95_one_way_minutes"],
                item["candidate_site_count"],
            ]
            for item in configurations
        ],
        dtype=float,
    )
    minimise = np.ones(3, dtype=bool)
    viewpoints = {
        "access_priority": np.asarray([0.55, 0.35, 0.10]),
        "tail_access_priority": np.asarray([0.25, 0.65, 0.10]),
        "infrastructure_sparing": np.asarray([0.25, 0.25, 0.50]),
    }
    viewpoint_results = {}
    for name, weights_view in viewpoints.items():
        result = weighted_sum(criteria, weights_view, minimise=minimise)
        viewpoint_results[name] = {
            "weights": weights_view.tolist(),
            "scores": result.scores.tolist(),
            "ranking": [
                configurations[index]["configuration_id"] for index in result.ranking.tolist()
            ],
        }
    smaa = stochastic_acceptability(
        criteria,
        minimise=minimise,
        draws=MCDA_DRAWS,
        seed=SEED,
    )
    labels = [item["configuration_id"] for item in configurations]
    mcda = {
        **common,
        "status": "materialized_normative_viewpoint_analysis",
        "alternatives": labels,
        "criteria": [
            "weighted_mean_one_way_minutes",
            "weighted_p95_one_way_minutes",
            "candidate_site_count_proxy",
        ],
        "clinical_safety_is_compensatory": False,
        "viewpoints": viewpoint_results,
        "stochastic_weight_analysis": {
            "draws": MCDA_DRAWS,
            "seed": SEED,
            "first_rank_probability": dict(
                zip(labels, smaa.first_rank_probability.tolist(), strict=True)
            ),
            "expected_rank": dict(zip(labels, smaa.expected_rank.tolist(), strict=True)),
        },
        "claim_boundary": (
            "Weights are explicit normative viewpoints. Candidate-site count is not cost or "
            "capacity, and clinical eligibility and safety are excluded from trade-offs."
        ),
    }

    normalised = weighted_sum(
        criteria,
        np.ones(criteria.shape[1]),
        minimise=minimise,
    ).normalised_matrix
    utility_draws = smaa.weight_samples @ normalised.T
    voi_summary = core_voi(utility_draws)
    evppi = {
        criterion: evppi_quantile_bins(utility_draws, smaa.weight_samples[:, index])
        for index, criterion in enumerate(mcda["criteria"])
    }
    voi = {
        **common,
        "status": "materialized_normative_decision_uncertainty",
        "alternatives": labels,
        "value_unit": "normalised_normative_utility",
        "monetary_evpi_status": "not_estimated",
        "current_best_under_mean_weights": labels[voi_summary.current_best_index],
        "evpi_per_policy_decision": voi_summary.evpi_per_decision,
        "probability_optimal": dict(
            zip(labels, voi_summary.probability_optimal.tolist(), strict=True)
        ),
        "expected_opportunity_loss": dict(
            zip(labels, voi_summary.expected_opportunity_loss.tolist(), strict=True)
        ),
        "evppi_by_normative_weight": evppi,
        "microdata_enbs_status": "not_estimable_from_public_inputs",
        "next_information_priority": (
            "aggregate facility capability and resource-envelope evidence before microdata"
        ),
        "claim_boundary": (
            "VOI quantifies uncertainty about normative criterion weights in unitless utility. "
            "It is not monetary ENBS, does not justify microdata, and is not a policy recommendation."
        ),
    }
    return {
        "scenario_summary": scenario_summary,
        "optimisation_frontier": frontier,
        "uncertainty_analysis": uncertainty,
        "mcda_outputs": mcda,
        "voi_outputs": voi,
    }


def materialize(
    demand_path: Path = DEFAULT_DEMAND,
    facilities_path: Path = DEFAULT_FACILITIES,
    route_path: Path = DEFAULT_ROUTES,
    spatial_path: Path = DEFAULT_SPATIAL_ROUTES,
    cost_path: Path = DEFAULT_COSTS,
    output_dir: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    demand, facilities, minutes, kilometres = _load_inputs(
        demand_path,
        facilities_path,
        route_path,
    )
    costs = json.loads(cost_path.read_text(encoding="utf-8"))
    vehicle = next(item for item in costs["parameters"] if item["id"] == "K01")
    outputs = build_outputs(
        demand,
        facilities,
        minutes,
        kilometres,
        spatial_path=spatial_path,
        vehicle_rate=float(vehicle["value"]),
        vehicle_rate_lower=float(vehicle["lower"]),
        vehicle_rate_upper=float(vehicle["upper"]),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    receipts = []
    for name, payload in outputs.items():
        path = output_dir / f"{name}.json"
        _write_json(path, payload)
        receipts.append({"output": name, "path": path.name, "sha256": _sha256(path)})
    receipt = {
        "schema_version": "1.0.0",
        "generated_at": _generated_at(),
        "status": "completed_source_backed_aggregate_analysis",
        "inputs": {
            logical_name: _sha256(path)
            for logical_name, path in {
                "aggregate_demand": demand_path,
                "candidate_facilities": facilities_path,
                "baseline_osrm_routes": route_path,
                "spatial_sensitivity_osrm_routes": spatial_path,
                "travel_cost_parameters": cost_path,
            }.items()
        },
        "outputs": receipts,
        "seed": SEED,
        "claim_boundary": (
            "Aggregate model outputs compare plausible candidate networks under declared "
            "assumptions. They do not establish clinical eligibility, confirmed service capability, "
            "observed capacity, operational feasibility, or a policy recommendation."
        ),
    }
    _write_json(output_dir / "receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demand", type=Path, default=DEFAULT_DEMAND)
    parser.add_argument("--facilities", type=Path, default=DEFAULT_FACILITIES)
    parser.add_argument("--routes", type=Path, default=DEFAULT_ROUTES)
    parser.add_argument("--spatial-routes", type=Path, default=DEFAULT_SPATIAL_ROUTES)
    parser.add_argument("--costs", type=Path, default=DEFAULT_COSTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.demand,
                args.facilities,
                args.routes,
                args.spatial_routes,
                args.costs,
                args.output,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

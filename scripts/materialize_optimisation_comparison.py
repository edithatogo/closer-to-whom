#!/usr/bin/env python3
"""Materialise tractable exact optimisation comparisons for national routes."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from closer_to_whom.optimisation import (
    ParetoPoint,
    maximal_coverage,
    pareto_frontier,
    solve_location_allocation,
)
from closer_to_whom.robust_optimisation import robust_p_median_oracle

ROOT = Path(__file__).resolve().parents[1]
SITE_COUNTS = (1, 3, 5)


def _inputs(demand_path: Path, routes_path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    demand = pl.read_parquet(demand_path).sort("demand_cell_id")
    facilities = sorted(pl.read_parquet(routes_path).get_column("facility_id").unique().to_list())
    routes = pl.read_parquet(routes_path).join(
        demand.select("demand_cell_id"), on="demand_cell_id", how="inner"
    )
    routes = routes.with_columns(
        pl.col("demand_cell_id")
        .replace({value: index for index, value in enumerate(demand["demand_cell_id"].to_list())})
        .alias("demand_index"),
        pl.col("facility_id")
        .replace({value: index for index, value in enumerate(facilities)})
        .alias("facility_index"),
    ).sort("demand_index", "facility_index")
    costs = routes["one_way_minutes"].to_numpy().reshape(demand.height, len(facilities))
    return costs, demand["expected_courses"].to_numpy(), facilities


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    cumulative = np.cumsum(weights[order]) / weights.sum()
    return float(ordered_values[np.searchsorted(cumulative, quantile, side="left")])


def _frontier(rows: list[dict[str, Any]], costs: np.ndarray, weights: np.ndarray) -> dict[str, Any]:
    points: list[ParetoPoint] = []
    details: dict[str, dict[str, Any]] = {}
    for row in rows:
        selected = tuple(row["selected_facility_indices"])
        served = costs[:, selected].min(axis=1)
        stressed = (costs * 1.10)[:, selected].min(axis=1)
        label = f"{row['objective']}-p{row['site_count']}"
        objectives = (
            float(np.average(served, weights=weights)),
            _weighted_quantile(served, weights, 0.9) - _weighted_quantile(served, weights, 0.5),
            float(row["site_count"]),
            float(np.average(stressed - served, weights=weights)),
        )
        points.append(ParetoPoint(label, objectives))
        details[label] = {
            "label": label,
            "site_count": row["site_count"],
            "objective": row["objective"],
            "selected_facility_ids": row["selected_facility_ids"],
            "access_weighted_mean_minutes": objectives[0],
            "equity_p90_minus_p50_minutes": objectives[1],
            "resource_site_count": objectives[2],
            "resilience_stress_delta_weighted_mean_minutes": objectives[3],
        }
    frontier = pareto_frontier(points, minimise=(True, True, True, True))
    return {
        "status": "materialized_non_dominated_frontier",
        "objective_directions": {
            "access_weighted_mean_minutes": "minimise",
            "equity_p90_minus_p50_minutes": "minimise",
            "resource_site_count": "minimise",
            "resilience_stress_delta_weighted_mean_minutes": "minimise",
        },
        "frontier": [details[point.label] for point in frontier],
        "candidate_count": len(points),
        "scenario": "counterfactual_uniform_route_time_stress_10_percent",
        "equity_scope": "aggregate travel-dispersion proxy; not individual or protected-group equity evidence",
        "claim_boundary": "Non-dominated configurations within the enumerated candidate set only; not a policy or operational recommendation.",
    }


def build_report(demand_path: Path, routes_path: Path) -> dict[str, Any]:
    costs, weights, facilities = _inputs(demand_path, routes_path)
    rows: list[dict[str, Any]] = []
    for count in SITE_COUNTS:
        for objective in ("p_median", "p_center"):
            solution = solve_location_allocation(
                costs, weights, site_count=count, objective=objective
            )
            rows.append(
                {
                    "site_count": count,
                    "objective": objective,
                    "solver": solution.solver,
                    "optimal": solution.optimal,
                    "objective_value": solution.objective_value,
                    "selected_facility_indices": list(solution.selected_indices),
                    "selected_facility_ids": [
                        facilities[index] for index in solution.selected_indices
                    ],
                }
            )
        coverage = maximal_coverage(costs, weights, site_count=count, threshold=60.0)
        rows.append(
            {
                "site_count": count,
                "objective": "maximal_coverage_at_60_minutes",
                "solver": coverage.solver,
                "optimal": coverage.optimal,
                "objective_value": coverage.objective_value,
                "selected_facility_indices": list(coverage.selected_indices),
                "selected_facility_ids": [facilities[index] for index in coverage.selected_indices],
            }
        )
    robust_started = time.perf_counter()
    scenario_costs = np.stack((costs, costs * 1.10))
    robust_rows = []
    for count in SITE_COUNTS:
        selections = robust_p_median_oracle(scenario_costs, weights, count)
        for selection in selections[:3]:
            robust_rows.append(
                {
                    "site_count": count,
                    "selected_facility_ids": [
                        facilities[index] for index in selection.selected_indices
                    ],
                    "expected_weighted_minutes": selection.expected_objective,
                    "worst_case_weighted_minutes": selection.worst_case_objective,
                    "maximum_regret_weighted_minutes": selection.maximum_regret,
                }
            )
    return {
        "schema_version": "1.0.0",
        "status": "materialized_exact_tractable_optimisation_comparison",
        "analysis_population": "aggregate_expected_course_cells",
        "site_counts": list(SITE_COUNTS),
        "coverage_threshold_minutes": 60.0,
        "rows": rows,
        "solver_scope": "Exact deterministic enumeration for p=1,3,5; robust enumeration is exact within the two-scenario finite scope.",
        "robust_analysis": {
            "status": "materialized_exact_counterfactual_robust_p_median",
            "solver": "robust_p_median_oracle",
            "optimality": "exact_within_declared_scope",
            "scenario_definitions": [
                {"id": "nominal_route_matrix", "observed": True},
                {"id": "counterfactual_uniform_route_time_stress_10_percent", "observed": False},
            ],
            "rows": robust_rows,
            "runtime_seconds": round(time.perf_counter() - robust_started, 6),
            "claim_boundary": "Stress scenario is structural and hypothetical; it is not an observed disruption forecast or operational assurance.",
        },
        "multiobjective_frontier": _frontier(rows, costs, weights),
        "source_inputs": {
            "demand_cells": demand_path.as_posix(),
            "route_matrix": routes_path.as_posix(),
            "demand_cells_sha256": hashlib.sha256(demand_path.read_bytes()).hexdigest(),
            "route_matrix_sha256": hashlib.sha256(routes_path.read_bytes()).hexdigest(),
        },
        "claim_boundary": (
            "Exactness applies only to the declared finite p=1,3,5 route-selection problems and their "
            "stated objectives. Candidate facilities remain plausible locations, not confirmed services; "
            "the results are not operational or policy recommendations."
        ),
        "observed_capacity": "unknown",
        "operational_recommendation": False,
        "generated_at": "derived_from_frozen_national_inputs",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demand", type=Path, default=ROOT / "data/derived/national-demand-cells.parquet"
    )
    parser.add_argument("--routes", type=Path, default=ROOT / "data/derived/route-matrix.parquet")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/national-analysis/optimisation-comparison.json",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_report(args.demand, args.routes), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()

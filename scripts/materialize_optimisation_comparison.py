#!/usr/bin/env python3
"""Materialise tractable exact optimisation comparisons for national routes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from closer_to_whom.optimisation import maximal_coverage, solve_location_allocation

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
                "selected_facility_ids": [facilities[index] for index in coverage.selected_indices],
            }
        )
    return {
        "schema_version": "1.0.0",
        "status": "materialized_exact_tractable_optimisation_comparison",
        "analysis_population": "aggregate_expected_course_cells",
        "site_counts": list(SITE_COUNTS),
        "coverage_threshold_minutes": 60.0,
        "rows": rows,
        "solver_scope": "Exact deterministic enumeration for p=1,3,5; larger networks remain heuristic in the existing frontier.",
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

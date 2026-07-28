#!/usr/bin/env python3
"""Materialise deterministic candidate-network single-site sensitivity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import polars as pl

ROOT = Path(__file__).resolve().parents[1]


def build_report(scenario_path: Path, demand_path: Path, routes_path: Path) -> dict[str, Any]:
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    demand = pl.read_parquet(demand_path).select("demand_cell_id", "expected_courses")
    routes = pl.read_parquet(routes_path).select("demand_cell_id", "facility_id", "one_way_minutes")
    if routes.height == 0 or routes["one_way_minutes"].is_null().any():
        raise ValueError("Route matrix must contain non-null route minutes")
    wide = demand.join(routes, on="demand_cell_id", how="inner")
    if wide.height != demand.height * routes["facility_id"].n_unique():
        raise ValueError("Route matrix must contain one row per demand cell and facility")
    rows: list[dict[str, Any]] = []
    for configuration in scenario["configurations"]:
        ids = configuration["candidate_facility_ids"]
        baseline = (
            wide.filter(pl.col("facility_id").is_in(ids))
            .group_by("demand_cell_id")
            .agg(pl.col("one_way_minutes").min().alias("minutes"))
            .join(demand, on="demand_cell_id")
        )
        baseline_total = float(baseline["expected_courses"].sum())
        for removed in ids:
            remaining = [facility_id for facility_id in ids if facility_id != removed]
            if not remaining:
                continue
            after = (
                wide.filter(pl.col("facility_id").is_in(remaining))
                .group_by("demand_cell_id")
                .agg(pl.col("one_way_minutes").min().alias("minutes_after"))
                .join(demand, on="demand_cell_id")
            )
            weighted_after = float(
                (after["minutes_after"] * after["expected_courses"]).sum() / baseline_total
            )
            weighted_base = float(
                (baseline["minutes"] * baseline["expected_courses"]).sum() / baseline_total
            )
            rows.append(
                {
                    "configuration_id": configuration["configuration_id"],
                    "removed_candidate_facility_id": removed,
                    "baseline_weighted_mean_one_way_minutes": weighted_base,
                    "post_removal_weighted_mean_one_way_minutes": weighted_after,
                    "change_in_weighted_mean_one_way_minutes": weighted_after - weighted_base,
                    "post_removal_share_expected_courses_within_60_minutes": float(
                        after.filter(pl.col("minutes_after") <= 60.0)["expected_courses"].sum()
                        / baseline_total
                    ),
                    "expected_courses": baseline_total,
                }
            )
    return {
        "schema_version": "1.0.0",
        "status": "materialized_candidate_network_single_site_routing_sensitivity",
        "analysis_population": "aggregate_expected_course_cells",
        "outage_scenario_type": "counterfactual_candidate_site_removal",
        "rows": sorted(
            rows, key=lambda row: (row["configuration_id"], row["removed_candidate_facility_id"])
        ),
        "source_inputs": {
            "scenario_summary": scenario_path.as_posix(),
            "national_demand_cells": demand_path.as_posix(),
            "route_matrix": routes_path.as_posix(),
            "scenario_summary_sha256": hashlib.sha256(scenario_path.read_bytes()).hexdigest(),
            "national_demand_cells_sha256": hashlib.sha256(demand_path.read_bytes()).hexdigest(),
            "route_matrix_sha256": hashlib.sha256(routes_path.read_bytes()).hexdigest(),
        },
        "claim_boundary": (
            "This is a deterministic routing sensitivity for hypothetical candidate-site removal. "
            "It is not an observed outage, service-continuity result, resilience guarantee, capacity claim, "
            "or operational recommendation; candidate capability remains unknown."
        ),
        "observed_capacity": "unknown",
        "operational_recommendation": False,
        "generated_at": "derived_from_frozen_national_inputs",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario", type=Path, default=ROOT / "reports/national-analysis/scenario_summary.json"
    )
    parser.add_argument(
        "--demand", type=Path, default=ROOT / "data/derived/national-demand-cells.parquet"
    )
    parser.add_argument("--routes", type=Path, default=ROOT / "data/derived/route-matrix.parquet")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/national-analysis/resilience-sensitivity.json",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_report(args.scenario, args.demand, args.routes), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()

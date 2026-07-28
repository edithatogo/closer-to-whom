#!/usr/bin/env python3
"""Materialise aggregate, ecological access summaries by area stratifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import polars as pl

ROOT = Path(__file__).resolve().parents[1]


def _group(value: object) -> str:
    return "unknown" if value is None else str(value)


def build_report(demand_path: Path, routes_path: Path) -> dict[str, Any]:
    demand = pl.read_parquet(demand_path).select(
        "demand_cell_id",
        "expected_courses",
        "deprivation_quintile",
        "deprivation_status",
        "rurality",
        "rurality_status",
    )
    routes = pl.read_parquet(routes_path).select("demand_cell_id", "one_way_minutes")
    if routes.height == 0 or routes["one_way_minutes"].is_null().any():
        raise ValueError("Route matrix must contain non-null route minutes")
    nearest = routes.group_by("demand_cell_id").agg(
        pl.col("one_way_minutes").min().alias("minimum_one_way_minutes")
    )
    cells = demand.join(nearest, on="demand_cell_id", how="inner")
    if cells.height != demand.height:
        raise ValueError("Route matrix does not cover every demand cell")

    rows: list[dict[str, Any]] = []
    for dimension, value_column, status_column in (
        ("deprivation_quintile", "deprivation_quintile", "deprivation_status"),
        ("rurality", "rurality", "rurality_status"),
    ):
        grouped = (
            cells.with_columns(
                pl.col(value_column).map_elements(_group, return_dtype=pl.String).alias("group"),
                pl.col(status_column).map_elements(_group, return_dtype=pl.String).alias("status"),
            )
            .group_by("group", "status")
            .agg(
                pl.len().alias("demand_cell_count"),
                pl.col("expected_courses").sum().alias("expected_courses"),
                (pl.col("expected_courses") * pl.col("minimum_one_way_minutes"))
                .sum()
                .alias("weighted_minutes"),
                pl.when(pl.col("minimum_one_way_minutes") <= 60.0)
                .then(pl.col("expected_courses"))
                .otherwise(0.0)
                .sum()
                .alias("courses_within_60_minutes"),
            )
            .sort("group", "status")
        )
        for row in grouped.iter_rows(named=True):
            courses = float(row["expected_courses"])
            rows.append(
                {
                    "dimension": dimension,
                    "group": row["group"],
                    "status": row["status"],
                    "demand_cell_count": int(row["demand_cell_count"]),
                    "expected_courses": courses,
                    "weighted_mean_minimum_one_way_minutes": (
                        float(row["weighted_minutes"]) / courses if courses else None
                    ),
                    "share_expected_courses_within_60_minutes": (
                        float(row["courses_within_60_minutes"]) / courses if courses else None
                    ),
                }
            )

    return {
        "schema_version": "1.0.0",
        "status": "materialized_aggregate_ecological_access_stratifiers",
        "analysis_population": "aggregate_expected_course_cells",
        "dimensions": ["deprivation_quintile", "rurality"],
        "rows": rows,
        "source_inputs": {
            "demand_cells": demand_path.as_posix(),
            "route_matrix": routes_path.as_posix(),
            "demand_cells_sha256": hashlib.sha256(demand_path.read_bytes()).hexdigest(),
            "route_matrix_sha256": hashlib.sha256(routes_path.read_bytes()).hexdigest(),
        },
        "unknown_policy": "Unknown or unmatched area stratifiers remain explicit unknown groups.",
        "claim_boundary": (
            "These are area-level ecological access summaries of modelled aggregate expected courses. "
            "They are not individual attributes, patient outcomes, observed journeys, realised access, "
            "ethnicity effects, or evidence of service capability or capacity."
        ),
        "operational_recommendation": False,
        "observed_capacity": "unknown",
        "generated_at": "derived_from_frozen_national_inputs",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demand", type=Path, default=ROOT / "data/derived/national-demand-cells.parquet"
    )
    parser.add_argument("--routes", type=Path, default=ROOT / "data/derived/route-matrix.parquet")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "reports/national-analysis/distributional-equity.json"
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

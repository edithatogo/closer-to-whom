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


def _weighted_quantile(values: list[float], weights: list[float], quantile: float) -> float | None:
    if not values or sum(weights) <= 0:
        return None
    order = sorted(range(len(values)), key=values.__getitem__)
    total = sum(weights)
    cumulative = 0.0
    for index in order:
        cumulative += weights[index]
        if cumulative >= quantile * total:
            return values[index]
    return values[order[-1]]


def _summarise(
    cells: pl.DataFrame, dimension: str, weight_column: str = "expected_courses"
) -> list[dict[str, Any]]:
    national_weight = float(cells[weight_column].sum())
    national_mean = float(
        (cells[weight_column] * cells["minimum_one_way_minutes"]).sum() / national_weight
    )
    rows: list[dict[str, Any]] = []
    for key, group in cells.group_by("group", "status", maintain_order=True):
        label, status = key
        weights = [float(value) for value in group[weight_column].to_list()]
        minutes = [float(value) for value in group["minimum_one_way_minutes"].to_list()]
        total = sum(weights)
        within = sum(
            weight for weight, minute in zip(weights, minutes, strict=True) if minute <= 60.0
        )
        worst = sum(
            weight for weight, minute in zip(weights, minutes, strict=True) if minute > 120.0
        )
        mean = (
            float(
                sum(weight * minute for weight, minute in zip(weights, minutes, strict=True))
                / total
            )
            if total
            else None
        )
        rows.append(
            {
                "dimension": dimension,
                "group": _group(label),
                "status": _group(status),
                "demand_cell_count": group.height,
                "expected_courses": total,
                "weighted_mean_minimum_one_way_minutes": mean,
                "weighted_p90_minimum_one_way_minutes": _weighted_quantile(minutes, weights, 0.9),
                "share_expected_courses_within_60_minutes": within / total if total else None,
                "share_expected_courses_over_120_minutes": worst / total if total else None,
                "difference_from_national_weighted_mean_minutes": mean - national_mean
                if mean is not None
                else None,
                "weight_basis": weight_column,
            }
        )
    return rows


def build_report(
    demand_path: Path,
    routes_path: Path,
    ethnicity_path: Path = ROOT / "data/derived/sa2-ethnicity.parquet",
    vehicle_path: Path = ROOT / "data/derived/sa2-vehicle-access.parquet",
) -> dict[str, Any]:
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
        grouped = cells.with_columns(
            pl.col(value_column).map_elements(_group, return_dtype=pl.String).alias("group"),
            pl.col(status_column).map_elements(_group, return_dtype=pl.String).alias("status"),
        ).select("group", "status", "demand_cell_id", "expected_courses", "minimum_one_way_minutes")
        rows.extend(_summarise(grouped, dimension))

    vehicle = pl.read_parquet(vehicle_path).select(
        "geography_code", "no_motor_vehicle_share", "vehicle_access_status"
    )
    vehicle_cells = (
        cells.join(
            pl.read_parquet(demand_path).select("demand_cell_id", "geography_code"),
            on="demand_cell_id",
        )
        .join(vehicle, on="geography_code", how="left")
        .with_columns(
            pl.when(pl.col("no_motor_vehicle_share").is_null())
            .then(pl.lit("unknown"))
            .when(pl.col("no_motor_vehicle_share") <= 0.05)
            .then(pl.lit("low_0_to_5_percent"))
            .when(pl.col("no_motor_vehicle_share") <= 0.15)
            .then(pl.lit("medium_5_to_15_percent"))
            .otherwise(pl.lit("high_over_15_percent"))
            .alias("group"),
            pl.col("vehicle_access_status").fill_null("unknown").alias("status"),
        )
    )
    rows.extend(_summarise(vehicle_cells, "vehicle_access"))

    ethnicity = pl.read_parquet(ethnicity_path).select(
        "geography_code", "ethnicity_group", "total_response_share", "ethnicity_status"
    )
    ethnicity_cells = (
        pl.read_parquet(demand_path)
        .select("demand_cell_id", "geography_code", "expected_courses")
        .join(nearest, on="demand_cell_id")
        .join(ethnicity, on="geography_code", how="left")
        .with_columns(
            pl.col("ethnicity_group").fill_null("unknown").alias("group"),
            pl.col("ethnicity_status").fill_null("unknown").alias("status"),
            (pl.col("expected_courses") * pl.col("total_response_share").fill_null(0.0)).alias(
                "ethnicity_weight"
            ),
        )
    )
    rows.extend(_summarise(ethnicity_cells, "ethnicity_total_response", "ethnicity_weight"))

    return {
        "schema_version": "1.0.0",
        "status": "materialized_aggregate_ecological_access_stratifiers",
        "analysis_population": "aggregate_expected_course_cells",
        "dimensions": [
            "deprivation_quintile",
            "rurality",
            "vehicle_access",
            "ethnicity_total_response",
        ],
        "rows": rows,
        "source_inputs": {
            "demand_cells": demand_path.as_posix(),
            "route_matrix": routes_path.as_posix(),
            "ethnicity": ethnicity_path.as_posix(),
            "vehicle_access": vehicle_path.as_posix(),
            "demand_cells_sha256": hashlib.sha256(demand_path.read_bytes()).hexdigest(),
            "route_matrix_sha256": hashlib.sha256(routes_path.read_bytes()).hexdigest(),
            "ethnicity_sha256": hashlib.sha256(ethnicity_path.read_bytes()).hexdigest(),
            "vehicle_access_sha256": hashlib.sha256(vehicle_path.read_bytes()).hexdigest(),
        },
        "unknown_policy": "Unknown or unmatched area stratifiers remain explicit unknown groups.",
        "claim_boundary": (
            "These are area-level ecological access summaries of modelled aggregate expected courses. "
            "They are not individual attributes, patient outcomes, observed journeys, realised access, "
            "ethnicity effects, or evidence of service capability or capacity. Ethnicity groups are "
            "overlapping total-response categories; their weighted rows are not additive population cells."
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

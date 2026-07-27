#!/usr/bin/env python3
"""Materialise the minimal frozen aggregate demand weights required by CTW-050."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import polars as pl

from closer_to_whom.io import write_parquet_deterministic


def build_analysis_demand(
    demographic: pl.DataFrame,
    routes: pl.DataFrame,
    *,
    annual_expected_courses: float,
) -> pl.DataFrame:
    """Allocate expected courses to route origins using the frozen female-population rule."""
    if annual_expected_courses <= 0:
        raise ValueError("annual_expected_courses must be positive")
    origins = (
        routes.select("demand_cell_id")
        .unique()
        .with_columns(
            pl.col("demand_cell_id")
            .str.extract(r"^SA2-(\d{6})-aggregate$", 1)
            .alias("geography_code")
        )
        .sort("demand_cell_id")
    )
    if origins.height != 2_313 or origins["geography_code"].null_count():
        raise ValueError("Routes must contain exactly 2,313 canonical aggregate SA2 origins")
    frame = origins.join(
        demographic.select("geography_code", "population_2025", "female_population_2023"),
        on="geography_code",
        how="left",
    )
    if frame["population_2025"].null_count():
        raise ValueError("Demographic source does not cover every routed SA2")
    known = frame.filter(pl.col("female_population_2023").is_not_null())
    female_share = float(known["female_population_2023"].sum()) / float(
        known["population_2025"].sum()
    )
    frame = frame.with_columns(
        pl.when(pl.col("female_population_2023").is_not_null())
        .then(pl.col("female_population_2023").cast(pl.Float64))
        .otherwise(pl.col("population_2025").cast(pl.Float64) * female_share)
        .alias("allocation_weight")
    )
    total_weight = float(frame["allocation_weight"].sum())
    result = frame.with_columns(
        (pl.col("allocation_weight") / total_weight * annual_expected_courses).alias(
            "expected_courses"
        )
    ).select("demand_cell_id", "geography_code", "expected_courses")
    if not math.isclose(
        float(result["expected_courses"].sum()),
        annual_expected_courses,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError("Analysis demand does not reconcile to the national calibration")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demographic", type=Path, required=True)
    parser.add_argument("--routes", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    calibration = json.loads(args.calibration.read_text(encoding="utf-8"))
    frame = build_analysis_demand(
        pl.read_parquet(args.demographic),
        pl.read_parquet(args.routes),
        annual_expected_courses=float(calibration["annual_expected_courses"]),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_parquet_deterministic(frame, args.output, sort_by=("demand_cell_id",))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

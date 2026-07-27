"""Materialize the minimal aggregate SA2 origin contract required by routing."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl

from closer_to_whom.io import write_parquet_deterministic

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POINTS = ROOT / "data/derived/sa2-routing-points.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/baseline-route-origins.parquet"
DEFAULT_REPORT = ROOT / "reports/baseline-route-origins.json"


def materialize(
    points_path: Path = DEFAULT_POINTS,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, Any]:
    """Build stable aggregate route origins without unrelated equity attributes."""
    points = pl.read_parquet(points_path)
    required = {"geography_code", "latitude", "longitude"}
    if missing := required - set(points.columns):
        raise ValueError(f"Routing points missing columns: {sorted(missing)}")
    origins = points.select(
        pl.concat_str(
            pl.lit("SA2-"),
            pl.col("geography_code").cast(pl.String),
            pl.lit("-aggregate"),
        ).alias("demand_cell_id"),
        pl.col("latitude").cast(pl.Float64),
        pl.col("longitude").cast(pl.Float64),
    ).sort("demand_cell_id")
    if origins.height == 0:
        raise ValueError("At least one aggregate route origin is required")
    if origins["demand_cell_id"].n_unique() != origins.height:
        raise ValueError("Aggregate route origin identifiers must be unique")
    if origins.null_count().row(0) != (0, 0, 0):
        raise ValueError("Aggregate route origins cannot contain nulls")
    if not origins["latitude"].is_between(-48.0, -33.0, closed="both").all():
        raise ValueError("Aggregate route-origin latitude is outside Aotearoa New Zealand")
    if not origins["longitude"].is_between(165.0, 180.0, closed="both").all():
        raise ValueError("Aggregate route-origin longitude is outside Aotearoa New Zealand")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(origins, output_path, sort_by=("demand_cell_id",))
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_minimal_aggregate_route_origins",
        "source_id": "candidate.statsnz-sa2-2023-centroid-true",
        "origin_rows": origins.height,
        "parquet_fingerprint": fingerprint,
        "excluded_attributes": [
            "expected_courses",
            "deprivation",
            "ethnicity",
            "rurality",
        ],
        "claim_boundary": (
            "Rows are aggregate SA2 routing origins, not patients, residences, observed journeys, "
            "demand, eligibility, service capability, or equity measurements."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--points", type=Path, default=DEFAULT_POINTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(materialize(args.points, args.output, args.report), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

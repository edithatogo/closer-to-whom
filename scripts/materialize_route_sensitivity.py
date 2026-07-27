"""Materialise OSRM routes for weighted aggregate SA1 sensitivity origins."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.osrm import LocalOsrmTableClient
from closer_to_whom.routing import route_cache_fingerprint

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORIGINS = ROOT / "data/derived/sa2-population-weighted-origins.parquet"
DEFAULT_FACILITIES = ROOT / "data/derived/facility-registry.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/route-matrix-spatial-sensitivity.parquet"
DEFAULT_REPORT = ROOT / "reports/routing-spatial-sensitivity.json"


def materialize(
    origins_path: Path,
    facilities_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    osrm_base_url: str,
    osrm_version: str,
) -> dict[str, object]:
    origins = pl.read_parquet(origins_path)
    facilities = pl.read_parquet(facilities_path)
    route_origins = origins.with_columns(
        pl.col("routing_point_id").alias("demand_cell_id")
    )
    engine = LocalOsrmTableClient(osrm_base_url, osrm_version)
    routes = (
        engine.matrix(route_origins, facilities)
        .rename({"demand_cell_id": "routing_point_id"})
        .join(
            origins.select(
                "routing_point_id",
                "geography_code",
                "routing_weight",
                "routing_point_method",
            ),
            on="routing_point_id",
            how="left",
        )
        .select(
            "geography_code",
            "routing_point_id",
            "routing_weight",
            "routing_point_method",
            "facility_id",
            "one_way_km",
            "one_way_minutes",
            "route_engine",
            "route_engine_version",
            "route_is_approximation",
        )
        .sort(("geography_code", "routing_point_id", "facility_id"))
    )
    expected_rows = origins.height * facilities.height
    if routes.height != expected_rows:
        raise ValueError("Spatial sensitivity route matrix is incomplete")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        routes,
        output_path,
        sort_by=("geography_code", "routing_point_id", "facility_id"),
    )
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_local_osrm_spatial_sensitivity",
        "origin_rows": origins.height,
        "facility_rows": facilities.height,
        "route_rows": routes.height,
        "route_engine": "osrm",
        "route_engine_version": osrm_version,
        "route_is_approximation": False,
        "route_cache_fingerprint": route_cache_fingerprint(
            route_origins, facilities, engine
        ),
        "parquet_fingerprint": fingerprint,
        "claim_boundary": (
            "Routes connect aggregate SA1 centroid sensitivity origins to plausible public-source "
            "facilities. They are not observed journeys, patient locations, service capability, "
            "capacity, eligibility, or treatment use."
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
    parser.add_argument("--origins", type=Path, default=DEFAULT_ORIGINS)
    parser.add_argument("--facilities", type=Path, default=DEFAULT_FACILITIES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--osrm-base-url", required=True)
    parser.add_argument("--osrm-version", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.origins,
                args.facilities,
                args.output,
                args.report,
                osrm_base_url=args.osrm_base_url,
                osrm_version=args.osrm_version,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

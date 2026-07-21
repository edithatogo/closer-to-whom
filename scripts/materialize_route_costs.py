"""Materialise deterministic route matrices and an explicit blocked-state report."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.routing import (
    OfflineApproximationEngine,
    build_route_matrix,
    route_cache_fingerprint,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMAND = ROOT / "data/derived/demand-cells.parquet"
DEFAULT_FACILITIES = ROOT / "data/derived/facility-registry.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/route-matrix.parquet"
DEFAULT_REPORT = ROOT / "reports/routing-costs-flow.json"

_ROUTE_SCHEMA = {
    "demand_cell_id": pl.String,
    "facility_id": pl.String,
    "one_way_km": pl.Float64,
    "one_way_minutes": pl.Float64,
    "route_engine": pl.String,
    "route_engine_version": pl.String,
    "route_is_approximation": pl.Boolean,
}


def materialize(
    demand_path: Path = DEFAULT_DEMAND,
    facilities_path: Path = DEFAULT_FACILITIES,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, object]:
    """Build a route matrix, failing closed when upstream evidence registries are empty."""
    demand = pl.read_parquet(demand_path) if demand_path.exists() else pl.DataFrame()
    facilities = pl.read_parquet(facilities_path) if facilities_path.exists() else pl.DataFrame()
    if demand.height and facilities.height:
        engine = OfflineApproximationEngine()
        routes = build_route_matrix(demand, facilities, engine)
        status = "materialized_offline_approximation"
        cache_fingerprint = route_cache_fingerprint(demand, facilities, engine)
    else:
        routes = pl.DataFrame(schema=_ROUTE_SCHEMA)
        status = "blocked_pending_demand_and_service_registries"
        cache_fingerprint = None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        routes, output_path, sort_by=("demand_cell_id", "facility_id")
    )
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "retrieval_date": datetime.now(UTC).date().isoformat(),
        "status": status,
        "demand_rows": demand.height,
        "facility_rows": facilities.height,
        "route_rows": routes.height,
        "route_engine": "offline-approximation:1" if routes.height else None,
        "route_engine_version": "1" if routes.height else None,
        "route_is_approximation": True,
        "route_cache_fingerprint": cache_fingerprint,
        "parquet_fingerprint": fingerprint,
        "cost_categories": {
            "car": "pending_source_and_rate_receipts",
            "public_transport": "pending_source_and_rate_receipts",
            "ferry": "pending_source_and_rate_receipts",
            "walking_waiting_transfer": "pending_source_and_rate_receipts",
            "parking": "pending_source_and_rate_receipts",
            "fares": "pending_source_and_rate_receipts",
            "accommodation": "pending_source_and_rate_receipts",
            "provider_travel": "pending_source_and_rate_receipts",
        },
        "cost_claim_status": "blocked_pending_source_and_rate_receipts",
        "claim_boundary": (
            "Offline approximation routes are development fallbacks, not road-network evidence; "
            "no national burden or service claim is made while upstream registries are empty."
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
    parser.add_argument("--demand", type=Path, default=DEFAULT_DEMAND)
    parser.add_argument("--facilities", type=Path, default=DEFAULT_FACILITIES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(materialize(args.demand, args.facilities, args.output, args.report), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

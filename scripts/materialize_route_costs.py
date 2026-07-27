"""Materialise deterministic route matrices and an explicit blocked-state report."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.osrm import LocalOsrmTableClient
from closer_to_whom.routing import (
    OfflineApproximationEngine,
    build_route_matrix,
    route_cache_fingerprint,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMAND = ROOT / "data/derived/national-demand-cells.parquet"
DEFAULT_FACILITIES = ROOT / "data/derived/facility-registry.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/route-matrix.parquet"
DEFAULT_REPORT = ROOT / "reports/routing-costs-flow.json"
DEFAULT_COST_PARAMETERS = ROOT / "reports/travel-cost-parameters.json"

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
    *,
    osrm_base_url: str | None = None,
    osrm_version: str | None = None,
    cost_parameters_path: Path = DEFAULT_COST_PARAMETERS,
) -> dict[str, object]:
    """Build a route matrix, failing closed when upstream evidence registries are empty."""
    demand = pl.read_parquet(demand_path) if demand_path.exists() else pl.DataFrame()
    facilities = pl.read_parquet(facilities_path) if facilities_path.exists() else pl.DataFrame()
    if demand.height and facilities.height:
        if osrm_base_url:
            if not osrm_version:
                raise ValueError("osrm_version is required with osrm_base_url")
            engine = LocalOsrmTableClient(osrm_base_url, osrm_version)
            routes = engine.matrix(demand, facilities)
            status = "materialized_local_osrm_road_matrix"
            cache_fingerprint = route_cache_fingerprint(demand, facilities, engine)
        else:
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
    cost_parameters = (
        json.loads(cost_parameters_path.read_text(encoding="utf-8"))
        if cost_parameters_path.exists()
        else None
    )
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "retrieval_date": datetime.now(UTC).date().isoformat(),
        "status": status,
        "demand_rows": demand.height,
        "facility_rows": facilities.height,
        "route_rows": routes.height,
        "route_engine": routes["route_engine"][0] if routes.height else None,
        "route_engine_version": routes["route_engine_version"][0] if routes.height else None,
        "route_is_approximation": (
            bool(routes["route_is_approximation"].any()) if routes.height else None
        ),
        "route_cache_fingerprint": cache_fingerprint,
        "parquet_fingerprint": fingerprint,
        "cost_parameters_receipt": (
            cost_parameters_path.relative_to(ROOT).as_posix() if cost_parameters else None
        ),
        "cost_parameters_sha256": (
            hashlib.sha256(cost_parameters_path.read_bytes()).hexdigest()
            if cost_parameters
            else None
        ),
        "cost_categories": (
            {name: details["status"] for name, details in cost_parameters["categories"].items()}
            if cost_parameters
            else dict.fromkeys(
                (
                    "car",
                    "public_transport",
                    "ferry",
                    "walking_waiting_transfer",
                    "parking",
                    "fares",
                    "accommodation",
                    "provider_travel",
                ),
                "pending_source_and_rate_receipts",
            )
        ),
        "cost_claim_status": (
            cost_parameters["status"]
            if cost_parameters
            else "blocked_pending_source_and_rate_receipts"
        ),
        "claim_boundary": (
            "Offline approximation routes are development fallbacks, not road-network evidence; "
            "plausible facilities do not establish drug-specific capability or capacity, and no "
            "national burden or service claim is made before the pinned road matrix is complete."
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
    parser.add_argument("--cost-parameters", type=Path, default=DEFAULT_COST_PARAMETERS)
    parser.add_argument("--osrm-base-url")
    parser.add_argument("--osrm-version")
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.demand,
                args.facilities,
                args.output,
                args.report,
                osrm_base_url=args.osrm_base_url,
                osrm_version=args.osrm_version,
                cost_parameters_path=args.cost_parameters,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

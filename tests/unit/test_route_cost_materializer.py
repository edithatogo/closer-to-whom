from pathlib import Path
from runpy import run_path

import polars as pl

materialize = run_path(
    Path(__file__).parents[2] / "scripts" / "materialize_route_costs.py",
    run_name="route_cost_test",
)["materialize"]


def test_route_cost_materializer_is_blocked_without_upstream_registries(tmp_path: Path) -> None:
    report = materialize(
        tmp_path / "missing-demand.parquet",
        tmp_path / "missing-facilities.parquet",
        tmp_path / "routes.parquet",
        tmp_path / "routing.json",
        cost_parameters_path=tmp_path / "missing-cost-parameters.json",
    )
    assert report["status"] == "blocked_pending_demand_and_service_registries"
    assert report["route_rows"] == 0
    assert report["route_engine"] is None
    assert report["retrieval_date"]
    assert report["cost_claim_status"] == "blocked_pending_source_and_rate_receipts"
    assert set(report["cost_categories"]) == {
        "car",
        "public_transport",
        "ferry",
        "walking_waiting_transfer",
        "parking",
        "fares",
        "accommodation",
        "provider_travel",
    }


def test_route_cost_materializer_requires_version_for_osrm(tmp_path: Path) -> None:
    demand = tmp_path / "demand.parquet"
    facilities = tmp_path / "facilities.parquet"
    pl.DataFrame(
        {"demand_cell_id": ["d"], "latitude": [-41.0], "longitude": [174.0]}
    ).write_parquet(demand)
    pl.DataFrame({"facility_id": ["f"], "latitude": [-41.1], "longitude": [174.1]}).write_parquet(
        facilities
    )
    try:
        materialize(
            demand,
            facilities,
            tmp_path / "routes.parquet",
            tmp_path / "report.json",
            osrm_base_url="http://127.0.0.1:5000",
        )
    except ValueError as error:
        assert "osrm_version" in str(error)
    else:
        raise AssertionError("OSRM version must be required")

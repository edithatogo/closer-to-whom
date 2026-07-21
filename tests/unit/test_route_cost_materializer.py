from pathlib import Path
from runpy import run_path

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
    )
    assert report["status"] == "blocked_pending_demand_and_service_registries"
    assert report["route_rows"] == 0
    assert report["route_engine"] is None
    assert report["retrieval_date"]

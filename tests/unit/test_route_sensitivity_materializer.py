from __future__ import annotations

import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import polars as pl

_SPEC = spec_from_file_location(
    "materialize_route_sensitivity",
    Path(__file__).parents[2] / "scripts" / "materialize_route_sensitivity.py",
)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)


def test_spatial_sensitivity_preserves_weights_and_origin_ids(tmp_path: Path) -> None:
    origins = pl.DataFrame(
        {
            "geography_code": ["100100"],
            "routing_point_id": ["SA2-100100-SA1-1"],
            "routing_weight": [1.0],
            "routing_point_method": ["sa1"],
            "latitude": [-41.0],
            "longitude": [174.0],
        }
    )
    facilities = pl.DataFrame(
        {
            "facility_id": ["F1"],
            "latitude": [-41.1],
            "longitude": [174.1],
        }
    )
    origins_path = tmp_path / "origins.parquet"
    facilities_path = tmp_path / "facilities.parquet"
    origins.write_parquet(origins_path)
    facilities.write_parquet(facilities_path)

    class FakeClient:
        identity = "osrm:test"

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def matrix(self, route_origins: pl.DataFrame, _facilities: pl.DataFrame) -> pl.DataFrame:
            return pl.DataFrame(
                {
                    "demand_cell_id": route_origins["demand_cell_id"],
                    "facility_id": ["F1"],
                    "one_way_km": [10.0],
                    "one_way_minutes": [12.0],
                    "route_engine": ["osrm"],
                    "route_engine_version": ["test"],
                    "route_is_approximation": [False],
                }
            )

    _MODULE.LocalOsrmTableClient = FakeClient
    _MODULE.route_cache_fingerprint = lambda *_args: "cache"
    report = _MODULE.materialize(
        origins_path,
        facilities_path,
        tmp_path / "routes.parquet",
        tmp_path / "report.json",
        osrm_base_url="http://127.0.0.1:5000",
        osrm_version="test",
    )
    routes = pl.read_parquet(tmp_path / "routes.parquet")
    assert routes["routing_point_id"].to_list() == ["SA2-100100-SA1-1"]
    assert routes["routing_weight"].to_list() == [1.0]
    assert report["route_rows"] == 1
    assert json.loads((tmp_path / "report.json").read_text())["route_is_approximation"] is False

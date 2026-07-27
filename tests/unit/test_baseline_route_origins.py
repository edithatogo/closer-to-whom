import importlib.util
from pathlib import Path

import polars as pl
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "materialize_baseline_route_origins",
    Path(__file__).parents[2] / "scripts" / "materialize_baseline_route_origins.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
materialize = _MODULE.materialize


def test_materializes_minimal_stable_route_origins(tmp_path: Path) -> None:
    points = tmp_path / "points.parquet"
    pl.DataFrame(
        {
            "geography_code": ["100200", "100100"],
            "latitude": [-41.2, -36.8],
            "longitude": [174.8, 175.1],
            "deprivation_decile": [10, 1],
        }
    ).write_parquet(points)

    output = tmp_path / "origins.parquet"
    report = materialize(points, output, tmp_path / "report.json")
    origins = pl.read_parquet(output)

    assert origins.columns == ["demand_cell_id", "latitude", "longitude"]
    assert origins["demand_cell_id"].to_list() == [
        "SA2-100100-aggregate",
        "SA2-100200-aggregate",
    ]
    assert report["origin_rows"] == 2
    assert "deprivation" in report["excluded_attributes"]


def test_rejects_duplicate_or_out_of_range_origins(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.parquet"
    pl.DataFrame(
        {
            "geography_code": ["100100", "100100"],
            "latitude": [-36.8, -36.9],
            "longitude": [174.8, 174.9],
        }
    ).write_parquet(duplicate)
    with pytest.raises(ValueError, match="unique"):
        materialize(duplicate, tmp_path / "out.parquet", tmp_path / "report.json")

    invalid = tmp_path / "invalid.parquet"
    pl.DataFrame(
        {
            "geography_code": ["100100"],
            "latitude": [0.0],
            "longitude": [174.8],
        }
    ).write_parquet(invalid)
    with pytest.raises(ValueError, match="latitude"):
        materialize(invalid, tmp_path / "out.parquet", tmp_path / "report.json")

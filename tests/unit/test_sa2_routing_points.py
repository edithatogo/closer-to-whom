import importlib.util
from pathlib import Path

import polars as pl
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "materialize_sa2_routing_points",
    Path(__file__).parents[2] / "scripts" / "materialize_sa2_routing_points.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
materialize = _MODULE.materialize


def test_materializes_paginated_population_centroids(tmp_path: Path) -> None:
    population = tmp_path / "population.parquet"
    pl.DataFrame({"AREA_POPES_SUB_004": ["100100", "100200"]}).write_parquet(population)

    def fetcher(offset: int, _page_size: int) -> dict:
        code = "100100" if offset == 0 else "100200"
        return {
            "features": [
                {
                    "attributes": {
                        "SA22023_V1_00": code,
                        "SA22023_V1_00_NAME": f"Area {code}",
                    },
                    "centroid": {"x": 174.0 + offset, "y": -41.0},
                }
            ],
            "exceededTransferLimit": offset == 0,
        }

    output = tmp_path / "points.parquet"
    result = materialize(
        population,
        output,
        tmp_path / "report.json",
        fetcher=fetcher,
        page_size=1,
    )
    points = pl.read_parquet(output)
    assert result["routing_point_count"] == 2
    assert points["routing_weight"].to_list() == [1.0, 1.0]
    assert points["routing_point_id"].to_list() == [
        "SA2-100100-centroid",
        "SA2-100200-centroid",
    ]


def test_rejects_missing_population_centroid(tmp_path: Path) -> None:
    population = tmp_path / "population.parquet"
    pl.DataFrame({"AREA_POPES_SUB_004": ["100100", "100200"]}).write_parquet(population)

    def fetcher(_offset: int, _page_size: int) -> dict:
        return {
            "features": [
                {
                    "attributes": {
                        "SA22023_V1_00": "100100",
                        "SA22023_V1_00_NAME": "Area",
                    },
                    "centroid": {"x": 174.0, "y": -41.0},
                }
            ],
            "exceededTransferLimit": False,
        }

    with pytest.raises(ValueError, match="100200"):
        materialize(
            population,
            tmp_path / "points.parquet",
            tmp_path / "report.json",
            fetcher=fetcher,
        )

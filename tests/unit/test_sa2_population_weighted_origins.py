from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import polars as pl

_SPEC = spec_from_file_location(
    "materialize_sa2_population_weighted_origins",
    Path(__file__).parents[2] / "scripts" / "materialize_sa2_population_weighted_origins.py",
)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
assign_sa2 = _MODULE.assign_sa2
build_origins = _MODULE.build_origins


def test_assign_sa2_uses_polygon_containment() -> None:
    sa1 = [
        {"sa1_code": "1", "population_2023": 10, "longitude": 0.5, "latitude": 0.5},
        {"sa1_code": "2", "population_2023": 20, "longitude": 1.5, "latitude": 0.5},
    ]
    sa2 = [
        {
            "properties": {"SA22023_V1_00": "100100"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
        },
        {
            "properties": {"SA22023_V1_00": "100200"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]],
            },
        },
    ]
    assert [row["geography_code"] for row in assign_sa2(sa1, sa2)] == [
        "100100",
        "100200",
    ]


def test_build_origins_weights_and_fallback() -> None:
    population = pl.DataFrame(
        {"geography_code": ["100100", "100200"], "population_2025": [100, 0]}
    )
    baseline = pl.DataFrame(
        {
            "geography_code": ["100100", "100200"],
            "routing_point_id": ["base-1", "base-2"],
            "latitude": [0.5, 1.5],
            "longitude": [0.5, 1.5],
        }
    )
    assigned = [
        {
            "sa1_code": "1",
            "population_2023": 25,
            "longitude": 0.4,
            "latitude": 0.4,
            "geography_code": "100100",
        },
        {
            "sa1_code": "2",
            "population_2023": 75,
            "longitude": 0.6,
            "latitude": 0.6,
            "geography_code": "100100",
        },
    ]
    result = build_origins(population, baseline, assigned)
    assert result.filter(pl.col("geography_code") == "100100")[
        "routing_weight"
    ].to_list() == [0.25, 0.75]
    fallback = result.filter(pl.col("geography_code") == "100200")
    assert fallback["routing_weight"].item() == 1.0
    assert fallback["routing_point_method"].item() == "true_centroid_zero_sa1_population_fallback"

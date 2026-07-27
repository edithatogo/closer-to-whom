from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import polars as pl

_SPEC = spec_from_file_location(
    "materialize_national_demand_cells",
    Path(__file__).parents[2] / "scripts" / "materialize_national_demand_cells.py",
)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
build_demand_cells = _MODULE.build_demand_cells


def test_build_demand_cells_reconciles_and_preserves_unknowns() -> None:
    demographic = pl.DataFrame(
        {
            "geography_code": ["100100", "100200"],
            "population_2025": [100, 20],
            "female_population_2023": [60, None],
        },
        schema={
            "geography_code": pl.String,
            "population_2025": pl.Int64,
            "female_population_2023": pl.Int64,
        },
    )
    routing = pl.DataFrame(
        {
            "geography_code": ["100100", "100200"],
            "routing_point_id": ["p1", "p2"],
            "latitude": [-41.0, -42.0],
            "longitude": [174.0, 175.0],
            "routing_point_method": ["true", "true"],
        }
    )
    rurality = pl.DataFrame(
        {
            "geography_code": ["100100", "100200"],
            "urban_rural_name": ["Urban", None],
            "rurality_status": ["matched", "unknown"],
        },
        schema={
            "geography_code": pl.String,
            "urban_rural_name": pl.String,
            "rurality_status": pl.String,
        },
    )
    deprivation = pl.DataFrame(
        {
            "geography_code": ["100100", "100200"],
            "deprivation_decile": [9, None],
            "deprivation_status": ["matched", "unknown"],
        },
        schema={
            "geography_code": pl.String,
            "deprivation_decile": pl.Int8,
            "deprivation_status": pl.String,
        },
    )
    result, audit = build_demand_cells(
        demographic,
        routing,
        rurality,
        deprivation,
        annual_expected_courses=12.0,
    )
    assert result.height == 2
    assert result["expected_courses"].sum() == 12.0
    assert result["deprivation_quintile"].to_list() == [5, None]
    assert result["rurality"].to_list() == ["Urban", "unknown"]
    assert audit["female_population_fallback_rows"] == 1
    assert audit["deprivation_explicit_unknown_rows"] == 1

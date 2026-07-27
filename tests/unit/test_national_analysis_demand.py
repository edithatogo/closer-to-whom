import importlib.util
from pathlib import Path

import polars as pl

_SPEC = importlib.util.spec_from_file_location(
    "materialize_national_analysis_demand",
    Path(__file__).parents[2] / "scripts" / "materialize_national_analysis_demand.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_analysis_demand = _MODULE.build_analysis_demand


def test_analysis_demand_uses_explicit_female_population_fallback() -> None:
    routes = pl.DataFrame(
        {"demand_cell_id": [f"SA2-{code:06d}-aggregate" for code in range(100_000, 102_313)]}
    )
    demographic = pl.DataFrame(
        {
            "geography_code": [f"{code:06d}" for code in range(100_000, 102_313)],
            "population_2025": [100] * 2_313,
            "female_population_2023": [50] * 2_312 + [None],
        }
    )
    result = build_analysis_demand(
        demographic,
        routes,
        annual_expected_courses=10.0,
    )
    assert result.height == 2_313
    assert abs(result["expected_courses"].sum() - 10.0) < 1e-9
    assert result["expected_courses"].null_count() == 0

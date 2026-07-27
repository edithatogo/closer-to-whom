from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import polars as pl

_SPEC = spec_from_file_location(
    "materialize_sa2_deprivation",
    Path(__file__).parents[2] / "scripts" / "materialize_sa2_deprivation.py",
)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
materialize = _MODULE.materialize
read_nzdep_xlsx = _MODULE.read_nzdep_xlsx


def test_read_nzdep_workbook_uses_declared_columns() -> None:
    source = Path(".tmp/NZDep2023_WgtAvSA2.xlsx")
    if not source.exists():
        return
    frame = read_nzdep_xlsx(source)
    assert frame.height == 2321
    assert frame["deprivation_decile"].drop_nulls().min() == 1
    assert frame["deprivation_decile"].drop_nulls().max() == 10


def test_materialize_preserves_blank_and_unmatched_as_unknown(tmp_path: Path) -> None:
    source = Path(".tmp/NZDep2023_WgtAvSA2.xlsx")
    if not source.exists():
        return
    workbook = read_nzdep_xlsx(source)
    matched = workbook.filter(pl.col("deprivation_decile").is_not_null()).row(0, named=True)
    blank = workbook.filter(pl.col("deprivation_decile").is_null()).row(0, named=True)
    population = pl.DataFrame(
        {
            "AREA_POPES_SUB_004": [
                int(matched["geography_code"]),
                int(blank["geography_code"]),
                999999,
            ],
            "OBS_VALUE": [100, 0, 25],
        }
    )
    population_path = tmp_path / "population.parquet"
    population.write_parquet(population_path)
    report = materialize(
        source,
        population_path,
        tmp_path / "deprivation.parquet",
        tmp_path / "report.json",
    )
    result = pl.read_parquet(tmp_path / "deprivation.parquet")
    assert report["matched_rows"] == 1
    assert report["unknown_source_value_blank_rows"] == 1
    assert report["unknown_sa2_version_mismatch_rows"] == 1
    assert result["deprivation_status"].to_list() == [
        "matched_nzdep2023_sa2_code",
        "unknown_source_value_blank",
        "unknown_sa2_version_mismatch",
    ]

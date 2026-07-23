import importlib.util
from pathlib import Path

import polars as pl
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "materialize_stats_nz_population",
    Path(__file__).parents[2] / "scripts" / "materialize_stats_nz_population.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
materialize = _MODULE.materialize


def test_materialize_aggregate_csv(tmp_path: Path) -> None:
    source = tmp_path / "population.csv"
    source.write_text("area,year,population\nA,2025,10\n", encoding="utf-8")
    output = tmp_path / "population.parquet"
    report = tmp_path / "quality.json"
    materialize(source, output, report)
    assert pl.read_parquet(output).height == 1
    assert '"rows": 1' in report.read_text(encoding="utf-8")


def test_materialize_rejects_individual_columns(tmp_path: Path) -> None:
    source = tmp_path / "population.csv"
    source.write_text("patient_id,population\n1,10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="forbidden"):
        materialize(source, tmp_path / "out.parquet", tmp_path / "quality.json")

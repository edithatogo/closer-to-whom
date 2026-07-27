import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "materialize_national_demand_calibration",
    Path(__file__).parents[2] / "scripts" / "materialize_national_demand_calibration.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
materialize = _MODULE.materialize


def _write_assumptions(path: Path, *, uptake: float = 0.631) -> None:
    path.write_text(
        "assumptions:\n"
        "  - {id: D03, value: 0.15, source_ids: [her2]}\n"
        f"  - {{id: D04, value: {uptake}, source_ids: [uptake]}}\n"
        "  - {id: D05, value: 0.93, source_ids: [stage]}\n"
        "  - {id: D06, value: 3660, source_ids: [incidence]}\n",
        encoding="utf-8",
    )


def test_materializes_source_backed_national_scenario(tmp_path: Path) -> None:
    assumptions = tmp_path / "assumptions.yaml"
    report = tmp_path / "report.json"
    _write_assumptions(assumptions)
    result = materialize(assumptions, report)
    assert result["annual_expected_courses"] == pytest.approx(322.16967)
    assert result["status"] == "materialized_national_scenario_not_spatially_allocated"
    assert result["source_ids"] == ["her2", "incidence", "stage", "uptake"]
    assert json.loads(report.read_text(encoding="utf-8"))[
        "annual_expected_courses"
    ] == pytest.approx(322.16967)


def test_rejects_invalid_proportion(tmp_path: Path) -> None:
    assumptions = tmp_path / "assumptions.yaml"
    _write_assumptions(assumptions, uptake=1.1)
    with pytest.raises(ValueError, match="D04"):
        materialize(assumptions, tmp_path / "report.json")

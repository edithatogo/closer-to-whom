import importlib.util
from pathlib import Path


def _module():
    path = Path(__file__).parents[2] / "scripts/check_national_scientific_outputs.py"
    spec = importlib.util.spec_from_file_location("check_national_scientific_outputs", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_national_reports_form_a_claim_bounded_scientific_set() -> None:
    receipt = _module().validate()
    assert receipt["status"] == "passed"
    assert receipt["configuration_count"] == 5
    assert "spatial_structural" in receipt["uncertainty_types"]
    assert len(receipt["report_sha256"]) == 9
    assert "distributional-equity" in receipt["report_names"]
    assert "capacity-cost-perspective" in receipt["report_names"]
    assert "resilience-sensitivity" in receipt["report_names"]
    assert "optimisation-comparison" in receipt["report_names"]

    report = _module().REPORT_DIR.joinpath("optimisation-comparison.json")
    import json

    optimisation = json.loads(report.read_text(encoding="utf-8"))
    assert optimisation["robust_analysis"]["optimality"] == "exact_within_declared_scope"
    assert optimisation["multiobjective_frontier"]["frontier"]
    assert all(row["solver_status"] == "optimal" for row in optimisation["rows"])
    assert all(row["optimality_gap"] == 0.0 for row in optimisation["rows"])

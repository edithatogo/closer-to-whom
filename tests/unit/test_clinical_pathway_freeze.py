from pathlib import Path
from runpy import run_path

audit = run_path(
    Path(__file__).parents[2] / "scripts" / "check_clinical_pathway_freeze.py",
    run_name="clinical_pathway_test",
)["audit"]


def test_synthetic_pathway_audit_is_safe_and_non_evidentiary(tmp_path: Path) -> None:
    report = audit(tmp_path / "clinical-pathway-freeze.json")
    assert report["status"] == "synthetic_fixtures_valid_non_evidentiary"
    assert report["safety_errors"] == []
    assert report["clinically_reviewed_count"] == 0

from pathlib import Path
from runpy import run_path

audit = run_path(
    Path(__file__).parents[2] / "scripts" / "check_clinical_pathway_freeze.py",
    run_name="clinical_pathway_test",
)["audit"]


def test_synthetic_pathway_audit_is_safe_but_blocked(tmp_path: Path) -> None:
    report = audit(tmp_path / "clinical-pathway-freeze.json")
    assert report["status"] == "blocked_pending_clinical_review"
    assert report["safety_errors"] == []
    assert report["clinically_reviewed_count"] == 0

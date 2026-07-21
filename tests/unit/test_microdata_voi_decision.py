from pathlib import Path
from runpy import run_path

validate = run_path(
    str(Path(__file__).parents[2] / "scripts" / "check_microdata_voi_decision.py"),
    run_name="microdata_voi_decision_test",
)["validate"]


def test_microdata_decision_is_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "decision.yaml"
    path.write_text(
        """status: blocked_on_ctw050
microdata_build_dependency: false
required_outputs: [voi_summary, research_design_comparison, governance_burden_assessment, ethics_scope_boundary]
output_contracts:
  voi_summary: blocked_pending_governance_decision
  research_design_comparison: blocked_pending_governance_decision
  governance_burden_assessment: blocked_pending_governance_decision
  ethics_scope_boundary: blocked_pending_governance_decision
decision_receipts: []
claim_boundary: No individual, confidential, row-level health data; separate protocol and ethics/HDEC scope determination required.
""",
        encoding="utf-8",
    )
    assert validate(path) == []


def test_determined_decision_requires_receipts(tmp_path: Path) -> None:
    path = tmp_path / "decision.yaml"
    path.write_text(
        """status: determined
microdata_build_dependency: false
required_outputs: [voi_summary, research_design_comparison, governance_burden_assessment, ethics_scope_boundary]
output_contracts:
  voi_summary: ready
  research_design_comparison: ready
  governance_burden_assessment: ready
  ethics_scope_boundary: determined
decision_receipts: [one]
claim_boundary: No individual, confidential, row-level health data; separate protocol and ethics/HDEC scope determination required.
""",
        encoding="utf-8",
    )
    assert any("one receipt per" in failure for failure in validate(path))

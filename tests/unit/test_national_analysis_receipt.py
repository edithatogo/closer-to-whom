from pathlib import Path
from runpy import run_path

validate = run_path(
    str(Path(__file__).parents[2] / "scripts" / "check_national_analysis_receipt.py"),
    run_name="national_analysis_receipt_test",
)["validate"]


def test_blocked_national_analysis_is_explicit(tmp_path: Path) -> None:
    path = tmp_path / "analysis.yaml"
    path.write_text(
        """status: blocked_on_prerequisites
prerequisites:
  service_census: pending
  public_input_freeze: pending
  clinical_pathway_review: pending
  route_costs: pending
  governance_review: pending
required_outputs: [scenario_summary, optimisation_frontier, uncertainty_analysis, mcda_outputs, voi_outputs]
analysis_receipts: []
claim_boundary: blocked; synthetic only; no observed capacity, clinical, or operational claims
""",
        encoding="utf-8",
    )
    assert validate(path) == []


def test_reviewable_analysis_requires_all_receipts(tmp_path: Path) -> None:
    path = tmp_path / "analysis.yaml"
    path.write_text(
        """status: ready_for_review
prerequisites:
  service_census: complete
  public_input_freeze: complete
  clinical_pathway_review: complete
  route_costs: complete
  governance_review: complete
required_outputs: [scenario_summary, optimisation_frontier, uncertainty_analysis, mcda_outputs, voi_outputs]
analysis_receipts: [one]
claim_boundary: blocked; synthetic only; no observed capacity, clinical, or operational claims
""",
        encoding="utf-8",
    )
    assert any("one receipt per" in failure for failure in validate(path))

import importlib.util
from pathlib import Path

import yaml

_SPEC = importlib.util.spec_from_file_location(
    "check_national_analysis_receipt",
    Path(__file__).parents[2] / "scripts" / "check_national_analysis_receipt.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate = _MODULE.validate


def test_ready_to_run_requires_complete_prerequisites_and_ready_outputs(tmp_path: Path) -> None:
    path = tmp_path / "receipt.yaml"
    payload = {
        "status": "ready_to_run",
        "prerequisites": {
            "service_census": "complete",
            "public_input_freeze": "complete",
            "clinical_pathway_review": "complete",
            "route_costs": "complete",
            "governance_review": "complete",
        },
        "required_outputs": [
            "scenario_summary",
            "optimisation_frontier",
            "uncertainty_analysis",
            "mcda_outputs",
            "voi_outputs",
        ],
        "output_contracts": {
            "scenario_summary": "ready_to_materialize",
            "optimisation_frontier": "ready_to_materialize",
            "uncertainty_analysis": "ready_to_materialize",
            "mcda_outputs": "ready_to_materialize",
            "voi_outputs": "ready_to_materialize",
        },
        "analysis_receipts": [],
        "claim_boundary": (
            "Publication remains blocked; synthetic fixtures do not establish observed capacity, "
            "clinical eligibility, or operational feasibility."
        ),
    }
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    assert validate(path) == []

    payload["output_contracts"]["scenario_summary"] = "blocked_pending_prerequisites"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    assert "runnable outputs must be ready_to_materialize" in validate(path)


def test_completed_accepts_out_of_scope_aggregate_governance(tmp_path: Path) -> None:
    path = tmp_path / "receipt.yaml"
    payload = {
        "status": "completed",
        "prerequisites": {
            "service_census": "complete",
            "public_input_freeze": "complete",
            "clinical_pathway_review": "complete",
            "route_costs": "complete",
            "governance_review": "out_of_scope_for_public_aggregate_harness",
        },
        "required_outputs": [
            "scenario_summary",
            "optimisation_frontier",
            "uncertainty_analysis",
            "mcda_outputs",
            "voi_outputs",
        ],
        "output_contracts": {
            "scenario_summary": "complete",
            "optimisation_frontier": "complete",
            "uncertainty_analysis": "complete",
            "mcda_outputs": "complete",
            "voi_outputs": "complete",
        },
        "analysis_receipts": [f"receipt-{index}" for index in range(5)],
        "claim_boundary": (
            "Publication remains blocked; synthetic fixtures do not establish observed capacity, "
            "clinical eligibility, or operational feasibility."
        ),
    }
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    assert validate(path) == []

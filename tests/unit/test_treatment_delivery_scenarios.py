import importlib.util
import json
from pathlib import Path


def _module():
    path = Path(__file__).parents[2] / "scripts/materialize_treatment_delivery_scenarios.py"
    spec = importlib.util.spec_from_file_location("materialize_treatment_delivery_scenarios", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scenario_register_preserves_unknown_capability(tmp_path: Path) -> None:
    output = tmp_path / "scenarios.json"
    _module().materialize(Path("scenarios/scenario-catalogue.yaml"), output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "materialized_evidence_bounded_scenario_register"
    assert payload["scenario_count"] == 11
    assert {row["capability_state"] for row in payload["scenarios"]} == {"unknown"}
    assert {row["clinical_eligibility_state"] for row in payload["scenarios"]} == {"not_estimated"}
    assert all("resource_profiles" in row for row in payload["scenarios"])
    assert {row["patient_travel_status"] for row in payload["scenarios"]} == {"not_estimated"}
    assert any(payload_row["resource_profiles"] for payload_row in payload["scenarios"])

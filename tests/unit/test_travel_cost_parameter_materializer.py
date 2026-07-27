from __future__ import annotations

import json
from pathlib import Path
from runpy import run_path

import yaml

materialize = run_path(
    Path(__file__).parents[2] / "scripts" / "materialize_travel_cost_parameters.py",
    run_name="travel_cost_parameter_test",
)["materialize"]


def test_materializer_preserves_supported_and_unknown_cost_categories(tmp_path: Path) -> None:
    assumptions = {
        "assumptions": [
            {"id": parameter_id, "value": index}
            for index, parameter_id in enumerate(("K01", "K02", "K03", "K04", "K05"))
        ]
    }
    assumptions_path = tmp_path / "assumptions.yaml"
    assumptions_path.write_text(yaml.safe_dump(assumptions), encoding="utf-8")
    output = tmp_path / "costs.json"

    report = materialize(assumptions_path, output)

    assert report["categories"]["car"]["status"] == "source_backed_scenario"
    assert report["categories"]["parking"]["status"] == "location_specific_rate_pending"
    assert report["categories"]["provider_travel"]["parameter_ids"] == []
    assert "K03 remains illustrative" in report["primary_analysis_rule"]
    assert json.loads(output.read_text(encoding="utf-8")) == report


def test_materializer_fails_closed_when_required_assumption_is_missing(tmp_path: Path) -> None:
    assumptions_path = tmp_path / "assumptions.yaml"
    assumptions_path.write_text(
        yaml.safe_dump({"assumptions": [{"id": "K01", "value": 0.37}]}),
        encoding="utf-8",
    )

    try:
        materialize(assumptions_path, tmp_path / "costs.json")
    except ValueError as error:
        assert "Missing required cost assumptions" in str(error)
    else:
        raise AssertionError("An incomplete cost freeze must fail closed")

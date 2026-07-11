from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from closer_to_whom.scenarios import active_scenarios, ensure_unique_scenarios, load_scenarios
from closer_to_whom.synthetic import synthetic_scenarios


def test_scenario_catalogue_round_trip_and_active_filter(tmp_path: Path) -> None:
    scenarios = synthetic_scenarios()
    catalogue = tmp_path / "scenarios.yaml"
    catalogue.write_text(
        yaml.safe_dump(
            {"scenarios": [item.model_dump(mode="json") for item in reversed(scenarios)]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    loaded = load_scenarios(catalogue)
    assert {item.scenario_id for item in loaded} == {item.scenario_id for item in scenarios}
    active = active_scenarios(loaded)
    assert tuple(item.scenario_id for item in active) == tuple(
        sorted(item.scenario_id for item in loaded if item.active)
    )


def test_scenario_catalogue_rejects_missing_root_and_duplicates(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("not_scenarios: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="top-level scenarios"):
        load_scenarios(invalid)

    scenario = synthetic_scenarios()[0]
    with pytest.raises(ValueError, match="unique"):
        ensure_unique_scenarios((scenario, scenario))

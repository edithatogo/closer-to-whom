"""Scenario loading, validation, and deterministic catalogues."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import yaml

from closer_to_whom.models import Scenario


def load_scenarios(path: Path) -> tuple[Scenario, ...]:
    """Load scenarios from a versioned YAML catalogue."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "scenarios" not in payload:
        raise ValueError("Scenario catalogue requires a top-level scenarios list")
    scenarios = tuple(Scenario.model_validate(item) for item in payload["scenarios"])
    ensure_unique_scenarios(scenarios)
    return scenarios


def ensure_unique_scenarios(scenarios: Iterable[Scenario]) -> None:
    """Require stable, unique scenario identifiers."""
    ids = [scenario.scenario_id for scenario in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("Scenario IDs must be unique")


def active_scenarios(scenarios: Iterable[Scenario]) -> tuple[Scenario, ...]:
    """Return active scenarios in stable order."""
    return tuple(sorted((item for item in scenarios if item.active), key=lambda item: item.scenario_id))

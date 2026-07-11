#!/usr/bin/env python3
"""Validate assumptions, source, scenario, schema, and Conductor contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from closer_to_whom.models import SourceRecord, UncertaintyParameter
from closer_to_whom.scenarios import load_scenarios

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _require_unique(items: list[dict[str, Any]], key: str, label: str) -> None:
    values = [str(item[key]) for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label} values: {values}")


def check_assumptions() -> None:
    payload = _load_yaml(ROOT / "assumptions/assumptions.yaml")
    assumptions = payload["assumptions"]
    _require_unique(assumptions, "id", "assumption ID")
    required = {"id", "domain", "name", "value", "status", "source_ids", "uncertainty", "rationale"}
    for item in assumptions:
        if missing := required - set(item):
            raise ValueError(f"Assumption {item.get('id')} missing: {sorted(missing)}")
        if not item["source_ids"]:
            raise ValueError(f"Assumption {item['id']} has no source IDs")


def check_distributions() -> None:
    payload = _load_yaml(ROOT / "assumptions/distributions.yaml")
    parameters = payload["parameters"]
    _require_unique(parameters, "parameter_id", "uncertainty parameter ID")
    for item in parameters:
        model_fields = {
            key: value for key, value in item.items() if key in UncertaintyParameter.model_fields
        }
        UncertaintyParameter.model_validate(model_fields)


def check_sources() -> None:
    payload = _load_yaml(ROOT / "data/public/source-registry.yaml")
    sources = payload["sources"]
    _require_unique(sources, "source_id", "source ID")
    for item in sources:
        model = SourceRecord.model_validate(
            {
                "source_id": item["source_id"],
                "title": item["title"],
                "publisher": item["publisher"],
                "url": item["url"],
                "retrieved_on": item["retrieved_on"],
                "licence_state": item["licence_state"],
                "redistribution_allowed": item["redistribution_allowed"],
                "notes": item.get("status", ""),
            }
        )
        if model.source_id.startswith("candidate.") and model.redistribution_allowed:
            raise ValueError(f"Candidate source cannot be redistributable: {model.source_id}")


def check_scenarios() -> None:
    load_scenarios(ROOT / "scenarios/scenario-catalogue.yaml")


def check_conductor() -> None:
    project = _load_yaml(ROOT / "conductor/project.yaml")
    state = _load_yaml(ROOT / "conductor/state.yaml")
    graph = json.loads((ROOT / "conductor/task-graph.json").read_text(encoding="utf-8"))
    if project["project_id"] != state["project_id"]:
        raise ValueError("Conductor project and state IDs differ")
    node_ids = {node["id"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError(f"Conductor edge references unknown node: {edge}")
    if not state.get("active_track"):
        raise ValueError("Conductor state requires an active track")


def main() -> None:
    check_assumptions()
    check_distributions()
    check_sources()
    check_scenarios()
    check_conductor()
    print("All repository contracts passed.")


if __name__ == "__main__":
    main()

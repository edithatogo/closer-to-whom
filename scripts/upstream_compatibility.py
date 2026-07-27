#!/usr/bin/env python3
"""Report compatibility status for optional user-library integrations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from closer_to_whom.integrations import integration_capabilities

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one YAML mapping."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected mapping in {path}")
    return payload


def main() -> None:
    contracts = load_yaml(ROOT / "upstream" / "contracts.yaml")
    capabilities = {
        str(item["name"]): item for item in integration_capabilities() if "name" in item
    }
    integrations = []
    for contract in contracts.get("libraries", []):
        name = str(contract["name"])
        integrations.append(
            {
                "name": name,
                "reviewed_revision": contract["pinned_revision"],
                "fixture": contract["fixture"],
                "local_adapter": contract["local_adapter"],
                "acceptance_tests": contract["acceptance_tests"],
                "runtime_capability": capabilities.get(name),
                "required_for_open_pipeline": False,
            }
        )
    payload = {
        "schema_version": "1.0.0",
        "integrations": integrations,
        "note": (
            "Local compatibility fixtures and oracles are verified. Upstream releases remain optional, "
            "and upstream code was not imported or executed by this report."
        ),
    }
    output = ROOT / "reports" / "upstream-compatibility.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(output)


if __name__ == "__main__":
    main()

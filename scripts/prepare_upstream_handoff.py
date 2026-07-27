#!/usr/bin/env python3
"""Summarise replayable upstream-library work without claiming remote publication."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "upstream" / "contracts.yaml"
REGISTRY = ROOT / "upstream" / "registry.yaml"


def load(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected mapping in {path}")
    return payload


def main() -> int:
    contracts = load(CONTRACTS)
    registry = load(REGISTRY)
    rows = []
    for item in contracts.get("libraries", []):
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "library": item["name"],
                "repository": item["repository"],
                "reviewed_revision": item["pinned_revision"],
                "issue_material": item["issue"],
                "fixture": item["fixture"],
                "local_adapter": item["local_adapter"],
                "acceptance_tests": item["acceptance_tests"],
                "remote_state": "metadata_and_revision_identity_verified",
                "upstream_execution_state": "not_executed",
            }
        )
    output = ROOT / "release" / "upstream-handoff.json"
    output.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "remote_receipt": registry["remote_receipt"],
                "fixture_receipt": registry["fixture_receipt"],
                "libraries": rows,
                "claim_boundary": registry["claim_boundary"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

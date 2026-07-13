#!/usr/bin/env python3
"""Validate optional upstream integration contracts and local fallback boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from closer_to_whom.integrations import integration_capabilities

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "ecosystem" / "tool-contracts.yaml"
ISSUES = ROOT / "upstream" / "issues"


def validate() -> list[str]:
    failures: list[str] = []
    capabilities = integration_capabilities()
    names = [str(item.get("name", "")) for item in capabilities]
    if len(names) != len(set(names)):
        failures.append("integration capability names must be unique")
    for item in capabilities:
        name = str(item.get("name", ""))
        for key in ("mechanism", "role"):
            if not item.get(key):
                failures.append(f"{name}: capability {key} is required")
        if item.get("required_for_open_pipeline") is not False:
            failures.append(f"{name}: optional integrations cannot be required for open pipeline")
    payload = yaml.safe_load(TOOLS.read_text(encoding="utf-8")) or {}
    tools = payload.get("tools", []) if isinstance(payload, dict) else []
    for tool in tools:
        if not isinstance(tool, dict):
            failures.append("tool contract must be a mapping")
            continue
        if tool.get("required") is not False:
            failures.append(f"{tool.get('repository', '<unknown>')}: tool must be optional")
        if not tool.get("executables"):
            failures.append(f"{tool.get('repository', '<unknown>')}: executable list is required")
    if not ISSUES.is_dir():
        failures.append("upstream/issues directory is missing")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Upstream compatibility failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated optional upstream compatibility contracts and local fallback boundaries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

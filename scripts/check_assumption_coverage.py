#!/usr/bin/env python3
"""Validate the assumptions register as a first-class model contract."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "assumptions" / "assumptions.yaml"
REQUIRED_KEYS = {"id", "status"}
ALLOWED_STATUSES = {
    "fixed",
    "base_case",
    "uncertain",
    "structural",
    "policy_counterfactual",
    "synthetic_fixture",
    "future_validation",
    "not_applicable",
    "active",
    "provisional",
}


def rows(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        candidate = payload.get("assumptions", payload)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, dict):
            result = []
            for key, value in candidate.items():
                row = dict(value) if isinstance(value, dict) else {"statement": value}
                row.setdefault("id", key)
                result.append(row)
            return result
    return []


def statement(row: dict[str, Any]) -> str:
    for key in ("statement", "assumption", "base_assumption", "description", "text"):
        if row.get(key):
            return str(row[key]).strip()
    return ""


def main() -> int:
    payload = yaml.safe_load(PATH.read_text(encoding="utf-8"))
    assumptions = rows(payload)
    failures: list[str] = []
    if len(assumptions) < 20:
        failures.append(f"expected a comprehensive register; found only {len(assumptions)} entries")
    seen: set[str] = set()
    prefixes: set[str] = set()
    for index, row in enumerate(assumptions):
        missing = REQUIRED_KEYS - row.keys()
        if missing:
            failures.append(f"row {index}: missing {sorted(missing)}")
        identifier = str(row.get("id", "")).strip()
        if not identifier:
            failures.append(f"row {index}: blank id")
        elif identifier in seen:
            failures.append(f"duplicate id: {identifier}")
        else:
            seen.add(identifier)
            prefixes.add(identifier[:1])
        if not statement(row):
            failures.append(f"{identifier or index}: no assumption statement")
        status = str(row.get("status", "")).strip()
        if status and status not in ALLOWED_STATUSES:
            # Existing projects may use richer statuses; require only nonblank and expose them.
            if len(status) < 3:
                failures.append(f"{identifier}: malformed status {status!r}")
    expected_prefixes = set("ADFCTEOUR")
    missing_prefixes = expected_prefixes - prefixes
    if missing_prefixes:
        failures.append(f"missing assumption domains/prefixes: {sorted(missing_prefixes)}")
    if failures:
        print("Assumption-register failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Validated {len(assumptions)} explicit assumptions across {len(prefixes)} domains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

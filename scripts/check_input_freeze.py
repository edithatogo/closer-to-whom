#!/usr/bin/env python3
"""Validate the public aggregate input-freeze manifest without fetching data."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "public" / "input-freeze.yaml"
REGISTRY = ROOT / "data" / "public" / "source-registry.yaml"
FROZEN = {"frozen", "active"}
REQUIRED = {
    "input_id",
    "title",
    "source_ids",
    "version",
    "licence_state",
    "evidence_grade",
    "status",
}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(
    manifest_path: Path = MANIFEST,
    registry_path: Path = REGISTRY,
) -> list[str]:
    """Return manifest failures; pending inputs are valid but cannot be used as frozen data."""
    manifest = _load(manifest_path)
    registry = _load(registry_path)
    source_rows = registry.get("sources", [])
    known_sources = {
        str(row.get("source_id"))
        for row in source_rows
        if isinstance(row, dict) and row.get("source_id")
    }
    inputs = manifest.get("inputs", [])
    failures: list[str] = []
    if not isinstance(inputs, list) or not inputs:
        return ["input-freeze manifest must contain at least one input"]
    seen: set[str] = set()
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            failures.append(f"input {index}: expected a mapping")
            continue
        missing = REQUIRED - item.keys()
        identifier = str(item.get("input_id", f"row-{index}"))
        if missing:
            failures.append(f"{identifier}: missing {sorted(missing)}")
        if identifier in seen:
            failures.append(f"duplicate input_id: {identifier}")
        seen.add(identifier)
        source_ids = item.get("source_ids", [])
        if not isinstance(source_ids, list) or not source_ids:
            failures.append(f"{identifier}: source_ids must be a non-empty list")
        else:
            unknown = set(map(str, source_ids)) - known_sources
            if unknown:
                failures.append(f"{identifier}: unknown source IDs {sorted(unknown)}")
        status = str(item.get("status", "")).lower()
        if status in FROZEN:
            if not item.get("version"):
                failures.append(f"{identifier}: frozen input requires version")
            if str(item.get("licence_state", "")).lower() in {"", "unknown", "pending"}:
                failures.append(f"{identifier}: frozen input requires licence_state")
            if not item.get("retrieval_receipt"):
                failures.append(f"{identifier}: frozen input requires retrieval_receipt")
            if not item.get("evidence_grade") or str(item["evidence_grade"]).lower() == "pending":
                failures.append(f"{identifier}: frozen input requires evidence_grade")
    freeze_date = manifest.get("freeze_date")
    if str(manifest.get("status", "")).lower() in FROZEN:
        if not freeze_date:
            failures.append("frozen manifest requires freeze_date")
        else:
            try:
                date.fromisoformat(str(freeze_date))
            except ValueError:
                failures.append("freeze_date must be an ISO date")
        pending = [
            str(item.get("input_id"))
            for item in inputs
            if str(item.get("status", "")).lower() not in FROZEN
        ]
        if pending:
            failures.append(f"frozen manifest contains pending inputs: {pending}")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Input-freeze failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated public input-freeze manifest; pending inputs remain non-frozen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

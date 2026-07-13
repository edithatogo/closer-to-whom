#!/usr/bin/env python3
"""Validate registry links to immutable public-source retrieval receipts."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "public" / "source-registry.yaml"
RECEIPT_ROOT = ROOT / "data" / "raw"
RECEIPT_STATUSES = {"captured", "adjudicated", "active", "frozen"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _records(payload: object) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    rows = payload.get("sources", [])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _url(item: dict[str, Any]) -> str:
    return str(item.get("url", item.get("landing_page", item.get("source_url", ""))))


def _receipt_path(item: dict[str, Any], repository_root: Path = ROOT) -> Path | None:
    declared = item.get("receipt_path", item.get("retrieval_receipt"))
    if not declared:
        return None
    path = (repository_root / str(declared)).resolve()
    try:
        path.relative_to(repository_root)
    except ValueError as exc:
        raise ValueError("receipt path must remain inside the repository") from exc
    return path


def _validate_receipt(item: dict[str, Any], path: Path) -> list[str]:
    source_id = str(item.get("source_id", item.get("id", "")))
    failures: list[str] = []
    display_path = (
        path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
    )
    if not path.is_file():
        return [f"{source_id}: declared receipt does not exist: {display_path}"]
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{source_id}: unreadable receipt {display_path}: {exc}"]
    if not isinstance(receipt, dict):
        return [f"{source_id}: receipt must be a JSON object"]
    if receipt.get("source_id") != source_id:
        failures.append(f"{source_id}: receipt source_id does not match registry")
    if receipt.get("url") != _url(item):
        failures.append(f"{source_id}: receipt URL does not match registry")
    digest = str(receipt.get("sha256", ""))
    if not SHA256.fullmatch(digest):
        failures.append(f"{source_id}: receipt sha256 must be 64 lowercase hex characters")
    try:
        byte_count = int(receipt["bytes"])
        retrieved = int(receipt["retrieved_unix_seconds"])
    except KeyError, TypeError, ValueError:
        failures.append(f"{source_id}: receipt needs integer bytes and retrieved_unix_seconds")
    else:
        if byte_count < 0:
            failures.append(f"{source_id}: receipt byte count cannot be negative")
        if retrieved <= 0:
            failures.append(f"{source_id}: receipt retrieval timestamp must be positive")
    if not receipt.get("content_type"):
        failures.append(f"{source_id}: receipt content_type is required")
    output_path = str(receipt.get("output_path", ""))
    if not output_path:
        failures.append(f"{source_id}: receipt output_path is required")
    return failures


def validate(registry_path: Path = REGISTRY) -> list[str]:
    """Return all source-receipt contract failures without fetching network data."""
    payload = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    items = _records(payload)
    failures: list[str] = []
    for item in items:
        source_id = str(item.get("source_id", item.get("id", "")))
        status = str(item.get("status", "")).lower()
        repository_root = (
            ROOT if registry_path.resolve() == REGISTRY.resolve() else registry_path.parent
        )
        receipt_path = _receipt_path(item, repository_root)
        if status in RECEIPT_STATUSES and receipt_path is None:
            failures.append(f"{source_id}: captured source must declare receipt_path")
        if receipt_path is not None:
            failures.extend(_validate_receipt(item, receipt_path))
        retrieved_on = item.get("retrieved_on")
        if retrieved_on is not None:
            try:
                date.fromisoformat(str(retrieved_on))
            except ValueError:
                failures.append(f"{source_id}: retrieved_on must be an ISO date")
        if status in RECEIPT_STATUSES and not item.get("evidence_grade"):
            failures.append(f"{source_id}: captured source must declare evidence_grade")
        if "healthpoint" in source_id.lower() and item.get("redistribution_allowed") is True:
            licence = str(item.get("licence_state", "")).lower()
            if "licensed" not in licence or item.get("licence_evidence") is None:
                failures.append(
                    f"{source_id}: Healthpoint redistribution requires explicit licence evidence"
                )
        parsed = urlparse(_url(item))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            failures.append(f"{source_id}: source URL is invalid")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Source-receipt failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated source registry receipt links; pending candidates remain explicitly pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

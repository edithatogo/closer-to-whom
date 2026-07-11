#!/usr/bin/env python3
"""Validate public-source registry, licensing, and fail-closed publication state."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "public" / "source-registry.yaml"


def records(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("sources", "records", "datasets"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        # keyed mapping fallback
        result = []
        for key, value in payload.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("id", key)
                result.append(item)
        return result
    return []


def first(item: dict[str, Any], *keys: str, default: object = None) -> object:
    for key in keys:
        if key in item:
            return item[key]
    return default


def main() -> int:
    payload = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    items = records(payload)
    failures: list[str] = []
    ids: set[str] = set()
    for index, item in enumerate(items):
        identifier = str(first(item, "id", "source_id", default=f"row-{index}"))
        if identifier in ids:
            failures.append(f"duplicate source id: {identifier}")
        ids.add(identifier)
        url = str(first(item, "url", "landing_page", "source_url", default=""))
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in {"https", "http"} or not parsed.netloc:
                failures.append(f"{identifier}: invalid URL {url!r}")
        data_class = str(first(item, "data_class", "classification", default="")).lower()
        if any(
            token in data_class
            for token in ("individual", "patient", "confidential", "identifiable")
        ):
            failures.append(f"{identifier}: prohibited data class {data_class!r}")
        redistributable = bool(first(item, "redistributable", "publishable", default=False))
        licence = str(first(item, "licence", "license", "licence_status", default="")).lower()
        if redistributable and not licence:
            failures.append(f"{identifier}: redistributable without licence status")
        live = bool(first(item, "enabled", "active", "live", default=False))
        verified = bool(first(item, "verified", "reviewed", default=False))
        if live and not verified:
            failures.append(f"{identifier}: enabled before source verification")
        if "healthpoint" in identifier.lower() and redistributable and "licensed" not in licence:
            failures.append(
                f"{identifier}: Healthpoint payload marked redistributable without explicit licence"
            )
    if not items:
        failures.append("source registry contains no records")
    if failures:
        print("Source-registry failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Validated {len(items)} source-registry entries with fail-closed publication rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

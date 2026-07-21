#!/usr/bin/env python3
"""Report public GitHub metadata drift without changing the frozen catalogue."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ecosystem" / "github-repositories.yaml"
SNAPSHOT = ROOT / "ecosystem" / "snapshot-provenance.yaml"
MetadataFetcher = Callable[[str], dict[str, Any]]


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def _repository_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if parsed.netloc != "github.com" or path.count("/") != 1:
        raise ValueError(f"Expected a public GitHub repository URL: {url}")
    return path


def fetch_metadata(repository_path: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository_path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "closer-to-whom-drift"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"GitHub metadata was not an object: {repository_path}")
    return payload


def build_report(
    registry_path: Path = REGISTRY,
    snapshot_path: Path = SNAPSHOT,
    *,
    fetcher: MetadataFetcher = fetch_metadata,
) -> dict[str, Any]:
    registry = _load(registry_path)
    snapshot = _load(snapshot_path)
    repositories = registry.get("repositories", [])
    if not isinstance(repositories, list):
        raise TypeError("Ecosystem registry repositories must be a list")
    changes: list[dict[str, Any]] = []
    unavailable: list[dict[str, str]] = []
    fields = ("default_branch", "archived", "fork", "license_spdx", "updated_at")
    for item in repositories:
        if not isinstance(item, dict) or not item.get("repository"):
            continue
        repository_url = str(item["repository"])
        repository_path = _repository_path(repository_url)
        try:
            current = fetcher(repository_path)
        except (OSError, urllib.error.URLError, ValueError) as exc:
            unavailable.append({"repository": repository_path, "error": str(exc)})
            continue
        observed = {
            "default_branch": current.get("default_branch"),
            "archived": current.get("archived"),
            "fork": current.get("fork"),
            "license_spdx": (current.get("license") or {}).get("spdx_id"),
            "updated_at": current.get("updated_at"),
        }
        frozen = {field: item.get(field) for field in fields}
        differences = {
            field: {"frozen": frozen[field], "current": observed[field]}
            for field in fields
            if frozen[field] is not None and observed[field] != frozen[field]
        }
        if differences:
            changes.append({"repository": repository_path, "differences": differences})
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "snapshot_date": snapshot.get("snapshot_date"),
        "repository_count": len(repositories),
        "changes": changes,
        "unavailable": unavailable,
        "claim_boundary": (
            "Metadata drift only. This report does not refresh the frozen catalogue, assess suitability, "
            "endorse external code, or import/build/execute external repositories."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Refresh authenticated public metadata receipts for LIB-010 repositories."""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "upstream" / "contracts.yaml"
MetadataFetcher = Callable[[str], tuple[dict[str, Any], dict[str, Any]]]


def repository_path(url: str) -> str:
    """Return owner/name for an exact public GitHub repository URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if parsed.scheme != "https" or parsed.netloc != "github.com" or path.count("/") != 1:
        raise ValueError(f"Expected an HTTPS GitHub repository URL: {url}")
    return path


def fetch_github(repository: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fetch repository and default-branch commit metadata without exposing credentials."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "closer-to-whom-upstream-receipt",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def get(url: str) -> dict[str, Any]:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError(f"GitHub response was not an object: {url}")
        return payload

    metadata = get(f"https://api.github.com/repos/{repository}")
    commit = get(f"https://api.github.com/repos/{repository}/commits/{metadata['default_branch']}")
    return metadata, commit


def build_receipt(
    contracts_path: Path = CONTRACTS,
    *,
    fetcher: MetadataFetcher = fetch_github,
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """Build a receipt and fail if a live revision differs from the reviewed pin."""
    payload = yaml.safe_load(contracts_path.read_text(encoding="utf-8")) or {}
    libraries = payload.get("libraries", []) if isinstance(payload, dict) else []
    if not isinstance(libraries, list):
        raise TypeError("upstream contract libraries must be a list")
    records: list[dict[str, Any]] = []
    for contract in sorted(libraries, key=lambda item: str(item["name"])):
        repository = repository_path(str(contract["repository"]))
        metadata, commit = fetcher(repository)
        observed_revision = str(commit.get("sha", ""))
        pinned_revision = str(contract["pinned_revision"])
        if observed_revision != pinned_revision:
            raise RuntimeError(
                f"{repository}: live default-branch revision {observed_revision} differs from reviewed pin "
                f"{pinned_revision}; review and update the contract explicitly"
            )
        records.append(
            {
                "name": contract["name"],
                "repository": repository,
                "default_branch": metadata.get("default_branch"),
                "revision": observed_revision,
                "archived": metadata.get("archived"),
                "fork": metadata.get("fork"),
                "license_spdx": (metadata.get("license") or {}).get("spdx_id"),
                "updated_at": metadata.get("updated_at"),
                "pushed_at": metadata.get("pushed_at"),
            }
        )
    return {
        "schema_version": "1.0.0",
        "retrieved_at": retrieved_at or datetime.now(UTC).isoformat(),
        "retrieval_method": "GitHub REST API with authenticated token when available",
        "repositories": records,
        "claim_boundary": (
            "Public repository metadata and revision identity only. This receipt does not import, build, "
            "execute, endorse, release, or assess the suitability or licence compatibility of upstream code."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_receipt()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

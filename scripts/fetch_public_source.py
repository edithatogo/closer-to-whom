#!/usr/bin/env python3
"""Explicit, allowlisted public-source retrieval for the local environment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from closer_to_whom.source_fetch import FetchPolicy, SourceFetchError, fetch_public_source

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "public" / "source-registry.yaml"


def _records(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ("sources", "records", "datasets"):
            if isinstance(payload.get(key), list):
                return [row for row in payload[key] if isinstance(row, dict)]
        return [dict(value, id=key) for key, value in payload.items() if isinstance(value, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = _records(yaml.safe_load(REGISTRY.read_text(encoding="utf-8")))
    match = next((row for row in rows if str(row.get("id", row.get("source_id", ""))) == args.source_id), None)
    if match is None:
        print(f"unknown source id: {args.source_id}", file=sys.stderr)
        return 2
    url = str(match.get("url", match.get("landing_page", match.get("source_url", ""))))
    if not url:
        print("source does not declare a direct retrievable URL", file=sys.stderr)
        return 2
    from urllib.parse import urlsplit

    host = urlsplit(url).hostname or ""
    output = args.output or ROOT / "data" / "cache" / args.source_id / Path(urlsplit(url).path).name
    policy = FetchPolicy(allow_network=args.allow_network, allowed_hosts=(host,))
    try:
        receipt = fetch_public_source(
            source_id=args.source_id,
            url=url,
            destination=output,
            policy=policy,
        )
    except SourceFetchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(receipt.as_json(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

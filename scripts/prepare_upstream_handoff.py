#!/usr/bin/env python3
"""Summarise replayable upstream-library work without claiming remote publication."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "upstream" / "registry.yaml"


def main() -> int:
    payload: Any = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}
    libraries = payload.get("libraries", payload if isinstance(payload, list) else [])
    if isinstance(libraries, dict):
        libraries = [
            dict(value, id=key) if isinstance(value, dict) else {"id": key, "state": value}
            for key, value in libraries.items()
        ]
    rows = []
    for item in libraries if isinstance(libraries, list) else []:
        if not isinstance(item, dict):
            continue
        identifier = str(item.get("id", item.get("name", "unknown")))
        issue_candidates = (
            list((ROOT / "upstream" / "issues").glob(f"*{identifier}*"))
            if (ROOT / "upstream" / "issues").exists()
            else []
        )
        patch_candidates = (
            list((ROOT / "upstream" / "patches").glob(f"*{identifier}*"))
            if (ROOT / "upstream" / "patches").exists()
            else []
        )
        rows.append(
            {
                "library": identifier,
                "remote_state": "unverified",
                "issue_material": [p.relative_to(ROOT).as_posix() for p in issue_candidates],
                "patch_material": [p.relative_to(ROOT).as_posix() for p in patch_candidates],
                "local_compatibility_implementation": item.get(
                    "local_compatibility_implementation"
                ),
            }
        )
    output = ROOT / "release" / "upstream-handoff.json"
    output.write_text(
        json.dumps({"schema_version": "1.0.0", "libraries": rows}, indent=2, sort_keys=True) + "\n"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

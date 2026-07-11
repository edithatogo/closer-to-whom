#!/usr/bin/env python3
"""Validate every committed YAML and JSON control-plane document."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PREFIXES = (".venv/", "dist/", "site/", "artifacts/demo/")


def tracked_files() -> list[Path]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def assert_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite JSON number at {path}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            assert_finite(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            assert_finite(item, f"{path}.{key}")


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(EXCLUDED_PREFIXES) or not path.is_file():
            continue
        try:
            if path.suffix == ".json":
                payload = json.loads(path.read_text(encoding="utf-8"))
                assert_finite(payload)
            elif path.suffix in {".yaml", ".yml"}:
                list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001 - report all parser failures together
            failures.append(f"{relative}: {exc}")
    if failures:
        print("Machine-readable document failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("All tracked JSON and YAML documents parse cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

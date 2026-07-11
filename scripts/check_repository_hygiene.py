#!/usr/bin/env python3
"""Enforce repository hygiene, privacy boundaries, and generated-artifact policy."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}
FORBIDDEN_NAMES = {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
MAX_FILE_BYTES = 10 * 1024 * 1024
LARGE_ALLOWLIST_PREFIXES = ("schemas/arrow/",)


def main() -> int:
    raw = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    failures: list[str] = []
    for token in raw.split(b"\0"):
        if not token:
            continue
        relative = token.decode()
        path = ROOT / relative
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden tracked file: {relative}")
        if (
            path.is_file()
            and path.stat().st_size > MAX_FILE_BYTES
            and not relative.startswith(LARGE_ALLOWLIST_PREFIXES)
        ):
            failures.append(f"unexpected tracked file >10 MiB: {relative}")
        if relative.startswith((".venv/", "site/", "dist/", "artifacts/demo/")):
            failures.append(f"generated/runtime directory tracked: {relative}")
    if failures:
        print("Repository hygiene failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Repository hygiene checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail closed on prohibited data paths, identifiers, and licence states."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_TRACKED_PREFIXES = ("data/raw/", "data/private/", "data/licensed/")
SENSITIVE_HEADER = re.compile(
    r"(^|[,;\t])\s*(nhi|patient_?id|full_?name|residential_?address)\s*([,;\t]|$)", re.IGNORECASE
)
NHI_LIKE = re.compile(r"\b[A-HJ-NP-Z]{3}[0-9]{4}\b")
TEXT_SUFFIXES = {".csv", ".tsv", ".json", ".yaml", ".yml", ".md", ".txt", ".py", ".toml"}
NHI_SCAN_PREFIXES = ("data/", "artifacts/", "release/", "tests/fixtures/", "inputs/")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], check=True, capture_output=True, text=True
    )
    return result.stdout.splitlines()


def main() -> None:
    failures: list[str] = []
    for relative in tracked_files():
        if relative.startswith(PROHIBITED_TRACKED_PREFIXES):
            failures.append(f"Prohibited tracked path: {relative}")
        path = ROOT / relative
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if SENSITIVE_HEADER.search(first_line):
            failures.append(f"Sensitive row-level header in {relative}")
        # Restrict identifier scanning to data-bearing paths. Source code and configuration
        # legitimately contain tokens such as GCH2023 and Ruff rule identifiers that match
        # the coarse lexical pattern but cannot be patient records.
        if relative.startswith(NHI_SCAN_PREFIXES) and NHI_LIKE.search(text):
            failures.append(f"NHI-like token in {relative}")

    sources = yaml.safe_load((ROOT / "data/public/source-registry.yaml").read_text())
    for source in sources["sources"]:
        if source["licence_state"] != "open" and source["redistribution_allowed"]:
            failures.append(f"Non-open source marked redistributable: {source['source_id']}")

    if failures:
        raise SystemExit("\n".join(failures))
    print("Privacy and licence checks passed.")


if __name__ == "__main__":
    main()

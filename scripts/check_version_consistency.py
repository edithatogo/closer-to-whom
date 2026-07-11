#!/usr/bin/env python3
"""Check release version consistency across machine-readable metadata."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = str(pyproject["project"]["version"])
    failures: list[str] = []

    init_text = (ROOT / "src" / "closer_to_whom" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)', init_text)
    if match and match.group(1) != version:
        failures.append(f"package __version__={match.group(1)} != pyproject={version}")

    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    citation_version = str(citation.get("version", ""))
    if citation_version and citation_version != version:
        failures.append(f"CITATION.cff={citation_version} != pyproject={version}")

    codemeta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))
    codemeta_version = str(codemeta.get("version", ""))
    if codemeta_version and codemeta_version != version:
        failures.append(f"codemeta.json={codemeta_version} != pyproject={version}")

    if failures:
        print("Version consistency failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Release metadata is consistent at version {version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

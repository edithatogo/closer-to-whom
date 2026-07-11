#!/usr/bin/env python3
"""Generate a deterministic lightweight CycloneDX-compatible component inventory."""

from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path


def main() -> None:
    components = []
    for distribution in sorted(importlib.metadata.distributions(), key=lambda item: item.metadata["Name"].lower()):
        name = distribution.metadata["Name"]
        if not name:
            continue
        components.append(
            {
                "type": "library",
                "name": name,
                "version": distribution.version,
                "purl": f"pkg:pypi/{name.lower()}@{distribution.version}",
            }
        )
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {"component": {"type": "application", "name": "closer-to-whom", "version": "0.2.0"}},
        "components": components,
    }
    output = Path("release/sbom.cdx.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

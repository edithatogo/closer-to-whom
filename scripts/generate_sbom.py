#!/usr/bin/env python3
"""Generate a deterministic lightweight CycloneDX-compatible component inventory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any


def build_sbom(artifact: Path | None = None) -> dict[str, object]:
    """Return a deterministic CycloneDX-compatible software inventory."""
    components: list[dict[str, str]] = []
    distributions = sorted(
        importlib.metadata.distributions(),
        key=lambda item: (item.metadata.get("Name") or "").lower(),
    )
    for distribution in distributions:
        name = distribution.metadata.get("Name")
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
    metadata: dict[str, Any] = {
        "component": {"type": "application", "name": "closer-to-whom", "version": "0.2.0"}
    }
    if artifact is not None:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        metadata["artifact"] = {
            "path": artifact.as_posix(),
            "sha256": digest,
            "type": "python-wheel",
        }
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": metadata,
        "components": components,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("release/sbom.cdx.json"),
        help="Destination path for the generated CycloneDX JSON document.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        help="Exact built artifact to bind into the SBOM metadata.",
    )
    return parser.parse_args()


def main() -> None:
    """Write the software bill of materials to the requested path."""
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_sbom(args.artifact), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output)


if __name__ == "__main__":
    main()

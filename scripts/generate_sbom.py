#!/usr/bin/env python3
"""Generate a deterministic lightweight CycloneDX-compatible component inventory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from datetime import UTC, datetime
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
        "timestamp": datetime(1970, 1, 1, tzinfo=UTC).isoformat().replace("+00:00", "Z"),
        "component": {"type": "application", "name": "closer-to-whom", "version": "0.2.0"},
    }
    properties: list[dict[str, str]] = []
    artifact_digest = "0" * 64
    if artifact is not None:
        artifact_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        properties = [
            {"name": "closer-to-whom:artifact:path", "value": artifact.as_posix()},
            {"name": "closer-to-whom:artifact:sha256", "value": artifact_digest},
            {"name": "closer-to-whom:artifact:type", "value": "python-wheel"},
        ]
    return {
        "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "serialNumber": f"urn:uuid:{artifact_digest[:8]}-{artifact_digest[8:12]}-4{artifact_digest[13:16]}-8{artifact_digest[17:20]}-{artifact_digest[20:32]}",
        "metadata": metadata,
        "components": components,
        "properties": properties,
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

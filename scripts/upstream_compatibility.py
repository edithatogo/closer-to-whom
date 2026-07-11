#!/usr/bin/env python3
"""Report compatibility status for optional user-library integrations."""

from __future__ import annotations

import json
from pathlib import Path

from closer_to_whom.integrations import integration_capabilities


def main() -> None:
    payload = {
        "schema_version": "1.0.0",
        "integrations": integration_capabilities(),
        "note": "Absence is supported through local compatibility adapters; upstream releases are optional.",
    }
    output = Path("reports/upstream-compatibility.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

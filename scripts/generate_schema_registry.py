#!/usr/bin/env python3
"""Generate deterministic Arrow schema registry files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow as pa

from closer_to_whom.contracts import DEMAND_SCHEMA, FACILITY_SCHEMA, RESULT_SCHEMA

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {"demand": DEMAND_SCHEMA, "facility": FACILITY_SCHEMA, "result": RESULT_SCHEMA}


def _fingerprint(schema: pa.Schema) -> str:
    """Hash the canonical Arrow IPC schema bytes."""
    return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()


def _describe(schema: pa.Schema) -> dict[str, object]:
    return {
        "fingerprint": _fingerprint(schema),
        "fields": [
            {"name": field.name, "type": str(field.type), "nullable": field.nullable}
            for field in schema
        ],
        "metadata": {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in sorted((schema.metadata or {}).items())
        },
    }


def generate(output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    index: dict[str, object] = {"schema_registry_version": "1.0.0", "schemas": {}}
    index_schemas: dict[str, object] = {}
    for name, schema in sorted(SCHEMAS.items()):
        ipc_path = output / f"{name}.schema.arrow"
        ipc_path.write_bytes(schema.serialize().to_pybytes())
        json_path = output / f"{name}.schema.json"
        payload = _describe(schema)
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        index_schemas[name] = {
            "ipc": ipc_path.name,
            "json": json_path.name,
            "fingerprint": payload["fingerprint"],
        }
        written.extend((ipc_path, json_path))
    index["schemas"] = index_schemas
    index_path = output / "index.json"
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(index_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "schemas" / "arrow")
    args = parser.parse_args()
    for path in generate(args.output):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

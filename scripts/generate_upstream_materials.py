#!/usr/bin/env python3
"""Generate deterministic LIB-010 issue bodies and Parquet compatibility fixtures."""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import version
from pathlib import Path
from typing import Any

import polars as pl
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "upstream" / "contracts.yaml"
RECEIPT = ROOT / "upstream" / "receipts" / "compatibility-fixtures.json"


def load_contracts(path: Path = CONTRACTS) -> list[dict[str, Any]]:
    """Load the canonical upstream contracts."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    libraries = payload.get("libraries", []) if isinstance(payload, dict) else []
    if not isinstance(libraries, list):
        raise TypeError("upstream contract libraries must be a list")
    return [item for item in libraries if isinstance(item, dict)]


def fixture_row(contract: dict[str, Any]) -> dict[str, str]:
    """Build one aggregate, non-sensitive compatibility record."""
    interface = contract["interface"]
    return {
        "contract_version": "1.0.0",
        "library": str(contract["name"]),
        "case_id": "aggregate-compatibility-001",
        "input_json": json.dumps(
            {"fields": str(interface["input"]), "synthetic": True},
            sort_keys=True,
            separators=(",", ":"),
        ),
        "expected_json": json.dumps(
            {"fields": str(interface["output"]), "status": "contract_only"},
            sort_keys=True,
            separators=(",", ":"),
        ),
        "boundary": "synthetic aggregate contract fixture; no person-level or licensed payload",
    }


def render_issue(contract: dict[str, Any]) -> str:
    """Render a patch-ready issue body from one contract."""
    interface = contract["interface"]
    operations = "\n".join(f"- `{operation}`" for operation in interface["operations"])
    acceptance = "\n".join(f"- `{command}`" for command in contract["acceptance_tests"])
    return f"""<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: {interface["summary"]}

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

{interface["summary"]}

Operations:

{operations}

Input contract: {interface["input"]}.

Output contract: {interface["output"]}.

## Compatibility fixture

- Deterministic Parquet fixture: `{contract["fixture"]}`
- Local compatibility oracle: `{contract["local_adapter"]}`
- Pinned repository identity: `{contract["pinned_revision"]}` on `{contract["default_branch"]}`

## Acceptance

{acceptance}
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
"""


def generate(root: Path = ROOT) -> dict[str, Any]:
    """Write all generated issue bodies, fixtures, and their hash receipt."""
    libraries = load_contracts(root / "upstream" / "contracts.yaml")
    fixture_records: list[dict[str, Any]] = []
    for contract in sorted(libraries, key=lambda item: str(item["name"])):
        issue_path = root / str(contract["issue"])
        issue_path.parent.mkdir(parents=True, exist_ok=True)
        issue_path.write_text(render_issue(contract), encoding="utf-8", newline="\n")

        fixture_path = root / str(contract["fixture"])
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        frame = pl.DataFrame([fixture_row(contract)]).select(
            "contract_version", "library", "case_id", "input_json", "expected_json", "boundary"
        )
        frame.write_parquet(fixture_path, compression="zstd", statistics=True)
        fixture_records.append(
            {
                "library": contract["name"],
                "path": fixture_path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
                "rows": frame.height,
                "columns": frame.columns,
            }
        )
    receipt = {
        "schema_version": "1.0.0",
        "generator": "scripts/generate_upstream_materials.py",
        "polars_version": version("polars"),
        "fixtures": fixture_records,
        "claim_boundary": (
            "Synthetic aggregate compatibility fixtures only; no upstream code was imported or executed."
        ),
    }
    receipt_path = root / "upstream" / "receipts" / "compatibility-fixtures.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return receipt


def main() -> int:
    receipt = generate()
    print(f"Generated {len(receipt['fixtures'])} upstream fixtures and issue bodies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

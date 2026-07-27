#!/usr/bin/env python3
"""Validate LIB-010 contracts, fixtures, proposals, receipts, and fallback boundaries."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import polars as pl
import yaml

from closer_to_whom.integrations import integration_capabilities

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "upstream" / "contracts.yaml"
REGISTRY = ROOT / "upstream" / "registry.yaml"
EXPECTED_NAMES = {
    "authentext",
    "fyi-cli",
    "healthpoint-rs",
    "innovate",
    "kairos",
    "mars",
    "open_social_data",
    "sourceright",
    "voiage",
}
FIXTURE_COLUMNS = [
    "contract_version",
    "library",
    "case_id",
    "input_json",
    "expected_json",
    "boundary",
]
REVISION = re.compile(r"^[0-9a-f]{40}$")


def load_mapping(path: Path) -> dict[str, Any]:
    """Load one YAML mapping."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate() -> list[str]:
    """Return all compatibility failures without mutating the repository."""
    failures: list[str] = []
    contracts = load_mapping(CONTRACTS)
    registry = load_mapping(REGISTRY)
    libraries = contracts.get("libraries", [])
    registry_libraries = registry.get("libraries", [])
    if not isinstance(libraries, list) or not isinstance(registry_libraries, list):
        return ["contract and registry libraries must be lists"]

    names = [str(item.get("name", "")) for item in libraries if isinstance(item, dict)]
    if set(names) != EXPECTED_NAMES or len(names) != len(EXPECTED_NAMES):
        failures.append("contracts must contain each of the nine expected libraries exactly once")
    registry_names = [
        str(item.get("name", "")) for item in registry_libraries if isinstance(item, dict)
    ]
    if registry_names != names:
        failures.append("registry library order and identity must match canonical contracts")

    capabilities = {
        str(item.get("name", "")): item
        for item in integration_capabilities()
        if isinstance(item, dict)
    }
    for name in EXPECTED_NAMES:
        capability = capabilities.get(name)
        if capability is None:
            failures.append(f"{name}: optional capability declaration is missing")
        elif capability.get("required_for_open_pipeline") is not False:
            failures.append(f"{name}: upstream integration must remain optional")

    receipt_path = ROOT / str(registry.get("remote_receipt", ""))
    fixture_receipt_path = ROOT / str(registry.get("fixture_receipt", ""))
    if not receipt_path.is_file():
        failures.append("authenticated remote receipt is missing")
        receipt: dict[str, Any] = {}
    else:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not fixture_receipt_path.is_file():
        failures.append("fixture hash receipt is missing")
        fixture_receipt: dict[str, Any] = {}
    else:
        fixture_receipt = json.loads(fixture_receipt_path.read_text(encoding="utf-8"))
    remote_by_name = {
        str(item.get("name", "")): item
        for item in receipt.get("repositories", [])
        if isinstance(item, dict)
    }
    fixture_by_name = {
        str(item.get("library", "")): item
        for item in fixture_receipt.get("fixtures", [])
        if isinstance(item, dict)
    }

    for contract in libraries:
        if not isinstance(contract, dict):
            failures.append("library contract must be a mapping")
            continue
        name = str(contract.get("name", ""))
        for key in (
            "repository",
            "default_branch",
            "pinned_revision",
            "issue",
            "local_adapter",
            "fixture",
            "interface",
            "acceptance_tests",
        ):
            if not contract.get(key):
                failures.append(f"{name}: {key} is required")
        revision = str(contract.get("pinned_revision", ""))
        if not REVISION.fullmatch(revision):
            failures.append(f"{name}: pinned revision must be a full lowercase Git commit")
        interface = contract.get("interface", {})
        if not isinstance(interface, dict):
            failures.append(f"{name}: interface must be a mapping")
            continue
        for key in ("summary", "operations", "input", "output"):
            if not interface.get(key):
                failures.append(f"{name}: interface {key} is required")
        operations = interface.get("operations", [])
        if not isinstance(operations, list) or len(operations) < 2:
            failures.append(f"{name}: at least two proposed operations are required")
        tests = contract.get("acceptance_tests", [])
        if not isinstance(tests, list) or not tests:
            failures.append(f"{name}: acceptance tests are required")
        else:
            for command in tests:
                if not str(command).startswith("uv run pytest -q tests/"):
                    failures.append(f"{name}: acceptance command must target a repository test")

        for field in ("issue", "local_adapter", "fixture"):
            path = ROOT / str(contract.get(field, ""))
            if not path.is_file():
                failures.append(f"{name}: {field} path is missing: {path.relative_to(ROOT)}")
        issue_path = ROOT / str(contract.get("issue", ""))
        if issue_path.is_file():
            body = issue_path.read_text(encoding="utf-8")
            for section in (
                "GENERATED — DO NOT EDIT",
                "## Proposed interface",
                "## Compatibility fixture",
                "## Acceptance",
                "## Handoff boundary",
            ):
                if section not in body:
                    failures.append(f"{name}: generated issue body is missing {section}")

        fixture_path = ROOT / str(contract.get("fixture", ""))
        if fixture_path.is_file():
            try:
                frame = pl.read_parquet(fixture_path)
            except (
                OSError,
                pl.exceptions.PolarsError,
            ) as exc:  # pragma: no cover - diagnostic boundary
                failures.append(f"{name}: fixture is not readable Parquet: {exc}")
            else:
                if frame.columns != FIXTURE_COLUMNS or frame.height != 1:
                    failures.append(f"{name}: fixture must have the canonical columns and one row")
                elif frame.item(0, "library") != name:
                    failures.append(f"{name}: fixture library identity differs")
                elif "synthetic aggregate" not in str(frame.item(0, "boundary")):
                    failures.append(f"{name}: fixture must state its synthetic aggregate boundary")
                for column in ("input_json", "expected_json"):
                    try:
                        json.loads(str(frame.item(0, column)))
                    except json.JSONDecodeError:
                        failures.append(f"{name}: {column} must contain valid JSON")
            fixture_record = fixture_by_name.get(name, {})
            observed_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            if fixture_record.get("sha256") != observed_hash:
                failures.append(f"{name}: fixture hash differs from the generated receipt")

        remote = remote_by_name.get(name, {})
        if remote.get("revision") != revision:
            failures.append(f"{name}: authenticated remote revision differs from contract pin")
        if remote.get("default_branch") != contract.get("default_branch"):
            failures.append(f"{name}: authenticated default branch differs from contract")

    if registry.get("remote_state") != "authenticated_metadata_and_revision_verified":
        failures.append(
            "registry remote state must describe authenticated metadata and revision verification"
        )
    if registry.get("upstream_execution_state") != "not_executed":
        failures.append("registry must not imply upstream code execution")
    if "not imported" not in str(registry.get("claim_boundary", "")):
        failures.append("registry claim boundary must state non-claims explicitly")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Upstream compatibility failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated nine optional upstream contracts, fixtures, receipts, and local fallbacks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

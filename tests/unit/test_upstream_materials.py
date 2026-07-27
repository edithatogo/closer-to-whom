from __future__ import annotations

import hashlib
import json
from pathlib import Path
from runpy import run_path
from typing import Any

import polars as pl
import pytest
import yaml

material_module = run_path(
    "scripts/generate_upstream_materials.py", run_name="upstream_materials_test"
)
remote_module = run_path("scripts/refresh_upstream_metadata.py", run_name="upstream_metadata_test")
generate = material_module["generate"]
build_receipt = remote_module["build_receipt"]


def test_generated_upstream_materials_are_deterministic(tmp_path: Path) -> None:
    contracts = Path("upstream/contracts.yaml").read_text(encoding="utf-8")
    contract_path = tmp_path / "upstream/contracts.yaml"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(contracts, encoding="utf-8")

    first = generate(tmp_path)
    first_hashes = {
        item["library"]: hashlib.sha256((tmp_path / item["path"]).read_bytes()).hexdigest()
        for item in first["fixtures"]
    }
    second = generate(tmp_path)
    second_hashes = {
        item["library"]: hashlib.sha256((tmp_path / item["path"]).read_bytes()).hexdigest()
        for item in second["fixtures"]
    }

    assert first_hashes == second_hashes
    assert len(first_hashes) == 9
    for item in second["fixtures"]:
        frame = pl.read_parquet(tmp_path / item["path"])
        assert frame.height == 1
        assert frame.item(0, "library") == item["library"]
        assert json.loads(frame.item(0, "input_json"))["synthetic"] is True


def test_remote_receipt_requires_exact_reviewed_revision(tmp_path: Path) -> None:
    contracts = {
        "libraries": [
            {
                "name": "example",
                "repository": "https://github.com/owner/example",
                "default_branch": "main",
                "pinned_revision": "a" * 40,
            }
        ]
    }
    contract_path = tmp_path / "contracts.yaml"
    contract_path.write_text(yaml.safe_dump(contracts), encoding="utf-8")

    def fetcher(_repository: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return (
            {
                "default_branch": "main",
                "archived": False,
                "fork": False,
                "license": {"spdx_id": "MIT"},
                "updated_at": "2026-07-27T00:00:00Z",
                "pushed_at": "2026-07-27T00:00:00Z",
            },
            {"sha": "a" * 40},
        )

    receipt = build_receipt(
        contract_path,
        fetcher=fetcher,
        retrieved_at="2026-07-27T00:00:00Z",
    )
    assert receipt["repositories"][0]["revision"] == "a" * 40
    assert "does not import" in receipt["claim_boundary"]

    def drifted(_repository: str) -> tuple[dict[str, Any], dict[str, Any]]:
        metadata, _commit = fetcher(_repository)
        return metadata, {"sha": "b" * 40}

    with pytest.raises(RuntimeError, match="differs from reviewed pin"):
        build_receipt(contract_path, fetcher=drifted)

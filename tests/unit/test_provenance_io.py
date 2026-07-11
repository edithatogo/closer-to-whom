from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from closer_to_whom.io import read_parquet, write_arrow_ipc, write_parquet_deterministic
from closer_to_whom.provenance import (
    assumptions_fingerprint,
    canonical_json_bytes,
    fingerprint_mapping,
    runtime_manifest,
    sha256_bytes,
    sha256_file,
    write_json,
)


def test_hashing_and_json(tmp_path: Path) -> None:
    assert sha256_bytes(b"x") == sha256_bytes(b"x")
    assert canonical_json_bytes({"b": 1, "a": 2}) == b'{"a":2,"b":1}'
    assert len(fingerprint_mapping({"a": 1})) == 64
    path = tmp_path / "x.txt"
    path.write_text("hello")
    assert len(sha256_file(path)) == 64
    json_path = tmp_path / "x.json"
    write_json(json_path, {"b": 1, "a": 2})
    assert list(json.loads(json_path.read_text())) == ["a", "b"]


def test_assumption_fingerprint_and_runtime(tmp_path: Path) -> None:
    left = tmp_path / "a.yaml"
    right = tmp_path / "b.yaml"
    left.write_text("x: 1\n")
    right.write_text("y: 2\n")
    assert assumptions_fingerprint([right, left]) == assumptions_fingerprint([left, right])
    manifest = runtime_manifest(Path.cwd(), deterministic=True)
    assert isinstance(manifest["created_at"], str)
    assert manifest["created_at"].endswith("+00:00")


def test_deterministic_io(tmp_path: Path) -> None:
    frame = pl.DataFrame({"id": [2, 1], "value": ["b", "a"]})
    first = write_parquet_deterministic(frame, tmp_path / "x.parquet", sort_by=("id",))
    second = write_parquet_deterministic(frame.reverse(), tmp_path / "y.parquet", sort_by=("id",))
    assert first == second
    assert read_parquet(tmp_path / "x.parquet").get_column("id").to_list() == [1, 2]
    table = frame.to_arrow()
    assert len(write_arrow_ipc(table, tmp_path / "x.arrow", sort_by=("id",))) == 64

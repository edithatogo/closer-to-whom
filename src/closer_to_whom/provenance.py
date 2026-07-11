"""Provenance, hashing, and assumption-fingerprint utilities."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson
import yaml


def sha256_bytes(payload: bytes) -> str:
    """Return a lowercase SHA-256 digest."""
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one file in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    """Serialise a JSON-compatible value in canonical key order."""
    return orjson.dumps(value, option=orjson.OPT_SORT_KEYS)


def fingerprint_mapping(value: Mapping[str, Any]) -> str:
    """Create a stable fingerprint for a JSON-compatible mapping."""
    return sha256_bytes(canonical_json_bytes(value))


def load_yaml(path: Path) -> Any:
    """Load one YAML file with safe parsing."""
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def assumptions_fingerprint(paths: Iterable[Path]) -> str:
    """Fingerprint ordered, parsed assumption files rather than formatting."""
    payload: list[dict[str, Any]] = []
    for path in sorted(paths, key=lambda item: item.as_posix()):
        payload.append({"path": path.as_posix(), "content": load_yaml(path)})
    return sha256_bytes(canonical_json_bytes(payload))


def git_revision(repo: Path) -> str:
    """Return the current Git revision or an explicit unavailable marker."""
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def runtime_manifest(repo: Path, *, deterministic: bool = False) -> dict[str, Any]:
    """Build a runtime and source manifest for a verification receipt."""
    timestamp = (
        datetime.fromtimestamp(int(os.environ.get("SOURCE_DATE_EPOCH", "0")), tz=UTC)
        if deterministic
        else datetime.now(tz=UTC)
    )
    return {
        "created_at": timestamp.isoformat(),
        "git_revision": git_revision(repo),
        "python": sys.version,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
    }


def write_json(path: Path, value: Any) -> None:
    """Write stable, newline-terminated JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

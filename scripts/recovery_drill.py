#!/usr/bin/env python3
"""Verify reconstruction of critical release and static-site files from Git history."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITICAL = (
    "release/space-deployment-receipt.json",
    "release/space-monitor-receipt.json",
    "release/publication-licence-receipt.json",
    "spaces/static/index.html",
    "spaces/static/aggregate-reports.json",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_sha(path: str) -> str:
    content = subprocess.run(
        ["git", "show", f"HEAD:{path}"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    return hashlib.sha256(content).hexdigest()


def _revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def run(
    output: Path, *, rto_seconds: int = 300, rpo: str = "latest merged main commit"
) -> dict[str, object]:
    started = time.monotonic()
    revision = _revision()
    expected = {path: _git_sha(path) for path in CRITICAL}
    with tempfile.TemporaryDirectory(prefix="closer-to-whom-recovery-") as directory:
        archive = Path(directory) / "source.tar"
        subprocess.run(
            ["git", "archive", "--format=tar", "-o", str(archive), "HEAD"], cwd=ROOT, check=True
        )
        subprocess.run(["tar", "-xf", str(archive), "-C", directory], check=True)
        reconstructed = {path: _sha(Path(directory) / path) for path in CRITICAL}
    elapsed = time.monotonic() - started
    passed = expected == reconstructed and elapsed <= rto_seconds
    receipt = {
        "schema_version": "1.0.0",
        "status": "passed" if passed else "failed",
        "source_revision": revision,
        "rto_seconds": rto_seconds,
        "rpo": rpo,
        "elapsed_seconds": round(elapsed, 3),
        "critical_files": {
            path: {
                "source_sha256": expected[path],
                "reconstructed_sha256": reconstructed[path],
                "matches": expected[path] == reconstructed[path],
            }
            for path in CRITICAL
        },
        "independent_storage": "not_claimed_by_local_drill",
        "claim_boundary": "Local Git archive reconstruction only; it does not prove independent durable storage, signed release authorization, or external recovery availability.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not passed:
        raise RuntimeError("recovery drill failed")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "release/recovery-drill-receipt.json")
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

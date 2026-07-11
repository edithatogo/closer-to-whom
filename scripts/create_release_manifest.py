#!/usr/bin/env python3
"""Create a content-addressed handover manifest."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from closer_to_whom.provenance import git_revision, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    files = {
        relative: {
            "sha256": sha256_file(ROOT / relative),
            "size_bytes": (ROOT / relative).stat().st_size,
        }
        for relative in tracked
        if (ROOT / relative).is_file()
    }
    payload = {
        "schema_version": "1.0.0",
        "project": "closer-to-whom",
        "version": "0.2.0",
        "git_revision": git_revision(ROOT),
        "tracked_file_count": len(files),
        "files": files,
    }
    output = ROOT / "release/source-manifest.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

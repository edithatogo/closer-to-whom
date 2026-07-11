#!/usr/bin/env python3
"""Build, install, and reproduce the synthetic pipeline in an isolated venv."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = file.relative_to(path).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        payload = file.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def run(command: list[str], **kwargs: object) -> None:
    subprocess.run(command, cwd=ROOT, check=True, **kwargs)


def main() -> int:
    receipt: dict[str, object] = {"status": "failed", "commands": []}
    with tempfile.TemporaryDirectory(prefix="ctw-clean-room-") as raw:
        work = Path(raw)
        dist = work / "dist"
        run([sys.executable, "-m", "build", "--outdir", str(dist)])
        wheel = next(dist.glob("*.whl"))
        venv = work / "venv"
        run([sys.executable, "-m", "venv", str(venv)])
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run([str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)])
        outputs = []
        for index in (1, 2):
            target = work / f"run-{index}"
            run(
                [
                    str(python),
                    "-m",
                    "closer_to_whom",
                    "demo",
                    "--output",
                    str(target),
                    "--seed",
                    "20260711",
                ]
            )
            outputs.append(digest_tree(target))
        receipt.update(
            {
                "status": "passed" if outputs[0] == outputs[1] else "failed",
                "wheel": wheel.name,
                "output_digests": outputs,
                "reproducible": outputs[0] == outputs[1],
            }
        )
    output = ROOT / "release" / "clean-room-receipt.json"
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the synthetic pipeline twice and compare canonical content digests."""

from __future__ import annotations

import tempfile
from pathlib import Path

from closer_to_whom.pipeline import compare_manifests, run_demo


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        left = root / "left"
        right = root / "right"
        run_demo(left, seed=20260711)
        run_demo(right, seed=20260711)
        if not compare_manifests(left / "manifest.json", right / "manifest.json"):
            raise SystemExit("Deterministic content digests differ between clean runs")
    print("Reproducibility check passed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Record reproducible microbenchmarks without making them correctness gates."""

from __future__ import annotations

import json
import time
from pathlib import Path

from closer_to_whom.pipeline import run_demo


def main() -> None:
    output = Path("artifacts/benchmark-demo")
    started = time.perf_counter()
    manifest = run_demo(output)
    duration = time.perf_counter() - started
    payload = {"synthetic_demo_seconds": duration, "rows": manifest["row_counts"]}
    path = Path("reports/benchmark.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()

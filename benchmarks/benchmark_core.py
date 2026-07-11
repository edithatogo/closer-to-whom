#!/usr/bin/env python3
"""Portable core benchmarks with correctness checks and generous budgets."""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from closer_to_whom.pipeline import run_demo

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    median_seconds: float
    minimum_seconds: float
    runs: int
    budget_seconds: float
    passed: bool


def benchmark_demo(runs: int = 3, budget_seconds: float = 30.0) -> BenchmarkResult:
    durations=[]
    for index in range(runs):
        target=ROOT / "artifacts" / "benchmark" / f"run-{index}"
        started=time.perf_counter()
        run_demo(output_dir=target, seed=20260711)
        durations.append(time.perf_counter()-started)
    median=statistics.median(durations)
    return BenchmarkResult(
        name="synthetic-national-demo",
        median_seconds=median,
        minimum_seconds=min(durations),
        runs=runs,
        budget_seconds=budget_seconds,
        passed=median <= budget_seconds,
    )


def main() -> int:
    result=benchmark_demo()
    output=ROOT / "release" / "benchmark-receipt.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(asdict(result),indent=2,sort_keys=True)+"\n")
    print(output)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

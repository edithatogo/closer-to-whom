#!/usr/bin/env python3
"""Run all JAX/XLA differential checks and write a machine receipt."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

from closer_to_whom.accel.jax_psa import differential_check

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = differential_check(draws=512, cells=256)
    payload = asdict(result)
    for key, value in list(payload.items()):
        if isinstance(value, float) and not math.isfinite(value):
            payload[key] = None
    payload["status"] = (
        "passed"
        if result.available and result.passed
        else ("skipped" if not result.available else "failed")
    )
    output = ROOT / "release" / "jax-differential-receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0 if (not result.available or result.passed) else 1


if __name__ == "__main__":
    raise SystemExit(main())

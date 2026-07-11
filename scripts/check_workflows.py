#!/usr/bin/env python3
"""Apply local least-privilege and reliability checks to GitHub workflows."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    failures: list[str] = []
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if "permissions" not in payload:
            failures.append(f"{path.name}: missing top-level permissions")
        jobs = payload.get("jobs", {})
        for job_name, job in jobs.items():
            if "timeout-minutes" not in job:
                failures.append(f"{path.name}:{job_name}: missing timeout-minutes")
            for step in job.get("steps", []):
                uses = step.get("uses")
                if uses and uses.endswith("@main"):
                    failures.append(f"{path.name}:{job_name}: action uses mutable @main")
        if payload.get("on") is None and payload.get(True) is None:
            failures.append(f"{path.name}: missing trigger")
    if failures:
        raise SystemExit("\n".join(failures))
    print("Workflow policy checks passed.")


if __name__ == "__main__":
    main()

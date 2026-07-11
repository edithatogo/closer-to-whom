#!/usr/bin/env python3
"""Static checks for least-privilege and bounded GitHub Actions workflows."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
DANGEROUS = ("pull_request_target",)


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        try:
            payload: Any = yaml.safe_load(text)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.name}: invalid YAML: {exc}")
            continue
        if not isinstance(payload, dict):
            failures.append(f"{path.name}: top-level workflow is not a mapping")
            continue
        trigger = payload.get("on") or payload.get(True)  # PyYAML YAML 1.1 compatibility
        trigger_text = str(trigger)
        if any(event in trigger_text for event in DANGEROUS):
            failures.append(f"{path.name}: pull_request_target is forbidden")
        if "permissions" not in payload:
            failures.append(f"{path.name}: missing explicit top-level permissions")
        jobs = payload.get("jobs", {})
        if not isinstance(jobs, dict) or not jobs:
            failures.append(f"{path.name}: no jobs")
            continue
        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                continue
            if "timeout-minutes" not in job:
                warnings.append(f"{path.name}:{job_name}: no timeout-minutes")
        if re.search(r"uses:\s*[^\s@]+@(?:main|master)\b", text):
            failures.append(f"{path.name}: action pinned to mutable main/master")
    if warnings:
        print("Workflow hardening warnings:")
        print("\n".join(f"- {warning}" for warning in warnings))
    if failures:
        print("Workflow hardening failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Workflow hardening checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

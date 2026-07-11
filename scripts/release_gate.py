#!/usr/bin/env python3
"""Run layered release gates and emit durable machine/human verification receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release"
LOG_DIR = RELEASE / "receipts" / "logs"
Status = Literal["passed", "failed", "skipped"]


@dataclass(frozen=True, slots=True)
class Gate:
    name: str
    command: tuple[str, ...]
    profiles: tuple[str, ...] = ("push", "local", "full")
    required: bool = True
    capability: str | None = None
    timeout_seconds: int = 900
    description: str = ""


@dataclass(frozen=True, slots=True)
class GateResult:
    name: str
    status: Status
    required: bool
    return_code: int | None
    elapsed_seconds: float
    command: list[str]
    log_path: str | None
    detail: str


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(command: list[str]) -> str:
    result = subprocess.run(
        ["git", *command], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def capability_available(capability: str | None) -> bool:
    if capability is None:
        return True
    if capability == "jax":
        return (
            subprocess.run(
                [sys.executable, "-c", "import jax"],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    return shutil.which(capability) is not None


def uv_command(*parts: str) -> tuple[str, ...]:
    uv = shutil.which("uv")
    return (uv, "run", *parts) if uv else (sys.executable, *parts)


def gates() -> tuple[Gate, ...]:
    py = uv_command("python")
    return (
        Gate(
            "compile",
            (*py, "-m", "compileall", "-q", "src", "scripts", "tests"),
            timeout_seconds=120,
        ),
        Gate("generated-files", (*py, "scripts/check_generated_files.py"), timeout_seconds=120),
        Gate(
            "lockfile-portability",
            (*py, "scripts/check_lockfile_portability.py"),
            timeout_seconds=120,
        ),
        Gate(
            "machine-readability",
            (*py, "scripts/check_machine_readability.py"),
            timeout_seconds=120,
        ),
        Gate("model-contracts", (*py, "scripts/check_contracts.py"), timeout_seconds=120),
        Gate(
            "assumption-contract",
            (*py, "scripts/check_assumption_coverage.py"),
            timeout_seconds=120,
        ),
        Gate("source-registry", (*py, "scripts/check_source_registry.py"), timeout_seconds=120),
        Gate("protocol-consistency", (*py, "scripts/check_protocol.py"), timeout_seconds=120),
        Gate("claim-boundaries", (*py, "scripts/check_claim_boundaries.py"), timeout_seconds=120),
        Gate(
            "privacy-and-licences",
            (*py, "scripts/check_privacy_and_licences.py"),
            timeout_seconds=120,
        ),
        Gate(
            "repository-hygiene", (*py, "scripts/check_repository_hygiene.py"), timeout_seconds=120
        ),
        Gate("workflow-structure", (*py, "scripts/check_workflows.py"), timeout_seconds=120),
        Gate(
            "workflow-hardening", (*py, "scripts/check_workflow_hardening.py"), timeout_seconds=120
        ),
        Gate(
            "version-consistency",
            (*py, "scripts/check_version_consistency.py"),
            timeout_seconds=120,
        ),
        Gate("ruff", (*uv_command("ruff"), "check", "."), timeout_seconds=180),
        Gate("ruff-format", (*uv_command("ruff"), "format", "--check", "."), timeout_seconds=180),
        Gate(
            "tests-fast",
            (*uv_command("pytest"), "-q", "--no-cov"),
            profiles=("push",),
            timeout_seconds=600,
        ),
        Gate(
            "tests-coverage",
            (*uv_command("pytest"),),
            profiles=("local", "full"),
            timeout_seconds=1200,
        ),
        Gate(
            "mypy",
            (*uv_command("mypy"), "src/closer_to_whom"),
            profiles=("local", "full"),
            timeout_seconds=600,
        ),
        Gate("pyright", (*uv_command("pyright"),), profiles=("local", "full"), timeout_seconds=600),
        Gate(
            "codespell",
            (*uv_command("codespell"), "."),
            profiles=("local", "full"),
            timeout_seconds=300,
        ),
        Gate(
            "docs",
            (*uv_command("mkdocs"), "build", "--strict"),
            profiles=("local", "full"),
            timeout_seconds=600,
        ),
        Gate(
            "package-build", (*py, "-m", "build"), profiles=("local", "full"), timeout_seconds=600
        ),
        Gate(
            "package-smoke",
            (*py, "scripts/smoke_install.py"),
            profiles=("local", "full"),
            timeout_seconds=600,
        ),
        Gate(
            "deterministic-demo",
            (*py, "scripts/check_reproducibility.py"),
            profiles=("local", "full"),
            timeout_seconds=900,
        ),
        Gate(
            "publication-readiness",
            (*py, "scripts/publication_readiness.py"),
            profiles=("local", "full"),
            timeout_seconds=180,
        ),
        Gate(
            "secret-scan",
            (*py, "scripts/secret_scan.py"),
            profiles=("local", "full"),
            timeout_seconds=180,
        ),
        Gate(
            "complexity-budget",
            (*py, "scripts/check_complexity_budget.py"),
            profiles=("full",),
            required=False,
            timeout_seconds=180,
        ),
        Gate(
            "dependency-audit",
            (*uv_command("pip-audit"),),
            profiles=("full",),
            required=False,
            timeout_seconds=600,
        ),
        Gate(
            "deptry",
            (*uv_command("deptry"), "src"),
            profiles=("full",),
            required=False,
            timeout_seconds=300,
        ),
        Gate(
            "vulture",
            (*uv_command("vulture"), "src", "scripts", "--min-confidence", "90"),
            profiles=("full",),
            required=False,
            timeout_seconds=300,
        ),
        Gate(
            "benchmark",
            (*py, "benchmarks/benchmark_core.py"),
            profiles=("full",),
            required=False,
            timeout_seconds=900,
        ),
        Gate(
            "clean-room",
            (*py, "scripts/clean_room_verify.py"),
            profiles=("full",),
            timeout_seconds=1200,
        ),
        Gate(
            "jax-differential",
            (*py, "scripts/jax_differential.py"),
            profiles=("local", "full"),
            required=False,
            capability="jax",
            timeout_seconds=600,
        ),
        Gate(
            "mojo-canary",
            (*py, "-m", "closer_to_whom", "mojo-canary", "--require"),
            profiles=("full",),
            required=False,
            capability="mojo",
            timeout_seconds=300,
        ),
        Gate(
            "docker-build",
            ("docker", "build", "-t", "closer-to-whom:verification", "."),
            profiles=("full",),
            required=False,
            capability="docker",
            timeout_seconds=1800,
        ),
    )


def run_gate(gate: Gate, env: dict[str, str]) -> GateResult:
    if not capability_available(gate.capability):
        return GateResult(
            name=gate.name,
            status="skipped",
            required=gate.required,
            return_code=None,
            elapsed_seconds=0.0,
            command=list(gate.command),
            log_path=None,
            detail=f"optional capability unavailable: {gate.capability}",
        )
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"{gate.name}.log"
    started = time.perf_counter()
    try:
        result = subprocess.run(
            gate.command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=gate.timeout_seconds,
            env=env,
        )
        elapsed = time.perf_counter() - started
        output = (
            f"$ {shlex.join(gate.command)}\n\n"
            f"[stdout]\n{result.stdout}\n\n[stderr]\n{result.stderr}\n"
        )
        log.write_text(output, encoding="utf-8")
        status: Status = "passed" if result.returncode == 0 else "failed"
        return GateResult(
            name=gate.name,
            status=status,
            required=gate.required,
            return_code=result.returncode,
            elapsed_seconds=round(elapsed, 3),
            command=list(gate.command),
            log_path=log.relative_to(ROOT).as_posix(),
            detail=gate.description or ("completed" if status == "passed" else "command failed"),
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        log.write_text(
            f"$ {shlex.join(gate.command)}\n\nTimed out after {gate.timeout_seconds}s\n{exc}",
            encoding="utf-8",
        )
        return GateResult(
            name=gate.name,
            status="failed",
            required=gate.required,
            return_code=None,
            elapsed_seconds=round(elapsed, 3),
            command=list(gate.command),
            log_path=log.relative_to(ROOT).as_posix(),
            detail=f"timed out after {gate.timeout_seconds}s",
        )


def write_junit(results: list[GateResult]) -> Path:
    testsuite = ET.Element(
        "testsuite",
        name="closer-to-whom-release-gates",
        tests=str(len(results)),
        failures=str(sum(result.status == "failed" for result in results)),
        skipped=str(sum(result.status == "skipped" for result in results)),
        time=str(round(sum(result.elapsed_seconds for result in results), 3)),
    )
    for result in results:
        case = ET.SubElement(
            testsuite,
            "testcase",
            name=result.name,
            time=str(result.elapsed_seconds),
        )
        if result.status == "failed":
            failure = ET.SubElement(case, "failure", message=result.detail)
            failure.text = result.log_path or result.detail
        elif result.status == "skipped":
            skipped = ET.SubElement(case, "skipped", message=result.detail)
            skipped.text = result.detail
    path = RELEASE / "verification-junit.xml"
    ET.ElementTree(testsuite).write(path, encoding="utf-8", xml_declaration=True)
    return path


def write_markdown(receipt: dict[str, object], results: list[GateResult]) -> Path:
    summary = receipt["summary"]
    lines = [
        "# Local verification report",
        "",
        f"- Profile: `{receipt['profile']}`",
        f"- Revision: `{receipt['git']['revision']}`",
        f"- Dirty at start: `{receipt['git']['dirty']}`",
        f"- Overall required-gate status: **{summary['required_status']}**",
        f"- Passed: {summary['passed']}; failed: {summary['failed']}; skipped: {summary['skipped']}",
        "",
        "A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.",
        "",
        "| Gate | Required | Status | Seconds | Evidence |",
        "|---|---:|---|---:|---|",
    ]
    for result in results:
        evidence = f"`{result.log_path}`" if result.log_path else result.detail
        lines.append(
            f"| `{result.name}` | {'yes' if result.required else 'no'} | **{result.status}** | "
            f"{result.elapsed_seconds:.3f} | {evidence} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.",
            "",
        ]
    )
    path = ROOT / "VALIDATION.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("push", "local", "full"), default="local")
    parser.add_argument("--keep-going", action="store_true", default=True)
    args = parser.parse_args()
    RELEASE.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")
    env.setdefault("HYPOTHESIS_PROFILE", "ci_extended" if args.profile != "push" else "ci")
    env.setdefault("SOURCE_DATE_EPOCH", git(["show", "-s", "--format=%ct", "HEAD"]) or "0")

    selected = [gate for gate in gates() if args.profile in gate.profiles]
    results: list[GateResult] = []
    for gate in selected:
        result = run_gate(gate, env)
        results.append(result)
        if result.status == "failed" and result.required and not args.keep_going:
            break

    required_failures = [r for r in results if r.required and r.status == "failed"]
    receipt: dict[str, object] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "profile": args.profile,
        "project": "closer-to-whom",
        "git": {
            "revision": git(["rev-parse", "HEAD"]),
            "describe": git(["describe", "--always", "--dirty", "--tags"]),
            "branch": git(["branch", "--show-current"]),
            "dirty": bool(git(["status", "--porcelain"])),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "digests": {
            "uv_lock_sha256": sha256(ROOT / "uv.lock"),
            "pyproject_sha256": sha256(ROOT / "pyproject.toml"),
            "assumptions_sha256": sha256(ROOT / "assumptions" / "assumptions.yaml"),
            "scenario_catalogue_sha256": sha256(ROOT / "scenarios" / "scenario-catalogue.yaml"),
            "source_registry_sha256": sha256(ROOT / "data" / "public" / "source-registry.yaml"),
        },
        "summary": {
            "required_status": "passed" if not required_failures else "failed",
            "passed": sum(r.status == "passed" for r in results),
            "failed": sum(r.status == "failed" for r in results),
            "skipped": sum(r.status == "skipped" for r in results),
            "required_failures": [r.name for r in required_failures],
        },
        "results": [asdict(result) for result in results],
        "claim_boundary": (
            "Repository and synthetic harness verification only; no validation of actual service "
            "capability, patient-level access, operational capacity, or clinical outcomes."
        ),
    }
    receipt_path = RELEASE / "verification-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    junit_path = write_junit(results)
    markdown_path = write_markdown(receipt, results)
    print(receipt_path)
    print(junit_path)
    print(markdown_path)
    return 0 if not required_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

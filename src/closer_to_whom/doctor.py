"""Environment and repository readiness diagnostics."""

from __future__ import annotations

import importlib.util
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from closer_to_whom.integrations import integration_capabilities


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One environment diagnostic."""

    diagnostic_id: str
    passed: bool
    required: bool
    detail: str


def run_doctor(repo: Path) -> tuple[Diagnostic, ...]:
    """Inspect core, optional, and local-handover capabilities."""
    diagnostics: list[Diagnostic] = [
        Diagnostic(
            "python.version",
            sys.version_info >= (3, 11),
            True,
            platform.python_version(),
        ),
        Diagnostic("repository.git", (repo / ".git").exists(), True, str(repo)),
        Diagnostic(
            "repository.assumptions",
            (repo / "assumptions/assumptions.yaml").exists(),
            True,
            "canonical assumptions registry",
        ),
    ]
    for module in ("numpy", "polars", "pyarrow", "pydantic", "scipy"):
        diagnostics.append(
            Diagnostic(
                f"python.{module}",
                importlib.util.find_spec(module) is not None,
                True,
                module,
            )
        )
    for command in ("git", "uv", "docker", "quarto", "cargo", "mojo"):
        diagnostics.append(
            Diagnostic(
                f"command.{command}",
                shutil.which(command) is not None,
                command in {"git"},
                shutil.which(command) or "not found",
            )
        )
    for capability in integration_capabilities():
        diagnostics.append(
            Diagnostic(
                f"integration.{capability['name']}",
                bool(capability["available"]),
                bool(capability["required_for_open_pipeline"]),
                str(capability["role"]),
            )
        )
    return tuple(diagnostics)


def doctor_payload(repo: Path) -> dict[str, object]:
    """Return a machine-readable diagnostic payload."""
    diagnostics = run_doctor(repo)
    return {
        "ready": all(item.passed for item in diagnostics if item.required),
        "diagnostics": [asdict(item) for item in diagnostics],
    }

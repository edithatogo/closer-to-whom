"""Isolated developer and CI sessions."""

from __future__ import annotations

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "typecheck", "tests", "contracts"]

DEV_EXTRAS = ".[dev,accel,geo,optimization,dashboard,docs]"


def install(session: nox.Session) -> None:
    session.install("-e", DEV_EXTRAS)


@nox.session(python="3.14")
def tests(session: nox.Session) -> None:
    install(session)
    session.env["HYPOTHESIS_PROFILE"] = "ci_extended"
    args = session.posargs or []
    session.run("pytest", *args)


@nox.session(python="3.14")
def lint(session: nox.Session) -> None:
    install(session)
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
    session.run("codespell", ".")
    session.run("python", "scripts/check_repository_hygiene.py")


@nox.session(python="3.14")
def typecheck(session: nox.Session) -> None:
    install(session)
    session.run("mypy", "src/closer_to_whom")
    session.run("pyright")


@nox.session(python="3.14")
def contracts(session: nox.Session) -> None:
    install(session)
    for script in (
        "check_contracts.py",
        "check_machine_readability.py",
        "check_assumption_coverage.py",
        "check_source_registry.py",
        "check_source_receipts.py",
        "check_input_freeze.py",
        "check_clinical_review_receipt.py",
        "check_governance_review.py",
        "check_national_analysis_receipt.py",
        "check_microdata_voi_decision.py",
        "check_publication_gate.py",
        "check_upstream_compatibility.py",
        "check_generated_files.py",
        "check_version_consistency.py",
        "check_workflows.py",
        "check_workflow_hardening.py",
        "check_claim_boundaries.py",
        "check_privacy_and_licences.py",
    ):
        session.run("python", f"scripts/{script}")


@nox.session(python="3.14")
def docs(session: nox.Session) -> None:
    install(session)
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.14")
def build(session: nox.Session) -> None:
    install(session)
    session.run("python", "-m", "build")
    session.run("python", "scripts/smoke_install.py")


@nox.session(python="3.14")
def reproducibility(session: nox.Session) -> None:
    install(session)
    session.run("python", "scripts/check_reproducibility.py")
    session.run("python", "scripts/clean_room_verify.py")


@nox.session(python="3.14")
def full(session: nox.Session) -> None:
    install(session)
    session.run("python", "scripts/release_gate.py", "--profile", "full")

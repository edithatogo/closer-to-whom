"""Isolated developer and CI sessions."""

from __future__ import annotations

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "typecheck", "tests", "contracts"]

DEV_EXTRAS = ".[dev,accel,geo,optimization,dashboard,docs]"


def install(session: nox.Session) -> None:
    session.install("-e", DEV_EXTRAS)


@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session: nox.Session) -> None:
    install(session)
    session.env["HYPOTHESIS_PROFILE"] = "ci" if session.python != "3.12" else "ci_extended"
    args = session.posargs or (["--no-cov", "-q"] if session.python != "3.12" else [])
    session.run("pytest", *args)


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    install(session)
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
    session.run("codespell", ".")
    session.run("python", "scripts/check_repository_hygiene.py")


@nox.session(python="3.12")
def typecheck(session: nox.Session) -> None:
    install(session)
    session.run("mypy", "src/closer_to_whom")
    session.run("pyright")


@nox.session(python="3.12")
def contracts(session: nox.Session) -> None:
    install(session)
    for script in (
        "check_contracts.py",
        "check_machine_readability.py",
        "check_assumption_coverage.py",
        "check_source_registry.py",
        "check_generated_files.py",
        "check_version_consistency.py",
        "check_workflows.py",
        "check_workflow_hardening.py",
        "check_claim_boundaries.py",
        "check_privacy_and_licences.py",
    ):
        session.run("python", f"scripts/{script}")


@nox.session(python="3.12")
def docs(session: nox.Session) -> None:
    install(session)
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12")
def build(session: nox.Session) -> None:
    install(session)
    session.run("python", "-m", "build")
    session.run("python", "scripts/smoke_install.py")


@nox.session(python="3.12")
def reproducibility(session: nox.Session) -> None:
    install(session)
    session.run("python", "scripts/check_reproducibility.py")
    session.run("python", "scripts/clean_room_verify.py")


@nox.session(python="3.12")
def full(session: nox.Session) -> None:
    install(session)
    session.run("python", "scripts/release_gate.py", "--profile", "full")

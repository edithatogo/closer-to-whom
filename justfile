set shell := ["bash", "-cu"]
set dotenv-load := false

_default:
    @just --list

bootstrap:
    ./scripts/bootstrap-local.sh

sync:
    uv sync --all-extras

sync-locked:
    test -f uv.lock
    uv sync --locked --all-extras

generate:
    uv run python scripts/generate_json_schemas.py
    uv run python scripts/generate_schema_registry.py
    uv run python scripts/generate_assumptions_appendix.py
    uv run python scripts/prepare_upstream_handoff.py

fmt:
    uv run ruff format .
    uv run ruff check --fix .

lint:
    uv run ruff check .
    uv run codespell .
    uv run python scripts/check_repository_hygiene.py

typecheck:
    uv run mypy src/closer_to_whom
    uv run pyright

test:
    HYPOTHESIS_PROFILE=ci_extended uv run pytest

contracts:
    uv run python scripts/check_contracts.py
    uv run python scripts/check_machine_readability.py
    uv run python scripts/check_assumption_coverage.py
    uv run python scripts/check_source_registry.py
    uv run python scripts/check_generated_files.py
    uv run python scripts/check_version_consistency.py
    uv run python scripts/check_workflows.py
    uv run python scripts/check_workflow_hardening.py

governance:
    uv run python scripts/check_claim_boundaries.py
    uv run python scripts/check_privacy_and_licences.py
    uv run python scripts/publication_readiness.py

docs:
    uv run mkdocs build --strict

demo out="artifacts/demo" seed="20260711":
    uv run python -m closer_to_whom demo --output {{out}} --seed {{seed}}
    uv run python -m closer_to_whom verify --input-dir {{out}} --output {{out}}/validation.json

verify:
    uv run python scripts/release_gate.py --profile local

full:
    uv run python scripts/release_gate.py --profile full

archive:
    uv run python scripts/package_handover.py

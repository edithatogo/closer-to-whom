SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help
PYTHON ?= python3
UV ?= uv
SEED ?= 20260711
OUT ?= artifacts/demo

.PHONY: help bootstrap sync sync-locked lock generate format lint typecheck test test-fast contracts governance security docs build demo benchmark clean-room check verify full release-gate release archive clean

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

bootstrap: ## Install uv if needed and prepare the locked local environment
	./scripts/bootstrap-local.sh

sync: ## Resolve and synchronise all development and optional dependencies
	$(UV) sync --all-extras

sync-locked: ## Synchronise from a committed uv.lock and fail if it is absent
	test -f uv.lock
	$(UV) sync --locked --all-extras

lock: ## Refresh the dependency lock intentionally
	$(UV) lock

generate: ## Regenerate JSON/Arrow schemas and the assumptions appendix
	$(UV) run python scripts/generate_json_schemas.py
	$(UV) run python scripts/generate_schema_registry.py
	$(UV) run python scripts/generate_assumptions_appendix.py
	$(UV) run python scripts/prepare_upstream_handoff.py

format: ## Apply deterministic Python formatting
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

lint: ## Run static lint and repository hygiene checks
	$(UV) run ruff check .
	$(UV) run codespell src scripts tests docs ecosystem protocol assumptions data/public schemas
	$(UV) run python scripts/check_complexity_budget.py
	$(UV) run python scripts/check_repository_hygiene.py

typecheck: ## Run mypy and Pyright
	$(UV) run mypy src/closer_to_whom
	$(UV) run pyright

test-fast: ## Fast local unit and property tests
	HYPOTHESIS_PROFILE=dev $(UV) run pytest -q --no-cov

test: ## Full test suite with branch coverage gate
	HYPOTHESIS_PROFILE=ci_extended $(UV) run pytest \
		--cov=closer_to_whom --cov-branch --cov-report=term-missing --cov-fail-under=89

contracts: ## Validate schemas, assumptions, source registry, generated files, and workflow contracts
	$(UV) run python scripts/check_contracts.py
	$(UV) run python scripts/check_machine_readability.py
	$(UV) run python scripts/check_assumption_coverage.py
	$(UV) run python scripts/check_source_registry.py
	$(UV) run python scripts/check_source_receipts.py
	$(UV) run python scripts/check_input_freeze.py
	$(UV) run python scripts/check_clinical_review_receipt.py
	$(UV) run python scripts/check_governance_review.py
	$(UV) run python scripts/check_generated_files.py
	$(UV) run python scripts/check_lockfile_portability.py
	$(UV) run python scripts/check_version_consistency.py
	$(UV) run python scripts/check_workflows.py
	$(UV) run python scripts/check_workflow_hardening.py

governance: ## Validate claim, privacy, licence, and publication boundaries
	$(UV) run python scripts/check_claim_boundaries.py
	$(UV) run python scripts/check_privacy_and_licences.py
	$(UV) run python scripts/publication_readiness.py

security: ## Run local security and dependency checks
	$(UV) run python scripts/secret_scan.py
	$(UV) run pip-audit
	$(UV) run bandit -q -r src scripts || true

docs: ## Build strict documentation
	$(UV) run mkdocs build --strict

build: ## Build wheel and source distribution
	rm -rf dist build
	$(UV) run python -m build

demo: ## Generate deterministic synthetic nationwide demonstration outputs
	$(UV) run python -m closer_to_whom demo --output $(OUT) --seed $(SEED)
	$(UV) run python -m closer_to_whom verify --input-dir $(OUT) --output $(OUT)/validation.json

service-census: ## Materialise the fail-closed public service census registry
	$(UV) run python scripts/materialize_service_census.py

public-demand: ## Materialise public aggregate demand and geography inputs
	$(UV) run python scripts/materialize_public_demand.py

clinical-pathway-audit: ## Audit synthetic pathway safety invariants and review blockers
	$(UV) run python scripts/check_clinical_pathway_freeze.py

route-costs: ## Materialise deterministic route matrices with fail-closed fallbacks
	$(UV) run python scripts/materialize_route_costs.py

benchmark: ## Run portable correctness-first benchmark
	$(UV) run python benchmarks/benchmark_core.py

clean-room: ## Build/install/reproduce in an isolated environment
	$(UV) run python scripts/clean_room_verify.py

check: lint typecheck test-fast contracts governance ## Run the fast local quality and governance gate

verify: generate lint typecheck test contracts governance docs build demo ## Run the local publication-oriented verification set
	$(UV) run python scripts/release_gate.py --profile local

full: verify clean-room benchmark security ## Run all locally available gates

release-gate: full ## Compatibility alias for the complete local release gate

release: full ## Build complete release metadata after full verification
	$(UV) run python scripts/create_release_manifest.py
	$(UV) run python scripts/generate_sbom.py --output release/sbom.cdx.json

archive: release ## Create handover archives and checksums
	$(UV) run python scripts/package_handover.py

clean: ## Remove generated runtime artefacts, caches, and build outputs
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache .hypothesis htmlcov site dist build artifacts/demo artifacts/benchmark
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

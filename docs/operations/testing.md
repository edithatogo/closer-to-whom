# Verification and test strategy

The harness follows a risk-based test pyramid plus independent release gates.

## Test layers

- unit tests for formulas, validators, and transforms;
- Hypothesis property tests for non-negativity, monotonicity, conservation, assignment, and optimisation bounds;
- metamorphic tests for scale invariance, facility dominance, and route/cost transformations;
- Arrow schema and source/assumption contract tests;
- end-to-end synthetic pipeline tests;
- golden digests for stable fixtures;
- JAX-versus-NumPy differential tests;
- Mojo canary and differential suite when installed;
- package build, clean-wheel install, CLI, dashboard, and container smoke tests;
- double-build reproducibility checks;
- privacy, licence, secret, claim-boundary, workflow, and generated-file drift checks;
- dependency vulnerability, SBOM, and workflow static analysis where tools are available.

## Failure semantics

Required gates fail closed. Optional integrations are recorded as unavailable, not silently skipped as passed. Release receipts distinguish pass, fail, skipped-not-installed, and not-applicable.

## Coverage

Coverage is a floor, not the quality measure. Publication-critical logic also needs property or differential evidence and explicit invariants.

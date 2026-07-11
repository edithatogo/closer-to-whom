# Threat model

## Assets

Public credibility, source provenance, model integrity, confidential/licensed material, release artefacts, Git history, dashboard availability, and policy interpretation.

## Principal threats and controls

| Threat | Control |
|---|---|
| Confidential data committed accidentally | deny-listed paths, secret/privacy scanner, pre-commit and CI, history review |
| Licensed payload exposed in Space image | fail-closed adapter, Docker context exclusions, image-content scan |
| Website text over-interpreted as capability | evidence grades, claim graph, second review, `unknown` state |
| Supply-chain compromise | least-privilege workflows, dependency scanning, SBOM, action review, signed/attested releases where available |
| Non-reproducible results | locked environments, deterministic sorting, exact content digests, double-build check |
| Numerical backend drift | NumPy oracle, JAX/Mojo differential tests, tolerances and promotion ADR |
| Policy overclaim | prohibited-claim scanner, model card, dashboard banner, manuscript checklist |
| Ecological fallacy | area-level labels, distributional reporting, explicit limitations |
| Malicious source content or prompt injection during evidence capture | treat source text as untrusted data, structured extraction, no execution, manual adjudication |
| Denial of service in public dashboard | precomputed cubes, bounded filters, non-root read-only container, health checks |
| Silent scenario or assumption change | machine fingerprints, semantic versioning, generated drift checks, decision log |

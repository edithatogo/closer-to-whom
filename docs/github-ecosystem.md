# GitHub ecosystem integration

This document is generated from `ecosystem/github-repositories.yaml`. Inclusion means a typed optional interface, public-data role, method/harness reuse, or publication workflow—not installation as a mandatory dependency.

## Snapshot

- Public repositories catalogued: **165**
- Repositories selected across all integration modes: **137**
- Public forks identified from the GitHub fork filter: **96**
- Selected forks used only through bounded source/workflow roles: **78**
- Core optional integrations: **18**
- Strong integrations: **79**
- Supporting workflow or reference integrations: **40**
- Explicitly excluded from the active ecosystem: **25**
- Selected repositories without a bounded pipeline: **0**
- Mandatory runtime dependencies on the owner's repositories: **0**

## Architecture rule

The project composes repositories through Arrow/Parquet, JSON/YAML, CLI, MCP, Git, RO-Crate, and publication manifests. Every selected repository belongs to at least one bounded cross-repository pipeline. External tools are discovered but not executed by default. Network and write operations require explicit human opt-in. Forks are never silently promoted to core or required runtime dependencies.

## Category coverage

| Category                | Repositories |
| ----------------------- | ------------ |
| agent_harness           | 26           |
| core_analysis           | 24           |
| data_evidence           | 20           |
| dissemination           | 15           |
| domain_reference        | 4            |
| local_ai                | 11           |
| platform_infrastructure | 25           |
| policy_rules            | 19           |
| publication             | 21           |

## Core typed integrations

| Repository          | Category                | Role                                                                                                                                           | Local oracle                                           | Issue draft                                                   |
| ------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |
| fyi-cli             | platform_infrastructure | Optional, human-authorised CLI/MCP workflow for preparing and tracking public OIA requests; never a data dependency.                           | src/closer_to_whom/integrations/fyi.py                 | upstream/issues/fyi-cli-machine-receipts.md                   |
| fyi-archive         | publication             | Checksum-addressed archive and evidence receipt target for public OIA responses and released source material.                                  | src/closer_to_whom/integrations/publication.py         | upstream/issues/fyi-archive-checksum-evidence-bundles.md      |
| open_social_data    | data_evidence           | Public-source catalogue, acquisition receipts, licence state, provenance, and Arrow/Parquet ingestion contracts.                               | data/public/source-registry.yaml                       | upstream/issues/open-social-data-licence-snapshot-manifest.md |
| osf-cli-go          | publication             | Dry-run-first Open Science Framework deposit, registration, metadata, and release-asset automation.                                            | src/closer_to_whom/integrations/publication.py         | upstream/issues/osf-cli-go-dry-run-deposit-plan.md            |
| reimbursement-atlas | core_analysis           | Dated travel-cost, reimbursement, evidence-readiness, and perspective contracts for patient, payer, provider, and societal costing.            | src/closer_to_whom/integrations/reimbursement.py       | upstream/issues/reimbursement-atlas-travel-cost-evidence.md   |
| rac-conformance     | policy_rules            | Independent rules-as-code policy interchange, oracle fixtures, and conformance testing for funding and eligibility assumptions.                | src/closer_to_whom/integrations/policy_interchange.py  | upstream/issues/rac-conformance-health-policy-interchange.md  |
| innovate            | core_analysis           | Aggregate adoption and diffusion trajectories for subcutaneous, community, home, and hybrid delivery scenarios.                                | src/closer_to_whom/integrations/adoption.py            | upstream/issues/innovate-bounded-adoption-arrow.md            |
| voiage              | core_analysis           | EVPI, EVPPI, EVSI, ENBS, structural uncertainty, and research-design value-of-information methods.                                             | src/closer_to_whom/integrations/voiage_adapter.py      | upstream/issues/voiage-research-design-structural-voi.md      |
| gtpcnz              | dissemination           | Reusable public-data health-policy model-lab architecture, Quarto publication pattern, dashboard, claim boundaries, and deployment workflow.   | src/closer_to_whom/dashboard/app.py                    | upstream/issues/gtpcnz-model-lab-contract.md                  |
| healthpoint-rs      | data_evidence           | Optional licensed Healthpoint FHIR discovery through fail-closed Rust CLI/MCP/Arrow contracts; never required for the open pipeline.           | src/closer_to_whom/integrations/healthpoint.py         | upstream/issues/healthpoint-rs-evidence-export.md             |
| kairos              | core_analysis           | Deterministic DES/ABM and implied-capacity simulation backend once defensible public operational parameters exist.                             | src/closer_to_whom/capacity.py                         | upstream/issues/kairos-capacity-envelope-arrow.md             |
| authentext          | local_ai                | Optional prose-quality and claim-boundary linting for manuscripts and dashboards; never an evidence source.                                    | scripts/check_claim_boundaries.py                      | upstream/issues/authentext-claim-boundary-policy.md           |
| sourceright         | platform_infrastructure | Claim–source provenance, evidence grading, citation verification, licence state, and Arrow evidence-graph interchange.                         | src/closer_to_whom/integrations/sourceright_adapter.py | upstream/issues/sourceright-evidence-licence-arrow.md         |
| mchs                | core_analysis           | Health-service resource, staffing, activity, and cost-envelope methods supporting implied capacity rather than claims about observed capacity. | src/closer_to_whom/capacity.py                         | upstream/issues/mchs-implied-capacity-envelope.md             |
| mars                | core_analysis           | Transparent surrogate modelling and diagnostics for expensive PSA, EVPPI, and optimisation loops.                                              | src/closer_to_whom/voi.py                              | upstream/issues/mars-evppi-surrogate-diagnostics.md           |
| ginsim              | core_analysis           | JAX/XLA numerical and simulation reference harness for accelerated probabilistic and policy-economic computation.                              | src/closer_to_whom/accel/jax_psa.py                    | upstream/issues/ginsim-jax-differential-receipts.md           |
| conductor-next      | agent_harness           | Machine-readable cross-repository planning, dependency graphs, agent receipts, verification gates, and handover orchestration.                 | conductor/task-graph.json                              | upstream/issues/conductor-next-cross-repository-ecosystem.md  |
| vop_poc_nz          | core_analysis           | Value-of-perspective, distributional economics, and explicit decision-maker viewpoint profiles for MCDA and VOI.                               | src/closer_to_whom/integrations/perspective.py         | upstream/issues/vop-poc-nz-perspective-contracts.md           |

## Core and strong integration contracts

| Repository                             | Tier   | Category                | Integration modes                                                      | Dependency policy  |
| -------------------------------------- | ------ | ----------------------- | ---------------------------------------------------------------------- | ------------------ |
| fyi-cli                                | core   | platform_infrastructure | cli_adapter, mcp_adapter, oia_workflow                                 | optional_adapter   |
| fyi-archive                            | core   | publication             | cli_adapter, publication_target, evidence_archive                      | optional_adapter   |
| open_social_data                       | core   | data_evidence           | arrow_contract, data_source, cli_adapter                               | optional_adapter   |
| osf-cli-go                             | core   | publication             | cli_adapter, publication_target, open_science_deposit                  | optional_adapter   |
| reimbursement-atlas                    | core   | core_analysis           | arrow_contract, cost_source, evidence_readiness                        | optional_adapter   |
| rac-conformance                        | core   | policy_rules            | conformance_contract, policy_interchange, oracle_harness               | optional_adapter   |
| rulespec-nz                            | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| sm-govt-nz                             | strong | dissemination           | dashboard_pattern, publication_target                                  | optional_or_source |
| policyengine-core                      | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| openfisca-aotearoa-br                  | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| innovate                               | core   | core_analysis           | python_adapter, arrow_contract, adoption_model                         | optional_adapter   |
| voiage                                 | core   | core_analysis           | python_adapter, value_of_information                                   | optional_adapter   |
| gtpcnz                                 | core   | dissemination           | dashboard_pattern, quarto_pattern, claim_boundary_pattern              | optional_adapter   |
| healthpoint-rs                         | core   | data_evidence           | cli_adapter, mcp_adapter, arrow_contract, licensed_data_source         | optional_adapter   |
| dnz                                    | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| UOGTO                                  | strong | policy_rules            | ontology, knowledge_graph, mcda_semantics                              | optional_or_source |
| nlp-policy-nz                          | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| foi-o                                  | strong | policy_rules            | ontology, oia_semantics                                                | optional_or_source |
| kairos                                 | core   | core_analysis           | arrow_contract, rust_backend, des_abm                                  | optional_adapter   |
| openfisca-aotearoa-betterules          | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| openfisca-core                         | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| entireio-cli                           | strong | agent_harness           | agent_session_receipt, git_integration                                 | optional_or_source |
| git-sync                               | strong | agent_harness           | repository_mirroring, publication_target                               | optional_or_source |
| standards_check                        | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| arxiv-latex-template                   | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| anz-legislation                        | strong | policy_rules            | cli_adapter, mcp_adapter, policy_source                                | optional_or_source |
| authentext                             | core   | local_ai                | agent_skill, claim_boundary_lint                                       | optional_adapter   |
| corpus-nz-hansard                      | strong | data_evidence           | data_source, parquet_contract, doi_snapshot                            | optional_or_source |
| microsim_oa                            | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| corpus-cases-medilegal-nz              | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| digitalnz                              | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| rust4pm                                | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| propel                                 | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| substack-cli-ts                        | strong | dissemination           | dashboard_pattern, publication_target                                  | optional_or_source |
| axiom-rules-engine                     | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| sourceright                            | core   | platform_infrastructure | cli_adapter, mcp_adapter, provenance_contract                          | optional_adapter   |
| mchs                                   | core   | core_analysis           | python_adapter, arrow_contract, resource_costing                       | optional_adapter   |
| corpus-legislation-nz                  | strong | data_evidence           | data_source, parquet_contract, doi_snapshot                            | optional_or_source |
| unofficial_formslibrary                | strong | data_evidence           | service_evidence_source                                                | optional_or_source |
| fe-reader                              | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| api-standards                          | strong | policy_rules            | security_standard, api_contract                                        | optional_or_source |
| nz-legislation                         | strong | policy_rules            | cli_adapter, mcp_adapter, policy_source                                | optional_or_source |
| merman                                 | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| astro-polyglot                         | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| pybibx                                 | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| codev                                  | strong | agent_harness           | agent_protocol, context_management                                     | optional_or_source |
| Kotahi                                 | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| openfisca-aotearoa                     | strong | policy_rules            | policy_source, rules_engine, conformance_contract                      | optional_or_source |
| joss                                   | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| mars                                   | core   | core_analysis           | python_adapter, surrogate_model                                        | optional_adapter   |
| typst                                  | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| conductor-upstream-canonical           | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| Budget_2026_MMH                        | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| NationalWeightedActivityUnitWrapper.jl | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| NwauCore.jl                            | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| api-standards-conformance              | strong | policy_rules            | conformance_contract, security_standard                                | optional_or_source |
| nzmedicines                            | strong | data_evidence           | clinical_evidence_source, policy_source                                | optional_or_source |
| lifecourse                             | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| nice-graph                             | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| academic-research-skills               | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| postiz-agent                           | strong | dissemination           | dashboard_pattern, publication_target                                  | optional_or_source |
| scholarly-publishing-agents            | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| ginsim                                 | core   | core_analysis           | jax_reference, psa_harness, policy_economics                           | optional_adapter   |
| conductor-next                         | core   | agent_harness           | agent_protocol, task_graph, machine_receipts                           | optional_adapter   |
| nhra_game                              | strong | core_analysis           | decision_model_reference, game_theory_reference, harness_pattern       | optional_or_source |
| rcagent                                | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| research-skills                        | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| knowledge-work-plugins-next            | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| co-researcher                          | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| linear-history                         | strong | agent_harness           | git_integration, provenance_contract                                   | optional_or_source |
| awesome-agent-skills                   | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| claude-scientific-skills               | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| ralph-codex                            | strong | agent_harness           | agent_protocol, task_execution                                         | optional_or_source |
| vbm-replication-extension              | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| osf-mcp-server                         | strong | publication             | mcp_adapter, publication_target                                        | optional_or_source |
| blueprint-extension                    | strong | agent_harness           | agent_protocol, workflow_reuse, machine_receipts                       | optional_or_source |
| vop_poc_nz                             | core   | core_analysis           | python_adapter, distributional_economics, perspective_profiles         | optional_adapter   |
| ee_trd                                 | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| wasm-typst-studio-rs                   | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| nztaxmicrosim                          | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| scimapping                             | strong | data_evidence           | evidence_map, method_reuse                                             | optional_or_source |
| nz_health_appropriations               | strong | data_evidence           | public_finance_source, time_series_source, evidence_receipt            | optional_or_source |
| synergy-dataset                        | strong | data_evidence           | systematic_review_benchmark, screening_workflow_reference, data_source | optional_or_source |
| DES_tutorial_AHEA                      | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| PRISMA2020                             | strong | publication             | reporting_standard, workflow_reference                                 | optional_or_source |
| prisma-flow-diagram                    | strong | publication             | publication_asset, reporting_standard                                  | optional_or_source |
| Academic-project-page-template         | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| PRISMA.jl                              | strong | publication             | method_reuse, reporting_standard                                       | optional_or_source |
| lifetimes                              | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| pydnz                                  | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| powerbi-cli                            | strong | dissemination           | dashboard_pattern, publication_target                                  | optional_or_source |
| Raconteur                              | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |
| Friction                               | strong | data_evidence           | data_source, arrow_contract, cli_adapter                               | optional_or_source |
| CAPITA                                 | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| interpret                              | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| lifestyles                             | strong | core_analysis           | arrow_contract, python_adapter, method_reuse                           | optional_or_source |
| paper-now                              | strong | publication             | publication_target, cli_adapter, workflow_reuse                        | optional_or_source |

## Cross-repository pipelines

| Pipeline                 | Repos | Purpose                                                                                                       | Gate                                                                                             |
| ------------------------ | ----- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| evidence-census          | 22    | Build the national public-source service census and evidence graph                                            | licence, source date, evidence grade, and redistribution status required                         |
| policy-conformance       | 18    | Represent funding, eligibility, safety, and policy assumptions as executable but reviewable contracts         | human-reviewed oracle and non-compensatory clinical constraints                                  |
| decision-analysis        | 24    | Run access, cost, equity, optimisation, adoption, capacity, uncertainty, and research-prioritisation analyses | reference-oracle parity, deterministic seeds, DSA/PSA/VOI and claim-boundary checks              |
| agent-harness            | 24    | Maintain an auditable, machine-readable, multi-agent development and research workflow                        | agents may propose; deterministic tools verify; human review controls publication                |
| open-science-publication | 23    | Create reproducible deposits, manuscripts, diagrams, public dashboards, and archival mirrors                  | dry-run plans by default; checksums and publication-readiness gate before writes                 |
| oia-transparency         | 4     | Use optional OIA requests to improve public evidence without making them a model dependency                   | no request submission without explicit human action                                              |
| public-dissemination     | 15    | Surface aggregate outputs and communicate limitations without creating a second source of truth               | dashboard and social outputs generated only from frozen aggregate artefacts                      |
| optional-local-ai        | 11    | Support private local drafting and agent workflows while keeping evidence and decisions deterministic         | not a factual source, not an autonomous policy decision-maker, and not required for reproduction |

## Explicit exclusions

| Repository               | Category                | Reason                                                                                                                                                                              |
| ------------------------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| vcpkg                    | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| pacx                     | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| apfs-rs                  | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| hpo-translations         | domain_reference        | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| human-phenotype-ontology | domain_reference        | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| Extras                   | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| staged-recipes           | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| f7fztfn9vz               | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| conan-center-index       | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| homebrew-mchs            | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| mchs-swift               | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| ollama-old               | local_ai                | Excluded from active composition: obsolete test copy superseded by the maintained ollama repository; retaining it would duplicate an optional local-AI role without research value. |
| leed_pdf_viewer          | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| spack-packages           | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| easybuild-easyconfigs    | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| spack                    | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| rquickshare              | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| ANE                      | platform_infrastructure | Excluded from active composition: reverse-engineered private Apple APIs and an explicit non-production status create avoidable security, stability, and reproducibility risk.       |
| packages                 | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| tweepy                   | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| client-py                | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| client-js                | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| todo.txt                 | platform_infrastructure | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| unisa-tbi                | domain_reference        | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |
| CFTRDataTransfer         | domain_reference        | Insufficient direct relevance, superseded tooling, restricted-data orientation, or general build infrastructure; retained in the audit for completeness only.                       |

## Complete machine-readable inventory

The canonical inventory contains every public repository in profile order, including forks, exclusions, guardrails, and local integration status. Use `closer-to-whom ecosystem export` to emit equivalent Arrow IPC and Parquet catalogues.

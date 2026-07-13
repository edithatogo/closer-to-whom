# Codex execution prompt — integrate and complete **Closer to whom?**

You are operating inside the destination Git repository. A single archive named `closer-to-whom-codex-handover.zip` has been copied into the repository root. Perform the complete integration and continue the implementation without asking the user to run any other command or provide any other file.

Use best judgement, preserve existing work, and make progress autonomously. Ask a question only when an irreversible external action genuinely requires consent. Missing credentials, unavailable services, or unavailable proprietary data are not reasons to stop: complete everything possible, record the blocked item in Conductor, and leave a replayable command or automation for the local environment.

## 1. Import safely and preserve Git history

1. Inspect the current repository, branch, remotes, worktree status, existing `AGENTS.md`, local instructions, and repository conventions before changing anything.
2. Create a dedicated integration branch such as `codex/closer-to-whom-integration-YYYYMMDD`. Never use `git reset --hard`, never discard uncommitted user work, and never overwrite a newer local implementation blindly.
3. Locate the archive by exact name first, then by a unique `*closer-to-whom*handover*.zip` match if necessary.
4. Verify the archive against its embedded manifest and checksums. Reject path traversal, absolute paths, symlinks escaping the extraction root, and unexpected executable binaries.
5. Extract to a temporary, ignored directory such as `.codex-handover/`.
6. The archive contains:
   - an embedded Git bundle with the handover history;
   - a complete source snapshot;
   - the nationwide GitHub-ecosystem catalogue and audit;
   - inherited validation and release evidence that must be treated as reported evidence and rerun locally;
   - the original 2017 briefing as reference material only.
7. Prefer the embedded Git bundle to preserve attribution and history. Run `git bundle verify`, fetch its branch and tags into a temporary remote namespace, and inspect the ancestry and diff. If the current repository is empty, adopt the handover history. If the current repository already has work, merge or import at path level with reviewed conflict resolution. Use `--allow-unrelated-histories` only when actually necessary.
8. Treat the source snapshot as a verification oracle and recovery source, not as authority to overwrite newer files. Reconcile bundle, snapshot, and current tree explicitly.
9. Do not commit the outer ZIP. Do not publish or commit the reference PDF by default; keep it in ignored local handover material unless the repository already has a deliberate source-material policy permitting it.
10. Make small, logical commits with Conventional Commit messages. Preserve the handover commit history where possible. Do not create a release tag until the full local release gate passes.

## 2. Read order and canonical state

Read and reconcile these before implementation:

1. all applicable `AGENTS.md` files and repository-local instructions;
2. `conductor/project.yaml`, `conductor/state.yaml`, `conductor/task-graph.json`, release gates, decisions, and active tracks;
3. `protocol/protocol.yaml`, `protocol/claim-boundaries.yaml`, and clinical-safety constraints;
4. `assumptions/assumptions.yaml`, distributions, MCDA profiles, and research designs;
5. `data/public/source-registry.yaml` and licence policy;
6. `ecosystem/github-repositories.yaml`, `ecosystem/pipelines.yaml`, `ecosystem/tool-contracts.yaml`, and the generated ecosystem audit;
7. Arrow/JSON schemas and registry indexes;
8. `HANDOVER.md`, architecture, model card, ethics/scope, publication protocol, and the original briefing in the extracted reference area;
9. inherited validation files under `handover/inherited/`, noting that these are claims to reproduce rather than automatically trusted pass results.

Machine-readable contracts are canonical. Generated prose must be regenerated from them where practicable. Never replace a structured contract with prose-only state.

## 3. Non-negotiable research boundaries

The project is an independent, ex-ante health-service policy evaluation and simulation using public, aggregate, non-identifiable information.

1. Use only publicly available aggregate inputs in the open pipeline. No patient-level, confidential, de-identified clinical, unpublished operational, or inferred individual records.
2. Do not create pseudo-patients. Use aggregate expected treatment demand cells, which may be fractional.
3. Treat undocumented service capability as **unknown**, not absent. A hospital, oncology clinic, outreach clinic, day unit, or haematology chemotherapy service does not by itself prove breast-cancer anti-HER2 capability.
4. Do not represent synthetic fixtures as observed New Zealand services, demand, travel, capacity, patient behaviour, waiting, attendance, adherence, outcomes, or cost-effectiveness.
5. Healthpoint access and redistribution are fail-closed. Use `healthpoint-rs` only when local credentials and licences explicitly permit the particular acquisition, transformation, storage, publication, and dashboard use. Synthetic fixtures must remain the default.
6. OIA requests using `fyi-cli` are optional evidence-development work, not build or analysis dependencies.
7. Clinical safety, product eligibility, funding status, medicine governance, emergency capability, cold chain, observation requirements, and healthcare-professional administration are hard constraints. Optimisation or MCDA may not trade them away.
8. Standalone subcutaneous trastuzumab and PHESGO are distinct pathways. PHESGO is pertuzumab plus trastuzumab and is not a universal substitute for trastuzumab alone. Do not model self-administration.
9. Home and community scenarios shift travel, time, cold-chain, observation, escalation, and resource burdens to providers; they are not zero-cost scenarios.
10. This phase cannot claim actual patient preferences or realised access. Nearest-site, district-first, central-preference, public-transport, and home-adoption behaviours are explicit scenarios.
11. Any future microdata or participant research is a separate protocol with governance and ethics-scope assessment. Maintain the HDEC/out-of-scope policy-evaluation framing without mislabelling generalisable research as audit merely to avoid review.
12. Keep the original policy insight central: administrative localisation or a service inside a domicile district does not necessarily reduce door-to-door burden, cost, or difficulty for every population.

## 4. Complete the nationwide New Zealand programme

Implement the model for all of Aotearoa New Zealand rather than limiting the architecture to the Northern Region. Northern results may remain a sentinel subset, but the production contracts, service census, demand system, routing, scenarios, optimisation, uncertainty, dashboard, and publication pipeline must be national.

### Service census

Build a reproducible, living, systematic public-source census of cancer and systemic anti-cancer treatment services. Search official Health New Zealand, Te Aho o Te Kahu, Pharmac, Medsafe, HPI/facility tables, service specifications, official reports, public OIA releases, archived former-DHB pages, and suitably licensed directories. Record source URL, retrieval timestamp, archive/checksum, licence, evidence grade, claim, and reviewer state.

Use evidence grades and conservative/plausible/broad network scenarios. Separate:

- facility existence;
- medical oncology presence;
- solid-tumour SACT capability;
- IV trastuzumab capability;
- subcutaneous trastuzumab capability;
- PHESGO capability;
- outreach clinic presence;
- treatment administration versus consultation only;
- public versus private delivery;
- current, historical, planned, and uncertain status.

### Aggregate demand and geography

Use public Census and statistical geography, NZDep, GCH rurality, public cancer-incidence information, and public treatment/funding anchors. Represent within-area uncertainty with population-weighted support points or public grids, never purported individuals. Calibrate only to public aggregate totals. Preserve ethnicity-method assumptions, overlapping total-response categories, ecological limitations, and uncertainty.

### Routing and travel burden

Use road-network and multimodal routing with engine/version fingerprints, tiled caching, deterministic keys, and reproducible fallbacks. Include car, public transport, ferry where relevant, walking/waiting/transfer time, appointment-time variants, parking, fares, tolls, accommodation where needed, and provider routing for home/mobile delivery.

Estimate:

- course-level round-trip distance and door-to-door time;
- direct patient and whānau costs;
- patient and accompanying-person time;
- National Travel Assistance reimbursement separately as a transfer;
- public-payer, provider, and societal perspectives;
- course-level distributions, tails, and better-off/worse-off shares;
- excess burden versus the least-burden clinically feasible option.

### Scenarios

Maintain explicit scenario status: current documented/funded, licensed but funding uncertain, commissioning counterfactual, or exploratory infrastructure option. Include at minimum:

- centralised IV;
- domicile-district allocation;
- nearest documented eligible IV service;
- alternative assignment rules within the documented network;
- new IV satellite sites;
- parking/shuttle/travel-support alternatives;
- hospital-based standalone SC trastuzumab where clinically applicable;
- hospital/satellite PHESGO for eligible pathways;
- GP/community healthcare-professional SC administration;
- home/mobile healthcare-professional SC administration after safe establishment;
- hybrid central-initiation and local/home maintenance;
- temporary site outage and resilience;
- low/central/high demand and capability networks.

Model early and metastatic disease separately, including differing visits, concurrent chemotherapy, monitoring, treatment duration, and residual hospital contacts.

### Capacity and infrastructure

Do not invent observed capacity. Calculate **implied requirements** under each scenario:

- administrations per site and period;
- active nursing minutes/hours and productive FTE;
- chair/treatment-space time;
- observation-space time;
- pharmacy or medicine-handling events;
- indicative service days;
- home/mobile provider kilometres, travel time, and staff time;
- resilience buffers and outage reallocation.

Use transparent low/central/high capacity envelopes only as scenario assumptions. Label them as assumptions, not current Health New Zealand capacity.

### Optimisation and MCDA

Implement and compare p-median, p-centre/minimax, maximal coverage, equity-constrained, resilient, and robust/multiobjective location-allocation. Generate Pareto frontiers across patient burden, direct cost, equity, infrastructure, provider workload, resilience, and optional emissions.

Use MCDA after optimisation to compare the efficient shortlist on factors not credibly collapsed into a single monetary outcome. Use transparent patient/whānau, Māori/equity, provider, payer, and societal viewpoints. Where no formal stakeholder elicitation exists, use stochastic multicriteria acceptability analysis and broad weight distributions rather than claiming consensus weights. Keep safety and clinical feasibility outside compensatory scoring.

### Uncertainty and value of information

Implement:

- deterministic one-way and two-way sensitivity analysis;
- structural scenarios;
- probabilistic sensitivity analysis using deterministic random or quasi-random streams;
- correlated inputs where defensible;
- probability of optimality, expected regret, Pareto membership, site-selection probability, and equity-condition probability;
- EVPI, EVPPI, EVSI, ENBS, and break-even research cost.

Explicitly compare the value of:

- further public-source searching;
- public OIA information;
- aggregate service-level operational research;
- patient-level microdata research;
- a patient transport/preference survey.

The decision question is whether resolving current uncertainty could change the preferred service configuration or an important equity conclusion enough to justify the research cost and governance burden.

## 5. Use the owner’s GitHub ecosystem intelligently

The handover contains a frozen public catalogue of 165 repositories, 96 identified forks, 137 repositories assigned a bounded role, and 18 proposed core typed integrations. Treat this as a starting inventory, not a live truth claim.

1. If GitHub network access is available, use the authenticated `gh` CLI or GitHub API to refresh all repositories accessible to the account, including private repositories only for local assessment. Never expose private repository names, metadata, code, or findings in public artefacts without explicit permission.
2. Reconcile renames, archived/deleted repositories, default branches, licences, release status, forks, and new repositories. Record the snapshot date and query method.
3. Include as many suitable repositories as provide a real, bounded role. Do not manufacture integrations merely to increase a count.
4. Forks, archived repositories, obsolete copies, reverse-engineered private APIs, and repositories with incompatible licences are reference-only or excluded unless a documented, safe use case exists.
5. No owner repository becomes a mandatory production runtime dependency merely because it exists. Use adapters, language-neutral Arrow/Parquet contracts, compatibility tests, pinned revisions, and local fallbacks.
6. The proposed core repositories include `sourceright`, `authentext`, `innovate`, `voiage`, `kairos`, `mars`, `open_social_data`, `healthpoint-rs`, `fyi-cli`, `fyi-archive`, `osf-cli-go`, `reimbursement-atlas`, `rac-conformance`, `gtpcnz`, `mchs`, `ginsim`, `conductor-next`, and `vop_poc_nz`. Verify each against its current upstream state before relying on it.
7. For reusable functionality that belongs in an owner library rather than only in this application:
   - create or reconcile a Conductor track;
   - open or update a GitHub issue when authenticated;
   - implement in an isolated worktree against the current default branch;
   - add unit, property, contract, compatibility, and migration tests;
   - run the upstream project’s own harness;
   - publish a draft PR only after the patch replays cleanly;
   - record the issue/PR/revision and compatibility receipt;
   - retain a local fallback until the upstream release is available.
8. If GitHub mutation is unavailable, prepare exact issue bodies, patch branches/bundles, and replay commands. Do not claim an issue, PR, merge, or release exists unless verified live.
9. Implement a safe ecosystem materialiser that is plan-only by default; source checkout requires explicit network and write flags and never automatically installs, imports, builds, or executes acquired repositories.

## 6. Technical architecture

Use a bleeding-edge but robust architecture:

- Python 3.14 as the sole orchestration and reference implementation;
- Polars as the default dataframe engine;
- Arrow IPC and Parquet as canonical language-neutral interchange;
- Pydantic or equivalent typed configuration and record contracts;
- JAX/XLA for vectorised repeated simulation where it provides measured value;
- Mojo as a first-class accelerator candidate for proven hot paths, with a pinned toolchain, parity fixtures, differential tests, benchmark gates, and a non-Mojo fallback;
- Rust for licence-safe connectors or performance-sensitive ingestion/routing where justified;
- Julia/JuMP only when it materially improves complex optimisation, via Arrow/Parquet or CLI boundaries;
- mature mathematical solvers with a documented open-source default and optional commercial backends;
- precomputed aggregate result cubes for the public dashboard.

Do not introduce a framework without a measured need, clear ownership, licence compatibility, and an exit path. Prefer typed protocols and small adapters over deep coupling.

Control resource use explicitly: cap Polars/BLAS/XLA threads, disable unsafe accelerator preallocation by default, record effective resource settings in run manifests, and test repeated runs for thread/file-descriptor/memory leakage.

## 7. Maximal harness engineering and CI/CD

Bring the repository to a high-assurance research-software standard. Implement or complete:

### Local developer experience

- `uv.lock` with public, portable sources;
- one-command bootstrap, doctor, check, verify, release-gate, dashboard, docs, and clean-room targets;
- `Makefile`, `justfile`, optional `mise`/`pixi`, devcontainer, Docker Compose, and clear local handover documentation;
- pre-commit and pre-push hooks;
- deterministic generated-file checks;
- conventional commits and commit-message validation.

### Code quality

- Ruff formatting and linting;
- strict Mypy and Pyright;
- docstring coverage;
- dead-code and complexity budgets;
- dependency hygiene;
- spelling and Markdown/YAML/JSON validation;
- import-boundary and architecture tests;
- no hidden network calls in unit tests.

### Testing

- unit and integration tests;
- Hypothesis property tests;
- metamorphic tests for routing, assignment, cost, optimisation, equity, and VOI invariants;
- differential tests across NumPy/Polars/JAX/Mojo/Rust/Julia implementations where applicable;
- golden-contract fixtures and schema migration tests;
- reproducibility tests across repeated runs and clean checkouts;
- fuzz tests for parsers and untrusted public-source inputs;
- performance budgets and regression benchmarks;
- resource-leak tests;
- mutation testing or bounded mutation canaries for critical decision logic;
- high branch coverage with stricter thresholds for safety, costing, optimisation, and publication-claim modules.

### Security and supply chain

- secret scanning;
- dependency and licence audit;
- CodeQL/static security analysis;
- dependency review;
- SBOM generation;
- provenance and build attestations;
- pinned GitHub Actions by immutable SHA where practicable;
- minimal workflow permissions;
- protected environments for deployment;
- Renovate and/or Dependabot;
- signed or annotated release tags and reproducible release manifests.

### CI/CD

Create or repair workflows for:

- Linux/macOS/Windows and supported Python versions;
- lint/type/test/coverage;
- clean-room installation from wheel/sdist;
- generated-file drift and contract compatibility;
- documentation and Quarto manuscript rendering;
- container build and health check;
- Hugging Face Spaces Docker deployment using secrets and protected environments;
- stable and nightly Mojo canaries;
- Rust and optional Julia compatibility;
- reproducibility and benchmark schedules;
- security, SBOM, provenance, and release publication;
- scheduled public-source and GitHub-ecosystem drift detection.

Every unavailable local tool must be reported as **not run**, never silently treated as passed. CI definitions alone are not execution evidence.

## 8. Agent-optimised and machine-readable workflow

Use Conductor as the project control plane. Maintain:

- dependency-aware tracks, tasks, blockers, owners, acceptance criteria, and receipts;
- ADRs and a decision log;
- canonical YAML/JSON scenario, assumption, source, facility, pathway, cost, uncertainty, MCDA, VOI, and publication contracts;
- Arrow schema registry and versioned migrations;
- provenance graph and claim-source links;
- deterministic task graph exports;
- machine-readable run manifests, environment fingerprints, hashes, and data licences;
- a model card, data card, service-census protocol, statistical analysis plan, economic-analysis plan, validation plan, threat model, and incident/retraction process.

Keep the system machine-readable and agent-optimised until manuscript freeze. Generate human-readable reports and manuscript sections from canonical state wherever possible.

## 9. Dashboard and publication

Prepare a Docker-based Hugging Face Space that serves only precomputed aggregate outputs. It must contain no individual points, licensed live payloads, secrets, or unreviewed operational claims. Include service atlas, scenario laboratory, travel/cost burden, equity, implied infrastructure, optimisation frontier, uncertainty, VOI, MCDA, assumptions, source provenance, limitations, and model/version pages.

Target a clinically focused NZMJ paper on nationwide or nationally structured results, with a Northern sentinel analysis only if useful. Keep the main clinical message understandable: who is likely to be made better or worse off, by how much, under which explicit assumptions. Put detailed robust optimisation, MCDA, PSA, and VOI methods in a second methods/decision-science paper and technical report. Preserve an explicit assumptions appendix and AI-use disclosure. Do not claim publication readiness before service-census freeze, clinical review, Māori/equity governance review, ethics-scope documentation, and all publication gates are complete.

## 10. Required completion behaviour

Proceed through implementation, verification, documentation, and Git commits autonomously. At the end:

1. leave the working tree clean except for deliberately ignored local handover material;
2. update Conductor state, task graph, decisions, receipts, validation, handover, and release notes;
3. run the strongest available local verification and record exact commands, versions, pass/fail/not-run status, durations, coverage, benchmark results, and hashes;
4. build wheel/sdist, documentation, container where available, deterministic synthetic demonstration, SBOM, release manifest, and an updated handover archive;
5. create an annotated candidate tag only if the complete release gate passes; otherwise commit the verified state without a misleading release tag;
6. prepare any upstream issues/PRs or offline patches required by the owner-library work;
7. produce one concise final terminal report containing:
   - integration strategy and commits;
   - imported handover revision;
   - work completed;
   - exact verification results;
   - generated artefacts and hashes;
   - upstream issue/PR status;
   - unresolved external dependencies and blocked tracks;
   - any claim-boundary, clinical, licence, privacy, equity, ethics, reproducibility, or publication concern.

Do not stop after merely unpacking or planning. Implement as much of the programme as the local environment permits, while keeping every claim auditable and every unavailable dependency explicit.

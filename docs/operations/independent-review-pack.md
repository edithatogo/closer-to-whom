# Independent review pack

This pack supports independent review of the software and its evidence boundary. It does not
replace clinical, Māori/equity, licensing, or ethics review, and reviewer completion must be
recorded in the applicable machine-readable receipt.

## Software and reproducibility

- PR: https://github.com/edithatogo/closer-to-whom/pull/36
- Public dashboard: https://edithatogo-closer-to-whom.static.hf.space
- Python support: 3.14 only.
- Local release receipt: `release/verification-receipt.json`.
- Claim boundary: synthetic or public aggregate demonstration only; no patient-level, observed
  capacity, clinical-outcome, causal, or actual waiting-time claims.
- Public Space content is precomputed aggregate data only; live Healthpoint payloads are excluded.

## Evidence candidates requiring adjudication

### Geography and public inputs

- Stats NZ, Statistical Standard for Geographic Areas 2023:
  https://www.stats.govt.nz/assets/Methods/Statistical-standard-for-geographic-areas-2023/Statistical-standard-for-geographic-areas-2023.pdf
- University of Otago, NZDep2023:
  https://www.otago.ac.nz/wellington/research/groups/research-groups-in-the-department-of-public-health/hirp/socioeconomic-deprivation-indexes
- University of Otago, GCH23:
  https://www.otago.ac.nz/centre-for-rural-health/research/geographic-classification-for-health

Recommended review decisions:

- [ ] Approve SSGA23 SA2 as the planned principal geography, subject to input and licence freeze.
- [ ] Approve GCH23 as a separate rurality stratifier, not a replacement for network travel.
- [ ] Confirm whether transformed GCH23 outputs may be redistributed under the stated licence.
- [ ] Confirm the version, retrieval receipt, and licence state for NZDep2023 and public Census inputs.

### Clinical and funding boundary

- Pharmac, current Phesgo funding decision:
  https://www.pharmac.govt.nz/news-and-resources/consultations-and-decisions/2025-11-decision-to-fund-treatments-for-multiple-sclerosis-eye-conditions-breast-cancer-and-lung-cancer
- Current model pathway review template: `data/public/clinical-pathway-review.yaml`.

Required reviewer roles:

- [ ] Medical oncology.
- [ ] Oncology pharmacy or medicine governance.
- [ ] Nursing or SACT service.
- [ ] Māori health interpretation.

Clinical review questions:

- [ ] Are medicine, formulation, indication, funding state, schedule, monitoring, and setting
      constraints accurate for each proposed pathway?
- [ ] Are initial higher-risk doses constrained to an eligible hospital-capable setting?
- [ ] Is home delivery explicitly healthcare-professional administered?
- [ ] Does the available evidence support the early-breast-cancer pathway, or must it remain a
      synthetic non-evidentiary demonstration?
- [ ] Are unresolved ambiguities recorded with a decision and dated receipt?

## Governance and ethics boundary

Review in `data/public/governance-review.yaml` must separately record:

- Māori/equity interpretation review;
- culturally safe interpretation constraints;
- unresolved equity risks; and
- ethics/HDEC scope determination.

No completed status should be recorded without dated receipts and named reviewers. A future
microdata or participant-research phase remains outside this build and requires a separate protocol.

## Approval rule

Independent approval should assess repository contracts, provenance, safety boundaries, licensing,
and reproducibility. Synthetic outputs must not be treated as evidence of New Zealand service
capability, demand, capacity, clinical eligibility, outcomes, or cost-effectiveness.

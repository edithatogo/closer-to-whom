# Systematic public-source census

The service atlas is a living, versioned census rather than an unstructured web search. Each candidate claim is represented as a facility–capability–time tuple linked to a source snapshot and an explicit evidence grade. Facility existence, oncology clinic presence, solid-tumour SACT capability, anti-HER2 capability, formulation-specific capability, outreach, and home delivery are separate claims.

The core rule is **unknown is not absent**. Lack of qualifying public evidence produces `unknown`, never `false`. Grade 1, drug-specific claims require a dated sole-developer qualified-clinician evidence receipt before publication. The repository is a sole-developer code harness and does not require a second GitHub approval. A conservative network uses only the strongest qualifying evidence; structural sensitivity analyses progressively include weaker but plausible evidence grades.

Search protocol, inclusion and exclusion rules, review state, source dates, retrieval dates, checksums, supersession, licensing, and redistribution decisions are machine-readable in `protocol/` and `data/public/`.

The 2026-07-21 capture includes 19 publicly documented Health New Zealand service locations. The
captured pages are covered by Health New Zealand's CC BY 4.0 website-text licence; photographs,
illustrations, logos, and third-party material remain excluded. These records are deliberately
`plausible` grade-3 facility-level cancer/SACT signals with no named anti-HER2 formulation. The
conservative network therefore remains empty until stronger evidence and the required clinical
review receipts are available; plausible and broad networks may include these locations.

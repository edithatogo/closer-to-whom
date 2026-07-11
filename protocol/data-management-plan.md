# Data management plan

## Scope

The development and publication phase accepts only public, aggregate, non-identifiable inputs. Confidential, de-identified patient-level, linked, or operationally restricted data are outside this protocol and must enter a separately governed future phase.

## Zones

1. `data/public/`: small, redistributable manifests and curated public extracts whose licence has been verified.
2. `data/cache/`: immutable downloaded bytes keyed by digest; ignored by Git.
3. `data/derived/`: reproducible aggregate transformations; ignored unless explicitly approved for release.
4. `artifacts/demo/`: synthetic demonstration outputs; ignored and reproducible.
5. `release/`: verification receipts and non-data release metadata.

## Required metadata

Every source must record identity, landing page, publisher, retrieval time, source date, content digest, licence status, redistribution status, transformation history, evidence grade, and review state. Unknown licensing is fail-closed.

## Publication

The dashboard consumes precomputed aggregate Arrow/Parquet result cubes. No raw source payload, exact confidential coordinate, API credential, live Healthpoint payload, or row represented as an actual patient may be served.

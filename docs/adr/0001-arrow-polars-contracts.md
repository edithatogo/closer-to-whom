# ADR 0001: Arrow and Polars are the canonical data plane

- Status: accepted
- Date: 2026-07-11

## Decision

Use Polars for transformations and Arrow/Parquet for language-neutral contracts, caches, and result cubes.

## Rationale

The project spans Python, Rust, Julia, Mojo, JAX, web presentation, and publication. Arrow avoids bespoke serialisation and supports schema fingerprints, zero-copy interfaces, partitioned processing, and deterministic aggregate exchange.

## Consequences

Every component must consume or emit versioned schemas. Pandas may be used only at external library boundaries, not as the canonical internal representation.

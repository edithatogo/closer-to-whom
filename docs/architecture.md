# Architecture

## Principles

1. **Arrow at every boundary.** Polars is the principal transformation engine; Arrow/Parquet schemas are the language-neutral exchange contract.
2. **Reference before acceleration.** NumPy/Polars implementations are correctness oracles. JAX and Mojo must pass differential tests before promotion.
3. **Precompute expensive work.** National routing, PSA, optimisation, and VOI produce versioned aggregate cubes. The public dashboard performs filtering and presentation, not unrestricted analysis.
4. **Fail closed.** Unknown source licences, undocumented facility capability, missing clinical review, and live Healthpoint access never silently become permissive.
5. **Separate uncertainty classes.** Parameter, spatial, structural, normative, and decision uncertainty retain distinct identities.
6. **Machine-readable first.** YAML/JSON/Arrow contracts are canonical; prose and tables are generated or checked against them.

## Layers

```text
Public source registry and licence ledger
               │
               ▼
Evidence census ──► facility capability registry
               │
Population + epidemiology ──► aggregate expected demand cells
               │
Transport networks ──► versioned origin–destination matrices
               │
Clinical pathways + scenario catalogue
               │
               ▼
Polars/Arrow simulation kernel
   ├── travel and cost consequences
   ├── equity distributions
   ├── implied capacity
   ├── optimisation
   ├── DSA / PSA / structural uncertainty
   ├── MCDA / SMAA
   └── VOI / future-research decision
               │
               ▼
Signed aggregate result cube + verification receipt
               │
        ┌──────┴───────┐
        ▼              ▼
Hugging Face Space   Quarto/NZMJ outputs
```

## Backends

- **Python/Polars/Arrow:** canonical implementation and orchestration.
- **JAX/XLA:** optional batched numerical kernels; CPU is the portability baseline.
- **Mojo:** experimental hot-path backend behind a canary and promotion ADR.
- **Rust/healthpoint-rs:** licensed acquisition interface when locally authorised.
- **Julia/JuMP:** optional Arrow-compatible solver service for large robust or stochastic optimisation.

No backend may alter the semantic contracts or bypass validation.

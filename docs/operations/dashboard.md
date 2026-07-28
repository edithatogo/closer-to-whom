# Public dashboard

The public Hugging Face Static Space reads embedded precomputed aggregate result cubes. It performs no live routing, web scraping, licensed-source access, clinical inference, or user-provided address calculation. The Docker image remains a local and CI smoke-test surface.

Required pages for publication:

1. service atlas with evidence grade and freeze date;
2. scenario laboratory;
3. patient and whānau burden;
4. equity distributions and ecological warning;
5. implied infrastructure;
6. optimisation frontier;
7. uncertainty and structural scenarios;
8. VOI and break-even research cost;
9. MCDA rank acceptability;
10. assumptions, provenance, source, and limitation ledger.

Accessibility, keyboard navigation, plain-language definitions, alternative text, downloadable aggregate tables, and low-bandwidth behaviour are release requirements.
## Supported command-line interfaces

The reviewed public product has read-only, machine-readable inspection commands:

```text
closer-to-whom national-summary
closer-to-whom space-provenance
closer-to-whom national-validate --output release/national-validation.json
closer-to-whom space-build --output spaces/static --revision <git-revision>
```

`national-summary` reads the reviewed candidate-network report. `space-provenance`
reads the static product provenance manifest. `national-validate` runs the
claim-bounded scientific-output validator and writes a machine-readable receipt.
`space-build` regenerates the deterministic no-JavaScript static bundle from
the reviewed reports; its revision argument is required so the generated page
can be tied to a source commit. These commands do not fetch live service data.

The supported workflow is:

1. run `national-validate` from the repository root;
2. inspect the receipt and source/licence boundaries;
3. run `space-build` with the approved commit revision;
4. run the release and publication gates before any hosted update.

The CLI is read-only with respect to source data and does not publish or
modify a hosted Space by itself.

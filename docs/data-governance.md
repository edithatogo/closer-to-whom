# Data, privacy, provenance, and licensing

## Public-data constraint

The open phase accepts only public aggregate, synthetic, or generated aggregate data. “Public” does not automatically mean redistributable. Every source needs an access state and a separate redistribution state.

## Prohibited material

- NHI or any health identifier;
- names, exact residential addresses, or person-level coordinates;
- de-identified confidential extracts;
- row-level treatment, attendance, waiting-time, or outcome records;
- live licensed Healthpoint payloads in Git, CI artefacts, container layers, or the Space;
- small cells that permit plausible re-identification.

## Source lifecycle

1. Discover a candidate source.
2. Record the URL, publisher, retrieval date, date represented, and source type.
3. Capture or archive where lawful.
4. Hash the captured object.
5. adjudicate licence and redistribution state;
6. extract a claim or parameter with an evidence grade;
7. second-review clinically material capability claims;
8. materialise only permitted fields into a versioned Arrow dataset;
9. retain transformation and release fingerprints.

## Facility inference

A facility code proves the existence of a coded facility, not oncology capability. An oncology clinic proves neither drug administration nor daily availability. Haematology chemotherapy does not automatically prove solid-tumour anti-HER2 capability. Outreach may mean consultation only. Missing public evidence remains `unknown`.

## Public outputs

The dashboard serves aggregate precomputed outputs. Maps should use sufficiently broad cells, suppress low expected-demand cells where necessary, and avoid exact demand routing points when disclosure risk or misinterpretation is material.

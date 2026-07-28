# Closer to whom? — evidence-linked national aggregate analysis

## Methods

We used frozen public aggregate inputs and deterministic travel-routing outputs to compare
candidate-network scenarios across Aotearoa New Zealand. Expected courses are aggregate model
cells, not patients or observed service use. The analysis does not add individual, confidential,
or row-level health data. Clinical eligibility and service capability remain hard unknown gates.

The package contains nine canonical reports: scenario summary, optimisation frontier, uncertainty,
MCDA, VOI, distributional equity, capacity/cost, resilience sensitivity, and exact optimisation
comparison. Exact optimisation is limited to the declared finite p=1,3,5 enumeration scope.

## Results

The deterministic candidate-network comparison contains **5** configurations. The
weighted mean one-way travel results are:

| Configuration | Candidate sites | Weighted mean minutes | Expected courses within 60 minutes |
|---|---:|---:|---:|
| candidate_network_01 | 1 | 373.6 | 7.1% |
| candidate_network_03 | 3 | 123.1 | 21.8% |
| candidate_network_05 | 5 | 76.6 | 55.3% |
| candidate_network_10 | 10 | 44.9 | 77.9% |
| candidate_network_19 | 19 | 30.8 | 87.2% |

Distributional outputs retain unknown groups and are ecological summaries. Capacity outputs are
arithmetic workload envelopes and a private-vehicle resource-cost scenario; observed staffing,
capacity, treatment mix, and omitted cost components are not estimated. Resilience results are
hypothetical candidate-site removal routing sensitivities, not observed outage performance.

## Limitations and bounded conclusions

The outputs support reproducible comparison of modelled aggregate access scenarios. They do not
support clinical guidance, service-capability claims, operational deployment, patient-level
inference, policy recommendation, or cost-effectiveness conclusions. Unsupported delivery settings,
provider travel, patient travel, and national treatment mix remain unknown or not estimated.

## Reproducibility and data statement

The exact report hashes, source/licence decision, release receipts, assumptions, and code revision
are recorded in the repository. Raw or licensed source payloads are not redistributed. The public
Space contains only precomputed aggregate outputs and provenance.

## Author and submission boundary

This is a prepared manuscript package, not journal submission or acceptance. Author disclosures,
funding, conflicts, AI disclosure, journal selection, and authenticated submission remain human-
controlled actions.

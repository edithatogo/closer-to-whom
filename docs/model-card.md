# Model card

## Model name

**Closer to whom?** Public-data geospatial anti-HER2 service-configuration model.

## Intended use

- compare potential travel time, distance, direct cost, and time burden under policy configurations;
- identify areas and aggregate population strata likely to gain or lose;
- estimate implied workload and infrastructure requirements when observed capacity is unavailable;
- generate efficient candidate service networks for deliberation;
- expose trade-offs through Pareto analysis and MCDA;
- quantify decision uncertainty and the value of obtaining better public, aggregate, or microdata evidence.

## Out-of-scope use

- individual clinical decisions;
- predicting where a specific person will attend;
- inferring actual service availability from undocumented webpages;
- operational rostering or queue forecasting without suitable data;
- estimating treatment effectiveness, adherence, survival, or causal outcomes;
- ranking communities or ethnic groups as inherently high or low access;
- publishing licensed source payloads without permission.

## Unit of analysis

A public geographic demand cell × aggregate population stratum × clinical pathway × policy scenario. Expected courses may be fractional. A row is never described as a patient.

## Inputs

Public aggregate population and epidemiology, public geographic boundaries and routing points, evidence-graded facility and policy records, public transport/road networks, explicit treatment pathways, public cost parameters, and declared assumptions.

## Outputs

Course-level travel, time, direct cost, reimbursement, provider burden, societal burden, better/worse distributions, equity summaries, implied capacity, optimisation frontiers, uncertainty intervals, MCDA rank acceptability, and VOI.

## Performance and validation

The software is verified using unit, property, metamorphic, contract, integration, differential, reproducibility, package, container, and dashboard tests. The public-data model can be calibrated to aggregate totals but cannot be individually validated until a future data phase.

## Ethical and equity risks

Area averages can conceal within-area variation. Ethnicity, deprivation, rurality, vehicle access, and disability proxies are ecological. Nearest-site assumptions may conflict with continuity, workplace, whānau, safety, and transport preferences. Equity weights are normative and are varied unless governance supports a frozen set.

## Current maturity

Research software alpha. Synthetic fixtures prove software behaviour; they are not policy findings. Publication readiness requires a frozen national service census, clinical review, source and licence adjudication, aggregate calibration, national routing, governance review, and full release receipt.

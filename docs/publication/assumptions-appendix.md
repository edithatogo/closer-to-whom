# Appendix: explicit assumptions

Generated from `assumptions/assumptions.yaml`; do not edit by hand.

| ID | Assumption | Status | Uncertainty / sensitivity | Claim boundary |
|---|---|---|---|---|
| A01 | permitted_data = public_aggregate_only. No individual, confidential, or non-public operational data are permitted. | hard_constraint | none |  |
| A02 | estimand = potential_access. The model estimates potential rather than realised access. | hard_constraint | structural |  |
| C01 | early_iv_demo_administrations = 18. Demonstrates cumulative travel; publication value requires clinical source and review. | synthetic_fixture | discrete |  |
| C02 | home_self_administration = excluded. Home scenarios are healthcare-professional administered. | hard_constraint | none |  |
| C03 | initial_higher_risk_doses = hospital_capable_setting. Initial and clinically constrained administrations remain at eligible facilities. | hard_constraint | pathway_specific |  |
| D01 | principal_geography = SA2_SSGA23. SA2 under Stats NZ SSGA23 balances public availability, interpretability, and disclosure protection; input and licence freeze remains pending. | planned_public_input | spatial |  |
| D02 | within_area_allocation = population_weighted_multiple_points. Multiple routing points reduce centroid bias in large areas. | planned_method | spatial |  |
| D03 | her2_positive_probability = 0.175. Midpoint of a public range used only until pathway-specific calibration. | placeholder_requires_source_freeze | beta |  |
| D04 | treatment_uptake = 0.85. Wide uncertainty prevents false precision before public calibration. | illustrative | beta |  |
| E01 | rurality_measure = GCH23_stratifier. GCH23 is a rurality stratifier; network travel remains the access measure. Its CC BY-ND restriction means transformed redistribution requires permission. | planned_public_input | structural |  |
| E02 | deprivation_measure = NZDep2023. Area deprivation is not interpreted as an individual attribute. | planned_public_input | ecological |  |
| E03 | equity_weights = scenario_range. No single weight set is represented as stakeholder-derived without governance. | normative_uncertainty | stochastic_mcda |  |
| F01 | conservative_evidence_threshold = 2. Primary analysis requires current explicit named treatment or solid-tumour SACT evidence. | protocol_rule | structural |  |
| F02 | undocumented_capability = unknown. Lack of public evidence is not evidence of absence. | hard_constraint | structural |  |
| F03 | observed_capacity = unavailable. The model estimates implied capacity and tests explicit capacity envelopes. | structural_limitation | structural |  |
| K01 | vehicle_running_cost = 0.37. Marginal running-cost base with broader-cost scenario. | requires_analysis_date_refresh | deterministic_scenario |  |
| K02 | nta_reimbursement = 0.44. Report gross burden, reimbursement, and societal resource cost separately. | temporary_rate_requires_date_check | deterministic_scenario |  |
| K03 | patient_time_value = 25. Primary reporting keeps time separate; monetisation is secondary. | illustrative | gamma |  |
| O01 | safety_constraints = non_compensatory. Clinical eligibility and safety cannot be traded against travel convenience. | hard_constraint | none |  |
| O02 | uncapacitated_interpretation = potential_geography_and_implied_capacity. Results do not claim current operational feasibility. | hard_constraint | structural |  |
| R01 | canonical_exchange = Arrow_Parquet. Language-neutral contracts enable Python, Rust, Julia, Mojo, and JAX components. | architecture | none |  |
| R02 | healthpoint_payloads = fail_closed. Live payloads remain private unless redistribution and dashboard permissions are explicit. | hard_constraint | none |  |
| T01 | publication_route_method = versioned_road_and_public_transport_engines. Straight-line distance is not the publication access measure. | planned_method | structural |  |
| T02 | synthetic_road_circuity = 1.25. Offline software tests only; never a policy estimate. | synthetic_fixture | uniform |  |
| T03 | synthetic_average_speed = 65. Offline software tests only. | synthetic_fixture | uniform |  |
| U01 | psa_sampling = scrambled_sobol. Low-discrepancy draws improve coverage for repeated model evaluation. | method | none |  |
| U02 | structural_uncertainty = reported_separately. Structural alternatives are not collapsed into false-precision intervals. | hard_constraint | none |  |
| V01 | microdata_decision_rule = positive_ENBS_and_decision_relevance. Granular research is justified only when it may change a material decision or equity conclusion. | method | decision |  |

Total assumptions: **28**.

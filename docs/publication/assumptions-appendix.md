# Appendix: explicit assumptions

Generated from `assumptions/assumptions.yaml`; do not edit by hand.

| ID | Assumption | Status | Uncertainty / sensitivity | Claim boundary |
|---|---|---|---|---|
| A01 | permitted_data = public_aggregate_only. No individual, confidential, or non-public operational data are permitted. | hard_constraint | none |  |
| A02 | estimand = potential_access. The model estimates potential rather than realised access. | hard_constraint | structural |  |
| C01 | early_iv_demo_administrations = 18. Demonstrates cumulative travel; publication value requires clinical source and review. | synthetic_fixture | discrete |  |
| C02 | home_self_administration = excluded. Home scenarios are healthcare-professional administered. | hard_constraint | none |  |
| C03 | initial_higher_risk_doses = hospital_capable_setting. Initial and clinically constrained administrations remain at eligible facilities. | hard_constraint | pathway_specific |  |
| D01 | principal_geography = SA2_SSGA23. SA2 under Stats NZ SSGA23 is frozen from the authenticated POPES_SUB_004 artifact for authorized local use; redistribution remains blocked pending licence adjudication. | frozen_public_input_artifact_only | spatial |  |
| D02 | within_area_allocation = official_true_centroid_baseline. The official Stats NZ true-centroid layer provides a deterministic aggregate baseline for all 2,313 denominator SA2s; population-weighted multi-point sensitivity remains required to quantify centroid bias. | materialized_public_aggregate | spatial |  |
| D03 | her2_positive_probability = 0.15. Te Aho reports approximately 15 percent HER2-positive nationally; subgroup differences remain structural scenarios and are not applied to SA2 cells. | captured_public_aggregate_estimate | structural_scenario |  |
| D04 | treatment_uptake = 0.631. Observed national QPI for chemotherapy plus trastuzumab among HER2-positive stage I-III diagnoses in 2020-2021; not a current small-area uptake rate. | captured_public_aggregate_qpi_2020_21 | structural_scenario |  |
| D05 | stage_i_iii_probability = 0.93. Te Aho reports approximately 80 percent stage I-II and 13 percent stage III; the sum is used only for a bounded national scenario. | captured_public_aggregate_estimate | structural_scenario |  |
| D06 | annual_female_breast_cancer_registrations = 3660. Ministry of Health reports 3,660 female breast-cancer registrations in 2022; Te Aho describes approximately 3,500 diagnoses in 2025. | captured_public_aggregate_2022 | temporal_scenario |  |
| E01 | rurality_measure = Stats_NZ_Urban_Rural_2023_centroid_class. Stats NZ Urban Rural 2023 is the open baseline stratifier at each official SA2 true centroid; network travel remains the access measure, and GCH23 remains a separate restricted sensitivity input. | materialized_public_aggregate | structural |  |
| E02 | deprivation_measure = NZDep2023. The official SA2 workbook supports 2,208 denominator areas; 48 source-blank and 57 version-mismatched areas remain explicit unknowns. Area deprivation is never interpreted as an individual attribute. | materialized_public_aggregate_with_explicit_unknowns | ecological |  |
| E03 | equity_weights = scenario_range. No single weight set is represented as stakeholder-derived without governance. | normative_uncertainty | stochastic_mcda |  |
| E04 | ethnicity_measure = Stats_NZ_2023_Census_total_response_broad_groups. Broad ethnicity groups overlap under total-response coding and are area distributions, never exclusive or individual assignments. | materialized_public_aggregate | ecological |  |
| E05 | vehicle_access_measure = occupied_private_dwellings_no_motor_vehicle_share. The SA2 household share is a contextual transport-access proxy, not observed vehicle availability for any person or treatment journey. | materialized_public_aggregate_proxy | ecological_proxy |  |
| F01 | conservative_evidence_threshold = 2. Primary analysis requires current explicit named treatment or solid-tumour SACT evidence. | protocol_rule | structural |  |
| F02 | undocumented_capability = unknown. Lack of public evidence is not evidence of absence. | hard_constraint | structural |  |
| F03 | observed_capacity = unavailable. The model estimates implied capacity and tests explicit capacity envelopes. | structural_limitation | structural |  |
| K01 | vehicle_running_cost = 0.37. Marginal running-cost base with broader-cost scenario. | captured_2025_26_rate_artifact_only | deterministic_scenario |  |
| K02 | nta_reimbursement = 0.34. Report gross burden, reimbursement, and societal resource cost separately. | captured_2024_rate_artifact_only | deterministic_scenario |  |
| K03 | patient_time_value = 25. Primary reporting keeps time separate; monetisation is secondary. | illustrative | gamma |  |
| O01 | safety_constraints = non_compensatory. Clinical eligibility and safety cannot be traded against travel convenience. | hard_constraint | none |  |
| O02 | uncapacitated_interpretation = potential_geography_and_implied_capacity. Results do not claim current operational feasibility. | hard_constraint | structural |  |
| R01 | canonical_exchange = Arrow_Parquet. Language-neutral contracts enable Python, Rust, Julia, Mojo, and JAX components. | architecture | none |  |
| R02 | healthpoint_payloads = fail_closed. Live payloads remain private unless redistribution and dashboard permissions are explicit. | hard_constraint | none |  |
| T01 | publication_route_method = self_hosted_osrm_on_pinned_osm_pbf. The national road matrix uses a pinned OSM extract and loopback-only OSRM table client; public demo servers and straight-line distances are not release evidence. | implemented_pending_network_build_and_matrix | structural |  |
| T02 | synthetic_road_circuity = 1.25. Offline software tests only; never a policy estimate. | synthetic_fixture | uniform |  |
| T03 | synthetic_average_speed = 65. Offline software tests only. | synthetic_fixture | uniform |  |
| U01 | psa_sampling = scrambled_sobol. Low-discrepancy draws improve coverage for repeated model evaluation. | method | none |  |
| U02 | structural_uncertainty = reported_separately. Structural alternatives are not collapsed into false-precision intervals. | hard_constraint | none |  |
| V01 | microdata_decision_rule = positive_ENBS_and_decision_relevance. Granular research is justified only when it may change a material decision or equity conclusion. | method | decision |  |

Total assumptions: **32**.

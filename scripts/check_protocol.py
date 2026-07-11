#!/usr/bin/env python3
"""Cross-check the machine-readable protocol, SAP, scenarios, and assumptions."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT=Path(__file__).resolve().parents[1]


def load(relative: str) -> Any:
    return yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))


def scenario_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload,list):
        return [row for row in payload if isinstance(row,dict)]
    if isinstance(payload,dict):
        for key in ("scenarios","catalogue"):
            if isinstance(payload.get(key),list):
                return [row for row in payload[key] if isinstance(row,dict)]
        return [dict(value,id=key) for key,value in payload.items() if isinstance(value,dict)]
    return []


def main() -> int:
    protocol=load("protocol/protocol.yaml")
    sap=load("protocol/statistical-analysis-plan.yaml")
    decision=load("protocol/decision-model-specification.yaml")
    clinical=load("protocol/clinical-safety-constraints.yaml")
    claims=load("protocol/claim-boundaries.yaml")
    scenarios=scenario_rows(load("scenarios/scenario-catalogue.yaml"))
    failures=[]
    if protocol.get("geography") != "Aotearoa New Zealand":
        failures.append("protocol is not national")
    if not protocol.get("public_data_only"):
        failures.append("protocol must remain public-data only")
    if protocol.get("human_participants") or protocol.get("confidential_data") or protocol.get("microdata"):
        failures.append("current protocol cannot include participants, confidential data, or microdata")
    required_uncertainty={"deterministic_sensitivity_analysis","probabilistic_sensitivity_analysis","structural_scenario_analysis","spatial_uncertainty"}
    if not required_uncertainty.issubset(set(protocol.get("analysis",{}).get("uncertainty",[]))):
        failures.append("protocol uncertainty set is incomplete")
    required_voi={"EVPI","EVPPI","EVSI","ENBS","break_even_research_cost"}
    if not required_voi.issubset(set(protocol.get("analysis",{}).get("value_of_information",[]))):
        failures.append("VOI plan is incomplete")
    if decision.get("normative_weights",{}).get("single_consensus_weight_set_claimed"):
        failures.append("MCDA must not claim an unelicited consensus weight set")
    if not sap.get("structural", sap.get("uncertainty",{}).get("structural",{})):
        failures.append("SAP must define structural uncertainty")
    scenario_text=" ".join(str(value).lower() for row in scenarios for value in row.values())
    for concept in ("home","community","subcutaneous","outage","hybrid"):
        if concept not in scenario_text:
            failures.append(f"scenario catalogue missing concept: {concept}")
    if len(scenarios) < 8:
        failures.append("scenario catalogue is not comprehensive")
    if not clinical.get("rules"):
        failures.append("clinical safety constraints are empty")
    if "actual_patient_journey" not in claims.get("forbidden_claim_classes_without_new_evidence",[]):
        failures.append("claim boundary does not prohibit actual patient journey claims")
    if failures:
        print("Protocol consistency failures:",file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures),file=sys.stderr)
        return 1
    print(f"Protocol cross-check passed for {len(scenarios)} national scenarios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

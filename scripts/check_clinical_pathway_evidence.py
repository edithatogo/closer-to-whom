"""Validate source-backed pathway constraints and unfrozen setting boundaries."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/public/clinical-pathway-evidence.yaml"
SOURCE_REGISTRY = ROOT / "data/public/source-registry.yaml"
REQUIRED_PATHWAYS = {
    "early_trastuzumab_iv",
    "early_trastuzumab_sc",
    "metastatic_phesgo",
}
REQUIRED_COUNTERFACTUALS = {
    "community_sc",
    "healthcare_professional_home_sc",
    "hybrid",
}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(
    evidence_path: Path = EVIDENCE,
    source_registry_path: Path = SOURCE_REGISTRY,
) -> list[str]:
    payload = _load(evidence_path)
    source_registry = _load(source_registry_path)
    source_ids = {
        str(source.get("source_id"))
        for source in source_registry.get("sources", [])
        if isinstance(source, dict)
    }
    failures: list[str] = []
    pathways = payload.get("pathways")
    if not isinstance(pathways, list):
        return ["pathways must be a list"]
    pathway_ids = {
        str(pathway.get("pathway_id")) for pathway in pathways if isinstance(pathway, dict)
    }
    if pathway_ids != REQUIRED_PATHWAYS:
        failures.append("pathways must enumerate the three required product pathways")
    for pathway in pathways:
        if not isinstance(pathway, dict):
            failures.append("each pathway must be a mapping")
            continue
        pathway_id = str(pathway.get("pathway_id", "<blank>"))
        declared_sources = set(map(str, pathway.get("source_ids", [])))
        if not declared_sources:
            failures.append(f"{pathway_id}: source_ids are required")
        if missing := declared_sources - source_ids:
            failures.append(f"{pathway_id}: unknown source_ids {sorted(missing)}")
        constraints = pathway.get("setting_constraints")
        if not isinstance(constraints, dict):
            failures.append(f"{pathway_id}: setting_constraints are required")
            continue
        if constraints.get("healthcare_professional") != "required":
            failures.append(f"{pathway_id}: healthcare professional must remain required")
        if constraints.get("home_or_community_evidence") != "unknown":
            failures.append(f"{pathway_id}: home/community evidence must remain unknown")
        if not isinstance(pathway.get("funding"), dict):
            failures.append(f"{pathway_id}: explicit funding state is required")
    counterfactuals = payload.get("counterfactuals")
    if not isinstance(counterfactuals, dict) or set(counterfactuals) != REQUIRED_COUNTERFACTUALS:
        failures.append("counterfactuals must enumerate community, home, and hybrid settings")
    elif any(
        not isinstance(value, dict) or value.get("status") != "unfrozen_policy_counterfactual"
        for value in counterfactuals.values()
    ):
        failures.append("home, community, and hybrid counterfactuals must remain unfrozen")
    boundary = str(payload.get("claim_boundary", "")).lower()
    for term in ("local capability", "capacity", "individual eligibility", "home/community"):
        if term not in boundary:
            failures.append(f"claim_boundary must preserve the {term} boundary")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Clinical pathway evidence failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated clinical pathway product constraints and unfrozen setting boundaries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
from runpy import run_path

import yaml

validate = run_path(
    Path(__file__).parents[2] / "scripts" / "check_clinical_pathway_evidence.py",
    run_name="clinical_pathway_evidence_test",
)["validate"]


def _write(path: Path, payload: object) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_complete_product_constraints_preserve_setting_unknowns(tmp_path: Path) -> None:
    source_ids = {
        "early_trastuzumab_iv": ["iv"],
        "early_trastuzumab_sc": ["sc"],
        "metastatic_phesgo": ["phesgo", "pharmac"],
    }
    evidence = {
        "pathways": [
            {
                "pathway_id": pathway_id,
                "source_ids": sources,
                "funding": {"status": "known_or_explicit_unknown"},
                "setting_constraints": {
                    "healthcare_professional": "required",
                    "home_or_community_evidence": "unknown",
                },
            }
            for pathway_id, sources in source_ids.items()
        ],
        "counterfactuals": {
            name: {"status": "unfrozen_policy_counterfactual"}
            for name in ("community_sc", "healthcare_professional_home_sc", "hybrid")
        },
        "claim_boundary": (
            "No local capability, capacity, individual eligibility, or home/community claim."
        ),
    }
    registry = {
        "sources": [
            {"source_id": source_id}
            for source_id in ("iv", "sc", "phesgo", "pharmac")
        ]
    }
    evidence_path = tmp_path / "evidence.yaml"
    registry_path = tmp_path / "registry.yaml"
    _write(evidence_path, evidence)
    _write(registry_path, registry)
    assert validate(evidence_path, registry_path) == []


def test_home_evidence_cannot_be_promoted_without_source(tmp_path: Path) -> None:
    evidence = {
        "pathways": [
            {
                "pathway_id": pathway_id,
                "source_ids": ["source"],
                "funding": {"status": "known_or_explicit_unknown"},
                "setting_constraints": {
                    "healthcare_professional": "required",
                    "home_or_community_evidence": "established",
                },
            }
            for pathway_id in (
                "early_trastuzumab_iv",
                "early_trastuzumab_sc",
                "metastatic_phesgo",
            )
        ],
        "counterfactuals": {
            name: {"status": "unfrozen_policy_counterfactual"}
            for name in ("community_sc", "healthcare_professional_home_sc", "hybrid")
        },
        "claim_boundary": (
            "No local capability, capacity, individual eligibility, or home/community claim."
        ),
    }
    evidence_path = tmp_path / "evidence.yaml"
    registry_path = tmp_path / "registry.yaml"
    _write(evidence_path, evidence)
    _write(registry_path, {"sources": [{"source_id": "source"}]})
    failures = validate(evidence_path, registry_path)
    assert sum("home/community evidence must remain unknown" in row for row in failures) == 3

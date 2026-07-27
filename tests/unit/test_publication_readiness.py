import importlib.util
from pathlib import Path

import yaml

_SPEC = importlib.util.spec_from_file_location(
    "publication_readiness",
    Path(__file__).parents[2] / "scripts" / "publication_readiness.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_payload = _MODULE.build_payload


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")


def test_readiness_is_derived_from_evidence_files(tmp_path: Path) -> None:
    _write(tmp_path / "data/public/source-registry.yaml", {"sources": []})
    _write(tmp_path / "assumptions/assumptions.yaml", {"assumptions": []})
    _write(tmp_path / "data/public/service-census-records.yaml", {"freeze_date": "2026-01-01"})
    _write(
        tmp_path / "data/public/service-census-review.yaml",
        {"status": "attested_sole_developer_clinician"},
    )
    _write(tmp_path / "data/public/clinical-pathway-review.yaml", {"status": "reviewed"})
    _write(
        tmp_path / "data/public/input-freeze.yaml",
        {"status": "frozen", "approval_receipt": "receipt.json"},
    )
    _write(
        tmp_path / "data/public/governance-review.yaml",
        {"status": "out_of_scope_for_public_aggregate_harness"},
    )
    _write(
        tmp_path / "data/public/national-analysis-receipt.yaml",
        {
            "calibration_status": "complete_national_scenario_not_spatially_allocated",
            "prerequisites": {"route_costs": "pending"},
        },
    )
    blockers = build_payload(tmp_path)["blockers"]
    assert blockers["service_census_frozen"] is True
    assert blockers["clinical_pathways_reviewed"] is True
    assert blockers["aggregate_calibration_complete"] is True
    assert blockers["national_network_routing_complete"] is False
    assert blockers["maori_equity_governance_review_complete"] == "not_required_for_scope"

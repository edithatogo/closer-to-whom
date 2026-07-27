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


def _evidence_tree(root: Path, *, route: str, analysis: str) -> None:
    _write(root / "data/public/source-registry.yaml", {"sources": []})
    _write(
        root / "assumptions/assumptions.yaml",
        {
            "assumptions": [
                {"id": "C01", "status": "synthetic_fixture"},
                {"id": "T02", "status": "synthetic_fixture"},
            ]
        },
    )
    _write(root / "data/public/service-census-records.yaml", {"freeze_date": "2026-01-01"})
    _write(
        root / "data/public/service-census-review.yaml",
        {"status": "attested_sole_developer_clinician"},
    )
    _write(root / "data/public/clinical-pathway-review.yaml", {"status": "reviewed"})
    _write(
        root / "data/public/input-freeze.yaml",
        {"status": "frozen", "approval_receipt": "receipt.json"},
    )
    _write(
        root / "data/public/governance-review.yaml",
        {"status": "out_of_scope_for_public_aggregate_harness"},
    )
    _write(
        root / "data/public/national-analysis-receipt.yaml",
        {
            "status": analysis,
            "calibration_status": "complete_national_scenario_spatially_allocated",
            "prerequisites": {"route_costs": route},
        },
    )


def test_readiness_is_blocked_when_routing_is_pending(tmp_path: Path) -> None:
    _evidence_tree(tmp_path, route="pending", analysis="ready_to_run")
    payload = build_payload(tmp_path)
    assert payload["publication_ready"] is False
    assert payload["blockers"]["national_network_routing_complete"] is False


def test_reviewed_aggregate_payload_ignores_legacy_synthetic_demo(tmp_path: Path) -> None:
    _evidence_tree(tmp_path, route="complete", analysis="completed")
    payload = build_payload(tmp_path)
    assert payload["publication_ready"] is True
    assert payload["blockers"]["national_analysis_complete"] is True
    assert payload["blockers"]["legacy_non_publication_assumption_ids"] == ["C01", "T02"]
    assert payload["blockers"]["unresolved_publication_assumption_ids"] == []

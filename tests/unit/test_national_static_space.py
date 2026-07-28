import importlib.util
import json
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "build_national_static_space",
    Path(__file__).parents[2] / "scripts" / "build_national_static_space.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build = _MODULE.build


def _write_reports(path: Path, *, operational: bool = False) -> None:
    common = {"operational_recommendation": False}
    scenario = {
        **common,
        "operational_recommendation": operational,
        "configurations": [
            {
                "configuration_id": "candidate_network_01",
                "candidate_site_count": 1,
                "weighted_mean_one_way_minutes": 10,
                "weighted_p95_one_way_minutes": 20,
                "share_expected_courses_within_60_minutes": 0.8,
            }
        ],
    }
    payloads = {
        "scenario_summary": scenario,
        "optimisation_frontier": common,
        "uncertainty_analysis": common,
        "mcda_outputs": {
            **common,
            "viewpoints": {
                "access_priority": {
                    "ranking": ["candidate_network_01"],
                    "weights": [0.5, 0.4, 0.1],
                }
            },
        },
        "voi_outputs": {
            **common,
            "current_best_under_mean_weights": "candidate_network_01",
            "evpi_per_policy_decision": 0.01,
            "next_information_priority": "aggregate capability",
        },
        "distributional-equity": {
            **common,
            "dimensions": ["deprivation_quintile", "rurality"],
            "rows": [],
        },
        "capacity-cost-perspective": {**common, "capacity_status": "not_estimable"},
        "resilience-sensitivity": {
            **common,
            "outage_scenario_type": "counterfactual_candidate_site_removal",
        },
    }
    path.mkdir()
    for name, payload in payloads.items():
        (path / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_national_space_embeds_only_bounded_precomputed_reports(tmp_path: Path) -> None:
    analysis = tmp_path / "analysis"
    _write_reports(analysis)
    target = build(analysis, tmp_path / "site", revision="abc123")
    html = target.read_text(encoding="utf-8")
    assert "abc123" in html
    assert "No patient records" in html
    assert "candidate_network_01" in html
    assert "No-JavaScript summary" in html
    assert "Additional reviewed outputs" in html


def test_national_space_rejects_operational_claim(tmp_path: Path) -> None:
    analysis = tmp_path / "analysis"
    _write_reports(analysis, operational=True)
    try:
        build(analysis, tmp_path / "site", revision="abc123")
    except ValueError as exc:
        assert "operational claim boundary" in str(exc)
    else:
        raise AssertionError("Operational claim must be rejected")

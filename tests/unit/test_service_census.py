from pathlib import Path
from runpy import run_path

import polars as pl
import pytest
import yaml

materialize = run_path(
    Path(__file__).parents[2] / "scripts" / "materialize_service_census.py",
    run_name="service_census_test",
)["materialize"]


def test_empty_census_materialises_a_reproducible_blocked_registry(tmp_path: Path) -> None:
    source_registry_path = tmp_path / "source-registry.yaml"
    source_registry_path.write_text("sources: []\n", encoding="utf-8")
    input_path = tmp_path / "census.yaml"
    input_path.write_text(
        "schema_version: '1.0.0'\nfreeze_date: null\nrecords: []\ndisagreements: []\n",
        encoding="utf-8",
    )
    flow = materialize(
        input_path=input_path,
        output_path=tmp_path / "registry.parquet",
        flow_path=tmp_path / "flow.json",
        disagreements_path=tmp_path / "disagreements.csv",
        source_registry=source_registry_path,
    )
    assert flow["facility_count"] == 0
    assert flow["network_counts"] == {"broad": 0, "conservative": 0, "plausible": 0}
    assert pl.read_parquet(tmp_path / "registry.parquet").height == 0


def test_current_public_census_contains_only_plausible_non_drug_specific_records() -> None:
    root = Path(__file__).parents[2]
    payload = yaml.safe_load(
        (root / "data" / "public" / "service-census-records.yaml").read_text(encoding="utf-8")
    )
    records = payload["records"]
    assert len(records) == 19
    assert {record["capability_status"] for record in records} == {"plausible"}
    assert {record["evidence_grade"] for record in records} == {"3_ambiguous_oncology_or_outreach"}
    assert all(record["formulations"] == [] for record in records)
    assert sum(record["redistribution_allowed"] is True for record in records) == 18
    dunedin = next(record for record in records if record["facility_id"] == "NZ-OTA-DUNEDIN")
    assert dunedin["redistribution_allowed"] is False


def test_national_coverage_audit_has_all_health_nz_regions() -> None:
    root = Path(__file__).parents[2]
    coverage = yaml.safe_load(
        (root / "reports" / "service-census-coverage.json").read_text(encoding="utf-8")
    )
    assert coverage["coverage_count"] == 16
    assert len(coverage["areas"]) == 16
    assert {area["status"] for area in coverage["areas"]} == {
        "documented_service_record",
        "regional_referral_coverage",
    }
    west_coast = next(area for area in coverage["areas"] if area["area"] == "West Coast")
    assert west_coast["status"] == "regional_referral_coverage"
    assert west_coast["record_count"] == 0


def test_service_census_review_queue_is_explicitly_pending() -> None:
    root = Path(__file__).parents[2]
    review = yaml.safe_load(
        (root / "data" / "public" / "service-census-review.yaml").read_text(encoding="utf-8")
    )
    assert review["status"] == "pending_external_review"
    assert len(review["review_records"]) == 19
    assert review["licence_adjudication"]["status"] == "adjudicated_for_site_text_only"
    assert review["licence_adjudication"]["licence"] == "CC-BY-4.0"
    assert any(decision["decision_id"] == "CTW-010-LIC-002" for decision in review["decisions"])


def test_capability_matrix_preserves_unknown_drug_specific_claims() -> None:
    root = Path(__file__).parents[2]
    matrix = yaml.safe_load(
        (root / "data" / "public" / "service-census-capabilities.yaml").read_text(encoding="utf-8")
    )
    assert len(matrix["records"]) == 19
    for record in matrix["records"]:
        assert record["claims"]["iv_trastuzumab"] == "unknown"
        assert record["claims"]["trastuzumab_sc"] == "unknown"
        assert record["claims"]["phesgo_sc"] == "unknown"


def test_non_open_evidence_cannot_be_published_as_redistributable(tmp_path: Path) -> None:
    source_registry_path = tmp_path / "source-registry.yaml"
    source_registry_path.write_text(
        """sources:
  - source_id: candidate.healthnz-facility-table
    title: Candidate Table
    publisher: HealthNZ
    url: https://example.com
    retrieved_on: 2026-07-12
    licence_state: restricted
    redistribution_allowed: false
""",
        encoding="utf-8",
    )
    input_path = tmp_path / "census.yaml"
    input_path.write_text(
        """
schema_version: '1.0.0'
freeze_date: '2026-07-12'
records:
  - facility_id: TEST-1
    name: Test facility
    region: Test
    district: Test
    latitude: -36.85
    longitude: 174.76
    facility_type: hospital
    public_or_private: candidate
    capability_status: unknown
    evidence_grade: 4_historical_or_indirect
    source_ids: [candidate.healthnz-facility-table]
    redistribution_allowed: true
disagreements: []
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="non-open source evidence"):
        materialize(
            input_path=input_path,
            output_path=tmp_path / "registry.parquet",
            flow_path=tmp_path / "flow.json",
            disagreements_path=tmp_path / "disagreements.csv",
            source_registry=source_registry_path,
        )


def test_malformed_disagreement_records_fail_closed(tmp_path: Path) -> None:
    source_registry_path = tmp_path / "source-registry.yaml"
    source_registry_path.write_text("sources: []\n", encoding="utf-8")
    input_path = tmp_path / "census.yaml"
    input_path.write_text(
        "schema_version: '1.0.0'\nrecords: []\ndisagreements: ['not-a-mapping']\n",
        encoding="utf-8",
    )
    with pytest.raises(TypeError, match="disagreement record"):
        materialize(
            input_path=input_path,
            output_path=tmp_path / "registry.parquet",
            flow_path=tmp_path / "flow.json",
            disagreements_path=tmp_path / "disagreements.csv",
            source_registry=source_registry_path,
        )

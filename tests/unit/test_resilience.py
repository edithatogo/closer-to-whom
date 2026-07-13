from __future__ import annotations

import polars as pl
import pytest

from closer_to_whom.resilience import evaluate_facility_outages


def test_facility_outage_is_aggregate_and_deterministic() -> None:
    results = pl.DataFrame(
        {
            "scenario_id": ["s1", "s1", "s1"],
            "pathway_id": ["p1", "p1", "p1"],
            "facility_id": ["f2", "f1", "f3"],
            "expected_courses": [2.0, 3.0, 5.0],
        }
    )
    observed = evaluate_facility_outages(results, {"all": ["f3"], "one": ["f1"]})
    assert observed.get_column("outage_scenario_id").to_list() == ["all", "one"]
    assert observed.get_column("affected_expected_courses").to_list() == [5.0, 3.0]
    assert observed.get_column("retained_assignment_expected_courses").to_list() == [5.0, 7.0]
    assert observed.get_column("rerouting_modelled").unique().to_list() == [False]
    assert observed.get_column("observed_capacity_claim").unique().to_list() == [False]


def test_facility_outage_requires_declared_nonempty_inputs() -> None:
    results = pl.DataFrame(
        {
            "scenario_id": ["s1"],
            "pathway_id": ["p1"],
            "facility_id": ["f1"],
            "expected_courses": [1.0],
        }
    )
    with pytest.raises(ValueError, match="At least one"):
        evaluate_facility_outages(results, {})
    with pytest.raises(ValueError, match="no facilities"):
        evaluate_facility_outages(results, {"empty": []})
    with pytest.raises(ValueError, match="negative"):
        evaluate_facility_outages(
            results.with_columns(pl.lit(-1.0).alias("expected_courses")), {"one": ["f1"]}
        )

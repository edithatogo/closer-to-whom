from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from closer_to_whom.doctor import doctor_payload
from closer_to_whom.integrations.adoption import logistic_adoption
from closer_to_whom.integrations.capabilities import integration_capabilities
from closer_to_whom.integrations.healthpoint import (
    HealthpointLicenceGrant,
    fetch_to_private_arrow,
    validate_publication_boundary,
)
from closer_to_whom.integrations.sourceright_adapter import ClaimLink, unresolved_claims
from closer_to_whom.integrations.voiage_adapter import calculate_core_voi
from closer_to_whom.simulation import simulate_all
from closer_to_whom.validation import validate_results


def test_adoption_curve_and_capabilities() -> None:
    assert logistic_adoption(2025, midpoint_year=2025, steepness=1) == pytest.approx(0.5)
    assert logistic_adoption(2030, midpoint_year=2025, steepness=1) > 0.9
    with pytest.raises(ValueError):
        logistic_adoption(2025, midpoint_year=2025, steepness=0)
    names = {item["name"] for item in integration_capabilities()}
    assert {"sourceright", "healthpoint-rs", "mojo"}.issubset(names)


def test_healthpoint_fail_closed(tmp_path: Path) -> None:
    grant = HealthpointLicenceGrant(False, False, False, False, "")
    with pytest.raises(PermissionError):
        validate_publication_boundary(grant)
    with pytest.raises(PermissionError):
        fetch_to_private_arrow(
            executable="missing",
            output_path=tmp_path / "data/licensed/x.arrow",
            grant=grant,
            config_path=tmp_path / "config.json",
        )


def test_claim_adapter_and_voiage_fallback() -> None:
    claims = (
        ClaimLink("c1", "Supported", ("s1",), "supported"),
        ClaimLink("c2", "Unknown", ("s2",), "unverified"),
    )
    assert [claim.claim_id for claim in unresolved_claims(claims)] == ["c2"]
    result = calculate_core_voi(np.array([[1.0, 2.0], [3.0, 1.0]]), prefer_voiage=False)
    assert result.evpi_per_decision >= 0


def test_result_validation_and_doctor(bundle: dict[str, object], tmp_path: Path) -> None:
    results = simulate_all(
        demand_cells=bundle["demand"],  # type: ignore[arg-type]
        facilities=bundle["facilities"],  # type: ignore[arg-type]
        pathways=bundle["pathways"],  # type: ignore[arg-type]
        scenarios=bundle["scenarios"],  # type: ignore[arg-type]
        cost_rates=bundle["cost_rates"],  # type: ignore[arg-type]
        assumptions_fingerprint="test",
    )
    checks = validate_results(results, output=tmp_path / "receipt.json")
    assert all(check.passed for check in checks)
    payload = doctor_payload(Path.cwd())
    assert "diagnostics" in payload

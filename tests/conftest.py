"""Global pytest configuration and reproducible Hypothesis profiles."""

from __future__ import annotations

import os
from collections.abc import Mapping

import pytest
from hypothesis import HealthCheck, settings

settings.register_profile(
    "ci",
    settings(
        deadline=None,
        derandomize=True,
        max_examples=100,
        suppress_health_check=(HealthCheck.too_slow,),
    ),
)
settings.register_profile(
    "ci_extended",
    settings(
        deadline=None,
        derandomize=True,
        max_examples=500,
        suppress_health_check=(HealthCheck.too_slow,),
    ),
)
settings.register_profile(
    "dev",
    settings(
        deadline=None,
        max_examples=50,
        suppress_health_check=(HealthCheck.too_slow,),
    ),
)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


@pytest.fixture(scope="session")
def bundle() -> Mapping[str, object]:
    """Return the deterministic aggregate-only fixture bundle used across tests."""
    from closer_to_whom.synthetic import synthetic_bundle

    return synthetic_bundle()

"""Adoption-curve fallback compatible with an eventual innovate backend."""

from __future__ import annotations

import math


def logistic_adoption(
    year: float,
    *,
    midpoint_year: float,
    steepness: float,
    ceiling: float = 1.0,
    floor: float = 0.0,
) -> float:
    """Return a bounded logistic uptake fraction for scenario analysis."""
    if steepness <= 0:
        raise ValueError("Adoption steepness must be positive")
    if not 0.0 <= floor <= ceiling <= 1.0:
        raise ValueError("Adoption floor and ceiling must satisfy 0 <= floor <= ceiling <= 1")
    return floor + (ceiling - floor) / (1.0 + math.exp(-steepness * (year - midpoint_year)))

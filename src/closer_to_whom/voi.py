"""Value-of-information analysis for policy and future data decisions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

import numpy as np


@dataclass(frozen=True, slots=True)
class VoiSummary:
    """Core value-of-information and decision-risk outputs."""

    current_best_index: int
    expected_net_benefit: np.ndarray
    evpi_per_decision: float
    expected_opportunity_loss: np.ndarray
    probability_optimal: np.ndarray


@dataclass(frozen=True, slots=True)
class ResearchValue:
    """Population-level value and net benefit of one research design."""

    research_id: str
    evsi_per_decision: float
    affected_decisions: float
    discounted_population_evsi: float
    research_cost: float
    expected_net_benefit_of_sampling: float
    break_even_research_cost: float


def validate_net_benefit(net_benefit: np.ndarray) -> None:
    """Validate a draw-by-alternative net-benefit matrix."""
    if net_benefit.ndim != 2 or net_benefit.shape[0] < 1 or net_benefit.shape[1] < 2:
        raise ValueError("Net benefit must have shape (draws, at least two alternatives)")
    if not np.all(np.isfinite(net_benefit)):
        raise ValueError("Net benefit contains non-finite values")


def core_voi(net_benefit: np.ndarray) -> VoiSummary:
    """Calculate EVPI, opportunity loss, and probability optimal."""
    validate_net_benefit(net_benefit)
    expected = np.mean(net_benefit, axis=0)
    current_best = int(np.argmax(expected))
    perfect = np.mean(np.max(net_benefit, axis=1))
    evpi = max(0.0, float(perfect - expected[current_best]))
    draw_best = np.max(net_benefit, axis=1, keepdims=True)
    opportunity_loss = np.mean(draw_best - net_benefit, axis=0)
    winners = np.argmax(net_benefit, axis=1)
    probability = np.bincount(winners, minlength=net_benefit.shape[1]) / net_benefit.shape[0]
    return VoiSummary(current_best, expected, evpi, opportunity_loss, probability)


def evppi_discrete_groups(net_benefit: np.ndarray, group_labels: Sequence[str | int]) -> float:
    """Calculate EVPPI exactly for a discrete or discretised parameter group."""
    validate_net_benefit(net_benefit)
    labels = np.asarray(group_labels)
    if labels.shape != (net_benefit.shape[0],):
        raise ValueError("Group labels must contain one label per PSA draw")
    expected_with_information = 0.0
    for label in np.unique(labels):
        mask = labels == label
        group_probability = float(np.mean(mask))
        conditional = np.mean(net_benefit[mask], axis=0)
        expected_with_information += group_probability * float(np.max(conditional))
    current = float(np.max(np.mean(net_benefit, axis=0)))
    return max(0.0, expected_with_information - current)


def evppi_quantile_bins(
    net_benefit: np.ndarray,
    parameter_draws: np.ndarray,
    *,
    bins: int = 20,
) -> float:
    """Estimate univariate EVPPI with equal-frequency bins as a transparent baseline."""
    if parameter_draws.shape != (net_benefit.shape[0],):
        raise ValueError("Parameter draws must align with net-benefit draws")
    if bins < 2:
        raise ValueError("At least two EVPPI bins are required")
    edges = np.unique(np.quantile(parameter_draws, np.linspace(0.0, 1.0, bins + 1)))
    if len(edges) <= 2:
        return 0.0
    labels = np.digitize(parameter_draws, edges[1:-1], right=True)
    return evppi_discrete_groups(net_benefit, cast(Sequence[str | int], labels))


def evsi_from_posterior_net_benefit(
    prior_net_benefit: np.ndarray,
    posterior_expected_net_benefit: np.ndarray,
) -> float:
    """Calculate EVSI from outer samples of posterior expected net benefit."""
    validate_net_benefit(prior_net_benefit)
    if posterior_expected_net_benefit.ndim != 2:
        raise ValueError("Posterior expected net benefit must be sample-by-alternative")
    if posterior_expected_net_benefit.shape[1] != prior_net_benefit.shape[1]:
        raise ValueError("Prior and posterior alternatives must align")
    current = float(np.max(np.mean(prior_net_benefit, axis=0)))
    with_sample = float(np.mean(np.max(posterior_expected_net_benefit, axis=1)))
    return max(0.0, with_sample - current)


def population_value(
    value_per_decision: float,
    *,
    annual_affected_decisions: float,
    years: int,
    discount_rate: float = 0.03,
    implementation_delay_years: int = 0,
) -> float:
    """Scale per-decision information value over a discounted policy horizon."""
    if value_per_decision < 0 or annual_affected_decisions < 0:
        raise ValueError("Information value and affected decisions must be non-negative")
    if years < 1 or implementation_delay_years < 0:
        raise ValueError("Years must be positive and delay non-negative")
    if discount_rate <= -1:
        raise ValueError("Discount rate must be greater than -1")
    total = 0.0
    for year in range(implementation_delay_years, implementation_delay_years + years):
        total += annual_affected_decisions / ((1.0 + discount_rate) ** year)
    return value_per_decision * total


def research_value(
    *,
    research_id: str,
    evsi_per_decision: float,
    annual_affected_decisions: float,
    years: int,
    research_cost: float,
    discount_rate: float = 0.03,
    implementation_delay_years: int = 1,
) -> ResearchValue:
    """Calculate ENBS and break-even cost for a candidate future study."""
    if research_cost < 0:
        raise ValueError("Research cost cannot be negative")
    population_evsi = population_value(
        evsi_per_decision,
        annual_affected_decisions=annual_affected_decisions,
        years=years,
        discount_rate=discount_rate,
        implementation_delay_years=implementation_delay_years,
    )
    affected = population_value(
        1.0,
        annual_affected_decisions=annual_affected_decisions,
        years=years,
        discount_rate=discount_rate,
        implementation_delay_years=implementation_delay_years,
    )
    return ResearchValue(
        research_id=research_id,
        evsi_per_decision=evsi_per_decision,
        affected_decisions=affected,
        discounted_population_evsi=population_evsi,
        research_cost=research_cost,
        expected_net_benefit_of_sampling=population_evsi - research_cost,
        break_even_research_cost=population_evsi,
    )


def perspective_net_benefit(
    components: Mapping[str, np.ndarray],
    weights: Mapping[str, float],
) -> np.ndarray:
    """Build a declared scalar decision value from disaggregated consequences.

    Positive component values are interpreted as burdens, so net benefit is their weighted negative
    sum. This function exists for VOI and does not replace disaggregated primary reporting.
    """
    if set(weights) - set(components):
        raise ValueError(
            f"Weights reference unknown components: {sorted(set(weights) - set(components))}"
        )
    shapes = {np.asarray(value).shape for value in components.values()}
    if len(shapes) != 1:
        raise ValueError("All consequence matrices must have the same shape")
    net = np.zeros(next(iter(shapes)), dtype=float)
    for name, weight in weights.items():
        if weight < 0:
            raise ValueError("Burden weights must be non-negative")
        net -= np.asarray(components[name], dtype=float) * weight
    return net

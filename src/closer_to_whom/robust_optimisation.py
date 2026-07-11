"""Small-instance robust selection and minimax-regret oracle."""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class RobustSelection:
    selected_indices: tuple[int, ...]
    expected_objective: float
    worst_case_objective: float
    maximum_regret: float


def robust_p_median_oracle(
    scenario_costs: FloatArray,
    demand: FloatArray,
    facilities_to_select: int,
    scenario_probabilities: FloatArray | None = None,
) -> list[RobustSelection]:
    """Enumerate configurations for validation and small policy shortlists.

    `scenario_costs` has shape scenario × origin × candidate facility.
    """

    costs=np.asarray(scenario_costs,dtype=np.float64)
    weights=np.asarray(demand,dtype=np.float64)
    if costs.ndim != 3:
        raise ValueError("scenario_costs must be scenario × origin × facility")
    scenarios, origins, facilities=costs.shape
    if weights.shape != (origins,):
        raise ValueError("demand shape does not match origins")
    if scenario_probabilities is None:
        probabilities=np.full(scenarios,1.0/scenarios,dtype=np.float64)
    else:
        probabilities=np.asarray(scenario_probabilities,dtype=np.float64)
        if probabilities.shape != (scenarios,) or (probabilities < 0).any():
            raise ValueError("invalid scenario probabilities")
        probabilities=probabilities/probabilities.sum()
    configurations=list(itertools.combinations(range(facilities),facilities_to_select))
    objectives=[]
    for selected in configurations:
        served=costs[:,:,selected].min(axis=2)
        objective=(served*weights[None,:]).sum(axis=1)
        objectives.append(objective)
    objective_matrix=np.vstack(objectives)
    best_per_scenario=objective_matrix.min(axis=0)
    rows=[]
    for selected, objective in zip(configurations,objective_matrix,strict=True):
        rows.append(RobustSelection(
            selected_indices=tuple(selected),
            expected_objective=float(objective @ probabilities),
            worst_case_objective=float(objective.max()),
            maximum_regret=float((objective-best_per_scenario).max()),
        ))
    return sorted(rows,key=lambda row:(row.maximum_regret,row.expected_objective,row.selected_indices))

"""VOIage capability adapter with a tested in-repository fallback."""

from __future__ import annotations

import importlib
from typing import Any

import numpy as np

from closer_to_whom.voi import VoiSummary, core_voi


def calculate_core_voi(net_benefit: np.ndarray, *, prefer_voiage: bool = True) -> VoiSummary:
    """Use VOIage when a compatible interface is installed, otherwise use the local oracle."""
    if prefer_voiage:
        try:
            module: Any = importlib.import_module("voiage")
            function = getattr(module, "core_voi", None)
            if callable(function):
                result = function(net_benefit)
                if isinstance(result, VoiSummary):
                    return result
        except (ImportError, AttributeError, TypeError, ValueError):
            pass
    return core_voi(net_benefit)

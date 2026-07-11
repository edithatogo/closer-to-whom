"""Structure-aware fuzz target for public model contracts.

Run with Hypothesis through the standard tests; this file is also suitable as a
seed for Atheris or OSS-Fuzz integration in a local environment.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from closer_to_whom.models import Scenario


def fuzz_one_input(payload: bytes) -> None:
    try:
        decoded: Any=json.loads(payload.decode("utf-8",errors="strict"))
    except (UnicodeDecodeError,json.JSONDecodeError):
        return
    try:
        Scenario.model_validate(decoded)
    except ValidationError:
        return

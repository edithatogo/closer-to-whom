"""Runtime capability discovery without hard dependencies."""

from __future__ import annotations

import importlib.util
import shutil
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class IntegrationCapability:
    """Availability and role of one optional integration."""

    name: str
    available: bool
    mechanism: str
    required_for_open_pipeline: bool
    role: str


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ImportError, ModuleNotFoundError, ValueError:
        return False


def integration_capabilities() -> tuple[dict[str, str | bool], ...]:
    """Return machine-readable optional integration status."""
    items = (
        IntegrationCapability(
            "sourceright",
            _module_available("sourceright"),
            "python",
            False,
            "claim-source provenance and citation verification",
        ),
        IntegrationCapability(
            "authentext",
            _module_available("authentext"),
            "python",
            False,
            "manuscript and dashboard language quality gates",
        ),
        IntegrationCapability(
            "innovate",
            _module_available("innovate"),
            "python/arrow",
            False,
            "adoption and diffusion scenarios",
        ),
        IntegrationCapability(
            "voiage",
            _module_available("voiage"),
            "python",
            False,
            "advanced EVPI, EVPPI, EVSI, and ENBS",
        ),
        IntegrationCapability(
            "kairos",
            _module_available("kairos"),
            "python/arrow",
            False,
            "future capacity and queue simulation",
        ),
        IntegrationCapability(
            "mars",
            _module_available("mars"),
            "python",
            False,
            "surrogates for expensive PSA and optimisation",
        ),
        IntegrationCapability(
            "open_social_data",
            _module_available("open_social_data"),
            "python/arrow",
            False,
            "public-source catalogue and ingestion",
        ),
        IntegrationCapability(
            "healthpoint-rs",
            shutil.which("healthpoint-rs") is not None,
            "command/arrow",
            False,
            "licensed service-registry acquisition",
        ),
        IntegrationCapability(
            "fyi-cli",
            shutil.which("fyi") is not None or shutil.which("fyi-cli") is not None,
            "command",
            False,
            "optional public OIA workflow",
        ),
        IntegrationCapability(
            "mojo",
            shutil.which("mojo") is not None,
            "command",
            False,
            "experimental accelerator canary",
        ),
    )
    return tuple(asdict(item) for item in items)

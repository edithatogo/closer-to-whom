"""Fail-closed Healthpoint-rs integration contract."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class HealthpointLicenceGrant:
    """Explicit local permissions needed before a live connector may run."""

    access_authorised: bool
    analysis_authorised: bool
    repository_redistribution_authorised: bool
    public_dashboard_authorised: bool
    grant_reference: str

    @property
    def live_fetch_allowed(self) -> bool:
        """Return whether local licensed acquisition may proceed."""
        return self.access_authorised and self.analysis_authorised and bool(self.grant_reference)


def validate_publication_boundary(grant: HealthpointLicenceGrant) -> None:
    """Reject any attempt to publish payloads without both explicit grants."""
    if not grant.repository_redistribution_authorised:
        raise PermissionError("Healthpoint payload redistribution is not explicitly authorised")
    if not grant.public_dashboard_authorised:
        raise PermissionError("Healthpoint payload use in a public dashboard is not authorised")


def fetch_to_private_arrow(
    *,
    executable: str,
    output_path: Path,
    grant: HealthpointLicenceGrant,
    config_path: Path,
) -> Path:
    """Invoke healthpoint-rs into a git-ignored private path after licence checks."""
    if not grant.live_fetch_allowed:
        raise PermissionError(
            "Live Healthpoint acquisition requires an explicit local licence grant"
        )
    resolved = output_path.resolve()
    if "data/licensed" not in resolved.as_posix() and "data/private" not in resolved.as_posix():
        raise ValueError("Healthpoint output must remain under data/licensed or data/private")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [executable, "export", "--config", str(config_path), "--output", str(output_path)],
        check=True,
    )
    receipt = output_path.with_suffix(output_path.suffix + ".licence.json")
    receipt.write_text(json.dumps(asdict(grant), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path

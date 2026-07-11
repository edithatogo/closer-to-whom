"""Minimal claim-source graph adapter pending a released sourceright interface."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClaimLink:
    """One claim linked to one or more source identifiers."""

    claim_id: str
    text: str
    source_ids: tuple[str, ...]
    status: str

    def __post_init__(self) -> None:
        if not self.claim_id or not self.text or not self.source_ids:
            raise ValueError("Claims require an ID, text, and at least one source")
        if self.status not in {"supported", "partially_supported", "unverified", "superseded"}:
            raise ValueError("Unknown claim status")


def unresolved_claims(claims: tuple[ClaimLink, ...]) -> tuple[ClaimLink, ...]:
    """Return claims that must not enter a publication-critical output."""
    return tuple(claim for claim in claims if claim.status in {"unverified", "partially_supported"})

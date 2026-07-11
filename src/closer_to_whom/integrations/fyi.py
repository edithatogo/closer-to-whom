"""Optional fyi-cli request-manifest integration."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def render_request(manifest: Path, *, output: Path, executable: str | None = None) -> Path:
    """Render an OIA request when fyi-cli is installed; never make it a model dependency."""
    command = executable or shutil.which("fyi") or shutil.which("fyi-cli")
    if command is None:
        raise RuntimeError("fyi-cli is not installed; the request manifest remains usable manually")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [command, "render", str(manifest)],
        check=True,
        capture_output=True,
        text=True,
    )
    output.write_text(result.stdout, encoding="utf-8")
    return output

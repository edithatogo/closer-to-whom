#!/usr/bin/env python3
"""Install the built wheel into an isolated environment and exercise the CLI."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    wheels = sorted((ROOT / "dist").glob("*.whl"))
    if not wheels:
        raise SystemExit("No wheel found under dist/")
    with tempfile.TemporaryDirectory() as directory:
        env = Path(directory) / "venv"
        uv = shutil.which("uv")
        if uv:
            subprocess.run([uv, "venv", "--python", sys.executable, str(env)], check=True)
        else:
            subprocess.run([sys.executable, "-m", "venv", str(env)], check=True)
        python = env / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        if uv:
            subprocess.run(
                [uv, "pip", "install", "--python", str(python), str(wheels[-1])], check=True
            )
        else:
            subprocess.run([str(python), "-m", "pip", "install", str(wheels[-1])], check=True)
        subprocess.run([str(python), "-m", "closer_to_whom", "schema-registry"], check=True)
    print("Wheel smoke install passed.")


if __name__ == "__main__":
    main()

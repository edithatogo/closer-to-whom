#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  python -m pip install --user uv
  export PATH="$HOME/.local/bin:$PATH"
fi
uv sync --locked --all-extras
uv run pre-commit install --install-hooks
uv run python scripts/generate_assumptions_appendix.py
uv run python scripts/generate_schema_registry.py
uv run closer-to-whom doctor --strict
printf 'Local bootstrap complete.\n'

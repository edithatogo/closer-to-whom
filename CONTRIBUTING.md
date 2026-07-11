# Contributing

Use a Conductor track and conventional commits. Read `AGENTS.md`, update machine contracts before prose, add risk-appropriate tests, and retain public-data and claim boundaries.

```bash
uv sync --all-extras
uv run pre-commit install --install-hooks
make check
```

Pull requests must state the decision or research question affected, assumptions changed, source and licence impact, clinical/equity impact, tests added, reproducibility result, and whether generated outputs changed.

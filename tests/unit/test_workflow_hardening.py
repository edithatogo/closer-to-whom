import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_workflow_hardening", ROOT / "scripts/check_workflow_hardening.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
_action_reference_failures = MODULE._action_reference_failures


def test_external_actions_require_full_commit_shas() -> None:
    text = """
    steps:
      - uses: actions/checkout@0123456789012345678901234567890123456789
      - uses: actions/setup-python@v4
      - uses: ./local-action
    """
    failures = _action_reference_failures(text, "fixture.yml")
    assert failures == [
        "fixture.yml: mutable or non-commit action reference: actions/setup-python@v4"
    ]

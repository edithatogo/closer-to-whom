from pathlib import Path
from runpy import run_path

from hypothesis import given, settings
from hypothesis import strategies as st

fuzz_one_input = run_path(
    Path(__file__).parents[2] / "fuzz" / "fuzz_models.py",
    run_name="fuzz_models_test",
)["fuzz_one_input"]


@settings(max_examples=200, deadline=1000)
@given(st.binary(max_size=4096))
def test_model_fuzz_target_accepts_arbitrary_bytes(payload: bytes) -> None:
    fuzz_one_input(payload)

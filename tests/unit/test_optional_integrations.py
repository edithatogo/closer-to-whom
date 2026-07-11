from __future__ import annotations

import io
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, ClassVar, Self

import numpy as np
import pytest

from closer_to_whom.integrations import voiage_adapter
from closer_to_whom.integrations.fyi import render_request
from closer_to_whom.integrations.healthpoint import (
    HealthpointLicenceGrant,
    fetch_to_private_arrow,
    validate_publication_boundary,
)
from closer_to_whom.integrations.voiage_adapter import calculate_core_voi
from closer_to_whom.source_fetch import FetchPolicy, SourceFetchError, fetch_public_source
from closer_to_whom.voi import core_voi


def test_fyi_render_is_optional_and_writes_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = tmp_path / "request.yaml"
    manifest.write_text("subject: test\n", encoding="utf-8")
    monkeypatch.setattr("closer_to_whom.integrations.fyi.shutil.which", lambda _name: None)
    with pytest.raises(RuntimeError, match="not installed"):
        render_request(manifest, output=tmp_path / "request.txt")

    monkeypatch.setattr(
        "closer_to_whom.integrations.fyi.subprocess.run",
        lambda *_args, **_kwargs: SimpleNamespace(stdout="Rendered request\n"),
    )
    output = render_request(manifest, output=tmp_path / "nested/request.txt", executable="fyi")
    assert output.read_text(encoding="utf-8") == "Rendered request\n"


def test_healthpoint_success_path_remains_private(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    grant = HealthpointLicenceGrant(True, True, True, True, "grant-1")
    assert grant.live_fetch_allowed
    validate_publication_boundary(grant)

    with pytest.raises(ValueError, match="data/licensed or data/private"):
        fetch_to_private_arrow(
            executable="healthpoint-rs",
            output_path=tmp_path / "public/output.arrow",
            grant=grant,
            config_path=tmp_path / "config.json",
        )

    calls: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> None:
        assert check
        calls.append(command)
        Path(command[-1]).write_bytes(b"ARROW")

    monkeypatch.setattr("closer_to_whom.integrations.healthpoint.subprocess.run", fake_run)
    output = tmp_path / "data/private/healthpoint.arrow"
    result = fetch_to_private_arrow(
        executable="healthpoint-rs",
        output_path=output,
        grant=grant,
        config_path=tmp_path / "config.json",
    )
    assert result == output
    assert calls and calls[0][0] == "healthpoint-rs"
    receipt = json.loads(output.with_suffix(".arrow.licence.json").read_text(encoding="utf-8"))
    assert receipt["grant_reference"] == "grant-1"


def test_voiage_adapter_accepts_compatible_result_and_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    net = np.array([[1.0, 2.0], [3.0, 1.0]])
    expected = core_voi(net)
    monkeypatch.setattr(
        voiage_adapter.importlib,
        "import_module",
        lambda _name: SimpleNamespace(core_voi=lambda _values: expected),
    )
    compatible = calculate_core_voi(net)
    assert compatible.current_best_index == expected.current_best_index
    assert compatible.evpi_per_decision == expected.evpi_per_decision
    np.testing.assert_allclose(compatible.expected_net_benefit, expected.expected_net_benefit)

    def fail_import(_name: str) -> Any:
        raise ImportError("unavailable")

    monkeypatch.setattr(voiage_adapter.importlib, "import_module", fail_import)
    fallback = calculate_core_voi(net)
    assert fallback.current_best_index == expected.current_best_index
    np.testing.assert_allclose(fallback.probability_optimal, expected.probability_optimal)


class _FakeResponse(io.BytesIO):
    status = 200
    headers: ClassVar[dict[str, str]] = {
        "Content-Type": "application/octet-stream",
        "ETag": '"example"',
        "Last-Modified": "Wed, 01 Jan 2025 00:00:00 GMT",
    }

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def test_public_source_fetch_success_and_security_limits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy = FetchPolicy(allow_network=True, allowed_hosts=("example.org",), max_bytes=32)
    monkeypatch.setattr(
        "closer_to_whom.source_fetch.urllib.request.urlopen",
        lambda *_args, **_kwargs: _FakeResponse(b"public bytes"),
    )
    receipt = fetch_public_source(
        source_id="example",
        url="https://data.example.org/source.bin",
        destination=tmp_path / "source.bin",
        policy=policy,
    )
    assert receipt.bytes == len(b"public bytes")
    assert receipt.content_type == "application/octet-stream"
    assert json.loads(receipt.as_json())["source_id"] == "example"

    with pytest.raises(SourceFetchError, match="HTTPS"):
        fetch_public_source(
            source_id="example",
            url="http://example.org/source.bin",
            destination=tmp_path / "http.bin",
            policy=policy,
        )

    monkeypatch.setattr(
        "closer_to_whom.source_fetch.urllib.request.urlopen",
        lambda *_args, **_kwargs: _FakeResponse(b"too many bytes"),
    )
    with pytest.raises(SourceFetchError, match="exceeds"):
        fetch_public_source(
            source_id="large",
            url="https://example.org/large.bin",
            destination=tmp_path / "large.bin",
            policy=FetchPolicy(
                allow_network=True,
                allowed_hosts=("example.org",),
                max_bytes=4,
            ),
        )

from __future__ import annotations

import subprocess
import sys


def test_machine_readable_contracts() -> None:
    subprocess.run([sys.executable, "scripts/check_contracts.py"], check=True)


def test_claim_boundaries() -> None:
    subprocess.run([sys.executable, "scripts/check_claim_boundaries.py"], check=True)


def test_privacy_and_licences() -> None:
    subprocess.run([sys.executable, "scripts/check_privacy_and_licences.py"], check=True)

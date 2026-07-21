from __future__ import annotations

from code_atlas.legal_readiness.selftest import main


def test_legal_readiness_backend() -> None:
    assert main() == 0

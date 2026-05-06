"""Write-limit law for Switch Engine."""

from __future__ import annotations

from contracts.shared_canon import FORBIDDEN_WRITES, REQUIRED_SWITCH_ARTIFACTS

ALLOWED_OUTPUTS = set(REQUIRED_SWITCH_ARTIFACTS)
ALLOWED_LOCAL_RUNTIME = {
    "verify_outputs",
    "logs",
}


def may_write_name(name: str) -> bool:
    return name in ALLOWED_OUTPUTS


def assert_write_allowed(name: str) -> None:
    if name in FORBIDDEN_WRITES or name not in ALLOWED_OUTPUTS:
        raise ValueError(f"Switch Engine may not write {name!r}")

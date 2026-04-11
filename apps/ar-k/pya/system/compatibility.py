from __future__ import annotations

KERNEL_VERSION = "1.0.0"
COMPATIBILITY_RULES = {
    "kernel": {"1.x": ["1.0.0"]},
    "contracts": "strict same-major",
    "engines": "must declare stage, entrypoint, permissions, dependencies, and compatibility",
}


def parse_major(version: str) -> str:
    return version.split(".", 1)[0]


def is_kernel_compatible(requirement: str, actual_version: str = KERNEL_VERSION) -> bool:
    if requirement.startswith("^"):
        return parse_major(requirement[1:]) == parse_major(actual_version)
    return requirement == actual_version

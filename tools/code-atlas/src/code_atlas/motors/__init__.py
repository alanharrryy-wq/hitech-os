# CODE_ATLAS_MOTOR_HUB_MODULE_V01
"""Motor Hub package for Code Atlas.

External execution stays behind an explicit lazy boundary so headless tooling can
import motor adapters without requiring the optional GUI runtime.
"""

from .specs import MotorSpec
from .registry import build_motor_registry, grouped_motor_registry
from .results import find_latest_fail_zip, find_latest_result_zip

__all__ = [
    "MotorSpec",
    "MotorProcessRunner",
    "build_motor_registry",
    "grouped_motor_registry",
    "find_latest_result_zip",
    "find_latest_fail_zip",
]


def __getattr__(name: str):
    if name == "MotorProcessRunner":
        from .runner import MotorProcessRunner
        return MotorProcessRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

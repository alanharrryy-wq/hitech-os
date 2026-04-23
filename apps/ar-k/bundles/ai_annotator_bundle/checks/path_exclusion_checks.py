"""Checks for exclusions and safe-ignore rules."""

from __future__ import annotations

from core.path_policy import is_excluded_path


class PathPolicyError(ValueError):
    """Raised when excluded paths are not ignored."""


FORBIDDEN_SCAN_PREFIXES = [
    "reports_real/",
    "reports/",
    ".ark_install/",
]


def assert_safe_ignore(path: str) -> None:
    if not is_excluded_path(path):
        raise PathPolicyError(f"Path should have been excluded but was not: {path}")


def assert_runtime_output_path(path: str) -> None:
    normalized = path.replace("\\", "/")
    if normalized.startswith("reports_real/"):
        raise PathPolicyError("AI Annotator may not write into reports_real/")
    if normalized.startswith("reports/registries/"):
        raise PathPolicyError("AI Annotator may not write into canonical registry area")

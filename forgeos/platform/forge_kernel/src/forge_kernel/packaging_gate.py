from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PackageLayer(str, Enum):
    KERNEL = "kernel"
    COMMONS = "commons"
    PRODUCT = "product"


@dataclass(frozen=True)
class PackageManifest:
    package_id: str
    layer: PackageLayer
    owner: str
    version: str
    required_kernel_range: str
    integrity_hash: str


@dataclass(frozen=True)
class GateResult:
    approved: bool
    reasons: tuple[str, ...]


class PackagingGate:
    """Base packaging gate for compatibility and integrity checks."""

    def validate(
        self,
        manifest: PackageManifest,
        kernel_version: str,
        verified_integrity_hash: str,
    ) -> GateResult:
        reasons: list[str] = []
        if not manifest.package_id:
            reasons.append("package_id is required")
        if not manifest.owner:
            reasons.append("owner is required")
        if not _version_in_range(kernel_version, manifest.required_kernel_range):
            reasons.append(
                "kernel version is outside required range: "
                f"{kernel_version} not in {manifest.required_kernel_range}"
            )
        if manifest.integrity_hash != verified_integrity_hash:
            reasons.append("integrity hash mismatch")
        return GateResult(approved=not reasons, reasons=tuple(reasons))


def _version_in_range(version: str, constraints: str) -> bool:
    for raw_part in constraints.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if not _evaluate_constraint(version, part):
            return False
    return True


def _evaluate_constraint(version: str, constraint: str) -> bool:
    operators = (">=", "<=", ">", "<", "==")
    for operator in operators:
        if constraint.startswith(operator):
            right = constraint[len(operator) :].strip()
            comparison = _compare_semver(version, right)
            if operator == "==":
                return comparison == 0
            if operator == ">":
                return comparison > 0
            if operator == ">=":
                return comparison >= 0
            if operator == "<":
                return comparison < 0
            if operator == "<=":
                return comparison <= 0
    raise ValueError(f"unsupported version constraint: '{constraint}'")


def _compare_semver(left: str, right: str) -> int:
    left_parts = _parse_semver(left)
    right_parts = _parse_semver(right)
    if left_parts < right_parts:
        return -1
    if left_parts > right_parts:
        return 1
    return 0


def _parse_semver(version: str) -> tuple[int, int, int]:
    segments = version.strip().split(".")
    if len(segments) != 3:
        raise ValueError(f"invalid semantic version '{version}'")
    try:
        major, minor, patch = (int(segment) for segment in segments)
    except ValueError as exc:
        raise ValueError(f"invalid semantic version '{version}'") from exc
    return (major, minor, patch)

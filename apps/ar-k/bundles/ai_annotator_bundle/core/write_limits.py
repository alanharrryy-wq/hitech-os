
"""Write limit helpers for the advisory-only annotator."""

from __future__ import annotations

from pathlib import Path

from core.bundle_constants import ADVISORY_OUTPUT_REL, FORBIDDEN_AUTHORITATIVE_WRITES, REQUIRED_ANNOTATION_ARTIFACTS, VERIFICATION_OUTPUT_REL


def is_annotation_artifact_name(name: str) -> bool:
    return name in REQUIRED_ANNOTATION_ARTIFACTS


def is_forbidden_authoritative_name(name: str) -> bool:
    return name in FORBIDDEN_AUTHORITATIVE_WRITES


def is_allowed_runtime_write(path: Path, root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception:
        return False
    rel_posix = rel.as_posix()
    if not rel_posix.startswith(ADVISORY_OUTPUT_REL):
        return False
    return path.name in REQUIRED_ANNOTATION_ARTIFACTS


def explain_write_limit() -> dict[str, object]:
    return {
        "allowed_runtime_root": ADVISORY_OUTPUT_REL,
        "verification_output_root": VERIFICATION_OUTPUT_REL,
        "allowed_files": REQUIRED_ANNOTATION_ARTIFACTS[:],
        "forbidden_authoritative_files": sorted(FORBIDDEN_AUTHORITATIVE_WRITES),
        "rule": "AI Annotator may emit only annotation artifacts and never rewrite authoritative state.",
        "verification_rule": "Verify may emit sample annotation artifacts only under bundle state for inspection.",
    }


def is_allowed_verification_output(path: Path, root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception:
        return False
    rel_posix = rel.as_posix()
    return rel_posix.startswith(f"{VERIFICATION_OUTPUT_REL}/") and path.name in REQUIRED_ANNOTATION_ARTIFACTS


def assert_example_output_dir(path: Path, root: Path) -> None:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception as exc:
        raise ValueError(f"Verification output escaped root: {path}") from exc
    rel_posix = rel.as_posix()
    if not rel_posix.startswith(f"{VERIFICATION_OUTPUT_REL}/"):
        raise ValueError(f"Verification output must stay under {VERIFICATION_OUTPUT_REL}: {rel_posix}")


def assert_only_annotation_artifacts(paths) -> None:
    bad = sorted({Path(path).name for path in paths if Path(path).name not in REQUIRED_ANNOTATION_ARTIFACTS})
    if bad:
        raise ValueError(f"Non-annotation artifacts detected in output surface: {bad}")

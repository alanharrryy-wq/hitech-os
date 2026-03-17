from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

WINDOWS_DRIVE_RE = re.compile(r"^[a-zA-Z]:[/\\]")
UNC_PREFIXES = ("\\\\", "//")
MAX_REL_PATH_LEN = 1024
REPARSE_POINT_FLAG = 0x0400
PROTECTED_PREFIXES = (".git", ".env", ".env.", ".github/workflows")


class PathGuardError(ValueError):
    pass


@dataclass(frozen=True)
class PathIssue:
    path: str
    reason: str
    worker: str = ""


def _is_absolute_like(raw: str) -> bool:
    text = raw.strip()
    if not text:
        return False
    if text.startswith("/"):
        return True
    if text.startswith(UNC_PREFIXES):
        return True
    if WINDOWS_DRIVE_RE.match(text):
        return True
    return False


def normalize_rel_path(raw: str, *, casefold_windows: bool = True) -> str:
    value = str(raw).strip()
    if not value:
        raise PathGuardError("empty path is not allowed")
    if "\x00" in value:
        raise PathGuardError("NUL byte is not allowed")
    if _is_absolute_like(value):
        raise PathGuardError(f"absolute path is not allowed: {value!r}")
    if ":" in value:
        # Reject drive tricks like C:foo or ADS-style path.
        raise PathGuardError(f"colon is not allowed in relative path: {value!r}")

    normalized = value.replace("\\", "/")
    pure = PurePosixPath(normalized)
    parts: list[str] = []
    for part in pure.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            raise PathGuardError(f"path traversal is not allowed: {value!r}")
        if part in {"~"}:
            raise PathGuardError(f"home shorthand is not allowed: {value!r}")
        parts.append(part)

    if not parts:
        raise PathGuardError(f"path resolves to empty: {value!r}")

    joined = "/".join(parts)
    if len(joined) > MAX_REL_PATH_LEN:
        raise PathGuardError(f"path exceeds max length ({MAX_REL_PATH_LEN}): {value!r}")

    if casefold_windows:
        joined = joined.lower()
    return joined


def canonical_path_key(raw: str) -> str:
    return normalize_rel_path(raw, casefold_windows=True)


def is_protected_path(rel_path: str) -> bool:
    normalized = normalize_rel_path(rel_path, casefold_windows=True)
    return any(
        normalized == prefix or normalized.startswith(prefix + "/")
        for prefix in PROTECTED_PREFIXES
    )


def ensure_within_root(root: Path, rel_path: str, *, allow_reparse_points: bool = False) -> Path:
    normalized = normalize_rel_path(rel_path)
    resolved_root = root.resolve(strict=False)
    candidate = (resolved_root / normalized).resolve(strict=False)
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise PathGuardError(
            f"path escapes root; rel_path={normalized!r} root={resolved_root.as_posix()} candidate={candidate.as_posix()}"
        )
    if not allow_reparse_points and _has_reparse_escape(resolved_root, normalized):
        raise PathGuardError(f"path uses symlink/junction escape: {normalized!r}")
    return candidate


def _has_reparse_escape(root: Path, rel_path: str) -> bool:
    cursor = root
    for part in rel_path.split("/"):
        cursor = cursor / part
        if not cursor.exists():
            continue
        if cursor.is_symlink():
            return True
        try:
            stat_info = cursor.stat()
        except OSError:
            continue
        attrs = getattr(stat_info, "st_file_attributes", 0)
        if attrs & REPARSE_POINT_FLAG:
            return True
    return False


def normalize_path_list(paths: Iterable[str]) -> list[str]:
    normalized = [normalize_rel_path(item) for item in paths]
    return sorted(set(normalized))


def validate_files_changed_entries(
    changes: Iterable[Mapping[str, Any]],
    *,
    worker: str = "",
) -> tuple[list[dict[str, Any]], list[PathIssue]]:
    cleaned: list[dict[str, Any]] = []
    issues: list[PathIssue] = []
    for entry in changes:
        path = str(entry.get("path", ""))
        try:
            normalized = normalize_rel_path(path)
        except PathGuardError as exc:
            issues.append(PathIssue(path=path, reason=str(exc), worker=worker))
            continue
        cleaned.append(
            {
                "path": normalized,
                "change_type": str(entry.get("change_type", "modified")),
                "reason": str(entry.get("reason", "")),
                "sha256": str(entry.get("sha256", "")),
            }
        )
    cleaned.sort(key=lambda item: (item["path"], item["change_type"], item["sha256"]))
    return cleaned, issues


def detect_scope_violations_for_paths(
    *,
    worker: str,
    paths: Iterable[str],
    allow_globs: Iterable[str],
    deny_globs: Iterable[str],
    enforce_protected: bool = True,
) -> list[PathIssue]:
    import fnmatch

    allow = list(allow_globs)
    deny = list(deny_globs)
    violations: list[PathIssue] = []
    for path in paths:
        try:
            normalized = normalize_rel_path(path)
        except PathGuardError as exc:
            violations.append(PathIssue(path=str(path), reason=str(exc), worker=worker))
            continue
        if allow and not any(fnmatch.fnmatch(normalized, glob) for glob in allow):
            violations.append(PathIssue(path=normalized, reason="outside allowlist", worker=worker))
        if any(fnmatch.fnmatch(normalized, glob) for glob in deny):
            violations.append(PathIssue(path=normalized, reason="matched denylist", worker=worker))
        if enforce_protected and is_protected_path(normalized):
            violations.append(PathIssue(path=normalized, reason="protected path", worker=worker))
    violations.sort(key=lambda item: (item.path, item.worker, item.reason))
    return violations

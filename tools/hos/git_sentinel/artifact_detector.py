#!/usr/bin/env python3
from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from .config import SentinelConfig
from .utils import path_matches_any


def _classify_path(rel_path: str, extension: str, config: SentinelConfig) -> tuple[str | None, str]:
    normalized = rel_path.replace("\\", "/")
    lower = normalized.lower()
    file_name = PurePosixPath(normalized).name.lower()

    for runtime_dir in config.runtime_artifact_dirs:
        prefix = runtime_dir.replace("\\", "/").strip("/")
        if lower == prefix.lower() or lower.startswith(prefix.lower() + "/"):
            return "runtime", f"inside runtime artifact dir '{prefix}'"

    if "/logs/" in lower or file_name.endswith(".log"):
        return "logs", "log filename/path"

    if extension in config.temporary_extensions or file_name.endswith("~"):
        return "temporary", "temporary extension"
    if any(token in file_name for token in ("tmp", "temp", "backup", "autosave")):
        return "temporary", "temporary filename token"

    if any(marker in lower for marker in config.cache_markers):
        return "cache", "cache marker in path"
    if extension in {".cache", ".pyc", ".pyo"}:
        return "cache", "cache extension"

    if any(marker in lower for marker in config.build_markers):
        return "build", "build marker in path"
    if extension in {".map", ".tsbuildinfo"}:
        return "build", "build artifact extension"

    if extension in {".zip", ".7z", ".rar", ".tar", ".gz", ".sqlite", ".db", ".dump"}:
        return "runtime", "archive/db artifact extension"
    return None, ""


def _derive_pattern(rel_path: str) -> str:
    pure = PurePosixPath(rel_path.replace("\\", "/"))
    parent = pure.parent.as_posix() if pure.parent.as_posix() != "." else ""
    suffix = pure.suffix
    if parent:
        if suffix:
            return f"{parent}/**/*{suffix}"
        return f"{parent}/**/*"
    if suffix:
        return f"*{suffix}"
    return pure.name


def classify_artifacts(scan_state: dict[str, Any], config: SentinelConfig) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    source_files: list[str] = []
    category_counts: dict[str, int] = {}
    pattern_counts: dict[str, int] = {}
    artifact_dirs: dict[str, int] = {}

    untracked_set = set(scan_state.get("untrackedFiles", []))
    for record in scan_state.get("files", []):
        path = str(record.get("path", ""))
        extension = str(record.get("extension", "")).lower()
        category, reason = _classify_path(path, extension, config)
        if category is None:
            source_files.append(path)
            continue

        category_counts[category] = category_counts.get(category, 0) + 1
        pattern = _derive_pattern(path)
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        top_dir = path.split("/", 1)[0] if "/" in path else path
        artifact_dirs[top_dir] = artifact_dirs.get(top_dir, 0) + 1

        artifacts.append(
            {
                "path": path,
                "category": category,
                "reason": reason,
                "pattern": pattern,
                "tracked": bool(record.get("tracked", False)),
                "untracked": path in untracked_set,
                "size": int(record.get("size", 0)),
                "extension": extension,
            }
        )

    # Runtime directories may include ignored files that do not appear in file records;
    # these are still relevant for telemetry and prediction.
    runtime_dir_warnings: list[dict[str, Any]] = []
    for entry in scan_state.get("runtimeArtifactDirectories", []):
        if not entry.get("exists"):
            continue
        file_count = int(entry.get("fileCount", 0))
        if file_count <= 0:
            continue
        runtime_dir_warnings.append(
            {
                "path": str(entry.get("path", "")),
                "fileCount": file_count,
            }
        )

    learnable_patterns = sorted(
        [{"pattern": pattern, "count": count} for pattern, count in pattern_counts.items()],
        key=lambda item: (-item["count"], item["pattern"]),
    )

    artifact_paths = [item["path"] for item in artifacts]
    cleanup_candidates = [
        item
        for item in artifacts
        if item.get("untracked", False)
        and item.get("category") in {"temporary", "logs", "cache", "build", "runtime"}
    ]
    removable_duplicates: list[dict[str, Any]] = []
    for group in scan_state.get("duplicateFiles", []):
        paths = [str(path) for path in group.get("paths", [])]
        if len(paths) < 2:
            continue
        if not all(path in artifact_paths for path in paths):
            continue
        removable_duplicates.append(group)

    return {
        "summary": {
            "artifactCount": len(artifacts),
            "sourceFileCount": len(source_files),
            "categoryCounts": dict(sorted(category_counts.items())),
            "runtimeDirWarnings": runtime_dir_warnings,
            "learnedPatternCount": len(learnable_patterns),
            "cleanupCandidateCount": len(cleanup_candidates),
        },
        "artifacts": sorted(artifacts, key=lambda item: (item["category"], item["path"])),
        "sourceFiles": sorted(source_files),
        "learnablePatterns": learnable_patterns,
        "artifactDirectories": [
            {"path": key, "count": value}
            for key, value in sorted(artifact_dirs.items(), key=lambda item: (-item[1], item[0]))
        ],
        "cleanupCandidates": sorted(cleanup_candidates, key=lambda item: item["path"]),
        "removableDuplicateGroups": removable_duplicates,
        "artifactPathSet": sorted(artifact_paths),
        "containsSourceRisk": any(path_matches_any(path, list(config.ignore_whitelist_globs)) for path in artifact_paths),
    }


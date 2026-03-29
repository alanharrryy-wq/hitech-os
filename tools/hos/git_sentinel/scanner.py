#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .config import SentinelConfig
from .git_utils import (
    git_deleted_tracked_files,
    git_modified_tracked_files,
    git_tracked_files,
    git_untracked_files,
    git_worktrees,
)
from .utils import file_sha256, is_binary_file, is_within, now_utc_iso, path_matches_any, rel_posix


def _should_skip_dir(rel_dir: str, config: SentinelConfig, dynamic_excludes: set[str]) -> bool:
    normalized = rel_dir.replace("\\", "/").strip("/")
    if not normalized:
        return False
    if normalized in dynamic_excludes:
        return True
    if any(normalized == item or normalized.startswith(item + "/") for item in dynamic_excludes):
        return True
    name = normalized.split("/")[-1]
    if name in {".git", "node_modules", "__pycache__"}:
        return True
    return path_matches_any(normalized, list(config.exclude_dir_globs))


def _count_files_in_dir(path: Path, max_entries: int = 100_000) -> int:
    count = 0
    for _root, _dirs, files in path.walk(top_down=True):
        count += len(files)
        if count >= max_entries:
            return max_entries
    return count


def _find_git_markers(repo_root: Path, config: SentinelConfig) -> list[Path]:
    markers: list[Path] = []
    for root, dirs, files in repo_root.walk(top_down=True):
        current = Path(root)
        if not is_within(repo_root, current):
            dirs[:] = []
            continue
        rel = current.resolve().relative_to(repo_root.resolve()).as_posix()
        filtered_dirs: list[str] = []
        for dir_name in dirs:
            rel_dir = f"{rel}/{dir_name}" if rel != "." else dir_name
            if _should_skip_dir(rel_dir, config, set()):
                continue
            filtered_dirs.append(dir_name)
        dirs[:] = filtered_dirs
        if rel.startswith(".git"):
            dirs[:] = []
            continue
        if ".git" in dirs:
            markers.append(current / ".git")
        if ".git" in files:
            markers.append(current / ".git")
    return sorted(set(markers), key=lambda item: item.as_posix())


def _collect_artifact_clusters(file_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counters: dict[str, dict[str, int]] = {}
    artifact_ext = {".tmp", ".temp", ".log", ".cache", ".zip", ".7z", ".tar", ".gz", ".sqlite", ".db", ".dump"}
    for row in file_records:
        rel_path = str(row.get("path", ""))
        ext = str(row.get("extension", "")).lower()
        if not rel_path:
            continue
        parent = rel_path.rsplit("/", 1)[0] if "/" in rel_path else "."
        bucket = counters.setdefault(parent, {"files": 0, "artifactLike": 0, "bytes": 0})
        bucket["files"] += 1
        bucket["bytes"] += int(row.get("size", 0))
        lower = rel_path.lower()
        if ext in artifact_ext or "/logs/" in lower or "/.cache/" in lower or "/__pycache__/" in lower:
            bucket["artifactLike"] += 1
    clusters: list[dict[str, Any]] = []
    for path, data in counters.items():
        artifact_like = data["artifactLike"]
        total_files = max(1, data["files"])
        ratio = artifact_like / total_files
        if artifact_like >= 5 and ratio >= 0.4:
            clusters.append(
                {
                    "path": path,
                    "artifactLikeFiles": artifact_like,
                    "totalFiles": total_files,
                    "ratio": round(ratio, 4),
                    "bytes": int(data["bytes"]),
                }
            )
    return sorted(clusters, key=lambda row: (-row["artifactLikeFiles"], row["path"]))


def _collect_unexpected_file_types(
    file_records: list[dict[str, Any]],
    untracked_files: list[str],
    config: SentinelConfig,
) -> list[dict[str, Any]]:
    allowed_ext = set(config.expected_text_extensions) | set(config.binary_extensions)
    untracked_set = set(untracked_files)
    counts: dict[str, int] = {}
    examples: dict[str, str] = {}
    for row in file_records:
        rel_path = str(row.get("path", ""))
        if rel_path not in untracked_set:
            continue
        ext = str(row.get("extension", "")).lower()
        if not ext:
            continue
        if ext in allowed_ext:
            continue
        counts[ext] = counts.get(ext, 0) + 1
        examples.setdefault(ext, rel_path)
    return [
        {"extension": ext, "count": count, "example": examples.get(ext, "")}
        for ext, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _normalize_runtime_entries(config: SentinelConfig) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel_dir in config.runtime_artifact_dirs:
        abs_dir = (config.repo_root / rel_dir).resolve()
        if not abs_dir.exists():
            entries.append(
                {
                    "path": rel_dir.replace("\\", "/"),
                    "exists": False,
                    "fileCount": 0,
                }
            )
            continue
        if not is_within(config.repo_root, abs_dir):
            entries.append(
                {
                    "path": rel_dir.replace("\\", "/"),
                    "exists": True,
                    "fileCount": 0,
                    "externalTarget": abs_dir.as_posix(),
                }
            )
            continue
        file_count = _count_files_in_dir(abs_dir) if abs_dir.is_dir() else 1
        entries.append(
            {
                "path": rel_dir.replace("\\", "/"),
                "exists": True,
                "fileCount": file_count,
            }
        )
    return sorted(entries, key=lambda item: item["path"])


def _is_unexpected_binary(rel_path: str, extension: str, config: SentinelConfig) -> bool:
    normalized = rel_path.replace("\\", "/")
    if extension.lower() not in set(config.binary_extensions):
        return False
    for allowed in config.allowed_binary_prefixes:
        allowed_norm = allowed.replace("\\", "/")
        if normalized == allowed_norm.rstrip("/") or normalized.startswith(allowed_norm.rstrip("/") + "/"):
            return False
    return True


def _collect_duplicate_files(
    file_records: list[dict[str, Any]],
    config: SentinelConfig,
) -> list[dict[str, Any]]:
    hashes: dict[str, list[str]] = {}
    for record in file_records:
        if bool(record.get("tracked", True)):
            continue
        if record.get("size", 0) <= 0:
            continue
        if int(record.get("size", 0)) > config.duplicate_hash_max_bytes:
            continue
        rel_path = str(record.get("path", ""))
        abs_path = config.repo_root / rel_path
        if not abs_path.exists() or not abs_path.is_file():
            continue
        try:
            digest = file_sha256(abs_path)
        except OSError:
            continue
        hashes.setdefault(digest, []).append(rel_path)

    duplicates: list[dict[str, Any]] = []
    for digest, paths in hashes.items():
        if len(paths) < 2:
            continue
        duplicates.append(
            {
                "hash": digest,
                "paths": sorted(paths),
                "count": len(paths),
            }
        )
    return sorted(duplicates, key=lambda item: (-item["count"], item["hash"]))


def scan_repository(config: SentinelConfig) -> dict[str, Any]:
    repo_root = config.repo_root
    generated_at = now_utc_iso()

    tracked_files = git_tracked_files(repo_root)
    tracked_set = set(tracked_files)
    untracked_files = git_untracked_files(repo_root)
    modified_files = git_modified_tracked_files(repo_root)
    deleted_files = git_deleted_tracked_files(repo_root)
    worktrees = git_worktrees(repo_root)
    worktree_paths = {item["path"] for item in worktrees}

    dynamic_excludes: set[str] = set()
    try:
        dynamic_excludes.add(config.output_root.resolve().relative_to(repo_root.resolve()).as_posix())
    except ValueError:
        pass

    file_records: list[dict[str, Any]] = []
    unexpected_binaries: list[dict[str, Any]] = []
    large_files: list[dict[str, Any]] = []
    broken_symlinks: list[str] = []
    invalid_permissions: list[dict[str, Any]] = []
    directory_count = 0
    total_size_bytes = 0

    for root, dirs, files in repo_root.walk(top_down=True):
        current = Path(root)
        if not is_within(repo_root, current):
            dirs[:] = []
            continue
        rel_current = rel_posix(current, repo_root)
        directory_count += 1
        filtered_dirs: list[str] = []
        for dir_name in dirs:
            rel_dir = f"{rel_current}/{dir_name}" if rel_current != "." else dir_name
            child_path = current / dir_name
            if not is_within(repo_root, child_path):
                continue
            if _should_skip_dir(rel_dir, config, dynamic_excludes):
                continue
            filtered_dirs.append(dir_name)
        dirs[:] = filtered_dirs

        for file_name in files:
            abs_path = current / file_name
            if not is_within(repo_root, abs_path):
                continue
            rel_path = rel_posix(abs_path, repo_root)
            if rel_path == ".git":
                continue
            if abs_path.is_symlink() and not abs_path.exists():
                broken_symlinks.append(rel_path)
                continue
            try:
                stat = abs_path.stat()
            except OSError:
                continue
            size = int(stat.st_size)
            ext = abs_path.suffix.lower()
            if ext in set(config.binary_extensions):
                binary = True
            elif ext in {
                ".py",
                ".ts",
                ".tsx",
                ".js",
                ".jsx",
                ".mjs",
                ".cjs",
                ".json",
                ".yml",
                ".yaml",
                ".md",
                ".txt",
                ".toml",
                ".ini",
                ".conf",
                ".sh",
                ".ps1",
                ".bat",
                ".cmd",
            }:
                binary = False
            else:
                binary = is_binary_file(abs_path)
            tracked = rel_path in tracked_set

            record = {
                "path": rel_path,
                "size": size,
                "extension": ext,
                "binary": binary,
                "tracked": tracked,
                "mtimeEpoch": int(stat.st_mtime),
                "readable": os.access(abs_path, os.R_OK),
            }
            file_records.append(record)
            total_size_bytes += size

            if _is_unexpected_binary(rel_path=rel_path, extension=ext, config=config):
                unexpected_binaries.append(
                    {
                        "path": rel_path,
                        "size": size,
                        "extension": ext,
                    }
                )

            if size >= config.large_file_threshold_bytes:
                large_files.append(
                    {
                        "path": rel_path,
                        "size": size,
                    }
                )
                if binary:
                    large_files[-1]["binary"] = True

            # Invalid permissions: file exists but not readable by process.
            if not os.access(abs_path, os.R_OK):
                invalid_permissions.append(
                    {
                        "path": rel_path,
                        "reason": "not readable",
                    }
                )

    git_markers = _find_git_markers(repo_root=repo_root, config=config)
    nested_git_markers: list[dict[str, Any]] = []
    for marker in git_markers:
        parent = marker.parent.resolve()
        if parent == repo_root.resolve():
            continue
        parent_text = parent.as_posix()
        kind = "registered_worktree" if parent_text in worktree_paths else "unmanaged_nested_git"
        nested_git_markers.append(
            {
                "markerPath": marker.as_posix(),
                "parentPath": parent_text,
                "kind": kind,
                "exists": marker.exists(),
            }
        )

    duplicates = _collect_duplicate_files(file_records=file_records, config=config)
    artifact_clusters = _collect_artifact_clusters(file_records=file_records)
    unexpected_file_types = _collect_unexpected_file_types(
        file_records=file_records,
        untracked_files=untracked_files,
        config=config,
    )
    runtime_dirs = _normalize_runtime_entries(config=config)

    summary = {
        "generatedAt": generated_at,
        "repoRoot": repo_root.as_posix(),
        "fileCount": len(file_records),
        "directoryCount": directory_count,
        "totalSizeBytes": total_size_bytes,
        "trackedFileCount": len(tracked_files),
        "untrackedFileCount": len(untracked_files),
        "modifiedTrackedCount": len(modified_files),
        "deletedTrackedCount": len(deleted_files),
        "nestedGitMarkers": len([item for item in nested_git_markers if item["kind"] == "unmanaged_nested_git"]),
        "largeFiles": len(large_files),
        "unexpectedBinaries": len(unexpected_binaries),
        "unexpectedFileTypes": len(unexpected_file_types),
        "duplicateGroups": len(duplicates),
        "artifactClusters": len(artifact_clusters),
        "invalidPermissions": len(invalid_permissions),
    }

    return {
        "summary": summary,
        "files": sorted(file_records, key=lambda item: item["path"]),
        "untrackedFiles": sorted(untracked_files),
        "trackedFiles": tracked_files,
        "trackedModifiedFiles": sorted(modified_files),
        "trackedDeletedFiles": sorted(deleted_files),
        "nestedGitMarkers": sorted(nested_git_markers, key=lambda item: item["markerPath"]),
        "runtimeArtifactDirectories": runtime_dirs,
        "unexpectedBinaries": sorted(unexpected_binaries, key=lambda item: (-item["size"], item["path"])),
        "largeFiles": sorted(large_files, key=lambda item: (-item["size"], item["path"])),
        "largeBinaryFiles": sorted(
            [row for row in large_files if bool(row.get("binary", False))],
            key=lambda item: (-item["size"], item["path"]),
        ),
        "unexpectedFileTypes": unexpected_file_types,
        "artifactClusters": artifact_clusters,
        "duplicateFiles": duplicates,
        "brokenSymlinks": sorted(set(broken_symlinks)),
        "invalidPermissions": invalid_permissions,
        "gitWorktrees": worktrees,
    }

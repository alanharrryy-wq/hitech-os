#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run_git(repo_root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(repo_root), *args]
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            "git command failed: "
            + " ".join(command)
            + f"\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def _split_non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def git_tracked_files(repo_root: Path) -> list[str]:
    completed = run_git(repo_root, ["ls-files", "-z"])
    return sorted([chunk for chunk in completed.stdout.split("\x00") if chunk.strip()])


def git_untracked_files(repo_root: Path) -> list[str]:
    completed = run_git(repo_root, ["ls-files", "--others", "--exclude-standard", "-z"])
    return sorted([chunk for chunk in completed.stdout.split("\x00") if chunk.strip()])


def git_deleted_tracked_files(repo_root: Path) -> list[str]:
    completed = run_git(repo_root, ["ls-files", "--deleted", "-z"])
    return sorted([chunk for chunk in completed.stdout.split("\x00") if chunk.strip()])


def git_modified_tracked_files(repo_root: Path) -> list[str]:
    completed = run_git(repo_root, ["status", "--porcelain", "--untracked-files=no"])
    lines = _split_non_empty_lines(completed.stdout)
    changed: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            changed.append(path)
    return sorted(set(changed))


def parse_worktree_porcelain(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                rows.append(current)
                current = {}
            continue
        if " " in line:
            key, value = line.split(" ", 1)
            current[key] = value.strip()
        else:
            current[line] = True
    if current:
        rows.append(current)
    return rows


def git_worktrees(repo_root: Path) -> list[dict[str, Any]]:
    completed = run_git(repo_root, ["worktree", "list", "--porcelain"], check=False)
    if completed.returncode != 0:
        return []
    parsed = parse_worktree_porcelain(completed.stdout)
    normalized: list[dict[str, Any]] = []
    for row in parsed:
        worktree = str(row.get("worktree", "")).strip()
        if not worktree:
            continue
        path = Path(worktree)
        normalized.append(
            {
                "path": path.resolve().as_posix(),
                "branch": str(row.get("branch", "")).replace("refs/heads/", ""),
                "head": str(row.get("HEAD", "")),
                "detached": bool(row.get("detached", False)),
                "prunable": bool(row.get("prunable", False)),
                "locked": bool(row.get("locked", False)),
                "bare": bool(row.get("bare", False)),
                "exists": path.exists(),
            }
        )
    return sorted(normalized, key=lambda item: item["path"])


def git_branch_activity(repo_root: Path) -> list[dict[str, Any]]:
    completed = run_git(
        repo_root,
        ["for-each-ref", "refs/heads", "--format=%(refname:short)|%(committerdate:unix)|%(upstream:short)"],
        check=False,
    )
    if completed.returncode != 0:
        return []
    rows: list[dict[str, Any]] = []
    for line in _split_non_empty_lines(completed.stdout):
        parts = line.split("|")
        if len(parts) != 3:
            continue
        branch, ts_raw, upstream = parts
        try:
            ts_value = int(ts_raw)
        except ValueError:
            ts_value = 0
        rows.append(
            {
                "branch": branch,
                "lastCommitEpoch": ts_value,
                "upstream": upstream,
            }
        )
    return sorted(rows, key=lambda row: row["branch"])


def git_top_modified_files(repo_root: Path, days: int = 90, limit: int = 200) -> list[dict[str, Any]]:
    completed = run_git(
        repo_root,
        [
            "log",
            f"--since={days} days ago",
            "--name-only",
            "--pretty=format:",
        ],
        check=False,
    )
    if completed.returncode != 0:
        return []
    counts: dict[str, int] = {}
    for line in completed.stdout.splitlines():
        path = line.strip()
        if not path:
            continue
        counts[path] = counts.get(path, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"path": path, "commits": count} for path, count in ranked[:limit]]


def git_growth_timeline(repo_root: Path, max_commits: int = 6000) -> list[dict[str, Any]]:
    completed = run_git(
        repo_root,
        ["log", "--reverse", f"--max-count={max_commits}", "--format=%ct|%H"],
        check=False,
    )
    if completed.returncode != 0:
        return []
    timeline: list[dict[str, Any]] = []
    for line in _split_non_empty_lines(completed.stdout):
        parts = line.split("|")
        if len(parts) != 2:
            continue
        ts_raw, commit = parts
        try:
            ts_value = int(ts_raw)
        except ValueError:
            continue
        timeline.append({"epoch": ts_value, "commit": commit})
    return timeline


def git_commit_file_sets(repo_root: Path, max_commits: int = 2500) -> list[list[str]]:
    completed = run_git(
        repo_root,
        [
            "log",
            f"--max-count={max_commits}",
            "--name-only",
            "--pretty=format:@@COMMIT@@%H",
        ],
        check=False,
    )
    if completed.returncode != 0:
        return []

    commits: list[list[str]] = []
    current: list[str] = []
    for raw_line in completed.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("@@COMMIT@@"):
            if current:
                commits.append(sorted(set(current)))
                current = []
            continue
        current.append(line)
    if current:
        commits.append(sorted(set(current)))
    return commits


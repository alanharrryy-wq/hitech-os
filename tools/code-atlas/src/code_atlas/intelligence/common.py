from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

EXCLUDED_PARTS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo",
    "__pycache__", ".pytest_cache", ".venv", "venv", ".cache",
}
HISTORICAL_PARTS = {"archive", "archives", "old", "legacy", "history", "historical", "backup", "backups"}
GENERATED_PARTS = {"generated", "dist", "build", ".next", "coverage"}
TEXT_SUFFIXES = {
    # Repository-neutral source text. Keep this coherent with languages recognized
    # by repository discovery so a file cannot be called source code and then be
    # silently excluded from physical/semantic evidence.
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts",
    ".java", ".kt", ".go", ".rs", ".cs", ".cpp", ".cc", ".c", ".h", ".rb", ".php",
    ".swift", ".scala",
    ".json", ".jsonc", ".md", ".txt", ".csv", ".toml", ".yaml", ".yml", ".xml", ".html",
    ".css", ".scss", ".sql", ".prisma", ".graphql", ".gql", ".sh", ".ps1", ".cmd", ".bat",
    ".ini", ".cfg",
}
SENSITIVE_NAME_RE = re.compile(
    r"(?i)(^|/)(?:\.env(?:\.|$)|[^/]*(?:secret|credential|password|private[_-]?key|access[_-]?token)[^/]*)"
)

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_repo_relative(repo: Path, value: str | Path) -> str:
    repo = repo.resolve()
    raw = str(value).replace("\\", "/").strip()
    if not raw:
        raise ValueError("EMPTY_REPOSITORY_PATH")
    candidate = Path(raw)
    if candidate.is_absolute():
        raise ValueError(f"ABSOLUTE_REPOSITORY_PATH_NOT_ALLOWED:{raw}")
    parts = [part for part in candidate.parts if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise ValueError(f"REPOSITORY_PATH_TRAVERSAL:{raw}")
    normalized = Path(*parts)
    resolved = (repo / normalized).resolve(strict=False)
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"REPOSITORY_PATH_ESCAPE:{raw}") from exc
    return normalized.as_posix()

def is_sensitive_path(rel: str) -> bool:
    return bool(SENSITIVE_NAME_RE.search(rel.replace("\\", "/")))

def is_historical_path(rel: str) -> bool:
    return bool(set(Path(rel).parts) & HISTORICAL_PARTS)

def is_generated_path(rel: str) -> bool:
    return bool(set(Path(rel).parts) & GENERATED_PARTS)

def is_text_path(rel: str) -> bool:
    path = Path(rel)
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {
        "LICENSE", "NOTICE", "Makefile", "Dockerfile", "CODEOWNERS", "AGENTS.md",
    }

def run_git(repo: Path, *args: str) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45, shell=False,
        )
        return p.returncode, p.stdout, p.stderr
    except Exception as exc:
        return 999, "", repr(exc)

def git_identity(repo: Path) -> dict[str, Any]:
    code, head, _ = run_git(repo, "rev-parse", "HEAD")
    tree_code, tree, _ = run_git(repo, "rev-parse", "HEAD^{tree}")
    branch_code, branch, _ = run_git(repo, "branch", "--show-current")
    remote_code, remote, _ = run_git(repo, "config", "--get", "remote.origin.url")
    status_code, status, _ = run_git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return {
        "isGit": code == 0 and bool(head.strip()),
        "head": head.strip() if code == 0 else None,
        "tree": tree.strip() if tree_code == 0 else None,
        "branch": branch.strip() if branch_code == 0 else None,
        "remote": remote.strip() if remote_code == 0 else None,
        "dirty": bool(status.strip()) if status_code == 0 else None,
    }

def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(str(v) for v in values if str(v).strip()))

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .common import (
    EXCLUDED_PARTS, git_identity, is_generated_path, is_historical_path,
    is_sensitive_path, is_text_path, run_git, sha256_file,
)

LANGUAGE_SUFFIXES = {
    ".py": "python", ".pyi": "python", ".js": "javascript", ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".java": "java", ".kt": "kotlin",
    ".go": "go", ".rs": "rust", ".cs": "csharp", ".cpp": "cpp", ".cc": "cpp",
    ".c": "c", ".h": "c-cpp-header", ".rb": "ruby", ".php": "php", ".swift": "swift",
    ".scala": "scala", ".sql": "sql", ".prisma": "prisma-schema",
}
FRAMEWORK_MARKERS = {
    "next": ("next.config.js", "next.config.mjs", "next.config.ts"),
    "vite": ("vite.config.js", "vite.config.ts", "vite.config.mjs"),
    "django": ("manage.py",),
    "flask": ("wsgi.py",),
    "rails": ("Gemfile", "config/routes.rb"),
    "cargo": ("Cargo.toml",),
    "go-module": ("go.mod",),
    "dotnet": (".sln",),
}
CI_PREFIXES = (".github/workflows/", ".gitlab-ci", "Jenkinsfile", "azure-pipelines", ".circleci/")
TEST_PARTS = {"test", "tests", "__tests__", "spec", "specs", "e2e"}
DB_NAMES = {
    "schema.prisma", "database.sqlite", "db.sqlite", "db.sqlite3", "database.sqlite3",
    "knexfile.js", "knexfile.ts", "alembic.ini",
}
MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile", "poetry.lock",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile",
    "composer.json", "mix.exs",
}
MAX_TEXT_BYTES = 2_500_000

def _tracked_entries(repo: Path) -> tuple[list[str], str, dict[str, dict[str, Any]]]:
    code, out, _ = run_git(repo, "ls-files", "-s", "-z")
    if code == 0:
        paths: list[str] = []
        meta: dict[str, dict[str, Any]] = {}
        for record in out.split("\0"):
            if not record or "\t" not in record:
                continue
            head, rel = record.split("\t", 1)
            parts = head.split()
            if len(parts) < 3:
                continue
            mode, blob, stage = parts[:3]
            paths.append(rel)
            meta[rel] = {"gitMode": mode, "gitBlobSha": blob, "gitStage": int(stage)}
        return sorted(paths), "git-index", meta
    paths = []
    for current, dirs, names in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_PARTS and not d.startswith(".code-atlas-out"))
        base = Path(current)
        try:
            rel_parts = base.relative_to(repo).parts
        except ValueError:
            continue
        if set(rel_parts) & EXCLUDED_PARTS:
            continue
        for name in sorted(names):
            path = base / name
            try:
                paths.append(path.relative_to(repo).as_posix())
            except ValueError:
                pass
    return sorted(set(paths)), "filesystem", {}

def _record(repo: Path, rel: str, git_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    path = repo / rel
    exists = path.exists() or path.is_symlink()
    size = None
    if exists:
        try:
            size = path.lstat().st_size
        except OSError:
            pass
    sensitive = is_sensitive_path(rel)
    git_meta = git_meta or {}
    return {
        "path": rel,
        "gitMode": git_meta.get("gitMode"),
        "gitBlobSha": git_meta.get("gitBlobSha"),
        "gitStage": git_meta.get("gitStage"),
        "exists": exists,
        "isSymlink": bool(exists and path.is_symlink()),
        "size": size,
        "suffix": Path(rel).suffix.lower(),
        "basename": Path(rel).name,
        "language": LANGUAGE_SUFFIXES.get(Path(rel).suffix.lower()),
        "isText": is_text_path(rel),
        "sensitiveName": sensitive,
        "contentRead": False,
        "fileSha256": None,
        "contentSha256": None,
        "historical": is_historical_path(rel),
        "generated": is_generated_path(rel),
    }

def _inspect_safe(repo: Path, row: dict[str, Any], max_text_bytes: int = MAX_TEXT_BYTES) -> tuple[str, str | None, str | None, bool]:
    if not row["exists"] or row["sensitiveName"]:
        return row["path"], None, None, False
    path = repo / row["path"]
    if not path.is_file() or path.is_symlink():
        return row["path"], None, None, False
    try:
        if not row["isText"] or (row["size"] or 0) > max_text_bytes:
            file_digest = None if row.get("gitBlobSha") else sha256_file(path)
            return row["path"], file_digest, None, False
        file_digest = sha256_file(path)
        path.read_text(encoding="utf-8", errors="replace")
        return row["path"], file_digest, file_digest, True
    except OSError:
        return row["path"], None, None, False

def _package_metadata(repo: Path, paths: set[str]) -> dict[str, Any]:
    packages: list[dict[str, Any]] = []
    for rel in sorted(paths):
        if Path(rel).name not in MANIFEST_NAMES:
            continue
        row = {"path": rel, "kind": Path(rel).name, "name": None, "scripts": [], "dependencies": []}
        if rel.endswith("package.json"):
            try:
                raw = json.loads((repo / rel).read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    row["name"] = raw.get("name")
                    row["scripts"] = sorted((raw.get("scripts") or {}).keys()) if isinstance(raw.get("scripts"), dict) else []
                    deps = {}
                    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                        if isinstance(raw.get(key), dict):
                            deps.update(raw[key])
                    row["dependencies"] = sorted(deps)
            except Exception:
                row["parseStatus"] = "UNREADABLE"
        packages.append(row)
    return {"count": len(packages), "packages": packages}

def _infer_frameworks(paths: set[str], packages: dict[str, Any]) -> list[dict[str, Any]]:
    found: dict[str, set[str]] = defaultdict(set)
    basenames = {Path(p).name for p in paths}
    for framework, markers in FRAMEWORK_MARKERS.items():
        for marker in markers:
            if marker.startswith("."):
                if any(p.endswith(marker) for p in paths):
                    found[framework].add(marker)
            elif marker in basenames or marker in paths:
                found[framework].add(marker)
    package_deps = set()
    for row in packages.get("packages", []):
        package_deps.update(row.get("dependencies") or [])
    dep_map = {
        "react": "react", "next": "next", "vue": "vue", "svelte": "svelte",
        "express": "express", "fastify": "fastify", "nestjs": "@nestjs/core",
        "prisma": "@prisma/client",
    }
    for framework, dep in dep_map.items():
        if dep in package_deps:
            found[framework].add(f"dependency:{dep}")
    return [{"id": key, "evidence": sorted(values)} for key, values in sorted(found.items())]


def _component_roots(paths: set[str], packages: dict[str, Any]) -> list[dict[str, Any]]:
    roots: dict[str, dict[str, Any]] = {}
    for row in packages.get("packages", []):
        rel = str(row.get("path") or "")
        parent = Path(rel).parent.as_posix()
        if parent == ".":
            parent = "."
        roots[parent] = {"root": parent, "kind": "package", "evidence": [rel]}
    top_counts = Counter(Path(p).parts[0] for p in paths if Path(p).parts)
    for top, count in top_counts.items():
        if top.startswith(".") or top in EXCLUDED_PARTS:
            continue
        if count >= 3 and top not in roots:
            roots[top] = {"root": top, "kind": "repository-region", "evidence": [f"file-count:{count}"]}
    return sorted(roots.values(), key=lambda row: row["root"])


def _semantic_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    text_candidates = [
        row for row in rows
        if row["exists"] and row["isText"] and not row["sensitiveName"]
    ]
    readable_candidates = [
        row for row in text_candidates
        if not row.get("isSymlink") and (row.get("size") or 0) <= MAX_TEXT_BYTES
    ]
    content_read = [row for row in text_candidates if row["contentRead"]]
    oversized = [row for row in text_candidates if (row.get("size") or 0) > MAX_TEXT_BYTES]
    symlinks = [row for row in text_candidates if row.get("isSymlink")]
    unreadable = [
        row for row in readable_candidates
        if not row["contentRead"]
    ]
    unsupported_or_binary = [
        row for row in rows
        if row["exists"] and not row["sensitiveName"] and not row["isText"]
    ]
    recognized_source = [
        row for row in rows
        if row["exists"] and row.get("language") and not row["sensitiveName"]
    ]
    recognized_read = [row for row in recognized_source if row["contentRead"]]
    recognized_unread = [row for row in recognized_source if not row["contentRead"]]
    return {
        "eligibleText": len(text_candidates),
        "readableEligibleText": len(readable_candidates),
        "contentRead": len(content_read),
        "percent": round(100 * len(content_read) / max(1, len(text_candidates)), 4),
        "oversizedText": len(oversized),
        "unreadableText": len(unreadable),
        "sensitiveSkipped": sum(1 for row in rows if row["exists"] and row["sensitiveName"]),
        "symlinkSkipped": len(symlinks),
        "unsupportedOrBinary": len(unsupported_or_binary),
        "recognizedSourceFiles": len(recognized_source),
        "recognizedSourceRead": len(recognized_read),
        "recognizedSourceUnreadable": len(recognized_unread),
        "recognizedSourceCoveragePercent": round(
            100 * len(recognized_read) / max(1, len(recognized_source)), 4
        ),
        "maxTextBytes": MAX_TEXT_BYTES,
        "rule": "COUNT_SKIPPED_AND_UNREADABLE_EXPLICITLY_NEVER_HIDE_RECOGNIZED_SOURCE",
    }
def discover_repository(repo_root: str | Path, *, workers: int = 18) -> dict[str, Any]:
    repo = Path(repo_root).expanduser().resolve()
    if not repo.is_dir():
        raise FileNotFoundError(f"REPOSITORY_NOT_FOUND:{repo}")
    paths, source, git_meta = _tracked_entries(repo)
    rows = [_record(repo, rel, git_meta.get(rel)) for rel in paths]
    by_path = {row["path"]: row for row in rows}
    with ThreadPoolExecutor(max_workers=max(1, min(18, workers))) as pool:
        for rel, file_digest, content_digest, read in pool.map(lambda row: _inspect_safe(repo, row), rows):
            row = by_path[rel]
            row["fileSha256"] = file_digest
            row["contentSha256"] = content_digest
            row["contentRead"] = read
    pathset = set(paths)
    languages = Counter(row["language"] for row in rows if row["language"])
    ci = sorted(p for p in paths if p.startswith(CI_PREFIXES) or Path(p).name in {"Jenkinsfile", ".gitlab-ci.yml"})
    tests = sorted(
        p for p in paths
        if set(part.lower() for part in Path(p).parts) & TEST_PARTS
        or Path(p).name.lower().startswith(("test_", "spec_"))
        or Path(p).stem.lower().endswith(("_test", ".spec", ".test"))
    )
    db = sorted(
        p for p in paths
        if Path(p).name in DB_NAMES
        or "migration" in {part.lower() for part in Path(p).parts}
        or Path(p).suffix.lower() in {".sql", ".prisma"}
    )
    ownership = sorted(p for p in paths if Path(p).name in {"CODEOWNERS", "OWNERS", "MAINTAINERS"})
    packages = _package_metadata(repo, pathset)
    semantic_coverage = _semantic_coverage(rows)
    sensitive = [row["path"] for row in rows if row["sensitiveName"]]
    return {
        "schemaVersion": "code_atlas_repository_discovery.v1",
        "repoRoot": str(repo),
        "identity": git_identity(repo),
        "inventorySource": source,
        "files": rows,
        "fileCount": len(rows),
        "physicalCoverage": {
            "enumerated": len(rows),
            "expected": len(paths),
            "percent": 100.0 if len(rows) == len(paths) else round(100 * len(rows) / max(1, len(paths)), 4),
            "gitBlobHashed": sum(1 for row in rows if row.get("gitBlobSha")),
            "sha256Inspected": sum(1 for row in rows if row.get("fileSha256")),
        },
        "semanticCoverage": semantic_coverage,
        "languages": [{"id": k, "files": v} for k, v in languages.most_common()],
        "frameworks": _infer_frameworks(pathset, packages),
        "packages": packages,
        "componentRoots": _component_roots(pathset, packages),
        "ciFiles": ci,
        "testFiles": tests,
        "databaseFiles": db,
        "ownershipFiles": ownership,
        "sensitivePaths": sensitive,
        "sensitivePolicy": "PATH_ONLY_NO_CONTENT_INGEST",
        "historicalCount": sum(1 for row in rows if row["historical"]),
        "generatedCount": sum(1 for row in rows if row["generated"]),
        "readOnly": True,
        "productionCertified": False,
    }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import ast
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

TOOL_NAME = "capatch dependency-map analyzer"
VERSION = "1.2.0"

# Default exclusions are deliberately generic: dependency caches, build output,
# generated reports, installer temp folders, and backup snapshots. They keep the
# analyzer focused on the live project tree while still allowing opt-in override
# through --include-hidden-dirs or repeated --exclude-dir values.
EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".turbo",
    "coverage",
    "out",
    "target",
    "reports",
    "backup",
    "backups",
    ".prisma_backups",
    ".prisma_installer_backups",
    ".prisma_installer_tmp",
    "_chatgpt_patch_backups",
    "_dependency_graphs",
}

BACKUP_SUFFIXES = (
    "_backups",
    "-backups",
    ".backup",
    ".bak",
)

SOURCE_EXT = {".py", ".pyw", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}
TS_RE = re.compile(
    r"(?:import\s+(?:type\s+)?(?:[^'\"]+?\s+from\s+)?|export\s+[^'\"]*?\s+from\s+|require\s*\(|import\s*\()\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)


def rel(p: Path, root: Path) -> str:
    try:
        return str(p.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def read_json(p: Path) -> dict[str, Any]:
    try:
        data = json.loads(text(p))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _split_extra_excludes(items: list[str] | None) -> set[str]:
    out: set[str] = set()
    for item in items or []:
        for part in str(item).split(","):
            cleaned = part.strip().lower()
            if cleaned:
                out.add(cleaned)
    return out


def should_exclude_dir(name: str, *, extra_excludes: set[str], include_hidden_dirs: bool) -> bool:
    cleaned = str(name or "").strip()
    lowered = cleaned.lower()
    if not lowered:
        return False
    if lowered in EXCLUDED_DIR_NAMES or lowered in extra_excludes:
        return True
    if any(lowered.endswith(suffix) for suffix in BACKUP_SUFFIXES):
        return True
    if lowered.endswith("_tmp") or lowered.endswith("-tmp"):
        return True
    if not include_hidden_dirs and lowered.startswith("."):
        return True
    return False


def walk(
    root: Path,
    max_files: int,
    *,
    extra_excludes: set[str] | None = None,
    include_hidden_dirs: bool = False,
) -> Iterable[Path]:
    count = 0
    extra = extra_excludes or set()
    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = sorted(
            d
            for d in dir_names
            if not should_exclude_dir(d, extra_excludes=extra, include_hidden_dirs=include_hidden_dirs)
        )
        for file_name in sorted(file_names):
            count += 1
            if count > max_files:
                return
            yield Path(current_root) / file_name


def _load_tsconfig_file(path: Path, root: Path) -> dict[str, Any]:
    data = read_json(path)
    compiler_options = data.get("compilerOptions") if isinstance(data.get("compilerOptions"), dict) else {}
    return {
        "path": rel(path, root),
        "dir": str(path.parent.resolve()),
        "base_url": str(compiler_options.get("baseUrl") or "."),
        "paths": compiler_options.get("paths") if isinstance(compiler_options.get("paths"), dict) else {},
    }


def discover_tsconfigs(
    root: Path,
    max_files: int,
    *,
    extra_excludes: set[str] | None = None,
    include_hidden_dirs: bool = False,
) -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []
    for candidate in walk(root, max_files, extra_excludes=extra_excludes, include_hidden_dirs=include_hidden_dirs):
        if candidate.name in {"tsconfig.json", "jsconfig.json"}:
            configs.append(_load_tsconfig_file(candidate, root))
    configs.sort(key=lambda item: len(str(item.get("dir", ""))), reverse=True)
    return configs


def root_tsconfig(root: Path, configs: list[dict[str, Any]]) -> dict[str, Any]:
    root_resolved = str(root.resolve())
    for cfg in configs:
        if str(cfg.get("dir", "")) == root_resolved:
            return {
                "path": str(cfg.get("path", "")),
                "base_url": str(cfg.get("base_url") or "."),
                "paths": cfg.get("paths") if isinstance(cfg.get("paths"), dict) else {},
            }
    return {"path": "", "base_url": ".", "paths": {}}


def nearest_tsconfig(path: Path, root: Path, configs: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        resolved = path.resolve()
    except Exception:
        resolved = path
    for cfg in configs:
        cfg_dir = Path(str(cfg.get("dir", ""))).expanduser()
        try:
            resolved.relative_to(cfg_dir.resolve())
            return cfg
        except Exception:
            continue
    return {"path": "", "dir": str(root.resolve()), "base_url": ".", "paths": {}}


def package(root: Path) -> dict[str, Any]:
    p = root / "package.json"
    if not p.exists():
        return {}
    data = read_json(p)
    deps: dict[str, str] = {}
    for key in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
        if isinstance(data.get(key), dict):
            deps.update({str(dep): str(version) for dep, version in data[key].items()})
    return {
        "name": str(data.get("name") or ""),
        "scripts": data.get("scripts") if isinstance(data.get("scripts"), dict) else {},
        "dependencies": deps,
    }


def workspaces(root: Path) -> list[str]:
    p = root / "pnpm-workspace.yaml"
    if not p.exists():
        return []
    out: list[str] = []
    for raw in text(p).splitlines():
        line = raw.strip()
        if line.startswith("-"):
            item = line[1:].strip().strip('"\'')
            if item:
                out.append(item)
    return out


def resolve_file(base: Path) -> Path | None:
    """Resolve TS/JS/Python import targets without lying about dotted module names.

    Important edge case: imports such as `./repository.prisma` or
    `@/modules/catalog/module.manifest` often point to files named
    `repository.prisma.ts` and `module.manifest.ts`.  `Path.with_suffix()`
    replaces the final suffix, so it probes `repository.ts` / `module.ts` and
    misses the real file.  We keep that legacy probe for ordinary imports, but
    also append suffixes to the full path string.  Tiny detail, huge amount of
    avoided clownery.
    """
    suffixes = [
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".mts",
        ".cts",
        ".py",
        ".pyw",
        ".d.ts",
        ".css",
        ".json",
    ]
    candidates: list[Path] = [base]
    for suffix in suffixes:
        try:
            candidates.append(base.with_suffix(suffix))
        except ValueError:
            pass
        candidates.append(Path(str(base) + suffix))
    candidates.extend(base / index_name for index_name in [
        "index.ts",
        "index.tsx",
        "index.js",
        "index.jsx",
        "index.mjs",
        "index.cjs",
        "index.d.ts",
        "__init__.py",
    ])

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _resolve_alias_target(spec: str, target_pattern: str, cfg_dir: Path, base_url: str) -> Path:
    raw_target = str(target_pattern)
    target_prefix = raw_target.split("*", 1)[0].rstrip("/\\")
    alias_prefix = ""
    return cfg_dir / base_url / target_prefix / alias_prefix / spec


def resolve_ts(spec: str, importer: Path, root: Path, cfg: dict[str, Any]) -> tuple[str, str]:
    if spec.startswith("."):
        hit = resolve_file((importer.parent / spec).resolve())
        return ("internal", rel(hit, root)) if hit else ("unresolved", spec)

    paths = cfg.get("paths") if isinstance(cfg.get("paths"), dict) else {}
    cfg_dir = Path(str(cfg.get("dir") or root)).expanduser().resolve()
    base_url = str(cfg.get("base_url") or ".")

    for alias, targets in paths.items():
        if not isinstance(targets, list):
            continue
        alias_text = str(alias)
        alias_prefix = alias_text.split("*", 1)[0]
        if not spec.startswith(alias_prefix):
            continue
        rest = spec[len(alias_prefix):]
        for raw_target in targets:
            target_prefix = str(raw_target).split("*", 1)[0].rstrip("/\\")
            candidate = (cfg_dir / base_url / target_prefix / rest).resolve()
            hit = resolve_file(candidate)
            if hit:
                return "internal", rel(hit, root)
        return "alias-unresolved", spec

    if spec.startswith("@/"):
        # Common Next.js convention. Only resolve heuristically when there is a
        # nearby src/ directory; otherwise keep it external instead of lying.
        for base_dir in (cfg_dir / "src", cfg_dir):
            hit = resolve_file((base_dir / spec[2:]).resolve())
            if hit:
                return "internal", rel(hit, root)

    return "external", spec.split("/", 1)[0] if not spec.startswith("@") else "/".join(spec.split("/")[:2])


def py_imports(path: Path, root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    source = rel(path, root)
    try:
        tree = ast.parse(text(path), filename=str(path))
    except SyntaxError as exc:
        return [{"source": source, "target": "<parse-error>", "kind": "python-parse-error", "raw": str(exc)}]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append({"source": source, "target": str(alias.name), "kind": "python-import", "raw": str(alias.name)})
        elif isinstance(node, ast.ImportFrom):
            module = "." * int(node.level or 0) + str(node.module or "")
            out.append({"source": source, "target": module, "kind": "python-relative-import" if node.level else "python-import", "raw": module})
    return out


def ts_imports(path: Path, root: Path, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    source = rel(path, root)
    for match in TS_RE.finditer(text(path)):
        spec = match.group(1).strip()
        kind, target = resolve_ts(spec, path, root, cfg)
        out.append({"source": source, "target": target, "kind": f"ts-{kind}-import", "raw": spec})
    return out


def analyze(
    root: Path,
    max_files: int = 5000,
    *,
    extra_excludes: set[str] | None = None,
    include_hidden_dirs: bool = False,
) -> dict[str, Any]:
    root = root.expanduser().resolve()
    pkg = package(root)
    workspace_patterns = workspaces(root)
    tsconfigs = discover_tsconfigs(root, max_files, extra_excludes=extra_excludes, include_hidden_dirs=include_hidden_dirs)
    files = list(walk(root, max_files, extra_excludes=extra_excludes, include_hidden_dirs=include_hidden_dirs))
    sources = [p for p in files if p.suffix.lower() in SOURCE_EXT]
    edges: list[dict[str, Any]] = []

    for p in sources:
        suffix = p.suffix.lower()
        if suffix in {".py", ".pyw"}:
            edges += py_imports(p, root)
        else:
            cfg = nearest_tsconfig(p, root, tsconfigs)
            edges += ts_imports(p, root, cfg)

    for dep, version in sorted((pkg.get("dependencies") or {}).items()):
        edges.append({"source": "package.json", "target": dep, "kind": "package-dependency", "raw": str(version)})

    counts: dict[str, int] = {}
    for p in sources:
        key = p.suffix.lower().lstrip(".") or "file"
        counts[key] = counts.get(key, 0) + 1

    unresolved = [e for e in edges if "unresolved" in e.get("kind", "")]
    return {
        "tool": TOOL_NAME,
        "version": VERSION,
        "root": str(root),
        "summary": {
            "files_scanned": len(files),
            "source_files": len(sources),
            "edges": len(edges),
            "unresolved_edges": len(unresolved),
            "source_counts": dict(sorted(counts.items())),
        },
        "project": {
            "package_name": pkg.get("name", ""),
            "package_manager": "pnpm" if workspace_patterns or (root / "pnpm-lock.yaml").exists() else "npm" if (root / "package.json").exists() else "unknown",
            "tsconfig": root_tsconfig(root, tsconfigs),
            "tsconfigs": [
                {"path": cfg.get("path", ""), "base_url": cfg.get("base_url", "."), "paths": cfg.get("paths", {})}
                for cfg in tsconfigs
            ],
            "pnpm_workspaces": workspace_patterns,
            "exclude_policy": {
                "default_excluded_dirs": sorted(EXCLUDED_DIR_NAMES),
                "backup_suffixes": list(BACKUP_SUFFIXES),
                "include_hidden_dirs": include_hidden_dirs,
                "extra_excludes": sorted(extra_excludes or []),
            },
        },
        "edges": edges,
        "unresolved": unresolved,
    }


def md(result: dict[str, Any]) -> str:
    summary = result.get("summary", {})
    project = result.get("project", {})
    lines = [
        "# Dependency Map Report",
        "",
        f"Root: `{result.get('root', '')}`",
        f"Analyzer version: `{result.get('version', '')}`",
        "",
        "## Summary",
        "",
        f"- Files scanned: `{summary.get('files_scanned', 0)}`",
        f"- Source files: `{summary.get('source_files', 0)}`",
        f"- Edges: `{summary.get('edges', 0)}`",
        f"- Unresolved edges: `{summary.get('unresolved_edges', 0)}`",
        f"- Package manager: `{project.get('package_manager', '')}`",
        f"- TS configs detected: `{len(project.get('tsconfigs') or [])}`",
        "",
        "## Top edges",
        "",
    ]
    for edge in list(result.get("edges", []))[:80]:
        lines.append(f"- `{edge.get('source')}` -> `{edge.get('target')}` ({edge.get('kind')}: `{edge.get('raw')}`)")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Universal dependency map analyzer installed by Capatch.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--output")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--exclude-dir", action="append", default=[], help="Extra directory name to exclude. May be repeated or comma-separated.")
    parser.add_argument("--include-hidden-dirs", action="store_true", help="Scan hidden directories. Default is to skip them.")
    args = parser.parse_args(argv)

    result = analyze(
        Path(args.root),
        args.max_files,
        extra_excludes=_split_extra_excludes(args.exclude_dir),
        include_hidden_dirs=bool(args.include_hidden_dirs),
    )
    content = json.dumps(result, indent=2, ensure_ascii=False) if args.format == "json" else md(result)
    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

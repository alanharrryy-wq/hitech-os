#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

DEFAULT_IGNORED_DIRS = {
    ".git",
    ".next",
    ".pnpm-store",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "venv",
}

DEFAULT_IGNORED_PREFIXES = (
    "docs/_root_archive/",
    "tools/_local/",
)

UI_SIGNAL_DEPS = (
    "next",
    "react",
    "react-dom",
    "vite",
    "tailwindcss",
    "postcss",
    "autoprefixer",
    "styled-components",
    "@emotion/react",
    "@emotion/styled",
    "@radix-ui/react-dialog",
    "framer-motion",
)

TOOLING_SIGNAL_DEPS = (
    "eslint",
    "stylelint",
    "prettier",
    "typescript",
    "vitest",
    "jest",
    "@playwright/test",
    "cypress",
    "turbo",
    "storybook",
    "@storybook/react",
    "@storybook/nextjs",
)

NEXT_CONFIG_FILENAMES = (
    "next.config.js",
    "next.config.cjs",
    "next.config.mjs",
    "next.config.ts",
)

STORYBOOK_CONFIG_MARKERS = (
    ".storybook/main.js",
    ".storybook/main.cjs",
    ".storybook/main.mjs",
    ".storybook/main.ts",
    ".storybook/preview.js",
    ".storybook/preview.cjs",
    ".storybook/preview.mjs",
    ".storybook/preview.ts",
)

PLAYWRIGHT_CONFIG_FILENAMES = (
    "playwright.config.ts",
    "playwright.config.js",
    "playwright.config.mjs",
    "playwright.config.cjs",
)

TRAILING_COMMA_PATTERN = re.compile(r",(?=\s*[}\]])")
WORKSPACE_LINE_PATTERN = re.compile(r'^\s*-\s*["\']?([^"\']+)["\']?\s*$')
TOP_LEVEL_YAML_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\s*:")


@dataclass(frozen=True)
class WorkspaceInfo:
    path: str
    name: str
    segment: str
    private: bool
    scripts: Tuple[str, ...]
    dependencies: Tuple[str, ...]
    dev_dependencies: Tuple[str, ...]
    peer_dependencies: Tuple[str, ...]
    tags: Tuple[str, ...]


def to_posix(path: Path) -> str:
    return path.as_posix()


def normalize_rel_path(repo_root: Path, target: Path) -> str:
    return to_posix(target.resolve().relative_to(repo_root.resolve()))


def try_normalize_rel_path(repo_root: Path, target: Path) -> str | None:
    try:
        return normalize_rel_path(repo_root, target)
    except ValueError:
        return None


def should_skip_rel_path(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in DEFAULT_IGNORED_PREFIXES)


def iter_repo_files(repo_root: Path) -> Iterable[Path]:
    root = repo_root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_dir = to_posix(current.relative_to(root)) if current != root else ""
        dirnames[:] = sorted(
            entry
            for entry in dirnames
            if entry not in DEFAULT_IGNORED_DIRS
            and not should_skip_rel_path(f"{rel_dir}/{entry}" if rel_dir else entry)
        )
        for filename in sorted(filenames):
            file_path = current / filename
            rel = try_normalize_rel_path(root, file_path)
            if rel is None:
                continue
            if should_skip_rel_path(rel):
                continue
            yield file_path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def remove_json_comments(raw: str) -> str:
    chars: List[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(raw):
        ch = raw[i]
        nxt = raw[i + 1] if i + 1 < len(raw) else ""
        if in_string:
            chars.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            chars.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            i += 2
            while i < len(raw) and raw[i] not in ("\n", "\r"):
                i += 1
            continue

        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(raw) and not (raw[i] == "*" and raw[i + 1] == "/"):
                i += 1
            i += 2
            continue

        chars.append(ch)
        i += 1

    return "".join(chars)


def load_json_like(path: Path) -> Any:
    raw = read_text(path)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        without_comments = remove_json_comments(raw)
        without_trailing_commas = TRAILING_COMMA_PATTERN.sub("", without_comments)
        return json.loads(without_trailing_commas)


def parse_workspace_patterns(path: Path) -> List[str]:
    if not path.exists():
        return []

    text = read_text(path)
    patterns: List[str] = []
    in_packages_block = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("packages:"):
            in_packages_block = True
            continue

        if in_packages_block and TOP_LEVEL_YAML_KEY_PATTERN.match(stripped):
            break

        if in_packages_block:
            match = WORKSPACE_LINE_PATTERN.match(line)
            if match:
                value = match.group(1).strip()
                if value and value not in patterns:
                    patterns.append(value)

    return patterns


def discover_workspace_dirs(repo_root: Path, patterns: Sequence[str]) -> List[Path]:
    discovered: Dict[str, Path] = {}
    for pattern in patterns:
        for candidate in sorted(repo_root.glob(pattern)):
            if not candidate.is_dir():
                continue
            package_json = candidate / "package.json"
            if not package_json.exists():
                continue
            rel = normalize_rel_path(repo_root, candidate)
            discovered[rel] = candidate
    return [discovered[key] for key in sorted(discovered)]


def gather_package_dependencies(package_json: Dict[str, Any], key: str) -> Tuple[str, ...]:
    section = package_json.get(key, {})
    if not isinstance(section, dict):
        return ()
    return tuple(sorted(name for name in section if isinstance(name, str)))


def infer_workspace_tags(workspace_path: Path, manifest: Dict[str, Any], segment: str) -> Tuple[str, ...]:
    deps = set(gather_package_dependencies(manifest, "dependencies"))
    dev_deps = set(gather_package_dependencies(manifest, "devDependencies"))
    peer_deps = set(gather_package_dependencies(manifest, "peerDependencies"))
    all_deps = deps | dev_deps | peer_deps

    tags: List[str] = []
    scripts = manifest.get("scripts", {})
    script_names = set(scripts.keys()) if isinstance(scripts, dict) else set()

    has_next_config = any((workspace_path / filename).exists() for filename in NEXT_CONFIG_FILENAMES)
    has_next = "next" in all_deps or has_next_config or (workspace_path / "next-env.d.ts").exists()
    has_vite = "vite" in all_deps or (workspace_path / "vite.config.ts").exists() or (workspace_path / "vite.config.js").exists()
    has_tailwind = "tailwindcss" in all_deps or any(workspace_path.glob("tailwind.config.*"))
    has_storybook = any("storybook" in dep for dep in all_deps) or any((workspace_path / marker).exists() for marker in STORYBOOK_CONFIG_MARKERS)
    has_playwright = "@playwright/test" in all_deps or any((workspace_path / filename).exists() for filename in PLAYWRIGHT_CONFIG_FILENAMES)
    has_vitest = "vitest" in all_deps or any(workspace_path.glob("vitest.config.*"))

    if segment == "apps":
        tags.append("application")
    elif segment == "packages":
        tags.append("library")
    elif segment == "services":
        tags.append("service")
    elif segment == "tools":
        tags.append("tooling")
    else:
        tags.append("workspace")

    if has_next:
        tags.append("nextjs")
    if has_vite:
        tags.append("vite")
    if has_tailwind:
        tags.append("tailwind")
    if has_storybook:
        tags.append("storybook")
    if has_playwright:
        tags.append("playwright")
    if has_vitest:
        tags.append("vitest")
    if "lint" in script_names:
        tags.append("lint-script")
    if "typecheck" in script_names:
        tags.append("typecheck-script")
    if "test" in script_names:
        tags.append("test-script")

    return tuple(sorted(set(tags)))


def parse_workspace_info(repo_root: Path, workspace_path: Path) -> WorkspaceInfo:
    package_path = workspace_path / "package.json"
    manifest = load_json_like(package_path)
    if not isinstance(manifest, dict):
        raise ValueError(f"invalid package.json object at {package_path}")

    rel_path = normalize_rel_path(repo_root, workspace_path)
    segment = rel_path.split("/", 1)[0]
    scripts = manifest.get("scripts", {})
    script_names = tuple(sorted(k for k in scripts.keys())) if isinstance(scripts, dict) else ()

    name = manifest.get("name")
    private = bool(manifest.get("private", False))
    if not isinstance(name, str) or not name:
        name = rel_path

    return WorkspaceInfo(
        path=rel_path,
        name=name,
        segment=segment,
        private=private,
        scripts=script_names,
        dependencies=gather_package_dependencies(manifest, "dependencies"),
        dev_dependencies=gather_package_dependencies(manifest, "devDependencies"),
        peer_dependencies=gather_package_dependencies(manifest, "peerDependencies"),
        tags=infer_workspace_tags(workspace_path, manifest, segment),
    )


def discover_tsconfigs(repo_root: Path) -> Dict[str, Dict[str, Any]]:
    tsconfigs: Dict[str, Dict[str, Any]] = {}
    for path in iter_repo_files(repo_root):
        name = path.name
        if not name.startswith("tsconfig") or path.suffix.lower() != ".json":
            continue
        rel = normalize_rel_path(repo_root, path)
        try:
            parsed = load_json_like(path)
            if not isinstance(parsed, dict):
                raise ValueError("tsconfig does not contain an object root")
            compiler = parsed.get("compilerOptions", {})
            if not isinstance(compiler, dict):
                compiler = {}
            path_aliases = compiler.get("paths", {})
            tsconfigs[rel] = {
                "extends": parsed.get("extends"),
                "composite": bool(compiler.get("composite", False)),
                "module": compiler.get("module"),
                "moduleResolution": compiler.get("moduleResolution"),
                "jsx": compiler.get("jsx"),
                "target": compiler.get("target"),
                "baseUrl": compiler.get("baseUrl"),
                "pathsAliasCount": len(path_aliases) if isinstance(path_aliases, dict) else 0,
                "includeCount": len(parsed.get("include", [])) if isinstance(parsed.get("include", []), list) else 0,
                "referencesCount": len(parsed.get("references", []))
                if isinstance(parsed.get("references", []), list)
                else 0,
            }
        except Exception as exc:  # noqa: BLE001
            tsconfigs[rel] = {"error": str(exc)}
    return dict(sorted(tsconfigs.items()))


def build_file_stats(repo_root: Path) -> Dict[str, Any]:
    extension_counter: Counter[str] = Counter()
    top_level_counter: Counter[str] = Counter()
    total_files = 0

    for path in iter_repo_files(repo_root):
        rel = normalize_rel_path(repo_root, path)
        top_level = rel.split("/", 1)[0] if "/" in rel else "."
        extension = path.suffix.lower() if path.suffix else "<none>"
        extension_counter[extension] += 1
        top_level_counter[top_level] += 1
        total_files += 1

    top_extensions = sorted(extension_counter.items(), key=lambda item: (-item[1], item[0]))[:25]
    return {
        "totalFiles": total_files,
        "topLevelCounts": dict(sorted(top_level_counter.items())),
        "topExtensions": [{"extension": ext, "count": count} for ext, count in top_extensions],
    }


def aggregate_dependency_signals(workspaces: Sequence[WorkspaceInfo], signals: Sequence[str]) -> List[Dict[str, Any]]:
    hits: Dict[str, List[str]] = defaultdict(list)
    for workspace in workspaces:
        all_deps = set(workspace.dependencies) | set(workspace.dev_dependencies) | set(workspace.peer_dependencies)
        for signal in signals:
            if signal in all_deps:
                hits[signal].append(workspace.path)

    rows: List[Dict[str, Any]] = []
    for signal in sorted(hits):
        rows.append(
            {
                "name": signal,
                "workspaceCount": len(hits[signal]),
                "workspaces": sorted(hits[signal]),
            }
        )
    return rows


def detect_repo_config_files(repo_root: Path) -> Dict[str, bool]:
    markers = {
        "eslintConfig": ("eslint.config.js", "eslint.config.cjs", "eslint.config.mjs"),
        "prettierConfig": ("prettier.config.js", "prettier.config.cjs", "prettier.config.mjs"),
        "stylelintConfig": (
            ".stylelintrc",
            ".stylelintrc.json",
            ".stylelintrc.cjs",
            "stylelint.config.js",
            "stylelint.config.cjs",
            "stylelint.config.mjs",
        ),
        "playwrightConfig": PLAYWRIGHT_CONFIG_FILENAMES,
    }
    result: Dict[str, bool] = {}
    for key, filenames in markers.items():
        result[key] = any((repo_root / filename).exists() for filename in filenames)
    return result


def detect_storybook_presence(repo_root: Path) -> bool:
    for marker in STORYBOOK_CONFIG_MARKERS:
        if (repo_root / marker).exists():
            return True
    return False


def normalize_dep_name(dep: str) -> str:
    if dep.startswith("@"):
        return dep
    return dep.split("/", 1)[0]


def build_turbo_probe(repo_root: Path, root_package: Dict[str, Any]) -> Dict[str, Any]:
    turbo_path = repo_root / "turbo.json"
    if not turbo_path.exists():
        return {"present": False, "error": "turbo.json not found"}

    turbo = load_json_like(turbo_path)
    if not isinstance(turbo, dict):
        return {"present": True, "error": "turbo.json is not an object"}

    tasks = turbo.get("tasks", {})
    if not isinstance(tasks, dict):
        return {"present": True, "error": "turbo.json tasks is not an object"}

    root_scripts = root_package.get("scripts", {})
    if not isinstance(root_scripts, dict):
        root_scripts = {}

    task_names = set(tasks.keys())
    task_rows: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []

    for task_name in sorted(task_names):
        config = tasks.get(task_name, {})
        if not isinstance(config, dict):
            config = {}

        outputs = config.get("outputs", [])
        if not isinstance(outputs, list):
            outputs = []
        outputs = [str(item) for item in outputs]
        outputs_sorted = sorted(outputs)

        depends_on = config.get("dependsOn", [])
        if not isinstance(depends_on, list):
            depends_on = []
        depends_on = [str(item) for item in depends_on]

        persistent = bool(config.get("persistent", False))
        cache = config.get("cache", True)

        unknown_dependencies = []
        for dep in depends_on:
            normalized = dep[1:] if dep.startswith("^") else dep
            if normalized and normalized not in task_names and not normalized.startswith("//"):
                unknown_dependencies.append(dep)

        if persistent and outputs_sorted:
            issues.append(
                {
                    "task": task_name,
                    "code": "PERSISTENT_TASK_HAS_OUTPUTS",
                    "detail": "Persistent tasks should not declare cached outputs.",
                }
            )

        if "build" in task_name and not outputs_sorted:
            issues.append(
                {
                    "task": task_name,
                    "code": "BUILD_TASK_WITHOUT_OUTPUTS",
                    "detail": "Build-like task has no outputs configured.",
                }
            )

        if task_name.startswith("ci:") and "cache" not in config:
            issues.append(
                {
                    "task": task_name,
                    "code": "CI_TASK_CACHE_IMPLICIT",
                    "detail": "CI task does not define cache policy explicitly.",
                }
            )

        if unknown_dependencies:
            issues.append(
                {
                    "task": task_name,
                    "code": "UNKNOWN_DEPENDENCY",
                    "detail": "Task depends on non-existent task names.",
                    "dependsOn": sorted(unknown_dependencies),
                }
            )

        task_rows.append(
            {
                "name": task_name,
                "dependsOn": sorted(depends_on),
                "outputs": outputs_sorted,
                "cache": cache,
                "persistent": persistent,
                "hasRootScript": task_name in root_scripts or f"turbo:{task_name}" in root_scripts,
            }
        )

    return {
        "present": True,
        "globalDependencies": sorted(str(item) for item in turbo.get("globalDependencies", []))
        if isinstance(turbo.get("globalDependencies", []), list)
        else [],
        "taskCount": len(task_rows),
        "tasks": task_rows,
        "issueCount": len(issues),
        "issues": sorted(issues, key=lambda item: (item.get("task", ""), item.get("code", ""))),
    }


def summarize_segments(workspaces: Sequence[WorkspaceInfo]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[str]] = defaultdict(list)
    for workspace in workspaces:
        grouped[workspace.segment].append(workspace.path)
    rows: List[Dict[str, Any]] = []
    for segment in sorted(grouped):
        rows.append(
            {
                "segment": segment,
                "count": len(grouped[segment]),
                "workspaces": sorted(grouped[segment]),
            }
        )
    return rows


def collect_next_apps(workspaces: Sequence[WorkspaceInfo]) -> List[str]:
    result = [workspace.path for workspace in workspaces if "nextjs" in workspace.tags and workspace.segment == "apps"]
    return sorted(result)


def collect_workspace_rows(workspaces: Sequence[WorkspaceInfo]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for workspace in sorted(workspaces, key=lambda item: item.path):
        rows.append(
            {
                "path": workspace.path,
                "name": workspace.name,
                "segment": workspace.segment,
                "private": workspace.private,
                "tags": list(workspace.tags),
                "scripts": list(workspace.scripts),
                "dependencies": list(workspace.dependencies),
                "devDependencies": list(workspace.dev_dependencies),
                "peerDependencies": list(workspace.peer_dependencies),
            }
        )
    return rows


def build_repo_map(repo_root: Path) -> Dict[str, Any]:
    pnpm_workspace_path = repo_root / "pnpm-workspace.yaml"
    patterns = parse_workspace_patterns(pnpm_workspace_path)
    workspace_dirs = discover_workspace_dirs(repo_root, patterns)
    workspaces = [parse_workspace_info(repo_root, path) for path in workspace_dirs]

    root_package_path = repo_root / "package.json"
    root_package = load_json_like(root_package_path) if root_package_path.exists() else {}
    if not isinstance(root_package, dict):
        root_package = {}

    repo_map = {
        "schemaVersion": 1,
        "repoRoot": ".",
        "workspacePatterns": patterns,
        "workspaceCount": len(workspaces),
        "segments": summarize_segments(workspaces),
        "workspaces": collect_workspace_rows(workspaces),
        "nextApps": collect_next_apps(workspaces),
        "signals": {
            "uiStack": aggregate_dependency_signals(workspaces, UI_SIGNAL_DEPS),
            "tooling": aggregate_dependency_signals(workspaces, TOOLING_SIGNAL_DEPS),
            "rootConfigFiles": detect_repo_config_files(repo_root),
            "storybookPresent": detect_storybook_presence(repo_root)
            or any("storybook" in workspace.tags for workspace in workspaces),
            "playwrightPresent": any("playwright" in workspace.tags for workspace in workspaces),
        },
        "tsconfigs": discover_tsconfigs(repo_root),
        "fileStats": build_file_stats(repo_root),
        "turboProbe": build_turbo_probe(repo_root, root_package),
    }
    return repo_map


def md_header(title: str) -> str:
    return f"## {title}\n"


def format_markdown(repo_map: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# BASELINE_DISCOVERY")
    lines.append("")
    lines.append("Deterministic scan generated by `tools/hos/discovery/repo_probe.py`.")
    lines.append("")

    lines.append(md_header("Summary").rstrip())
    lines.append(f"- Workspace patterns: {len(repo_map.get('workspacePatterns', []))}")
    lines.append(f"- Workspaces discovered: {repo_map.get('workspaceCount', 0)}")
    lines.append(f"- Next.js apps: {len(repo_map.get('nextApps', []))}")
    lines.append(f"- Total files scanned (ignored dirs excluded): {repo_map.get('fileStats', {}).get('totalFiles', 0)}")
    lines.append("")

    lines.append(md_header("Segments").rstrip())
    for segment in repo_map.get("segments", []):
        lines.append(f"- `{segment['segment']}`: {segment['count']} workspace(s)")
    lines.append("")

    lines.append(md_header("Next.js Apps").rstrip())
    next_apps = repo_map.get("nextApps", [])
    if next_apps:
        for path in next_apps:
            lines.append(f"- `{path}`")
    else:
        lines.append("- None detected")
    lines.append("")

    lines.append(md_header("UI + Tooling Signals").rstrip())
    ui_stack = repo_map.get("signals", {}).get("uiStack", [])
    tooling = repo_map.get("signals", {}).get("tooling", [])
    lines.append("- UI stack signals:")
    if ui_stack:
        for row in ui_stack:
            lines.append(f"  - `{row['name']}` in {row['workspaceCount']} workspace(s)")
    else:
        lines.append("  - None")
    lines.append("- Tooling signals:")
    if tooling:
        for row in tooling:
            lines.append(f"  - `{row['name']}` in {row['workspaceCount']} workspace(s)")
    else:
        lines.append("  - None")
    lines.append("")

    lines.append(md_header("Turbo Probe").rstrip())
    turbo_probe = repo_map.get("turboProbe", {})
    if not turbo_probe.get("present", False):
        lines.append(f"- Turbo probe unavailable: {turbo_probe.get('error', 'unknown error')}")
    else:
        lines.append(f"- Tasks: {turbo_probe.get('taskCount', 0)}")
        lines.append(f"- Issues: {turbo_probe.get('issueCount', 0)}")
        if turbo_probe.get("issues"):
            lines.append("- Issue details:")
            for issue in turbo_probe["issues"]:
                task = issue.get("task", "?")
                code = issue.get("code", "?")
                detail = issue.get("detail", "")
                lines.append(f"  - `{task}` `{code}`: {detail}")
    lines.append("")

    lines.append(md_header("TSConfig Patterns").rstrip())
    tsconfigs = repo_map.get("tsconfigs", {})
    lines.append(f"- TSConfig files: {len(tsconfigs)}")
    for path, config in tsconfigs.items():
        if "error" in config:
            lines.append(f"- `{path}`: ERROR `{config['error']}`")
            continue
        module_res = config.get("moduleResolution", "n/a")
        jsx = config.get("jsx", "n/a")
        alias_count = config.get("pathsAliasCount", 0)
        lines.append(f"- `{path}`: moduleResolution={module_res}, jsx={jsx}, pathsAliasCount={alias_count}")
    lines.append("")

    lines.append(md_header("Top-Level File Distribution").rstrip())
    top_level_counts = repo_map.get("fileStats", {}).get("topLevelCounts", {})
    for key in sorted(top_level_counts):
        lines.append(f"- `{key}`: {top_level_counts[key]}")
    lines.append("")

    lines.append(md_header("Top Extensions").rstrip())
    for item in repo_map.get("fileStats", {}).get("topExtensions", []):
        lines.append(f"- `{item['extension']}`: {item['count']}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic repository scanner for HITECH OS.")
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument(
        "--md-out",
        default="docs/system/BASELINE_DISCOVERY.md",
        help="Markdown report output path (relative to repo unless absolute).",
    )
    parser.add_argument(
        "--json-out",
        default="docs/system/REPO_MAP.json",
        help="JSON map output path (relative to repo unless absolute).",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print markdown report to stdout after writing outputs.",
    )
    return parser.parse_args(argv)


def resolve_output_path(repo_root: Path, path_arg: str) -> Path:
    candidate = Path(path_arg)
    if candidate.is_absolute():
        return candidate
    return (repo_root / candidate).resolve()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = Path(args.repo).resolve()
    if not repo_root.exists():
        raise FileNotFoundError(f"repository root does not exist: {repo_root}")

    repo_map = build_repo_map(repo_root)
    markdown = format_markdown(repo_map)

    md_out = resolve_output_path(repo_root, args.md_out)
    json_out = resolve_output_path(repo_root, args.json_out)

    write_text(md_out, markdown)
    write_text(json_out, json.dumps(repo_map, indent=2, sort_keys=True) + "\n")

    if args.stdout:
        sys.stdout.write(markdown)
    else:
        sys.stdout.write(
            f"[repo_probe] wrote {to_posix(md_out)} and {to_posix(json_out)} "
            f"(workspaces={repo_map.get('workspaceCount', 0)} files={repo_map.get('fileStats', {}).get('totalFiles', 0)})\n"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

DEFAULT_IGNORED_DIRS = {
    ".git",
    ".turbo",
    ".venv",
    "_attic",
    "_local",
    "_reports",
    "_triage",
    "artifacts",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "logs",
    "node_modules",
    "runs",
    "venv",
    "worktrees",
}

SPECIFIER_PATTERN = re.compile(
    r"""
    (?P<lead>
        import\s+(?:type\s+)?(?:[\w*\s{},]+\s+from\s+)?|
        export\s+(?:type\s+)?(?:\*\s+from\s+|\{[^}]*\}\s+from\s+)|
        import\s*\(
    )
    ["'](?P<specifier>[^"']+)["']
    """,
    re.VERBOSE | re.MULTILINE,
)


@dataclass(frozen=True)
class Violation:
    file: str
    line: int
    specifier: str


def to_posix(path: Path) -> str:
    return path.as_posix()


def load_allowlist(config_path: Path) -> Sequence[Dict[str, str]]:
    if not config_path.exists():
        raise FileNotFoundError(f"allowlist config not found: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    allow = data.get("allow", [])
    if not isinstance(allow, list):
        raise ValueError("allowlist config must contain an array field named 'allow'")

    normalized: List[Dict[str, str]] = []
    for entry in allow:
        if not isinstance(entry, dict):
            raise ValueError("allowlist entries must be objects")
        file_glob = entry.get("file_glob")
        specifier_glob = entry.get("specifier_glob", "*.js")
        if not isinstance(file_glob, str) or not isinstance(specifier_glob, str):
            raise ValueError("allowlist entries require string fields: file_glob, specifier_glob")
        normalized.append({"file_glob": file_glob, "specifier_glob": specifier_glob})
    return normalized


def collect_source_files(repo_root: Path) -> List[Path]:
    files: List[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in DEFAULT_IGNORED_DIRS for part in path.parts):
            continue
        if any(part.startswith("_backup") for part in path.parts):
            continue
        if path.suffix not in {".ts", ".tsx", ".mts", ".cts"}:
            continue
        if path.name.endswith(".d.ts"):
            continue
        rel_posix = to_posix(path.relative_to(repo_root))
        if "/src/" not in rel_posix and not rel_posix.startswith("src/"):
            continue
        files.append(path)
    files.sort(key=lambda value: to_posix(value.relative_to(repo_root)))
    return files


def is_relative_js_specifier(specifier: str) -> bool:
    return specifier.startswith(("./", "../")) and specifier.endswith(".js")


def is_allowed(rel_file: str, specifier: str, allowlist: Sequence[Dict[str, str]]) -> bool:
    for entry in allowlist:
        if fnmatch(rel_file, entry["file_glob"]) and fnmatch(specifier, entry["specifier_glob"]):
            return True
    return False


def line_of_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_file(repo_root: Path, file_path: Path, allowlist: Sequence[Dict[str, str]]) -> List[Violation]:
    rel_file = to_posix(file_path.relative_to(repo_root))
    text = file_path.read_text(encoding="utf-8")
    violations: List[Violation] = []
    for match in SPECIFIER_PATTERN.finditer(text):
        specifier = match.group("specifier")
        if not is_relative_js_specifier(specifier):
            continue
        if is_allowed(rel_file, specifier, allowlist):
            continue
        violations.append(
            Violation(
                file=rel_file,
                line=line_of_offset(text, match.start("specifier")),
                specifier=specifier,
            )
        )
    return violations


def scan_repo(repo_root: Path, allowlist: Sequence[Dict[str, str]]) -> Tuple[List[Violation], int]:
    files = collect_source_files(repo_root)
    violations: List[Violation] = []
    for file_path in files:
        violations.extend(scan_file(repo_root, file_path, allowlist))
    violations.sort(key=lambda item: (item.file, item.line, item.specifier))
    return violations, len(files)


def as_report(repo_root: Path, violations: Iterable[Violation], scanned_files: int, config: Path) -> Dict[str, Any]:
    payload = {
        "guard": "no_js_src_imports",
        "repo": to_posix(repo_root),
        "config": to_posix(config),
        "scannedFiles": scanned_files,
        "violationCount": 0,
        "violations": [],
    }
    for item in violations:
        payload["violations"].append({"file": item.file, "line": item.line, "specifier": item.specifier})
    payload["violationCount"] = len(payload["violations"])
    return payload


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail if TS source imports relative .js modules without allowlist.")
    parser.add_argument("--repo", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--config",
        default="tools/codex/guards/no_js_src_imports.allowlist.json",
        help="Allowlist JSON path (relative to repo unless absolute).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report only.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = Path(args.repo).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()

    allowlist = load_allowlist(config_path)
    violations, scanned_files = scan_repo(repo_root, allowlist)
    report = as_report(repo_root, violations, scanned_files, config_path)

    if args.json:
        sys.stdout.write(json.dumps(report, sort_keys=True, indent=2) + "\n")
    else:
        if report["violationCount"] == 0:
            sys.stdout.write(
                f"[guard:no-js-src-imports] PASS scanned={report['scannedFiles']} violations=0 config={report['config']}\n"
            )
        else:
            sys.stdout.write(
                f"[guard:no-js-src-imports] FAIL scanned={report['scannedFiles']} violations={report['violationCount']} config={report['config']}\n"
            )
            for item in report["violations"]:
                sys.stdout.write(f" - {item['file']}:{item['line']} imports {item['specifier']}\n")

    return 0 if report["violationCount"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

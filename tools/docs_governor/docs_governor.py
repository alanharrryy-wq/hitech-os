#!/usr/bin/env python3
"""Documentation governance checks for Hitech repositories."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


ALLOWED_ROOT_DOC_FILES = {
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE",
    "CLA.md",
}

ALLOWED_DOC_TOP_LEVEL_DIRS = {
    "adr",
    "runbooks",
    "playbooks",
    "security",
    "architecture",
    "releases",
    "_generated",
}

DISALLOWED_DOC_DIRS = {
    "docs2",
    "documentation",
    "wiki",
    "notes",
    "design_docs",
    "random_docs",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "_codex_worktrees",
}

DOC_EXTENSIONS = {".md", ".rst", ".adoc", ".txt"}
ADR_PATTERN = re.compile(r"^(\d{4})-[a-z0-9][a-z0-9-]*\.md$")
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SIMILARITY_THRESHOLD = 70.0
MAX_DOC_DEPTH = 5


@dataclass
class Finding:
    rule: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"rule": self.rule, "path": self.path, "message": self.message}


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def timestamp_for_filename() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def normalize_relpath(path_text: str) -> Path:
    return Path(path_text.replace("\\", "/"))


def collect_repo_files_and_disallowed_dirs(
    repo_root: Path,
) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    disallowed_dirs: list[Path] = []

    for current_root, dir_names, file_names in os.walk(repo_root):
        current = Path(current_root)
        try:
            rel_dir = current.relative_to(repo_root)
        except ValueError:
            continue

        kept_dirs: list[str] = []
        for directory in sorted(dir_names):
            rel_candidate = directory if rel_dir == Path(".") else str(rel_dir / directory)
            rel_candidate_path = normalize_relpath(rel_candidate)
            if directory in DISALLOWED_DOC_DIRS:
                disallowed_dirs.append(rel_candidate_path)
            if directory in SKIP_DIRS:
                continue
            kept_dirs.append(directory)
        dir_names[:] = kept_dirs

        for file_name in sorted(file_names):
            rel_file = Path(file_name) if rel_dir == Path(".") else rel_dir / file_name
            files.append(normalize_relpath(rel_file.as_posix()))

    return sorted(files, key=lambda p: p.as_posix()), sorted(
        disallowed_dirs, key=lambda p: p.as_posix()
    )


def is_doc_file(rel_path: Path) -> bool:
    if not rel_path.parts:
        return False
    if rel_path.parts[0].lower() == "docs":
        return True
    if rel_path.name in ALLOWED_ROOT_DOC_FILES:
        return True
    return rel_path.suffix.lower() in DOC_EXTENSIONS


def get_new_files(repo_root: Path, base_ref: str | None) -> tuple[list[Path], list[str]]:
    warnings: list[str] = []
    new_files: set[Path] = set()

    if base_ref:
        result = run_git(repo_root, ["diff", "--name-only", "--diff-filter=A", f"{base_ref}...HEAD"])
        if result.returncode != 0:
            warnings.append(
                f"git diff failed for base ref '{base_ref}', falling back to git status."
            )
        else:
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                new_files.add(normalize_relpath(line))

    status_result = run_git(repo_root, ["status", "--porcelain"])
    if status_result.returncode != 0:
        warnings.append("git status failed; unable to detect new files.")
        return sorted(new_files, key=lambda p: p.as_posix()), warnings

    for raw in status_result.stdout.splitlines():
        if len(raw) < 3:
            continue
        status = raw[:2]
        path_part = raw[3:].strip()
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1]

        is_added = status == "??" or "A" in status
        if not is_added:
            continue
        new_files.add(normalize_relpath(path_part))

    return sorted(new_files, key=lambda p: p.as_posix()), warnings


def docs_depth(rel_path: Path) -> int:
    if len(rel_path.parts) < 2 or rel_path.parts[0].lower() != "docs":
        return 0
    # docs/<dir1>/<dir2>/file.md -> depth 2
    return max(0, len(rel_path.parts) - 2)


def relative_paths_to_strings(paths: list[Path]) -> list[str]:
    return [p.as_posix() for p in sorted(paths, key=lambda item: item.as_posix())]


def check_doc_locations(
    new_docs: list[Path], failures: list[Finding], allowed_root_lower: set[str]
) -> None:
    for doc in new_docs:
        parts = doc.parts
        if not parts:
            continue

        if len(parts) == 1:
            if doc.name.lower() in allowed_root_lower:
                continue
            failures.append(
                Finding(
                    rule="allowed_locations",
                    path=doc.as_posix(),
                    message=(
                        "Root documentation files must be one of: "
                        + ", ".join(sorted(ALLOWED_ROOT_DOC_FILES))
                        + "."
                    ),
                )
            )
            continue

        if parts[0].lower() == "docs":
            if len(parts) == 2:
                continue

            top_level = parts[1].lower()
            if top_level not in ALLOWED_DOC_TOP_LEVEL_DIRS:
                failures.append(
                    Finding(
                        rule="allowed_locations",
                        path=doc.as_posix(),
                        message=(
                            "Documentation under docs/ must be inside: docs/, docs/adr/, "
                            "docs/runbooks/, docs/playbooks/, docs/security/, "
                            "docs/architecture/, docs/releases/, or docs/_generated/<RUN_ID>/."
                        ),
                    )
                )
                continue

            if top_level == "_generated":
                if len(parts) < 4:
                    failures.append(
                        Finding(
                            rule="generated_sandbox",
                            path=doc.as_posix(),
                            message="Generated docs must use docs/_generated/<RUN_ID>/... structure.",
                        )
                    )
                    continue
                run_id = parts[2]
                if not RUN_ID_PATTERN.match(run_id):
                    failures.append(
                        Finding(
                            rule="generated_sandbox",
                            path=doc.as_posix(),
                            message=(
                                "Generated docs RUN_ID contains invalid characters. "
                                "Allowed: letters, numbers, dot, underscore, dash."
                            ),
                        )
                    )
            continue

        failures.append(
            Finding(
                rule="allowed_locations",
                path=doc.as_posix(),
                message="New documentation must live in docs/ or be an allowed root doc file.",
            )
        )


def check_adr_structure(repo_root: Path, all_docs: list[Path], failures: list[Finding]) -> None:
    adr_readme = repo_root / "docs" / "adr" / "README.md"
    adr_template = repo_root / "docs" / "adr" / "0000-template.md"
    if not adr_readme.exists():
        failures.append(
            Finding(
                rule="adr_structure",
                path="docs/adr/README.md",
                message="Required ADR README is missing.",
            )
        )
    if not adr_template.exists():
        failures.append(
            Finding(
                rule="adr_structure",
                path="docs/adr/0000-template.md",
                message="Required ADR template is missing.",
            )
        )

    adr_numbers: set[int] = set()
    for doc in all_docs:
        if len(doc.parts) < 3 or doc.parts[0].lower() != "docs" or doc.parts[1].lower() != "adr":
            continue

        if len(doc.parts) != 3:
            failures.append(
                Finding(
                    rule="adr_structure",
                    path=doc.as_posix(),
                    message="ADR files must be directly under docs/adr/.",
                )
            )
            continue

        name = doc.name
        if name in {"README.md", "0000-template.md"}:
            continue

        match = ADR_PATTERN.match(name)
        if not match:
            failures.append(
                Finding(
                    rule="adr_structure",
                    path=doc.as_posix(),
                    message="ADR filename must match docs/adr/0001-title.md format.",
                )
            )
            continue

        number = int(match.group(1))
        if number == 0:
            failures.append(
                Finding(
                    rule="adr_structure",
                    path=doc.as_posix(),
                    message="ADR numbering starts at 0001. 0000 is reserved for the ADR template.",
                )
            )
            continue
        if number in adr_numbers:
            failures.append(
                Finding(
                    rule="adr_structure",
                    path=doc.as_posix(),
                    message=f"Duplicate ADR number detected: {number:04d}.",
                )
            )
            continue
        adr_numbers.add(number)


def check_duplicate_names(
    new_docs: list[Path], all_docs: list[Path], failures: list[Finding], warnings: list[Finding]
) -> None:
    existing_docs = [doc for doc in all_docs if doc not in new_docs]
    existing_file_names = {doc.name.lower() for doc in existing_docs}
    existing_stem_map: dict[str, set[str]] = {}
    for doc in existing_docs:
        key = doc.stem.lower()
        existing_stem_map.setdefault(key, set()).add(doc.name.lower())

    seen_new_file_names: set[str] = set()
    warned_pairs: set[tuple[str, str]] = set()
    for new_doc in sorted(new_docs, key=lambda p: p.as_posix()):
        new_file_name = new_doc.name.lower()
        new_stem = new_doc.stem.lower()

        if new_file_name in seen_new_file_names or new_file_name in existing_file_names:
            failures.append(
                Finding(
                    rule="duplicate_docs",
                    path=new_doc.as_posix(),
                    message="Document name already exists in repository.",
                )
            )
        seen_new_file_names.add(new_file_name)

        for existing_stem in sorted(existing_stem_map):
            if existing_stem == new_stem:
                continue
            score = SequenceMatcher(None, new_stem, existing_stem).ratio() * 100
            if score > SIMILARITY_THRESHOLD:
                pair_key = (new_file_name, existing_stem)
                if pair_key in warned_pairs:
                    continue
                warned_pairs.add(pair_key)
                warnings.append(
                    Finding(
                        rule="duplicate_similarity",
                        path=new_doc.as_posix(),
                        message=(
                            f"Document name similarity is {score:.1f}% with existing name "
                            f"'{existing_stem}'."
                        ),
                    )
                )


def check_doc_depth(all_docs: list[Path], failures: list[Finding]) -> None:
    for doc in all_docs:
        if not doc.parts or doc.parts[0].lower() != "docs":
            continue
        depth = docs_depth(doc)
        if depth > MAX_DOC_DEPTH:
            failures.append(
                Finding(
                    rule="docs_depth",
                    path=doc.as_posix(),
                    message=f"docs/ depth {depth} exceeds maximum allowed depth {MAX_DOC_DEPTH}.",
                )
            )


def check_generated_docs_sandbox(repo_root: Path, all_docs: list[Path], failures: list[Finding]) -> None:
    generated_root = repo_root / "docs" / "_generated"
    if not generated_root.exists():
        return

    if not generated_root.is_dir():
        failures.append(
            Finding(
                rule="generated_sandbox",
                path="docs/_generated",
                message="docs/_generated exists but is not a directory.",
            )
        )
        return

    run_dirs = [entry for entry in sorted(generated_root.iterdir())]
    for entry in run_dirs:
        rel = entry.relative_to(repo_root).as_posix()
        if entry.is_file():
            failures.append(
                Finding(
                    rule="generated_sandbox",
                    path=rel,
                    message="Files are not allowed directly under docs/_generated/.",
                )
            )
            continue
        if not RUN_ID_PATTERN.match(entry.name):
            failures.append(
                Finding(
                    rule="generated_sandbox",
                    path=rel,
                    message=(
                        "RUN_ID directory name contains invalid characters. "
                        "Allowed: letters, numbers, dot, underscore, dash."
                    ),
                )
            )
        index_file = entry / "index.md"
        if not index_file.exists() or not index_file.is_file():
            failures.append(
                Finding(
                    rule="generated_sandbox",
                    path=rel,
                    message="Each docs/_generated/<RUN_ID>/ folder must contain index.md.",
                )
            )

    for doc in all_docs:
        if len(doc.parts) >= 2 and doc.parts[0].lower() == "docs" and doc.parts[1] == "_generated":
            if len(doc.parts) < 4:
                failures.append(
                    Finding(
                        rule="generated_sandbox",
                        path=doc.as_posix(),
                        message="Generated docs must use docs/_generated/<RUN_ID>/... structure.",
                    )
                )
                continue
            run_id = doc.parts[2]
            if not RUN_ID_PATTERN.match(run_id):
                failures.append(
                    Finding(
                        rule="generated_sandbox",
                        path=doc.as_posix(),
                        message=(
                            "Generated docs RUN_ID contains invalid characters. "
                            "Allowed: letters, numbers, dot, underscore, dash."
                        ),
                    )
                )


def check_documentation_limits(
    new_docs: list[Path], max_new_docs: int, failures: list[Finding]
) -> None:
    if len(new_docs) > max_new_docs:
        failures.append(
            Finding(
                rule="doc_limits",
                path="docs/",
                message=(
                    f"New documentation file count {len(new_docs)} exceeds max_new_docs "
                    f"limit {max_new_docs}."
                ),
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Hitech docs governance checks.")
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument(
        "--report-dir",
        default=None,
        help="Output directory for governance report JSON.",
    )
    parser.add_argument(
        "--base-ref",
        default=None,
        help="Optional git base ref for detecting new docs with git diff.",
    )
    parser.add_argument(
        "--max-new-docs",
        default=50,
        type=int,
        help="Maximum number of new documentation files allowed per run.",
    )
    return parser.parse_args()


def ensure_git_repo(repo_root: Path) -> list[Finding]:
    failures: list[Finding] = []
    if not repo_root.exists() or not repo_root.is_dir():
        failures.append(
            Finding(
                rule="repo_validity",
                path=str(repo_root),
                message="Repository path is missing or not a directory.",
            )
        )
        return failures
    if not (repo_root / ".git").exists():
        failures.append(
            Finding(
                rule="repo_validity",
                path=str(repo_root),
                message="Repository is not a valid git repository (.git not found).",
            )
        )
    return failures


def write_report(report: dict, report_dir: Path, repo_name: str) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{timestamp_for_filename()}_{repo_name}.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return report_path


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    report_dir = (
        Path(args.report_dir).resolve()
        if args.report_dir
        else (repo_root / "tools" / "docs_governor" / "reports").resolve()
    )
    start_time = utc_now_iso()

    failures: list[Finding] = ensure_git_repo(repo_root)
    warning_strings: list[str] = []
    warning_findings: list[Finding] = []
    all_files: list[Path] = []
    all_docs: list[Path] = []
    new_files: list[Path] = []
    new_docs: list[Path] = []
    disallowed_dirs: list[Path] = []

    if not failures:
        all_files, disallowed_dirs = collect_repo_files_and_disallowed_dirs(repo_root)
        all_docs = [path for path in all_files if is_doc_file(path)]
        new_files, git_warnings = get_new_files(repo_root, args.base_ref)
        warning_strings.extend(git_warnings)
        new_docs = [path for path in new_files if is_doc_file(path)]

        for bad_dir in disallowed_dirs:
            failures.append(
                Finding(
                    rule="disallowed_directories",
                    path=bad_dir.as_posix(),
                    message="Disallowed documentation directory detected.",
                )
            )

        check_doc_locations(
            new_docs=new_docs,
            failures=failures,
            allowed_root_lower={item.lower() for item in ALLOWED_ROOT_DOC_FILES},
        )
        check_adr_structure(repo_root=repo_root, all_docs=all_docs, failures=failures)
        check_duplicate_names(
            new_docs=new_docs,
            all_docs=all_docs,
            failures=failures,
            warnings=warning_findings,
        )
        check_doc_depth(all_docs=all_docs, failures=failures)
        check_generated_docs_sandbox(repo_root=repo_root, all_docs=all_docs, failures=failures)
        check_documentation_limits(
            new_docs=new_docs, max_new_docs=args.max_new_docs, failures=failures
        )

    end_time = utc_now_iso()
    repo_name = repo_root.name.lower() if repo_root.name else "repo"
    status = "fail" if failures else "pass"

    report = {
        "repo": str(repo_root),
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "new_docs": relative_paths_to_strings(new_docs),
        "all_docs_count": len(all_docs),
        "new_docs_count": len(new_docs),
        "violations": [item.as_dict() for item in sorted(failures, key=lambda f: (f.rule, f.path, f.message))],
        "warnings": [item.as_dict() for item in sorted(warning_findings, key=lambda w: (w.rule, w.path, w.message))],
        "tool_warnings": sorted(set(warning_strings)),
        "rules": {
            "allowed_doc_locations": [
                "docs/",
                "docs/adr/",
                "docs/runbooks/",
                "docs/playbooks/",
                "docs/security/",
                "docs/architecture/",
                "docs/releases/",
                "docs/_generated/<RUN_ID>/",
            ],
            "allowed_root_docs": sorted(ALLOWED_ROOT_DOC_FILES),
            "allowed_docs_top_level_dirs": sorted(ALLOWED_DOC_TOP_LEVEL_DIRS),
            "disallowed_dirs": sorted(DISALLOWED_DOC_DIRS),
            "similarity_warn_threshold": SIMILARITY_THRESHOLD,
            "docs_max_depth": MAX_DOC_DEPTH,
            "max_new_docs": args.max_new_docs,
        },
    }

    report_path = write_report(report, report_dir, repo_name)
    print(str(report_path))

    if failures:
        for violation in report["violations"]:
            print(
                f"[FAIL] {violation['rule']} :: {violation['path']} :: {violation['message']}"
            )
        return 1

    for warning in report["warnings"]:
        print(f"[WARN] {warning['rule']} :: {warning['path']} :: {warning['message']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

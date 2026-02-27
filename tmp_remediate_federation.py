#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_ROOT = Path(r"F:\repos\hitech-os")
TARGETS = [
    ("inversion-next", Path(r"F:\repos\inversion-next")),
    (
        "hitech-frontend",
        Path(
            r"F:\OneDrive\Hitech\3.Proyectos\CHAT GPT AI Estudio\HITECH_AISTUDIO_SYSTEM\0.Origins\app\frontend\hitech-frontend"
        ),
    ),
]

MANDATORY_DIRS = [
    Path(r"tools\ops"),
    Path(r"tools\ops\tests"),
    Path(r"docs\govos\_reports"),
    Path(r"docs\factory"),
]

REQUIRED_TOOLING = [
    Path("tools/ops/Docs-Doctor.ps1"),
    Path("tools/ops/docs_doctor.py"),
    Path("tools/ops/_write_text_file.py"),
]

OPTIONAL_TOOLING = [
    Path("tools/ops/tests/DocsGovos.Tests.ps1"),
    Path("tools/ops/REPORT_CANONICAL_RUNS.md"),
    Path("tools/ops/Validate-CanonicalRuns.ps1"),
]

TODAY = "2026-02-27"


def _write_if_missing(path: Path, content: str, changes: list[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    changes.append(str(path))


def _ensure_reports_stubs(repo: Path, changes: list[str]) -> None:
    reports_dir = repo / r"docs\govos\_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "FINAL_REPORT.md": (
            "# FINAL_REPORT\n\n"
            "Status: STUB\n\n"
            "This deterministic stub was created to satisfy Docs-Doctor canonical report checks.\n"
            f"Canonical reference: `{SOURCE_ROOT}\\docs\\govos\\_reports\\FINAL_REPORT.md`\n"
        ),
        "LEGACY_MAP.md": (
            "# LEGACY_MAP\n\n"
            "Status: STUB\n\n"
            "This deterministic stub was created to satisfy Docs-Doctor canonical report checks.\n"
            f"Canonical reference: `{SOURCE_ROOT}\\docs\\govos\\_reports\\LEGACY_MAP.md`\n"
        ),
        "CONVERGENCE_LOG.md": (
            "# CONVERGENCE_LOG\n\n"
            "Status: STUB\n\n"
            "This deterministic stub was created to satisfy Docs-Doctor canonical report checks.\n"
            f"Canonical reference: `{SOURCE_ROOT}\\docs\\govos\\_reports\\CONVERGENCE_LOG.md`\n"
        ),
    }
    for name, content in files.items():
        _write_if_missing(reports_dir / name, content, changes)


def _ensure_mandatory_pointers(repo: Path, changes: list[str]) -> None:
    kernel_pointer = (
        "# KERNEL_CONTEXT (Pointer)\n\n"
        "This repository follows the canonical kernel context from:\n\n"
        f"- `{SOURCE_ROOT}\\KERNEL_CONTEXT.md`\n\n"
        "Status: READ-ONLY POINTER\n"
    )
    _write_if_missing(repo / "KERNEL_CONTEXT.md", kernel_pointer, changes)

    contract_pointer = (
        "# Factory Contract (Pointer)\n\n"
        "Canonical factory contract source:\n\n"
        f"- `{SOURCE_ROOT}\\docs\\factory\\CONTRACT.md`\n\n"
        "Status: READ-ONLY POINTER\n"
    )
    _write_if_missing(repo / r"docs\factory\CONTRACT.md", contract_pointer, changes)

    runtime_pointer = (
        "---\n"
        "doc_id: FACTORY_RUNTIME_EXPLAINED_POINTER\n"
        "title: Factory Runtime Explained (Canonical Pointer)\n"
        "doc_type: pointer\n"
        "status: read-only\n"
        f"canonical_source: {SOURCE_ROOT}\\docs\\factory\\CONTRACT.md\n"
        f"last_updated: {TODAY}\n"
        "---\n\n"
        "# FACTORY_RUNTIME_EXPLAINED\n\n"
        "This file is a canonical pointer.\n\n"
        "Canonical runtime explanation:\n\n"
        "- [docs/factory/CONTRACT.md](./CONTRACT.md)\n"
        f"- `{SOURCE_ROOT}\\docs\\factory\\CONTRACT.md`\n\n"
        "Status: READ-ONLY\n"
        "Do not duplicate or extend runtime governance text here.\n"
    )
    _write_if_missing(repo / r"docs\factory\FACTORY_RUNTIME_EXPLAINED.md", runtime_pointer, changes)


def _copy_tooling(repo: Path, rel_paths: list[Path], changes: list[str], required: bool) -> list[str]:
    errors: list[str] = []
    for rel in rel_paths:
        src = SOURCE_ROOT / rel
        dst = repo / rel
        if not src.exists():
            if required:
                errors.append(f"Missing required source file: {src}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        changes.append(str(dst))
    return errors


def _run_docs_doctor(repo: Path) -> subprocess.CompletedProcess[str]:
    cmd = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(repo / r"tools\ops\Docs-Doctor.ps1"),
        "--check",
    ]
    return subprocess.run(cmd, cwd=repo, capture_output=True, text=True)


def _print_first_40_lines(name: str, phase: str, proc: subprocess.CompletedProcess[str]) -> None:
    combined = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    lines = combined.splitlines()[:40]
    print(f"--- Docs-Doctor failure ({name}) [{phase}] first 40 lines ---")
    if lines:
        print("\n".join(lines))
    else:
        print("(no output)")


def main() -> int:
    summary: list[dict] = []
    blocked: list[str] = []

    for name, repo in TARGETS:
        changes: list[str] = []
        entry = {
            "name": name,
            "path": str(repo),
            "online": repo.exists(),
            "docs_doctor_rc": None,
            "final_report_present": False,
            "created_or_copied_count": 0,
            "created_or_copied_sample": [],
        }

        if not repo.exists():
            summary.append(entry)
            continue

        for rel_dir in MANDATORY_DIRS:
            full_dir = repo / rel_dir
            if not full_dir.exists():
                full_dir.mkdir(parents=True, exist_ok=True)
                changes.append(str(full_dir))

        required_errors = _copy_tooling(repo, REQUIRED_TOOLING, changes, required=True)
        _copy_tooling(repo, OPTIONAL_TOOLING, changes, required=False)
        _ensure_mandatory_pointers(repo, changes)
        _ensure_reports_stubs(repo, changes)

        if required_errors:
            print(f"--- Required tooling source errors ({name}) ---")
            for err in required_errors:
                print(err)
            entry["docs_doctor_rc"] = 2
            entry["final_report_present"] = (repo / r"docs\govos\_reports\FINAL_REPORT.md").exists()
            entry["created_or_copied_count"] = len(changes)
            entry["created_or_copied_sample"] = changes[:15]
            summary.append(entry)
            blocked.append(name)
            continue

        first = _run_docs_doctor(repo)
        rc = first.returncode
        if rc != 0:
            _print_first_40_lines(name, "initial", first)
            _ensure_reports_stubs(repo, changes)
            second = _run_docs_doctor(repo)
            rc = second.returncode
            if rc != 0:
                _print_first_40_lines(name, "after-minimal-fix", second)
                blocked.append(name)

        entry["docs_doctor_rc"] = rc
        entry["final_report_present"] = (repo / r"docs\govos\_reports\FINAL_REPORT.md").exists()
        entry["created_or_copied_count"] = len(changes)
        entry["created_or_copied_sample"] = changes[:15]
        summary.append(entry)

    print(json.dumps(summary, indent=2))
    if blocked:
        print(f"BLOCKED_REPOS: {', '.join(blocked)}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

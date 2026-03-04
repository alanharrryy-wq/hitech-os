from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_FALLBACK_REPO = Path(r"F:\repos\hitech-os")
DEPRECATED_MARKER = "## Deprecated: Run-Scoped Worktrees (Do Not Use)"
RUN_ID_SEGMENT_RE = re.compile(r"^\d{8}(?:_\d+|_\d{6}_[A-Z0-9]{4})$")
NEW_RUN_ID_SEGMENT_RE = re.compile(r"^\d{8}_\d{6}_[A-Z0-9]{4}$")


@dataclass(frozen=True)
class RepoContext:
    repo_root: Path
    debug_dir: Path
    worktrees_root: Path


def _git_toplevel(start: Path) -> Path | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    if not value:
        return None
    return Path(value).resolve()


def _resolve_repo_root(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve(strict=False)
    for probe in (Path.cwd(), Path(__file__).resolve().parents[3]):
        detected = _git_toplevel(probe)
        if detected:
            return detected
    if DEFAULT_FALLBACK_REPO.exists():
        return DEFAULT_FALLBACK_REPO.resolve()
    raise RuntimeError("unable to resolve repo root")


def _ctx(explicit_repo_root: str | None = None) -> RepoContext:
    repo_root = _resolve_repo_root(explicit_repo_root)
    debug_dir = repo_root / "tools" / "codex" / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    worktrees_root = repo_root / "tools" / "codex" / "worktrees"
    return RepoContext(repo_root=repo_root, debug_dir=debug_dir, worktrees_root=worktrees_root)


def _run_git(repo_root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout


def _heads(repo_root: Path) -> list[str]:
    out = _run_git(repo_root, ["for-each-ref", "--format=%(refname)", "refs/heads"])
    return sorted([line.strip() for line in out.splitlines() if line.strip()])


def _worktree_paths(repo_root: Path) -> list[str]:
    out = _run_git(repo_root, ["worktree", "list", "--porcelain"])
    rows: list[str] = []
    for line in out.splitlines():
        if line.startswith("worktree "):
            raw = line.split(" ", 1)[1].strip()
            rows.append(Path(raw).resolve(strict=False).as_posix())
    return sorted(dict.fromkeys(rows))


def _worktree_disk_dirs(worktrees_root: Path) -> list[str]:
    if not worktrees_root.exists():
        return []
    rows: list[str] = []
    for item in sorted(worktrees_root.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir():
            rows.append(item.resolve(strict=False).as_posix())
    return rows


def _worktree_disk_segments(worktrees_root: Path) -> list[str]:
    if not worktrees_root.exists():
        return []
    rows: list[str] = []
    for item in sorted(worktrees_root.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir():
            rows.append(item.name)
    return rows


def _is_forbidden_run_scoped_worktree_path(path_value: str) -> bool:
    normalized = str(path_value).replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    for index, part in enumerate(parts[:-1]):
        if parts[index] == "worktrees" and index + 1 < len(parts):
            return bool(RUN_ID_SEGMENT_RE.fullmatch(parts[index + 1]))
    return False


def _scan_attempt_patterns(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    patterns = (
        "git worktree add",
        "codex/factory/",
        "worktrees/<RUN_ID>",
        "guard_trip:",
    )

    def iter_files(path: Path) -> list[Path]:
        if not path.exists():
            return []
        if path.is_file():
            return [path]
        return [item for item in path.rglob("*") if item.is_file()]

    for source in paths:
        for file_path in iter_files(source):
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            lines = text.splitlines()
            for index, line in enumerate(lines, start=1):
                lowered = line.lower()
                for pattern in patterns:
                    if pattern.lower() in lowered:
                        findings.append(f"{file_path.as_posix()}:{index}:{line.strip()[:180]}")
                        break
    return sorted(dict.fromkeys(findings))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"baseline payload must be object: {path.as_posix()}")
    return payload


def capture_baseline(repo_root: str | None = None, baseline_path: str | None = None) -> dict[str, Any]:
    context = _ctx(repo_root)
    payload = {
        "repo_root": context.repo_root.as_posix(),
        "refs_heads": _heads(context.repo_root),
        "worktree_paths": _worktree_paths(context.repo_root),
        "worktree_disk_dirs": _worktree_disk_dirs(context.worktrees_root),
        "worktree_disk_segments": _worktree_disk_segments(context.worktrees_root),
    }
    target = Path(baseline_path).resolve(strict=False) if baseline_path else (context.debug_dir / "unification_baseline.json")
    _write_json(target, payload)
    return {"status": "PASS", "baseline": target.as_posix(), "snapshot": payload}


def write_guard_reports(
    *,
    baseline_path: str | None,
    repo_root: str | None,
    scan_paths: list[str],
) -> dict[str, Any]:
    context = _ctx(repo_root)
    baseline_file = (
        Path(baseline_path).resolve(strict=False)
        if baseline_path
        else (context.debug_dir / "unification_baseline.json").resolve(strict=False)
    )
    baseline = _load_json(baseline_file)

    heads_before = sorted([str(item) for item in baseline.get("refs_heads", [])])
    heads_after = _heads(context.repo_root)
    new_heads = sorted(set(heads_after) - set(heads_before))
    codex_factory_before = sorted([item for item in heads_before if item.startswith("refs/heads/codex/factory/")])
    codex_factory_after = sorted([item for item in heads_after if item.startswith("refs/heads/codex/factory/")])

    branch_report = {
        "refs_heads_count_before": len(heads_before),
        "refs_heads_count_after": len(heads_after),
        "refs_heads_list_before": heads_before,
        "refs_heads_list_after": heads_after,
        "codex_factory_heads_present_before": bool(codex_factory_before),
        "codex_factory_heads_present_after": bool(codex_factory_after),
        "codex_factory_heads_list_before": codex_factory_before,
        "codex_factory_heads_list_after": codex_factory_after,
    }

    worktrees_before = sorted([str(item) for item in baseline.get("worktree_paths", [])])
    worktrees_after = _worktree_paths(context.repo_root)
    worktree_count_increased = len(worktrees_after) > len(worktrees_before)

    forbidden_after = sorted([item for item in worktrees_after if _is_forbidden_run_scoped_worktree_path(item)])
    forbidden_before = sorted([item for item in worktrees_before if _is_forbidden_run_scoped_worktree_path(item)])
    forbidden_new = sorted(set(forbidden_after) - set(forbidden_before))

    segments_before = sorted([str(item) for item in baseline.get("worktree_disk_segments", [])])
    segments_after = _worktree_disk_segments(context.worktrees_root)
    new_run_scoped_segments = sorted(
        [segment for segment in set(segments_after) - set(segments_before) if NEW_RUN_ID_SEGMENT_RE.fullmatch(segment)]
    )

    scan_targets = [Path(item).resolve(strict=False) for item in scan_paths if str(item).strip()]
    attempted_evidence: list[str] = []
    for segment in new_run_scoped_segments:
        attempted_evidence.append(f"new_run_scoped_dir:{(context.worktrees_root / segment).as_posix()}")
    attempted_evidence.extend(_scan_attempt_patterns(scan_targets))
    attempted_evidence = sorted(dict.fromkeys(attempted_evidence))
    attempted = bool(attempted_evidence)

    worktree_report = {
        "worktree_count_before": len(worktrees_before),
        "worktree_count_after": len(worktrees_after),
        "worktree_paths_before": worktrees_before,
        "worktree_paths_after": worktrees_after,
        "forbidden_run_scoped_paths_found": bool(forbidden_after),
        "forbidden_paths_list": forbidden_after,
        "attempted_run_scoped_creation": attempted,
        "attempted_evidence": attempted_evidence,
    }

    _write_json(context.debug_dir / "branch_guard_report.json", branch_report)
    _write_json(context.debug_dir / "worktree_guard_report.json", worktree_report)

    failures: list[str] = []
    if len(heads_after) != len(heads_before):
        failures.append(f"refs_heads_count_changed:{len(heads_before)}->{len(heads_after)}")
    if new_heads:
        failures.append(f"new_heads_detected:{','.join(new_heads)}")
    if codex_factory_after:
        failures.append(f"codex_factory_heads_present:{','.join(codex_factory_after)}")
    if worktree_count_increased:
        failures.append(f"worktree_count_increased:{len(worktrees_before)}->{len(worktrees_after)}")
    if forbidden_new:
        failures.append(f"new_forbidden_run_scoped_paths:{','.join(forbidden_new)}")
    if attempted:
        failures.append("attempted_run_scoped_creation:true")

    return {
        "status": "PASS" if not failures else "BLOCKED",
        "baseline": baseline_file.as_posix(),
        "branch_report": (context.debug_dir / "branch_guard_report.json").as_posix(),
        "worktree_report": (context.debug_dir / "worktree_guard_report.json").as_posix(),
        "failures": failures,
    }


def write_unification_grep_report(*, repo_root: str | None) -> dict[str, Any]:
    context = _ctx(repo_root)
    scope_map = {
        "code": context.repo_root / "tools" / "codex" / "factory",
        "docs_factory": context.repo_root / "docs" / "factory",
        "docs_mirror": context.repo_root / "factory" / "01 Mirror" / "docs",
    }

    code_run_scoped_patterns = (
        re.compile(r'CODEX_DIR\s*/\s*"worktrees"\s*/\s*run_id'),
        re.compile(r'tools/codex/worktrees/\s*["\']?\s*\+\s*run_id'),
        re.compile(r"tools/codex/worktrees/<RUN_ID>"),
    )
    docs_run_scoped_pattern = re.compile(r"tools/codex/worktrees/(<RUN_ID>|<run_id>|\d{8}(?:_\d+|_\d{6}_[A-Z0-9]{4}))")

    matches: dict[str, list[dict[str, Any]]] = {key: [] for key in scope_map}
    offending: list[dict[str, Any]] = []
    active_code_references_run_scoped = False
    run_scoped_mentions_outside_deprecated = False
    deprecated_marker_found_in_docs = False
    deprecated_mentions_exist = False

    for scope, root in scope_map.items():
        if not root.exists():
            continue
        files = [
            item
            for item in root.rglob("*")
            if item.is_file()
            and "__pycache__" not in item.parts
            and item.suffix.lower() not in {".pyc", ".pyo"}
        ]
        for file_path in sorted(files, key=lambda p: p.as_posix().lower()):
            rel = file_path.relative_to(context.repo_root).as_posix()
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            in_deprecated = False
            for index, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped == DEPRECATED_MARKER:
                    deprecated_marker_found_in_docs = True
                    in_deprecated = True
                elif in_deprecated and stripped.startswith("## ") and stripped != DEPRECATED_MARKER:
                    in_deprecated = False

                if "tools/codex/worktrees/" not in line and (scope != "code" or "run_id" not in line):
                    continue

                row = {"file": rel, "line": index, "excerpt": stripped[:220]}
                if "tools/codex/worktrees/" in line:
                    matches[scope].append(row)

                if scope == "code":
                    if rel.endswith("tools/codex/factory/unification_evidence.py"):
                        continue
                    if any(pattern.search(line) for pattern in code_run_scoped_patterns):
                        active_code_references_run_scoped = True
                        offending.append({**row, "reason": "active_code_run_scoped"})
                    continue

                if docs_run_scoped_pattern.search(line):
                    if in_deprecated:
                        deprecated_mentions_exist = True
                    else:
                        run_scoped_mentions_outside_deprecated = True
                        offending.append({**row, "reason": "run_scoped_doc_outside_deprecated"})

    report = {
        "matches": matches,
        "active_code_references_run_scoped": active_code_references_run_scoped,
        "run_scoped_mentions_outside_deprecated": run_scoped_mentions_outside_deprecated,
        "deprecated_marker_found_in_docs": deprecated_marker_found_in_docs,
        "offending_files": offending,
    }

    _write_json(context.debug_dir / "unification_grep_report.json", report)

    failures: list[str] = []
    if active_code_references_run_scoped:
        failures.append("active_code_references_run_scoped=true")
    if run_scoped_mentions_outside_deprecated:
        failures.append("run_scoped_mentions_outside_deprecated=true")
    if deprecated_mentions_exist and not deprecated_marker_found_in_docs:
        failures.append("deprecated_marker_found_in_docs=false_with_deprecated_mentions")

    return {
        "status": "PASS" if not failures else "BLOCKED",
        "report": (context.debug_dir / "unification_grep_report.json").as_posix(),
        "failures": failures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate unification evidence reports")
    sub = parser.add_subparsers(dest="command", required=True)

    baseline = sub.add_parser("capture-baseline", help="Capture refs/worktree baseline snapshot")
    baseline.add_argument("--repo-root", default=None)
    baseline.add_argument("--baseline-path", default=None)

    guards = sub.add_parser("write-guards", help="Write before/after branch + worktree guard reports")
    guards.add_argument("--repo-root", default=None)
    guards.add_argument("--baseline-path", default=None)
    guards.add_argument("--scan-path", action="append", default=[])

    grep = sub.add_parser("write-grep", help="Write unification grep report")
    grep.add_argument("--repo-root", default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "capture-baseline":
        payload = capture_baseline(repo_root=args.repo_root, baseline_path=args.baseline_path)
    elif args.command == "write-guards":
        payload = write_guard_reports(
            baseline_path=args.baseline_path,
            repo_root=args.repo_root,
            scan_paths=list(args.scan_path or []),
        )
    elif args.command == "write-grep":
        payload = write_unification_grep_report(repo_root=args.repo_root)
    else:
        payload = {"status": "BLOCKED", "error": f"unsupported command: {args.command}"}

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(payload.get("status", "")).upper() == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

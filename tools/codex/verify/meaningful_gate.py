from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import path depends on launcher
    from factory.path_guard import PathGuardError, normalize_rel_path
except Exception:  # pragma: no cover - package mode fallback
    from tools.codex.factory.path_guard import PathGuardError, normalize_rel_path

PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"
WARN = "WARN"

EMPTY_DECLARATIONS = "EMPTY_DECLARATIONS"
EMPTY_PATCH = "EMPTY_PATCH"
PHANTOM_PATHS = "PHANTOM_PATHS"
NO_GIT_MUTATION = "NO_GIT_MUTATION"
PATCH_NOT_APPLICABLE = "PATCH_NOT_APPLICABLE"
DECLARATION_MISMATCH = "DECLARATION_MISMATCH"

FAIL_MODES = (
    EMPTY_DECLARATIONS,
    EMPTY_PATCH,
    PHANTOM_PATHS,
    NO_GIT_MUTATION,
    PATCH_NOT_APPLICABLE,
    DECLARATION_MISMATCH,
)


def _repo_root_default() -> Path:
    return Path(__file__).resolve().parents[3]


def _runs_dir_default(repo_root: Path) -> Path:
    return repo_root / "tools" / "codex" / "runs"


def _canonical_path(raw: str) -> str:
    candidate = str(raw or "").strip()
    if not candidate:
        return ""
    try:
        normalized = normalize_rel_path(candidate, casefold_windows=False)
    except PathGuardError:
        normalized = candidate.replace("\\", "/").strip()
        while "//" in normalized:
            normalized = normalized.replace("//", "/")
        while normalized.startswith("./"):
            normalized = normalized[2:]
        normalized = normalized.strip("/")
    if os.name == "nt":
        return normalized.lower()
    return normalized


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _run_git(repo_root: Path, args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "cmd": ["git", *args],
        "rc": int(proc.returncode),
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
    }


def _parse_git_name_status(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            continue
        status = columns[0].strip()
        for path_raw in columns[1:]:
            path = _canonical_path(path_raw)
            if not path:
                continue
            parsed[path] = status
    return parsed


def _parse_git_status(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if len(line) < 3:
            continue
        status = line[:2]
        path_raw = line[3:].strip()
        if not path_raw:
            continue
        if " -> " in path_raw:
            path_raw = path_raw.split(" -> ", 1)[1].strip()
        path = _canonical_path(path_raw.strip('"'))
        if not path:
            continue
        parsed[path] = status.strip() or "M"
    return parsed


def _collect_git_mutations(repo_root: Path, base_ref: str) -> tuple[dict[str, str], list[str]]:
    details: list[str] = []
    merged: dict[str, str] = {}

    head_ref = _run_git(repo_root, ["rev-parse", "HEAD"])
    if head_ref["rc"] != 0:
        details.append("HEAD is not available.")
        return {}, details
    head = head_ref["stdout"].strip()

    base_resolve = _run_git(repo_root, ["rev-parse", "--verify", f"{base_ref}^{{commit}}"])
    if base_resolve["rc"] != 0:
        details.append(f"base_ref is not resolvable: {base_ref}")
        base = head
    else:
        base = base_resolve["stdout"].strip()

    if base and head:
        diff_range = _run_git(repo_root, ["diff", "--name-status", "--no-renames", f"{base}..{head}"])
        if diff_range["rc"] == 0:
            merged.update(_parse_git_name_status(diff_range["stdout"]))
        else:
            details.append("git diff base..head failed.")

    status = _run_git(repo_root, ["status", "--porcelain=v1", "--untracked-files=all"])
    if status["rc"] == 0:
        merged.update(_parse_git_status(status["stdout"]))
    else:
        details.append("git status --porcelain failed.")

    return merged, details


def _parse_patch_paths(diff_text: str) -> list[str]:
    paths: set[str] = set()
    for raw_line in diff_text.splitlines():
        line = raw_line.strip()
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                left = parts[2][2:] if parts[2].startswith("a/") else parts[2]
                right = parts[3][2:] if parts[3].startswith("b/") else parts[3]
                if left == "/dev/null":
                    chosen = right
                elif right == "/dev/null":
                    chosen = left
                else:
                    chosen = right
                normalized = _canonical_path(chosen)
                if normalized:
                    paths.add(normalized)
            continue
        if line.startswith("+++ b/") or line.startswith("--- a/"):
            candidate = line[6:].strip()
            if candidate == "/dev/null":
                continue
            normalized = _canonical_path(candidate)
            if normalized:
                paths.add(normalized)
    return sorted(paths)


def _patch_check(repo_root: Path, patch_path: Path) -> tuple[bool, str]:
    forward = _run_git(repo_root, ["apply", "--check", "--verbose", patch_path.as_posix()])
    if forward["rc"] == 0:
        return True, "forward"
    reverse = _run_git(repo_root, ["apply", "--check", "--reverse", "--verbose", patch_path.as_posix()])
    if reverse["rc"] == 0:
        return True, "reverse"
    detail = (forward.get("stderr") or forward.get("stdout") or "").strip()
    if not detail:
        detail = (reverse.get("stderr") or reverse.get("stdout") or "").strip()
    return False, detail


def _build_markdown(payload: dict[str, Any]) -> str:
    fail_modes = payload.get("fail_modes", [])
    stats = payload.get("stats", {})
    lines = [
        "# VERIFY_MEANINGFUL_GATE",
        "",
        f"- Verdict: `{payload.get('verdict', BLOCKED)}`",
        f"- NOOP: `{str(payload.get('noop', False)).lower()}`",
        f"- NOOP reason: `{payload.get('noop_reason', '')}`",
        f"- NOOP ack: `{payload.get('noop_ack', '')}`",
        f"- Fail modes: `{', '.join(fail_modes) if fail_modes else '<none>'}`",
        "",
        "## Stats",
        f"- changed_files_count: `{stats.get('changed_files_count', 0)}`",
        f"- diff_bytes: `{stats.get('diff_bytes', 0)}`",
        f"- declared_paths_count: `{stats.get('declared_paths_count', 0)}`",
        f"- git_paths_count: `{stats.get('git_paths_count', 0)}`",
        "",
        "## Samples (up to 10)",
    ]
    for path in payload.get("samples", []):
        lines.append(f"- `{path}`")
    if not payload.get("samples"):
        lines.append("- <none>")
    details = payload.get("details", {})
    notes = details.get("notes", [])
    if notes:
        lines.extend(["", "## Notes"])
        for item in notes:
            lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def run_meaningful_gate(
    run_id: str,
    *,
    repo_root: Path | None = None,
    runs_dir: Path | None = None,
    write_outputs: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or _repo_root_default()).resolve()
    all_runs = Path(runs_dir or _runs_dir_default(root)).resolve()
    run_dir = all_runs / run_id
    z_dir = run_dir / "Z_integrator"
    files_changed_path = z_dir / "FILES_CHANGED.json"
    diff_path = z_dir / "DIFF.patch"
    manifest_path = run_dir / "RUN_MANIFEST.json"
    report_json = run_dir / "VERIFY_MEANINGFUL_GATE.json"
    report_md = run_dir / "VERIFY_MEANINGFUL_GATE.md"

    notes: list[str] = []
    fail_modes: set[str] = set()
    blocked = False

    base_ref = "HEAD"
    if manifest_path.exists():
        try:
            manifest = _read_json(manifest_path)
            base_ref = str(manifest.get("base_ref") or "HEAD")
        except Exception:
            notes.append("RUN_MANIFEST.json is unreadable; base_ref fallback to HEAD.")
    else:
        notes.append("RUN_MANIFEST.json is missing; base_ref fallback to HEAD.")

    if not run_dir.exists():
        blocked = True
        notes.append(f"run directory missing: {run_dir.as_posix()}")

    files_changed: dict[str, Any] = {}
    if files_changed_path.exists():
        try:
            files_changed = dict(_read_json(files_changed_path))
        except Exception:
            blocked = True
            notes.append(f"FILES_CHANGED.json is unreadable: {files_changed_path.as_posix()}")
    else:
        fail_modes.add(EMPTY_DECLARATIONS)
        notes.append("FILES_CHANGED.json is missing.")

    diff_text = ""
    if diff_path.exists():
        diff_text = diff_path.read_text(encoding="utf-8")
    else:
        fail_modes.add(EMPTY_PATCH)
        notes.append("DIFF.patch is missing.")

    changes_raw = files_changed.get("changes", [])
    changes = [entry for entry in changes_raw if isinstance(entry, dict)]
    declared_paths: list[str] = sorted(
        {
            _canonical_path(str(entry.get("path", "")))
            for entry in changes
            if _canonical_path(str(entry.get("path", "")))
        }
    )

    noop = bool(files_changed.get("noop", False))
    noop_reason = str(files_changed.get("noop_reason", "")).strip()
    noop_ack = str(files_changed.get("noop_ack", "")).strip()
    noop_declared = bool(noop and noop_reason and noop_ack)

    diff_bytes = len(diff_text.encode("utf-8"))
    if not noop_declared and not changes:
        fail_modes.add(EMPTY_DECLARATIONS)
    if not noop_declared and not diff_text.strip():
        fail_modes.add(EMPTY_PATCH)

    phantom_paths: list[str] = []
    for entry in changes:
        raw_path = str(entry.get("path", ""))
        path = _canonical_path(raw_path)
        if not path:
            continue
        change_type = str(entry.get("change_type", "modified")).strip().lower()
        exists = (root / path).exists()
        expects_exists = change_type not in {"deleted"}
        if expects_exists != exists:
            phantom_paths.append(path)
    if phantom_paths:
        fail_modes.add(PHANTOM_PATHS)

    git_mutations, git_notes = _collect_git_mutations(root, base_ref=base_ref)
    notes.extend(git_notes)
    runs_prefix = _canonical_path("tools/codex/runs")
    filtered_git_mutations = {
        path: status
        for path, status in git_mutations.items()
        if not (path == runs_prefix or path.startswith(runs_prefix + "/"))
    }
    if len(filtered_git_mutations) != len(git_mutations):
        notes.append("excluded run-artifact paths from git mutation set")
    git_paths = sorted(filtered_git_mutations.keys())
    if not noop_declared and not git_paths:
        fail_modes.add(NO_GIT_MUTATION)

    patch_paths = _parse_patch_paths(diff_text)
    declared_set = set(declared_paths)
    patch_set = set(patch_paths)
    git_set = set(git_paths)

    declared_not_in_git = sorted(declared_set - git_set)
    patch_not_in_git = sorted(patch_set - git_set)
    declared_patch_mismatch = sorted((declared_set - patch_set) | (patch_set - declared_set))
    if declared_not_in_git or patch_not_in_git or declared_patch_mismatch:
        fail_modes.add(DECLARATION_MISMATCH)

    patch_applies = True
    patch_apply_detail = ""
    if diff_text.strip() and not noop_declared:
        patch_applies, patch_apply_detail = _patch_check(root, diff_path)
        if not patch_applies:
            fail_modes.add(PATCH_NOT_APPLICABLE)
    elif not diff_text.strip():
        patch_applies = False
        patch_apply_detail = "patch is empty"

    if blocked:
        verdict = BLOCKED
    elif fail_modes:
        verdict = FAIL
    elif noop_declared and not changes:
        verdict = PASS
    else:
        verdict = PASS

    sample_pool = sorted(
        {
            *declared_paths,
            *patch_paths,
            *git_paths,
            *phantom_paths,
            *declared_not_in_git,
            *patch_not_in_git,
            *declared_patch_mismatch,
        }
    )
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "verdict": verdict,
        "fail_modes": sorted(mode for mode in fail_modes if mode in FAIL_MODES),
        "noop": noop_declared,
        "noop_reason": noop_reason if noop_declared else "",
        "noop_ack": noop_ack if noop_declared else "",
        "stats": {
            "changed_files_count": len(changes),
            "diff_bytes": diff_bytes,
            "declared_paths_count": len(declared_paths),
            "git_paths_count": len(git_paths),
        },
        "samples": sample_pool[:10],
        "details": {
            "base_ref": base_ref,
            "declared_paths": declared_paths,
            "patch_paths": patch_paths,
            "git_paths": git_paths,
            "phantom_paths": sorted(set(phantom_paths)),
            "declared_not_in_git": declared_not_in_git,
            "patch_not_in_git": patch_not_in_git,
            "declared_patch_mismatch": declared_patch_mismatch,
            "patch_applies": patch_applies,
            "patch_apply_detail": patch_apply_detail,
            "notes": sorted(set(notes)),
        },
        "outputs": {
            "json": report_json.as_posix(),
            "md": report_md.as_posix(),
        },
    }

    if write_outputs and run_dir.exists():
        _write_json(report_json, payload)
        _write_text(report_md, _build_markdown(payload))
    return payload


def _exit_code(verdict: str) -> int:
    if verdict == PASS or verdict == WARN:
        return 0
    if verdict == FAIL or verdict == BLOCKED:
        return 2
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HITECH-OS meaningful execution gate verifier")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--repo-root")
    parser.add_argument("--runs-dir")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_meaningful_gate(
        args.run_id,
        repo_root=Path(args.repo_root).resolve() if args.repo_root else None,
        runs_dir=Path(args.runs_dir).resolve() if args.runs_dir else None,
        write_outputs=not args.no_write,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return _exit_code(str(payload.get("verdict", BLOCKED)))


if __name__ == "__main__":
    raise SystemExit(main())

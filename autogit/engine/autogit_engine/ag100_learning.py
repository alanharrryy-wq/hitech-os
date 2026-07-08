from __future__ import annotations

import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

SCHEMA = "autogit.ag100_learning.v1"
DEFAULT_MAX_JSON_BYTES = 64 * 1024 * 1024
DEFAULT_COPY_BYTES = 2_500_000

SAFE_SELF_HEAL_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".json", ".csv", ".yml", ".yaml",
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".css", ".html", ".ps1", ".psm1", ".cmd", ".bat",
}

RUNTIME_NOISE_GLOBS = [
    "**/*.db-wal",
    "**/*.db-shm",
    "**/*.sqlite-wal",
    "**/*.sqlite-shm",
    "**/.wrangler/**",
    "**/.cache/**",
    "**/node_modules/**",
    "**/.next/**",
    "**/.turbo/**",
]

TRAILING_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+): trailing whitespace\.", re.MULTILINE)
EOF_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+): new blank line at EOF\.", re.MULTILINE)

def _now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")

def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "item"))[:140] or "item"

def find_repo_root(start: Path | str) -> Path:
    p = Path(start).resolve()
    if p.is_file():
        p = p.parent
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            return candidate
    return p

def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")

def _run_git(repo: Path, args: list[str], timeout: int = 180) -> dict:
    try:
        cp = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            shell=False,
        )
        return {
            "cmd": ["git", *args],
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
        }
    except Exception as exc:
        return {"cmd": ["git", *args], "returncode": 999, "stdout": "", "stderr": repr(exc)}

def _runner_run(runner, args: list[str], *, name: str, timeout: int = 180, check: bool = False):
    if runner is not None and hasattr(runner, "run"):
        return runner.run(args, timeout=timeout, check=check, name=name)

    class Result:
        pass

    cp = subprocess.run(
        list(map(str, args)),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        shell=False,
    )
    res = Result()
    res.returncode = cp.returncode
    res.stdout = cp.stdout
    res.stderr = cp.stderr
    if check and cp.returncode != 0:
        raise RuntimeError(f"{name} failed rc={cp.returncode}")
    return res

def _normalize_rel(rel: str) -> str:
    return str(rel or "").replace("\\", "/").strip("/")

def _match_any(rel: str, patterns: list[str]) -> bool:
    r = _normalize_rel(rel).lower()
    for pat in patterns:
        p = _normalize_rel(pat).lower()
        if fnmatch.fnmatch(r, p):
            return True
        if p.startswith("**/") and fnmatch.fnmatch(r, p[3:]):
            return True
    return False

def classify_local_path(rel: str) -> str:
    r = _normalize_rel(rel)
    if _match_any(r, RUNTIME_NOISE_GLOBS):
        return "runtime_noise"
    if r.startswith("autogit/"):
        return "autogit_tooling"
    if r.startswith("apps/terminal-de-venta-system/products/tablet/app/app/tablet-lab/") or "/tablet-lab/" in r:
        return "likely_intentional_tablet_lab_work"
    if "runtime" in r.lower() and r.lower().endswith(".json"):
        return "runtime_config_or_override_requires_decision"
    if r.startswith("apps/") or r.startswith("products/") or r.startswith("tools/"):
        return "project_work_requires_decision"
    return "unclassified_requires_decision"

def json_text_for_validation(path: Path, max_text_bytes: int = 2 * 1024 * 1024, max_json_bytes: int | None = None) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return ""
    limit = max_json_bytes or max(max_text_bytes * 64, DEFAULT_MAX_JSON_BYTES)
    if p.stat().st_size > limit:
        return ""
    data = p.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")

def _is_probably_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except Exception:
        return True
    return b"\x00" in chunk

def is_safe_self_heal_path(path: Path, allowed_exts: set[str] | None = None) -> bool:
    allowed = allowed_exts or SAFE_SELF_HEAL_EXTENSIONS
    name = path.name.lower()
    if name.startswith(".env") or "secret" in name or "credential" in name or "token" in name:
        return False
    if path.suffix.lower() not in allowed:
        return False
    return not _is_probably_binary(path)

def clean_text_file(path: Path) -> dict:
    """Remove trailing spaces/tabs and collapse EOF blank tail to a single newline."""
    p = Path(path)
    before = p.read_bytes()
    text = before.decode("utf-8", errors="replace")

    crlf = text.count("\r\n")
    lf = text.count("\n")
    newline = "\r\n" if crlf and crlf >= max(1, lf // 2) else "\n"

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")

    trailing_lines: list[int] = []
    fixed_lines: list[str] = []
    # split("\n") keeps a final "" if file ends in newline; handle all logical lines.
    for idx, line in enumerate(lines, 1):
        fixed = line.rstrip(" \t")
        if fixed != line:
            trailing_lines.append(idx)
        fixed_lines.append(fixed)

    while fixed_lines and fixed_lines[-1].strip() == "":
        fixed_lines.pop()

    new_text = "\n".join(fixed_lines) + "\n"
    if newline == "\r\n":
        new_text = new_text.replace("\n", "\r\n")
    after = new_text.encode("utf-8")

    changed = after != before
    if changed:
        p.write_bytes(after)

    return {
        "changed": changed,
        "trailing_lines": trailing_lines,
        "sha256_before": hashlib.sha256(before).hexdigest(),
        "sha256_after": hashlib.sha256(after).hexdigest(),
        "newline": "CRLF" if newline == "\r\n" else "LF",
    }

def _paths_from_cached_check(text: str) -> list[str]:
    paths: list[str] = []
    for regex in (TRAILING_RE, EOF_RE):
        for m in regex.finditer(text or ""):
            rel = _normalize_rel(m.group("path"))
            if rel and rel not in paths:
                paths.append(rel)
    return paths

def _staged_paths(repo: Path, runner=None) -> list[str]:
    if runner is not None and hasattr(runner, "run"):
        cp = runner.run(["git", "diff", "--cached", "--name-only", "-z"], timeout=180, name="ag100_staged_paths_z")
        raw = (cp.stdout or "").encode("utf-8", errors="replace")
    else:
        p = subprocess.run(["git", "diff", "--cached", "--name-only", "-z"], cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        raw = p.stdout
    return [x.decode("utf-8", errors="replace") for x in raw.split(b"\0") if x]

def autofix_staged_whitespace(repo: Path, runner=None, report: Path | None = None, group_paths: list[str] | None = None, label: str | None = None) -> dict:
    """Self-heal safe staged text files when git diff --cached --check reports whitespace/EOF blockers.

    Scope is intentionally narrow:
    - only staged files;
    - if group_paths is provided, only files in that group;
    - only allowlisted text extensions;
    - no binary files;
    - writes backups/current files under the active report.
    """
    repo = Path(repo)
    label = _safe_name(label or "staged")
    root = (Path(report) if report else repo / ".autogit-ag100") / "ag100_self_heal" / label
    backups = root / "backups_before_changes"
    current = root / "current_files_after_fix"
    backups.mkdir(parents=True, exist_ok=True)
    current.mkdir(parents=True, exist_ok=True)

    before = _runner_run(runner, ["git", "diff", "--cached", "--check"], name=f"ag100_cached_diff_check_{label}_before", timeout=180)
    before_text = (getattr(before, "stdout", "") or "") + "\n" + (getattr(before, "stderr", "") or "")
    staged = set(_normalize_rel(p) for p in _staged_paths(repo, runner))
    group = set(_normalize_rel(p) for p in (group_paths or []))

    reported = set(_paths_from_cached_check(before_text))
    if group:
        candidates = [p for p in sorted(staged & group)]
    else:
        candidates = [p for p in sorted(staged)]

    # If git reported exact files, prioritize them but still sweep all safe files in the group
    # because one file can have several trailing-whitespace lines and git may stop early.
    candidate_set = []
    for p in [*sorted(reported), *candidates]:
        if p in staged and (not group or p in group) and p not in candidate_set:
            candidate_set.append(p)

    fixed = []
    skipped = []
    for rel in candidate_set:
        path = repo / rel
        if not path.exists() or not path.is_file():
            skipped.append({"path": rel, "reason": "missing"})
            continue
        if not is_safe_self_heal_path(path):
            skipped.append({"path": rel, "reason": "extension_or_binary_not_allowlisted"})
            continue
        try:
            before_hash = _sha256(path)
            backup = backups / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
            result = clean_text_file(path)
            if result["changed"]:
                cur = current / rel
                cur.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, cur)
                fixed.append({"path": rel, **result, "backup": str(backup)})
            else:
                skipped.append({"path": rel, "reason": "no_text_change", "sha256": before_hash})
        except Exception as exc:
            skipped.append({"path": rel, "reason": repr(exc)})

    if fixed:
        _runner_run(runner, ["git", "add", "--", *[x["path"] for x in fixed]], name=f"ag100_git_add_self_healed_{label}", timeout=180, check=True)

    after = _runner_run(runner, ["git", "diff", "--cached", "--check"], name=f"ag100_cached_diff_check_{label}_after", timeout=180)
    after_text = (getattr(after, "stdout", "") or "") + "\n" + (getattr(after, "stderr", "") or "")

    summary = {
        "schema": SCHEMA,
        "created_at": _now(),
        "label": label,
        "before_returncode": getattr(before, "returncode", None),
        "after_returncode": getattr(after, "returncode", None),
        "before_output_tail": before_text[-4000:],
        "after_output_tail": after_text[-4000:],
        "candidate_count": len(candidate_set),
        "fixed": fixed,
        "skipped": skipped,
        "ok": getattr(after, "returncode", 1) == 0,
    }
    _write_json(root / "AG100_SELF_HEAL.json", summary)
    return summary

def write_group_checkpoint(repo: Path, runner, report: Path, *, index: int, total: int, group: dict, phase: str, extra: dict | None = None) -> dict:
    repo = Path(repo)
    safe_group = _safe_name(group.get("group") if isinstance(group, dict) else "group")
    root = Path(report) / "ag100_checkpoints" / f"{index:02d}_{safe_group}"
    root.mkdir(parents=True, exist_ok=True)

    status = _run_git(repo, ["status", "--short", "--branch"])
    branch = _run_git(repo, ["branch", "--show-current"])
    head = _run_git(repo, ["rev-parse", "HEAD"])
    staged = _run_git(repo, ["diff", "--cached", "--name-status"])
    cached_check = _run_git(repo, ["diff", "--cached", "--check"])

    data = {
        "schema": "autogit.ag100_group_checkpoint.v1",
        "created_at": _now(),
        "index": index,
        "total": total,
        "phase": phase,
        "group": group,
        "branch": (branch.get("stdout") or "").strip(),
        "head": (head.get("stdout") or "").strip(),
        "status": status,
        "staged_name_status": staged,
        "cached_check": cached_check,
        "extra": extra or {},
    }
    _write_json(root / f"{_safe_name(phase)}.json", data)
    return data

def _copy_small_current_file(repo: Path, rel: str, dest_root: Path, max_bytes: int = DEFAULT_COPY_BYTES) -> dict:
    src = repo / rel
    item = {"path": rel, "exists": src.exists(), "copied": False}
    if not src.exists() or not src.is_file():
        return item
    item["size"] = src.stat().st_size
    item["sha256"] = _sha256(src)
    if item["size"] > max_bytes:
        item["reason"] = "too_large"
        return item
    if _is_probably_binary(src):
        item["reason"] = "binary_or_non_text"
        return item
    dest = dest_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    item["copied"] = True
    return item

def capture_failure_context(repo: Path | str, fail_dir: Path | str, report: Path | None = None, exc: BaseException | None = None) -> dict:
    repo = find_repo_root(repo)
    fail = Path(fail_dir)
    root = fail / "ag100_failure_context"
    root.mkdir(parents=True, exist_ok=True)

    commands = {
        "git_status_failure": ["status", "--short", "--branch"],
        "git_branch_failure": ["branch", "--show-current"],
        "git_head_failure": ["rev-parse", "HEAD"],
        "git_main_to_head_failure": ["log", "--oneline", "--decorate", "main..HEAD"],
        "git_cached_name_status_failure": ["diff", "--cached", "--name-status"],
        "git_cached_check_failure": ["diff", "--cached", "--check"],
        "git_worktree_check_failure": ["diff", "--check"],
        "git_staged_paths_failure": ["diff", "--cached", "--name-only", "-z"],
    }
    outputs = {}
    for name, args in commands.items():
        outputs[name] = _run_git(repo, args)
        _write_json(root / f"{name}.json", outputs[name])
        if "stdout" in outputs[name] or "stderr" in outputs[name]:
            _write_text(root / f"{name}.txt", (outputs[name].get("stdout") or "") + (outputs[name].get("stderr") or ""))

    staged_raw = outputs["git_staged_paths_failure"].get("stdout") or ""
    staged_paths = [p for p in staged_raw.split("\0") if p]
    copied = [_copy_small_current_file(repo, _normalize_rel(p), root / "current_staged_files") for p in staged_paths[:500]]

    blockers = _paths_from_cached_check(
        (outputs["git_cached_check_failure"].get("stdout") or "") + "\n" +
        (outputs["git_cached_check_failure"].get("stderr") or "")
    )

    summary = {
        "schema": "autogit.ag100_failure_context.v1",
        "created_at": _now(),
        "repo": str(repo),
        "exception": repr(exc) if exc is not None else None,
        "partial_report": str(report) if report else None,
        "staged_paths": staged_paths,
        "cached_check_blocker_paths": blockers,
        "copied_current_staged_files": copied,
        "suggested_next_step": "Inspect this ZIP, fix only the blocker paths, then rerun apply-plan with --allow-drift if commits already exist in main..HEAD.",
    }
    _write_json(root / "AG100_FAILURE_CONTEXT.json", summary)
    _write_text(root / "CONTINUATION_AG100.md", "\n".join([
        "# AG100 Failure Continuation",
        "",
        "This fail ZIP includes staged paths, branch, HEAD, main..HEAD, cached diff check, working-tree check, and small current staged files.",
        "",
        "Do not reset or clean blindly.",
        "",
        "If AutoGit already created commits, continue with `apply-plan --allow-drift` after fixing only the reported blocker files.",
        "",
        "Cached-check blocker paths:",
        *[f"- `{p}`" for p in blockers],
        "",
    ]))
    return summary

def write_post_run_hygiene_report(repo: Path | str, runner, report: Path | str, context: str = "post_run") -> dict:
    repo = find_repo_root(repo)
    root = Path(report) / "ag100_post_run_hygiene"
    root.mkdir(parents=True, exist_ok=True)
    status = _run_git(repo, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    raw = status.get("stdout") or ""
    entries = []
    parts = raw.split("\0")
    for item in parts:
        if not item:
            continue
        path = item[3:] if len(item) > 3 else item
        path = _normalize_rel(path)
        entries.append({"status": item[:2], "path": path, "class": classify_local_path(path)})

    summary = {
        "schema": "autogit.ag100_post_run_hygiene.v1",
        "created_at": _now(),
        "context": context,
        "repo": str(repo),
        "entries": entries,
        "counts": {},
    }
    for e in entries:
        summary["counts"][e["class"]] = summary["counts"].get(e["class"], 0) + 1

    _write_json(root / "AG100_POST_RUN_HYGIENE.json", summary)
    md = [
        "# AG100 Post-run Hygiene",
        "",
        f"Context: `{context}`",
        "",
        "## Counts",
        "",
        *[f"- `{k}`: `{v}`" for k, v in sorted(summary["counts"].items())],
        "",
        "## Entries",
        "",
        *[f"- `{e['status']}` `{e['path']}` → `{e['class']}`" for e in entries],
        "",
    ]
    _write_text(root / "AG100_POST_RUN_HYGIENE.md", "\n".join(md))
    return summary

def write_learning_ledger_event(repo: Path | str, event: dict) -> None:
    repo = find_repo_root(repo)
    ledger = repo / "autogit" / "docs" / "AUTOGIT_LEARNING_LEDGER.md"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    line = f"\n## {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {event.get('title','AutoGit learning')}\n\n"
    line += event.get("body", "").rstrip() + "\n"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(line)

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .common import CODEX_DIR, DEFAULT_BRANCH_PREFIX, REPO_ROOT, RUNS_DIR, WORKERS, ensure_dir, write_json
from .locks import LockAcquisitionError, acquire_run_lock, acquire_worker_lock


def worktree_root(run_id: str) -> Path:
    return CODEX_DIR / "worktrees" / run_id


def worktree_path(run_id: str, worker: str) -> Path:
    return worktree_root(run_id) / worker


def branch_name(run_id: str, worker: str, branch_prefix: str = DEFAULT_BRANCH_PREFIX) -> str:
    return f"{branch_prefix}/{run_id}/{worker}"


def _sorted_workers(workers: list[str] | None) -> list[str]:
    chosen = workers or list(WORKERS)
    cleaned = [item.strip() for item in chosen if str(item).strip()]
    return sorted(set(cleaned))


def _run(args: list[str], cwd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 0,
            "stdout": "",
            "stderr": "",
            "dry_run": True,
        }
    proc = subprocess.run(args, cwd=str(cwd or REPO_ROOT), text=True, capture_output=True, check=False)
    return {
        "cmd": args,
        "cwd": str(cwd or REPO_ROOT),
        "rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "dry_run": False,
    }


def _resolve_commit(ref: str, *, cwd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"ref": ref, "rc": 0, "commit": "DRYRUN", "stderr": "", "stdout": ""}
    proc = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=str(cwd or REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "ref": ref,
        "rc": proc.returncode,
        "commit": proc.stdout.strip(),
        "stderr": proc.stderr,
        "stdout": proc.stdout,
    }


def create_worktrees(
    run_id: str,
    *,
    workers: list[str] | None = None,
    base_ref: str = "HEAD",
    branch_prefix: str = DEFAULT_BRANCH_PREFIX,
    dry_run: bool = False,
) -> dict[str, Any]:
    chosen = _sorted_workers(workers)
    root = worktree_root(run_id)
    ensure_dir(root)
    steps: list[dict[str, Any]] = []
    base_ref_commit = _resolve_commit(base_ref, dry_run=dry_run)
    lock_errors: list[str] = []

    try:
        run_lock = acquire_run_lock(run_id, owner="worktrees.create")
    except LockAcquisitionError as exc:
        return {
            "run_id": run_id,
            "operation": "create",
            "status": "BLOCKED",
            "steps": [],
            "blocked": len(chosen),
            "lock_error": str(exc),
            "base_ref": base_ref,
            "base_ref_commit": base_ref_commit,
        }

    try:
        for worker in chosen:
            target = worktree_path(run_id, worker)
            branch = branch_name(run_id, worker, branch_prefix=branch_prefix)
            worker_actions: list[dict[str, Any]] = []
            try:
                worker_lock = acquire_worker_lock(run_id, worker, owner="worktrees.create")
            except LockAcquisitionError as exc:
                lock_errors.append(str(exc))
                steps.append(
                    {
                        "worker": worker,
                        "status": "BLOCKED",
                        "detail": str(exc),
                        "path": target.as_posix(),
                        "branch": branch,
                        "actions": [],
                        "base_ref_commit": base_ref_commit,
                    }
                )
                continue

            try:
                if target.exists():
                    head_commit = _resolve_commit("HEAD", cwd=target, dry_run=dry_run)
                    step_payload = {
                        "worker": worker,
                        "status": "PASS",
                        "detail": "worktree already exists",
                        "path": target.as_posix(),
                        "branch": branch,
                        "actions": [],
                        "base_ref_commit": base_ref_commit,
                        "worktree_commit": head_commit,
                        "commit_match": head_commit.get("commit") == base_ref_commit.get("commit") or dry_run,
                    }
                    steps.append(step_payload)
                    continue

                check_branch = _run(["git", "show-ref", "--verify", f"refs/heads/{branch}"], dry_run=dry_run)
                worker_actions.append(check_branch)
                branch_exists = check_branch["rc"] == 0

                if branch_exists:
                    add_cmd = ["git", "worktree", "add", target.as_posix(), branch]
                else:
                    add_cmd = ["git", "worktree", "add", "-b", branch, target.as_posix(), base_ref]
                add_result = _run(add_cmd, dry_run=dry_run)
                worker_actions.append(add_result)

                head_commit = _resolve_commit("HEAD", cwd=target, dry_run=dry_run)
                worker_actions.append({"commit_check": head_commit})
                commit_match = head_commit.get("commit") == base_ref_commit.get("commit") or dry_run

                status = "PASS" if add_result["rc"] == 0 and commit_match else "BLOCKED"
                detail = "created" if status == "PASS" else "failed to create worktree or commit mismatch"
                steps.append(
                    {
                        "worker": worker,
                        "status": status,
                        "detail": detail,
                        "path": target.as_posix(),
                        "branch": branch,
                        "actions": worker_actions,
                        "base_ref_commit": base_ref_commit,
                        "worktree_commit": head_commit,
                        "commit_match": commit_match,
                    }
                )
            finally:
                worker_lock.release()
    finally:
        run_lock.release()

    blocked = [step for step in steps if step["status"] != "PASS"]
    payload = {
        "run_id": run_id,
        "operation": "create",
        "status": "PASS" if not blocked else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked),
        "lock_errors": lock_errors,
        "base_ref": base_ref,
        "base_ref_commit": base_ref_commit,
    }
    state_path = RUNS_DIR / run_id / "WORKTREE_STATE.json"
    write_json(state_path, payload)
    return payload


def verify_worktrees(run_id: str, *, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = _sorted_workers(workers)
    steps: list[dict[str, Any]] = []
    for worker in chosen:
        target = worktree_path(run_id, worker)
        git_dir = target / ".git"
        ok = target.exists() and git_dir.exists()
        commit_info = _resolve_commit("HEAD", cwd=target, dry_run=not ok)
        steps.append(
            {
                "worker": worker,
                "status": "PASS" if ok else "BLOCKED",
                "path": target.as_posix(),
                "git_marker": git_dir.as_posix(),
                "detail": "verified" if ok else "missing worktree or git marker",
                "head_commit": commit_info.get("commit", ""),
            }
        )
    blocked = [step for step in steps if step["status"] != "PASS"]
    return {
        "run_id": run_id,
        "operation": "verify",
        "status": "PASS" if not blocked else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked),
    }


def sync_worktrees(run_id: str, *, workers: list[str] | None = None, dry_run: bool = False) -> dict[str, Any]:
    chosen = _sorted_workers(workers)
    steps: list[dict[str, Any]] = []
    for worker in chosen:
        target = worktree_path(run_id, worker)
        if not target.exists():
            steps.append(
                {
                    "worker": worker,
                    "status": "BLOCKED",
                    "detail": "worktree does not exist",
                    "path": target.as_posix(),
                    "actions": [],
                }
            )
            continue

        actions = [
            _run(["git", "fetch", "--all", "--prune"], cwd=target, dry_run=dry_run),
            _run(["git", "status", "--porcelain=v1"], cwd=target, dry_run=dry_run),
            _resolve_commit("HEAD", cwd=target, dry_run=dry_run),
        ]
        blocked = [item for item in actions if item["rc"] != 0]
        steps.append(
            {
                "worker": worker,
                "status": "PASS" if not blocked else "BLOCKED",
                "detail": "synced" if not blocked else "sync failed",
                "path": target.as_posix(),
                "actions": actions,
            }
        )

    blocked_steps = [step for step in steps if step["status"] != "PASS"]
    return {
        "run_id": run_id,
        "operation": "sync",
        "status": "PASS" if not blocked_steps else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked_steps),
    }


def _build_code_open_command(
    *,
    target: Path,
    new_window: bool = False,
    goto_path: Path | None = None,
) -> list[str]:
    cmd = ["code"]
    if new_window:
        cmd.append("-n")
    if goto_path is not None:
        cmd.extend(["--goto", goto_path.as_posix()])
    else:
        cmd.append(target.as_posix())
    return cmd


def open_worktrees(
    run_id: str,
    *,
    workers: list[str] | None = None,
    dry_run: bool = False,
    new_window: bool = False,
    goto: str | None = None,
) -> dict[str, Any]:
    chosen = _sorted_workers(workers)
    steps: list[dict[str, Any]] = []
    for worker in chosen:
        target = worktree_path(run_id, worker)
        if not target.exists():
            steps.append(
                {
                    "worker": worker,
                    "status": "BLOCKED",
                    "detail": "worktree missing",
                    "path": target.as_posix(),
                    "actions": [],
                }
            )
            continue

        goto_path: Path | None = None
        goto_missing = False
        if goto:
            raw = Path(goto)
            goto_path = raw if raw.is_absolute() else target / raw
            goto_missing = not goto_path.exists()

        command = _build_code_open_command(
            target=target,
            new_window=new_window,
            goto_path=goto_path,
        )
        action = _run(command, dry_run=dry_run)
        if action["rc"] != 0:
            status = "WARN"
            detail = "failed to open VS Code"
        elif goto_missing:
            status = "WARN"
            detail = "opened VS Code (goto target missing)"
        else:
            status = "PASS"
            detail = "opened"
        steps.append(
            {
                "worker": worker,
                "status": status,
                "detail": detail,
                "path": target.as_posix(),
                "goto": goto_path.as_posix() if goto_path else "",
                "actions": [action],
            }
        )

    blocked_steps = [step for step in steps if step["status"] == "BLOCKED"]
    return {
        "run_id": run_id,
        "operation": "open",
        "status": "PASS" if not blocked_steps else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked_steps),
    }

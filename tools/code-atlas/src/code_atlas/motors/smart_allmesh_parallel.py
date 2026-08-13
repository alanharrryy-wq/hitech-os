#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Smart AllMesh parallel supervisor v2.

Runs multiple task-scoped AutoMesh jobs concurrently without mutating the repo.
V2 adds balanced lane scheduling, cooperative fail-fast cancellation restricted to
supervisor-owned child processes, deterministic parallel repo snapshots governed by
the same global worker budget, and strong child evidence provenance validation.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    from .prisma_automesh_runtime import (
        DEFAULT_GLOBAL_BUDGET_ROOT,
        GlobalWorkerBudget,
        ProgressReporter,
        atomic_zip_dir,
        capture_exception,
        extract_zip_verified,
        make_run_id,
        safe_rmtree,
        short_run_id,
        stream_command,
        write_json_atomic,
    )
except ImportError:
    from prisma_automesh_runtime import (
        DEFAULT_GLOBAL_BUDGET_ROOT,
        GlobalWorkerBudget,
        ProgressReporter,
        atomic_zip_dir,
        capture_exception,
        extract_zip_verified,
        make_run_id,
        safe_rmtree,
        short_run_id,
        stream_command,
        write_json_atomic,
    )

GLOBAL_WORKER_LIMIT = 18
DEFAULT_OUT = Path(r"F:\descargasf")
TEXT_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".scss", ".sass",
    ".json", ".md", ".yml", ".yaml", ".html", ".txt", ".ps1", ".py", ".prisma", ".svg",
}
EXCLUDE_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "out", ".turbo", ".cache",
    ".prisma_installer_backups", "coverage", "playwright-report", "test-results",
    ".venv", "venv", "__pycache__", ".pytest_cache", ".pnpm-store", "tmp", "temp",
    "_local", "backups", "backup", "salvage", "evidence", "archive", "archives",
}
REQUIRED_CHILD_EVIDENCE = (
    ".governance/current/AUTHORITY_READSET.lock.json",
    "reports/APP_IMPACT_MATRIX.md",
    "reports/CONTRACT_AND_GATE_MATRIX.json",
    "reports/MISSING_OR_UNMAPPED_RISK.md",
    "reports/AGENT_PROMPT_ENVELOPE.md",
    "reports/AUTHORITY_MESH_REPORT.md",
    "reports/LAYERS_MAP.json",
    "reports/LAYERS_MAP.md",
)


@dataclass(frozen=True)
class MeshTask:
    task_id: str
    task: str
    surface: str = ""


def _slug(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return (cleaned[:48] or fallback).lower()


def _run_git(repo: Path, args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=str(repo),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        shell=False,
    )
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _iter_repo_text_files(repo: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(repo, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        root_path = Path(root)
        try:
            relative_parts = root_path.relative_to(repo).parts
        except ValueError:
            relative_parts = ()
        if any(part in EXCLUDE_DIRS for part in relative_parts):
            continue
        for name in sorted(files):
            path = root_path / name
            if path.suffix.lower() in TEXT_EXTS:
                yield path


def _snapshot_entry(
    repo: Path,
    path: Path,
    index: int,
    budget: GlobalWorkerBudget | None,
) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    rel = path.relative_to(repo).as_posix()
    try:
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode):
            target = os.readlink(path)
            digest = hashlib.sha256(target.encode("utf-8", errors="surrogatepass")).hexdigest().upper()
            after = os.lstat(path)
            unstable = (
                before.st_mtime_ns != after.st_mtime_ns
                or before.st_size != after.st_size
                or target != os.readlink(path)
            )
            return rel, {
                "kind": "symlink",
                "size": before.st_size,
                "sha256": digest,
                "link_target": target,
                "unstable_during_capture": unstable,
            }, None
        if not stat.S_ISREG(before.st_mode):
            return rel, None, None

        if budget is None:
            digest = _sha256(path)
        else:
            with budget.lease(f"snapshot-{index}"):
                digest = _sha256(path)
        after = os.lstat(path)
        unstable = before.st_mtime_ns != after.st_mtime_ns or before.st_size != after.st_size
        return rel, {
            "kind": "file",
            "size": after.st_size,
            "sha256": digest,
            "unstable_during_capture": unstable,
        }, None
    except (FileNotFoundError, PermissionError, OSError) as exc:
        return rel, None, {
            "path": rel,
            "type": type(exc).__name__,
            "message": str(exc),
        }


def repo_snapshot(
    repo: Path,
    *,
    workers: int = GLOBAL_WORKER_LIMIT,
    budget_root: Path | None = None,
    run_id: str = "repo-snapshot",
) -> dict[str, Any]:
    """Deterministic content fingerprint; fails closed if capture itself is unstable."""
    head = _run_git(repo, ["git", "rev-parse", "HEAD"])
    status = _run_git(repo, ["git", "status", "--porcelain=v1", "--untracked-files=all"])
    paths = sorted(_iter_repo_text_files(repo), key=lambda value: value.relative_to(repo).as_posix())
    worker_count = max(1, min(GLOBAL_WORKER_LIMIT, int(workers), max(1, len(paths))))
    budget = (
        GlobalWorkerBudget(Path(budget_root), slots=GLOBAL_WORKER_LIMIT, run_id=f"{run_id}-snapshot")
        if budget_root is not None
        else None
    )
    files: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    try:
        if worker_count == 1:
            entries = [_snapshot_entry(repo, path, index, budget) for index, path in enumerate(paths)]
        else:
            with cf.ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="allmesh-snapshot") as executor:
                futures = [
                    executor.submit(_snapshot_entry, repo, path, index, budget)
                    for index, path in enumerate(paths)
                ]
                entries = [future.result() for future in futures]
    finally:
        if budget is not None:
            budget.close()

    unstable: list[str] = []
    for rel, entry, error in sorted(entries, key=lambda row: row[0]):
        if error is not None:
            errors.append(error)
            continue
        if entry is None:
            continue
        if entry.pop("unstable_during_capture", False):
            unstable.append(rel)
        files[rel] = entry

    canonical = json.dumps(
        {
            "head": head.get("stdout", "").strip(),
            "status": status.get("stdout", ""),
            "files": files,
        },
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    stable_capture = not unstable and not errors and head.get("returncode") == 0 and status.get("returncode") == 0
    return {
        "head": head,
        "status": status,
        "file_count": len(files),
        "files": files,
        "hash_workers": worker_count,
        "budget_root": str(budget_root) if budget_root is not None else "",
        "stable_capture": stable_capture,
        "unstable_during_capture": unstable[:200],
        "capture_errors": errors[:200],
        "fingerprint": hashlib.sha256(canonical).hexdigest().upper(),
    }


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_files = before.get("files", {})
    after_files = after.get("files", {})
    before_keys = set(before_files)
    after_keys = set(after_files)
    changed = sorted(
        key for key in before_keys & after_keys
        if before_files[key].get("sha256") != after_files[key].get("sha256")
        or before_files[key].get("size") != after_files[key].get("size")
        or before_files[key].get("kind") != after_files[key].get("kind")
        or before_files[key].get("link_target") != after_files[key].get("link_target")
    )
    stable = (
        bool(before.get("stable_capture"))
        and bool(after.get("stable_capture"))
        and before.get("fingerprint") == after.get("fingerprint")
    )
    return {
        "stable": stable,
        "before_capture_stable": bool(before.get("stable_capture")),
        "after_capture_stable": bool(after.get("stable_capture")),
        "before_fingerprint": before.get("fingerprint"),
        "after_fingerprint": after.get("fingerprint"),
        "head_before": before.get("head", {}).get("stdout", "").strip(),
        "head_after": after.get("head", {}).get("stdout", "").strip(),
        "status_before": before.get("status", {}).get("stdout", ""),
        "status_after": after.get("status", {}).get("stdout", ""),
        "added": sorted(after_keys - before_keys)[:200],
        "removed": sorted(before_keys - after_keys)[:200],
        "changed": changed[:200],
        "changed_count": len(changed),
        "capture_errors_before": before.get("capture_errors", [])[:200],
        "capture_errors_after": after.get("capture_errors", [])[:200],
        "unstable_before": before.get("unstable_during_capture", [])[:200],
        "unstable_after": after.get("unstable_during_capture", [])[:200],
    }


def parse_tasks(task_values: list[str], task_spec: str) -> list[MeshTask]:
    tasks: list[MeshTask] = []
    if task_spec:
        raw = json.loads(Path(task_spec).read_text(encoding="utf-8"))
        entries = raw.get("tasks") if isinstance(raw, dict) else raw
        if not isinstance(entries, list):
            raise ValueError("TASK_SPEC_INVALID: expected a list or {\"tasks\": [...]}.")
        for index, entry in enumerate(entries, 1):
            if isinstance(entry, str):
                text = entry.strip()
                surface = ""
                requested_id = ""
            elif isinstance(entry, dict):
                text = str(entry.get("task", "")).strip()
                surface = str(entry.get("surface", "")).strip()
                requested_id = str(entry.get("id", "")).strip()
            else:
                raise ValueError(f"TASK_SPEC_INVALID_ENTRY:{index}")
            if not text:
                raise ValueError(f"TASK_SPEC_EMPTY_TASK:{index}")
            task_id = _slug(requested_id or f"task-{index}", f"task-{index}")
            tasks.append(MeshTask(task_id=task_id, task=text, surface=surface))

    for value in task_values:
        text = value.strip()
        if text:
            index = len(tasks) + 1
            tasks.append(MeshTask(task_id=f"task-{index}", task=text, surface=""))

    if len(tasks) < 2:
        raise ValueError("PARALLEL_AUTOMESH_REQUIRES_AT_LEAST_TWO_TASKS")

    seen: set[str] = set()
    normalized: list[MeshTask] = []
    for index, item in enumerate(tasks, 1):
        base = _slug(item.task_id, f"task-{index}")
        candidate = base
        suffix = 2
        while candidate in seen:
            candidate = f"{base}-{suffix}"
            suffix += 1
        seen.add(candidate)
        normalized.append(MeshTask(candidate, item.task, item.surface))
    return normalized


def worker_caps(task_count: int, parallel: int, requested_workers: int) -> list[int]:
    """Balanced per-lane caps whose active sum is <=18 and uses all available budget."""
    active = max(1, min(GLOBAL_WORKER_LIMIT, parallel, task_count))
    requested = max(1, min(GLOBAL_WORKER_LIMIT, requested_workers))
    available = min(GLOBAL_WORKER_LIMIT, active * requested)
    base, remainder = divmod(available, active)
    caps = [base + (1 if index < remainder else 0) for index in range(active)]
    if any(cap < 1 or cap > requested for cap in caps):
        raise RuntimeError("PARALLEL_WORKER_CAP_RANGE_BROKEN")
    if sum(caps) > GLOBAL_WORKER_LIMIT:
        raise RuntimeError("PARALLEL_WORKER_CAP_INVARIANT_BROKEN")
    return caps


def _read_child_manifest(extracted_root: Path) -> dict[str, Any]:
    manifest_path = extracted_root / "RUN_MANIFEST.json"
    if not manifest_path.exists():
        raise RuntimeError(f"CHILD_RUN_MANIFEST_MISSING:{manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _norm_path(value: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(value)))


def validate_child_provenance(
    extracted_root: Path,
    manifest: dict[str, Any],
    *,
    expected_run_id: str,
    expected_task: str,
    expected_surface: str,
    expected_repo: Path,
    expected_budget_root: Path,
    expected_worker_cap: int,
    expected_git_head: str,
) -> dict[str, Any]:
    expected = {
        "kind": "PRISMA_AUTOMESH_RUN",
        "status": "PASS",
        "run_id": expected_run_id,
        "task": expected_task,
        "surface_argument": expected_surface,
        "workers_local_cap": expected_worker_cap,
        "global_worker_budget": GLOBAL_WORKER_LIMIT,
        "repo_git_head": expected_git_head,
    }
    mismatches: list[str] = []
    for key, value in expected.items():
        if manifest.get(key) != value:
            mismatches.append(f"{key}:expected={value!r}:actual={manifest.get(key)!r}")
    if _norm_path(str(manifest.get("repo", ""))) != _norm_path(expected_repo):
        mismatches.append("repo:path-mismatch")
    if _norm_path(str(manifest.get("budget_root", ""))) != _norm_path(expected_budget_root):
        mismatches.append("budget_root:path-mismatch")

    evidence_hashes = manifest.get("evidence_hashes")
    if not isinstance(evidence_hashes, dict):
        mismatches.append("evidence_hashes:missing-or-invalid")
        evidence_hashes = {}

    verified_hashes: dict[str, str] = {}
    for rel in REQUIRED_CHILD_EVIDENCE:
        path = extracted_root / rel
        if not path.exists() or not path.is_file():
            mismatches.append(f"evidence_missing:{rel}")
            continue
        actual_hash = _sha256(path)
        expected_hash = str(evidence_hashes.get(rel, "")).upper()
        if actual_hash != expected_hash:
            mismatches.append(f"evidence_hash_mismatch:{rel}")
        verified_hashes[rel] = actual_hash

    if mismatches:
        raise RuntimeError("CHILD_PROVENANCE_MISMATCH:" + "|".join(mismatches))
    return {
        "verified": True,
        "required_evidence_count": len(REQUIRED_CHILD_EVIDENCE),
        "verified_hashes": verified_hashes,
    }


def run_lane_scheduler(
    tasks: list[MeshTask],
    lane_caps: list[int],
    runner: Callable[[int, MeshTask, int, int, threading.Event], dict[str, Any]],
    on_complete: Callable[[dict[str, Any], int], None] | None = None,
) -> list[dict[str, Any]]:
    """Fixed lanes eliminate cap handoff races while fail-fast cancels queued/running work."""
    queue = deque(enumerate(tasks))
    queue_lock = threading.Lock()
    completed: list[dict[str, Any]] = []
    completed_lock = threading.Lock()
    cancel_event = threading.Event()

    def lane_worker(lane_index: int, lane_cap: int) -> None:
        while not cancel_event.is_set():
            with queue_lock:
                if not queue:
                    return
                index, item = queue.popleft()
            try:
                result = runner(index, item, lane_index, lane_cap, cancel_event)
            except BaseException:
                cancel_event.set()
                raise
            with completed_lock:
                completed.append(result)
                done = len(completed)
            if on_complete is not None:
                on_complete(result, done)

    first_error: BaseException | None = None
    with cf.ThreadPoolExecutor(max_workers=len(lane_caps), thread_name_prefix="allmesh-lane") as executor:
        futures = [
            executor.submit(lane_worker, lane_index, lane_cap)
            for lane_index, lane_cap in enumerate(lane_caps)
        ]
        for future in cf.as_completed(futures):
            try:
                future.result()
            except BaseException as exc:
                if first_error is None:
                    first_error = exc
                    cancel_event.set()
                    for pending in futures:
                        pending.cancel()
        if first_error is not None:
            raise first_error

    return completed


def run_parallel(args: argparse.Namespace) -> int:
    tasks = parse_tasks(list(args.task or []), args.task_spec)
    parallel = max(1, min(GLOBAL_WORKER_LIMIT, int(args.parallel), len(tasks)))
    caps = worker_caps(len(tasks), parallel, int(args.workers))

    repo = Path(args.repo).expanduser().resolve()
    if not (repo / ".git").exists():
        raise RuntimeError(f"NO_GIT_REPO:{repo}")

    out_root = Path(args.out_root).expanduser()
    out_root.mkdir(parents=True, exist_ok=True)
    budget_root = Path(args.budget_root).expanduser()
    budget_root.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id.strip() or make_run_id("allmesh-parallel")
    short_id = short_run_id(run_id)
    stamp = dt.datetime.now().strftime("%d%m %H%M%S")
    work_root = out_root / ".allmesh_parallel_work" / run_id
    staging = work_root / "staging"
    final_payload = work_root / "final_payload"
    progress_path = staging / "parallel_progress.jsonl"
    staging.mkdir(parents=True, exist_ok=False)
    final_payload.mkdir(parents=True, exist_ok=False)

    reporter = ProgressReporter(
        run_id=run_id,
        jsonl_path=progress_path,
        width=34,
        component="smart-allmesh-parallel-v2",
    )
    reporter.start_heartbeat(5.0)

    result_zip = out_root / f"allmesh-par_{stamp}_{short_id}_result.zip"
    fail_zip = out_root / f"allmesh-par_{stamp}_{short_id}_fail.zip"
    report: dict[str, Any] = {
        "kind": "PRISMA_SMART_ALLMESH_PARALLEL_CERTIFICATION",
        "version": "2.0.0",
        "run_id": run_id,
        "status": "PENDING",
        "repo": str(repo),
        "task_count": len(tasks),
        "parallel_limit": parallel,
        "global_worker_limit": GLOBAL_WORKER_LIMIT,
        "requested_workers_per_task": max(1, min(GLOBAL_WORKER_LIMIT, int(args.workers))),
        "lane_worker_caps": caps,
        "lane_worker_sum_cap": sum(caps),
        "shared_budget_root": str(budget_root),
        "read_only_repo": True,
        "fail_fast": True,
        "children": [],
    }
    final_zip: Path | None = None

    try:
        reporter.emit(3, "capturando snapshot inicial del repo")
        before = repo_snapshot(
            repo,
            workers=GLOBAL_WORKER_LIMIT,
            budget_root=budget_root,
            run_id=f"{run_id}-before",
        )
        write_json_atomic(final_payload / "REPO_SNAPSHOT_BEFORE.json", before)
        if not before.get("stable_capture"):
            raise RuntimeError("REPO_SNAPSHOT_INITIAL_CAPTURE_UNSTABLE")
        expected_git_head = before.get("head", {}).get("stdout", "").strip()

        automesh = Path(__file__).resolve().with_name("smart_allmesh_automesh.py")
        if not automesh.exists():
            raise RuntimeError(f"NO_AUTOMESH:{automesh}")

        reporter.emit(
            12,
            "lanzando AutoMesh independientes con lanes elásticos",
            done=0,
            total=len(tasks),
            details={"parallel": parallel, "lane_worker_caps": caps, "sum": sum(caps)},
        )

        def run_one(
            index: int,
            item: MeshTask,
            lane_index: int,
            local_workers: int,
            cancel_event: threading.Event,
        ) -> dict[str, Any]:
            if cancel_event.is_set():
                raise RuntimeError(f"{item.task_id}:CANCELLED_BEFORE_START")
            child_run_id = f"{run_id}__{item.task_id}__{index:03d}"
            child_root = staging / "tasks" / item.task_id
            child_out = child_root / "automesh_out"
            child_log = child_root / "automesh.log"
            child_progress = child_root / "automesh_progress.jsonl"
            child_out.mkdir(parents=True, exist_ok=False)

            command = [
                sys.executable,
                str(automesh),
                "--task", item.task,
                "--repo", str(repo),
                "--out", str(child_out),
                "--workers", str(local_workers),
                "--shards", str(max(local_workers, min(216, int(args.shards)))),
                "--max-files", str(max(1, int(args.max_files))),
                "--max-mb", str(max(1, int(args.max_mb))),
                "--run-id", child_run_id,
                "--progress-jsonl", str(child_progress),
                "--budget-root", str(budget_root),
            ]
            if item.surface:
                command += ["--surface", item.surface]

            child = stream_command(
                command,
                cwd=None,
                log_path=child_log,
                reporter=reporter,
                heartbeat_label=f"{item.task_id}: AutoMesh trabajando",
                cancel_event=cancel_event,
            )
            marker_name = "OK_RESULT_ZIP" if child["returncode"] == 0 else "FAIL_ZIP"
            marker_path = child.get("markers", {}).get(marker_name)
            if child.get("cancelled"):
                raise RuntimeError(f"{item.task_id}:CANCELLED_BY_FAIL_FAST")
            if not marker_path:
                cancel_event.set()
                raise RuntimeError(f"{item.task_id}:AUTOMESH_DID_NOT_REPORT_{marker_name}")
            child_zip = Path(marker_path)
            if not child_zip.exists():
                cancel_event.set()
                raise RuntimeError(f"{item.task_id}:AUTOMESH_ZIP_MISSING:{child_zip}")

            extracted = final_payload / "tasks" / item.task_id / "authority_mesh"
            extraction = extract_zip_verified(child_zip, extracted)
            manifest = _read_child_manifest(extracted)
            child_zip_hash = _sha256(child_zip)

            if child["returncode"] != 0 or manifest.get("status") != "PASS":
                cancel_event.set()
                raise RuntimeError(f"{item.task_id}:CHILD_AUTOMESH_FAIL")

            provenance = validate_child_provenance(
                extracted,
                manifest,
                expected_run_id=child_run_id,
                expected_task=item.task,
                expected_surface=item.surface,
                expected_repo=repo,
                expected_budget_root=budget_root,
                expected_worker_cap=local_workers,
                expected_git_head=expected_git_head,
            )

            if child_log.exists():
                target_log = final_payload / "tasks" / item.task_id / "automesh.log"
                target_log.parent.mkdir(parents=True, exist_ok=True)
                target_log.write_text(child_log.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

            return {
                "task_id": item.task_id,
                "task": item.task,
                "surface": item.surface,
                "run_id": child_run_id,
                "lane_index": lane_index,
                "local_worker_cap": local_workers,
                "returncode": child["returncode"],
                "zip": extraction,
                "zip_sha256": child_zip_hash,
                "manifest_status": manifest.get("status"),
                "manifest_budget_root": manifest.get("budget_root"),
                "provenance": provenance,
            }

        completed_lock = threading.Lock()

        def on_complete(_result: dict[str, Any], done: int) -> None:
            with completed_lock:
                reporter.emit(
                    12 + int(done * 66 / len(tasks)),
                    "AutoMesh paralelo completado",
                    done=done,
                    total=len(tasks),
                )

        completed = run_lane_scheduler(tasks, caps, run_one, on_complete=on_complete)
        completed.sort(key=lambda item: item["task_id"])
        run_ids = [item["run_id"] for item in completed]
        if len(run_ids) != len(set(run_ids)):
            raise RuntimeError("CHILD_RUN_ID_COLLISION")
        report["children"] = completed
        report["unique_child_run_ids"] = True
        report["provenance_verified"] = all(item.get("provenance", {}).get("verified") for item in completed)

        reporter.emit(82, "capturando snapshot final del repo")
        after = repo_snapshot(
            repo,
            workers=GLOBAL_WORKER_LIMIT,
            budget_root=budget_root,
            run_id=f"{run_id}-after",
        )
        write_json_atomic(final_payload / "REPO_SNAPSHOT_AFTER.json", after)
        drift = compare_snapshots(before, after)
        write_json_atomic(final_payload / "REPO_DRIFT_REPORT.json", drift)
        report["repo_drift"] = drift
        if not drift["stable"]:
            raise RuntimeError("REPO_CHANGED_DURING_PARALLEL_AUTOMESH")

        report["status"] = "PASS"
        report["certification"] = "PASS_AUTOMESH_MULTI_TASK_CROSS_PROCESS_PARALLEL_SAFE_V2"
        report["finished_at"] = dt.datetime.now().isoformat()
        write_json_atomic(final_payload / "PARALLEL_CERTIFICATION.json", report)
        (final_payload / "PARALLEL_CERTIFICATION.md").write_text(
            "# PRISMA AutoMesh Parallel Certification v2\n\n"
            f"- Status: `{report['status']}`\n"
            f"- Certification: `{report['certification']}`\n"
            f"- Tasks: `{len(tasks)}`\n"
            f"- Parallel lanes: `{parallel}`\n"
            f"- Global worker contract: `{GLOBAL_WORKER_LIMIT}`\n"
            f"- Lane caps: `{caps}`\n"
            f"- Sum of active lane caps: `{sum(caps)}`\n"
            f"- Repo stable: `{drift['stable']}`\n"
            f"- Provenance verified: `{report['provenance_verified']}`\n"
            f"- Fail-fast: `true`\n"
            f"- Shared budget root: `{budget_root}`\n",
            encoding="utf-8",
        )
        if progress_path.exists():
            (final_payload / "parallel_progress.jsonl").write_text(
                progress_path.read_text(encoding="utf-8", errors="replace"),
                encoding="utf-8",
            )

        reporter.emit(94, "publicando ZIP final atómico")
        atomic_zip_dir(final_payload, result_zip, include_root=False, compression_level=8)
        final_zip = result_zip
        reporter.emit(100, "AutoMesh paralelo v2 certificado", status="PASS", details={"zip": str(result_zip)})
        print(f"FINAL_RESULT_ZIP={result_zip}", flush=True)
        return 0

    except Exception as exc:
        report["status"] = "FAIL"
        report["certification"] = "FAIL_AUTOMESH_MULTI_TASK_PARALLEL_CERTIFICATION_V2"
        report["error"] = capture_exception(exc)
        report["finished_at"] = dt.datetime.now().isoformat()
        try:
            write_json_atomic(final_payload / "PARALLEL_CERTIFICATION.json", report)
            (final_payload / "ERROR.txt").write_text(
                report["error"].get("traceback", repr(exc)),
                encoding="utf-8",
                errors="replace",
            )
            if progress_path.exists():
                (final_payload / "parallel_progress.jsonl").write_text(
                    progress_path.read_text(encoding="utf-8", errors="replace"),
                    encoding="utf-8",
                )
            reporter.emit(96, "empaquetando fail ZIP atómico", status="FAIL")
            atomic_zip_dir(final_payload, fail_zip, include_root=False, compression_level=8)
            final_zip = fail_zip
            reporter.emit(100, "certificación v2 falló", status="FAIL", details={"zip": str(fail_zip)})
            print(f"FINAL_FAIL_ZIP={fail_zip}", flush=True)
        except Exception as packaging_exc:
            print("PARALLEL_AUTOMESH_FATAL_PACKAGING_ERROR=" + json.dumps(capture_exception(packaging_exc), ensure_ascii=False), flush=True)
            print(f"PARALLEL_AUTOMESH_WORK_ROOT_PRESERVED={work_root}", flush=True)
        return 1
    finally:
        reporter.stop_heartbeat()
        if final_zip is not None and final_zip.exists():
            safe_rmtree(work_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA Smart AllMesh parallel supervisor v2")
    parser.add_argument("--repo", default=os.environ.get("ALLMESH_REPO", r"F:\repos\hitech-os"))
    parser.add_argument("--out-root", default=os.environ.get("ALLMESH_OUT_ROOT", str(DEFAULT_OUT)))
    parser.add_argument("--budget-root", default=str(DEFAULT_GLOBAL_BUDGET_ROOT))
    parser.add_argument("--task", action="append", default=[], help="Repeat at least twice for parallel tasks.")
    parser.add_argument("--task-spec", default="", help="JSON file containing tasks with optional id/surface.")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--workers", type=int, default=18, help="Requested workers per lane; coordinator balances the active sum to <=18.")
    parser.add_argument("--shards", type=int, default=54)
    parser.add_argument("--max-files", type=int, default=120)
    parser.add_argument("--max-mb", type=int, default=40)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()
    return run_parallel(args)


if __name__ == "__main__":
    raise SystemExit(main())

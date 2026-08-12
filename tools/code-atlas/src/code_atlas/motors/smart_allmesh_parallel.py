#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Smart AllMesh parallel supervisor v1.

Runs multiple task-scoped AutoMesh jobs concurrently without mutating the repo.
The supervisor keeps every task in a private workspace, constrains the sum of
local child worker caps to 18, reuses the runtime cross-process worker budget,
verifies repository stability before publishing, and emits one atomic final ZIP.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from .prisma_automesh_runtime import (
        DEFAULT_GLOBAL_BUDGET_ROOT,
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
    for root, dirs, files in os.walk(repo):
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


def repo_snapshot(repo: Path) -> dict[str, Any]:
    """Content fingerprint used to fail closed if the source tree moves mid-run."""
    head = _run_git(repo, ["git", "rev-parse", "HEAD"])
    status = _run_git(repo, ["git", "status", "--porcelain=v1", "--untracked-files=all"])
    files: dict[str, dict[str, Any]] = {}
    for path in _iter_repo_text_files(repo):
        try:
            rel = path.relative_to(repo).as_posix()
            stat = path.stat()
            files[rel] = {
                "size": stat.st_size,
                "sha256": _sha256(path),
            }
        except (FileNotFoundError, PermissionError, OSError):
            continue
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
    return {
        "head": head,
        "status": status,
        "file_count": len(files),
        "files": files,
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
    )
    return {
        "stable": before.get("fingerprint") == after.get("fingerprint"),
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
    active = max(1, min(GLOBAL_WORKER_LIMIT, parallel, task_count))
    requested = max(1, min(GLOBAL_WORKER_LIMIT, requested_workers))
    base, remainder = divmod(GLOBAL_WORKER_LIMIT, active)
    caps = [min(requested, base + (1 if index < remainder else 0)) for index in range(active)]
    if sum(caps) > GLOBAL_WORKER_LIMIT:
        raise RuntimeError("PARALLEL_WORKER_CAP_INVARIANT_BROKEN")
    return caps


def _read_child_manifest(extracted_root: Path) -> dict[str, Any]:
    manifest_path = extracted_root / "RUN_MANIFEST.json"
    if not manifest_path.exists():
        raise RuntimeError(f"CHILD_RUN_MANIFEST_MISSING:{manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


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
        component="smart-allmesh-parallel",
    )
    reporter.start_heartbeat(5.0)

    result_zip = out_root / f"allmesh-par_{stamp}_{short_id}_result.zip"
    fail_zip = out_root / f"allmesh-par_{stamp}_{short_id}_fail.zip"
    report: dict[str, Any] = {
        "kind": "PRISMA_SMART_ALLMESH_PARALLEL_CERTIFICATION",
        "version": "1.0.0",
        "run_id": run_id,
        "status": "PENDING",
        "repo": str(repo),
        "task_count": len(tasks),
        "parallel_limit": parallel,
        "global_worker_limit": GLOBAL_WORKER_LIMIT,
        "requested_workers_per_task": max(1, min(GLOBAL_WORKER_LIMIT, int(args.workers))),
        "wave_worker_caps": caps,
        "wave_worker_sum_cap": sum(caps),
        "shared_budget_root": str(budget_root),
        "read_only_repo": True,
        "children": [],
    }
    final_zip: Path | None = None

    try:
        reporter.emit(3, "capturando snapshot inicial del repo")
        before = repo_snapshot(repo)
        write_json_atomic(final_payload / "REPO_SNAPSHOT_BEFORE.json", before)

        automesh = Path(__file__).resolve().with_name("smart_allmesh_automesh.py")
        if not automesh.exists():
            raise RuntimeError(f"NO_AUTOMESH:{automesh}")

        reporter.emit(
            12,
            "lanzando AutoMesh independientes con presupuesto coordinado",
            done=0,
            total=len(tasks),
            details={"parallel": parallel, "worker_caps": caps},
        )

        def run_one(index_and_task: tuple[int, MeshTask]) -> dict[str, Any]:
            index, item = index_and_task
            slot = index % parallel
            local_workers = caps[slot]
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
            )
            marker_name = "OK_RESULT_ZIP" if child["returncode"] == 0 else "FAIL_ZIP"
            marker_path = child.get("markers", {}).get(marker_name)
            if not marker_path:
                raise RuntimeError(f"{item.task_id}:AUTOMESH_DID_NOT_REPORT_{marker_name}")
            child_zip = Path(marker_path)
            if not child_zip.exists():
                raise RuntimeError(f"{item.task_id}:AUTOMESH_ZIP_MISSING:{child_zip}")

            extracted = final_payload / "tasks" / item.task_id / "authority_mesh"
            extraction = extract_zip_verified(child_zip, extracted)
            manifest = _read_child_manifest(extracted)
            if manifest.get("run_id") != child_run_id:
                raise RuntimeError(f"{item.task_id}:RUN_ID_MISMATCH")
            if child["returncode"] != 0 or manifest.get("status") != "PASS":
                raise RuntimeError(f"{item.task_id}:CHILD_AUTOMESH_FAIL")

            if child_log.exists():
                target_log = final_payload / "tasks" / item.task_id / "automesh.log"
                target_log.parent.mkdir(parents=True, exist_ok=True)
                target_log.write_text(child_log.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

            return {
                "task_id": item.task_id,
                "task": item.task,
                "surface": item.surface,
                "run_id": child_run_id,
                "local_worker_cap": local_workers,
                "returncode": child["returncode"],
                "zip": extraction,
                "manifest_status": manifest.get("status"),
                "manifest_budget_root": manifest.get("budget_root"),
            }

        completed: list[dict[str, Any]] = []
        with cf.ThreadPoolExecutor(max_workers=parallel, thread_name_prefix="allmesh-parallel") as executor:
            future_map = {
                executor.submit(run_one, pair): pair[1].task_id
                for pair in enumerate(tasks)
            }
            for future in cf.as_completed(future_map):
                completed.append(future.result())
                done = len(completed)
                reporter.emit(
                    12 + int(done * 66 / len(tasks)),
                    "AutoMesh paralelo completado",
                    done=done,
                    total=len(tasks),
                )

        completed.sort(key=lambda item: item["task_id"])
        run_ids = [item["run_id"] for item in completed]
        if len(run_ids) != len(set(run_ids)):
            raise RuntimeError("CHILD_RUN_ID_COLLISION")
        report["children"] = completed
        report["unique_child_run_ids"] = True

        reporter.emit(82, "capturando snapshot final del repo")
        after = repo_snapshot(repo)
        write_json_atomic(final_payload / "REPO_SNAPSHOT_AFTER.json", after)
        drift = compare_snapshots(before, after)
        write_json_atomic(final_payload / "REPO_DRIFT_REPORT.json", drift)
        report["repo_drift"] = drift
        if not drift["stable"]:
            raise RuntimeError("REPO_CHANGED_DURING_PARALLEL_AUTOMESH")

        report["status"] = "PASS"
        report["certification"] = "PASS_AUTOMESH_MULTI_TASK_CROSS_PROCESS_PARALLEL_SAFE"
        report["finished_at"] = dt.datetime.now().isoformat()
        write_json_atomic(final_payload / "PARALLEL_CERTIFICATION.json", report)
        (final_payload / "PARALLEL_CERTIFICATION.md").write_text(
            "# PRISMA AutoMesh Parallel Certification\n\n"
            f"- Status: `{report['status']}`\n"
            f"- Certification: `{report['certification']}`\n"
            f"- Tasks: `{len(tasks)}`\n"
            f"- Parallel processes: `{parallel}`\n"
            f"- Global worker contract: `{GLOBAL_WORKER_LIMIT}`\n"
            f"- Sum of local caps per wave: `{sum(caps)}`\n"
            f"- Repo stable: `{drift['stable']}`\n"
            f"- Unique child run IDs: `true`\n"
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
        reporter.emit(100, "AutoMesh paralelo certificado", status="PASS", details={"zip": str(result_zip)})
        print(f"FINAL_RESULT_ZIP={result_zip}", flush=True)
        return 0

    except Exception as exc:
        report["status"] = "FAIL"
        report["certification"] = "FAIL_AUTOMESH_MULTI_TASK_PARALLEL_CERTIFICATION"
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
            reporter.emit(100, "certificación falló", status="FAIL", details={"zip": str(fail_zip)})
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
    parser = argparse.ArgumentParser(description="PRISMA Smart AllMesh parallel supervisor v1")
    parser.add_argument("--repo", default=os.environ.get("ALLMESH_REPO", r"F:\repos\hitech-os"))
    parser.add_argument("--out-root", default=os.environ.get("ALLMESH_OUT_ROOT", str(DEFAULT_OUT)))
    parser.add_argument("--budget-root", default=str(DEFAULT_GLOBAL_BUDGET_ROOT))
    parser.add_argument("--task", action="append", default=[], help="Repeat at least twice for parallel tasks.")
    parser.add_argument("--task-spec", default="", help="JSON file containing tasks with optional id/surface.")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--workers", type=int, default=18, help="Requested local workers per task; coordinator clamps the wave sum to 18.")
    parser.add_argument("--shards", type=int, default=54)
    parser.add_argument("--max-files", type=int, default=120)
    parser.add_argument("--max-mb", type=int, default=40)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()
    return run_parallel(args)


if __name__ == "__main__":
    raise SystemExit(main())

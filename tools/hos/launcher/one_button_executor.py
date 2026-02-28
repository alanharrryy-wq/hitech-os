
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WORKERS: tuple[str, ...] = (
    "A_core",
    "B_tooling",
    "C_features",
    "D_validation",
    "Z_aggregator",
)

OFFICIAL_SHARED_BASE = Path(r"F:\repos\hitech-os\factory\shared\01 Prompt_Packs")
INBOX_DIR_NAME = "01 En_bruto"
RUNS_DIR_NAME = "02 Runs"
ARCHIVE_DIR_NAME = "03 Archive"
NEXT_PACK_NAME = "PROMPTS_PACK_NEXT.txt"
NEXT_PACK_TMP_NAME = "PROMPTS_PACK_NEXT.tmp"

EXIT_SUCCESS = 0
EXIT_PIPELINE_FAILURE = 2
EXIT_PREFLIGHT_FAILURE = 3


class PreflightError(RuntimeError):
    pass


class PipelineError(RuntimeError):
    pass


@dataclass(frozen=True)
class SharedPaths:
    base: Path
    inbox: Path
    runs: Path
    archive: Path


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    pack_dir: Path
    raw_pack: Path
    materialized_dir: Path
    workers_dir: Path
    debug_dir: Path


@dataclass
class CommandRecord:
    stage: str
    command: list[str]
    rc: int
    output_tail: str


class ExecutorLogger:
    def __init__(self) -> None:
        self._log_path: Path | None = None

    def bind(self, log_path: Path) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_path = log_path
        self.log("executor", f"log_path={log_path.as_posix()}")

    def log(self, stage: str, message: str, *, level: str = "INFO") -> None:
        stamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
        line = f"{stamp} [{level}] [{stage}] {message.rstrip()}"
        print(line, flush=True)
        if self._log_path:
            with self._log_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(line + "\n")


def _truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _tail_lines(text: str, max_lines: int = 40) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    lines = stripped.splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[-max_lines:])


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def _run_capture(
    *,
    stage: str,
    command: list[str],
    cwd: Path,
    logger: ExecutorLogger,
    records: list[CommandRecord],
    timeout_seconds: float | None = None,
) -> subprocess.CompletedProcess[str]:
    logger.log(stage, "CMD: " + " ".join(command))
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        tail = _tail_lines((exc.stdout or "") + "\n" + (exc.stderr or ""))
        records.append(CommandRecord(stage=stage, command=list(command), rc=124, output_tail=tail))
        raise PipelineError(f"command timeout in stage '{stage}'") from exc
    except OSError as exc:
        records.append(CommandRecord(stage=stage, command=list(command), rc=127, output_tail=str(exc)))
        raise PipelineError(f"command launch failed in stage '{stage}': {exc}") from exc

    output_tail = _tail_lines(completed.stdout + ("\n" + completed.stderr if completed.stderr else ""))
    records.append(
        CommandRecord(
            stage=stage,
            command=list(command),
            rc=int(completed.returncode),
            output_tail=output_tail,
        )
    )
    logger.log(stage, f"RC={completed.returncode}")
    if output_tail:
        logger.log(stage, "OUTPUT_TAIL:\n" + output_tail, level="CMD")
    return completed


def _run_stream(
    *,
    stage: str,
    command: list[str],
    cwd: Path,
    logger: ExecutorLogger,
    records: list[CommandRecord],
) -> int:
    logger.log(stage, "CMD: " + " ".join(command))
    lines: list[str] = []
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        records.append(CommandRecord(stage=stage, command=list(command), rc=127, output_tail=str(exc)))
        raise PipelineError(f"command launch failed in stage '{stage}': {exc}") from exc

    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\r\n")
        lines.append(line)
        logger.log(stage, line, level="CMD")
    rc = int(process.wait())
    output_tail = _tail_lines("\n".join(lines))
    records.append(CommandRecord(stage=stage, command=list(command), rc=rc, output_tail=output_tail))
    logger.log(stage, f"RC={rc}")
    return rc


def _parse_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty JSON payload")
    return dict(json.loads(stripped))

def _git_toplevel(start_dir: Path) -> Path | None:
    if shutil.which("git") is None:
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(start_dir), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    output = completed.stdout.strip()
    if not output:
        return None
    return Path(output).resolve()


def _resolve_repo_root() -> Path:
    fallback = Path(r"F:\repos\hitech-os")
    script_repo_hint = Path(__file__).resolve().parents[3]
    for probe in (script_repo_hint, Path.cwd()):
        detected = _git_toplevel(probe)
        if detected:
            return detected
    if fallback.exists():
        return fallback.resolve()
    raise PreflightError("unable to resolve repository root via git and fallback path is missing")


def _resolve_powershell() -> str:
    for command in ("pwsh", "powershell"):
        resolved = shutil.which(command)
        if resolved:
            return resolved
    raise PreflightError("PowerShell executable is not available in PATH")


def _resolve_code_command() -> str | None:
    for command in ("code", "code.cmd"):
        resolved = shutil.which(command)
        if resolved:
            return resolved

    local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
    program_files = os.environ.get("ProgramFiles", "").strip()
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "").strip()
    candidates = [
        Path(local_appdata) / "Programs" / "Microsoft VS Code" / "Code.exe" if local_appdata else None,
        Path(program_files) / "Microsoft VS Code" / "Code.exe" if program_files else None,
        Path(program_files_x86) / "Microsoft VS Code" / "Code.exe" if program_files_x86 else None,
        Path(r"C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
    ]
    for item in candidates:
        if item and item.exists():
            return str(item)
    return None


def _ensure_shared_paths(base: Path) -> SharedPaths:
    base.mkdir(parents=True, exist_ok=True)
    inbox = base / INBOX_DIR_NAME
    runs = base / RUNS_DIR_NAME
    archive = base / ARCHIVE_DIR_NAME
    inbox.mkdir(parents=True, exist_ok=True)
    runs.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)
    return SharedPaths(base=base, inbox=inbox, runs=runs, archive=archive)


def _resolve_inbox_pack(inbox_dir: Path) -> Path:
    files = [item for item in inbox_dir.iterdir() if item.is_file()]
    txt_candidates = sorted(item for item in files if item.suffix.lower() == ".txt")
    next_txt = inbox_dir / NEXT_PACK_NAME
    if not next_txt.exists():
        if (inbox_dir / NEXT_PACK_TMP_NAME).exists():
            raise PreflightError(
                f"inbox ready signal not received yet: expected {NEXT_PACK_NAME}, found only {NEXT_PACK_TMP_NAME}"
            )
        raise PreflightError(f"missing inbox pack: {next_txt.as_posix()}")

    if len(txt_candidates) != 1 or txt_candidates[0].name.lower() != NEXT_PACK_NAME.lower():
        found = ", ".join(item.name for item in txt_candidates) if txt_candidates else "<none>"
        raise PreflightError(
            "inbox must contain exactly one candidate .txt pack named "
            f"{NEXT_PACK_NAME}; found: {found}"
        )

    try:
        text = next_txt.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PreflightError(f"inbox pack is not UTF-8: {next_txt.as_posix()} ({exc})") from exc
    except OSError as exc:
        raise PreflightError(f"inbox pack is not readable: {next_txt.as_posix()} ({exc})") from exc

    if not text.strip():
        raise PreflightError(f"inbox pack is empty: {next_txt.as_posix()}")
    return next_txt


def _collect_existing_run_ids(day_prefix: str, repo_root: Path) -> set[str]:
    found: set[str] = set()
    roots = [
        repo_root / "tools" / "codex" / "runs",
        repo_root / "tools" / "codex" / "prompts",
        repo_root / "tools" / "codex" / "prompt_zips",
    ]
    pattern = re.compile(rf"^{re.escape(day_prefix)}_(\d+)$")
    for root in roots:
        if not root.exists():
            continue
        if root.name == "prompt_zips":
            entries = [item.stem for item in root.glob("*.zip") if item.is_file()]
        else:
            entries = [item.name for item in root.iterdir()]
        for name in entries:
            if pattern.fullmatch(name):
                found.add(name)
    return found


def _fallback_next_run_id(repo_root: Path) -> str:
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
    existing = _collect_existing_run_ids(day, repo_root=repo_root)
    max_seq = 0
    for run_id in existing:
        try:
            seq = int(run_id.rsplit("_", 1)[1])
        except (IndexError, ValueError):
            continue
        max_seq = max(max_seq, seq)
    return f"{day}_{max_seq + 1}"


def _generate_run_id(repo_root: Path, logger: ExecutorLogger, records: list[CommandRecord]) -> str:
    validator_path = repo_root / "tools" / "codex" / "dispatch" / "validator.py"
    command = [sys.executable, str(validator_path), "next-run-id"]
    completed = _run_capture(
        stage="run_id_generate",
        command=command,
        cwd=repo_root,
        logger=logger,
        records=records,
    )
    if completed.returncode == 0:
        try:
            payload = _parse_json(completed.stdout)
            run_id = str(payload.get("run_id", "")).strip()
            if run_id:
                return run_id
        except Exception:
            pass

    fallback = _fallback_next_run_id(repo_root=repo_root)
    logger.log("run_id_generate", f"fallback run_id selected: {fallback}", level="WARN")
    return fallback


def _create_run_paths(shared_runs_root: Path, run_id: str) -> RunPaths:
    run_dir = shared_runs_root / run_id
    pack_dir = run_dir / "pack"
    raw_pack = pack_dir / "raw_pack.txt"
    materialized_dir = pack_dir / "materialized"
    workers_dir = run_dir / "workers"
    debug_dir = run_dir / "_debug"

    for path in (pack_dir, materialized_dir, workers_dir, debug_dir):
        path.mkdir(parents=True, exist_ok=True)

    return RunPaths(
        run_dir=run_dir,
        pack_dir=pack_dir,
        raw_pack=raw_pack,
        materialized_dir=materialized_dir,
        workers_dir=workers_dir,
        debug_dir=debug_dir,
    )


def _canonical_run_root(repo_root: Path, run_id: str) -> Path:
    return repo_root / "tools" / "codex" / "runs" / run_id

def _normalize_compare(path: Path) -> str:
    return str(path.resolve(strict=False)).rstrip("\\/").lower()


def _ensure_worker_junction(
    *,
    link_path: Path,
    target_path: Path,
    repo_root: Path,
    logger: ExecutorLogger,
    records: list[CommandRecord],
) -> None:
    target_path.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(str(link_path)):
        if link_path.exists() and _normalize_compare(link_path) == _normalize_compare(target_path):
            logger.log("junction", f"reusing junction: {link_path.as_posix()} -> {target_path.as_posix()}")
            return
        raise PreflightError(
            "worker link path already exists with unexpected target/type: "
            f"{link_path.as_posix()} (expected target: {target_path.as_posix()})"
        )

    link_path.parent.mkdir(parents=True, exist_ok=True)
    command = ["cmd", "/c", "mklink", "/J", str(link_path), str(target_path)]
    completed = _run_capture(
        stage=f"junction_create_{link_path.name}",
        command=command,
        cwd=repo_root,
        logger=logger,
        records=records,
    )
    if completed.returncode != 0:
        raise PreflightError(
            "failed creating worker junction: "
            f"{link_path.as_posix()} -> {target_path.as_posix()}"
        )
    if not link_path.exists():
        raise PreflightError(f"junction creation did not produce path: {link_path.as_posix()}")
    if _normalize_compare(link_path) != _normalize_compare(target_path):
        raise PreflightError(
            "junction target mismatch after creation: "
            f"{link_path.as_posix()} -> {link_path.resolve(strict=False).as_posix()} "
            f"(expected {target_path.as_posix()})"
        )


def _validate_workers_dir_shape(workers_dir: Path) -> None:
    entries = {item.name for item in workers_dir.iterdir()}
    expected = set(WORKERS)
    unexpected = sorted(entries - expected)
    missing = sorted(expected - entries)
    if unexpected or missing:
        raise PreflightError(
            "workers directory shape mismatch; "
            f"missing={','.join(missing) if missing else '<none>'}; "
            f"unexpected={','.join(unexpected) if unexpected else '<none>'}"
        )


def _materialize_pack_precheck(
    *,
    repo_root: Path,
    run_id: str,
    pack_path: Path,
    materialized_mirror_dir: Path,
    logger: ExecutorLogger,
    records: list[CommandRecord],
) -> None:
    validator_path = repo_root / "tools" / "codex" / "dispatch" / "validator.py"
    command = [
        sys.executable,
        str(validator_path),
        "materialize-pack",
        "--run-id",
        run_id,
        "--pack-path",
        str(pack_path),
    ]
    completed = _run_capture(
        stage="materialize_pack_precheck",
        command=command,
        cwd=repo_root,
        logger=logger,
        records=records,
    )
    if completed.returncode != 0:
        raise PreflightError("materialize-pack precheck failed; inbox pack will not be archived")

    prompts_dir = repo_root / "tools" / "codex" / "prompts" / run_id
    if prompts_dir.exists():
        for item in sorted(prompts_dir.iterdir(), key=lambda path: path.name):
            if item.is_file():
                target = materialized_mirror_dir / item.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
    try:
        if prompts_dir.exists():
            shutil.rmtree(prompts_dir)
    except OSError as exc:
        raise PreflightError(
            "failed to clean precheck prompt folder before run_iter: "
            f"{prompts_dir.as_posix()} ({exc})"
        ) from exc


def _archive_inbox_pack(pack_path: Path, archive_root: Path, run_id: str) -> Path:
    archive_root.mkdir(parents=True, exist_ok=True)
    target = archive_root / f"PACK_{run_id}.txt"
    if target.exists():
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = archive_root / f"PACK_{run_id}_{stamp}.txt"
    pack_path.replace(target)
    return target


def _mirror_logs(repo_root: Path, run_paths: RunPaths, run_id: str) -> dict[str, Any]:
    copied: dict[str, list[str]] = {
        "canonical_debug": [],
        "prompt_logs": [],
    }
    canonical_debug = repo_root / "tools" / "codex" / "runs" / run_id / "_debug"
    prompt_logs = repo_root / "tools" / "codex" / "prompts" / run_id / "logs"
    mirror_root = run_paths.debug_dir
    for label, source in (
        ("canonical_debug", canonical_debug),
        ("prompt_logs", prompt_logs),
    ):
        if not source.exists():
            continue
        destination = mirror_root / label
        for item in sorted(source.rglob("*"), key=lambda path: path.as_posix()):
            if not item.is_file():
                continue
            relative = item.relative_to(source)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            copied[label].append(target.as_posix())
    return {
        "source_canonical_debug": canonical_debug.as_posix(),
        "source_prompt_logs": prompt_logs.as_posix(),
        "mirrored": copied,
    }


def _pending_workers_from_wait_payload(payload: dict[str, Any]) -> list[str]:
    pending = payload.get("pending_workers")
    if isinstance(pending, list):
        chosen = [str(item) for item in pending if str(item) in WORKERS]
        if chosen:
            return chosen

    workers = payload.get("workers")
    if isinstance(workers, list):
        chosen: list[str] = []
        for entry in workers:
            if not isinstance(entry, dict):
                continue
            worker = str(entry.get("worker", ""))
            status = str(entry.get("status", "")).upper()
            if worker in WORKERS and status != "PASS":
                chosen.append(worker)
        if chosen:
            return chosen
    return []


def _int_from_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        parsed = int(raw.strip())
    except ValueError:
        return default
    return parsed


def _attempt_outer_retry(
    *,
    repo_root: Path,
    run_id: str,
    logger: ExecutorLogger,
    records: list[CommandRecord],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": True,
        "attempted": False,
        "succeeded": False,
        "worker": "",
        "note": "",
    }

    validator_path = repo_root / "tools" / "codex" / "dispatch" / "validator.py"
    dispatch_script = repo_root / "tools" / "codex" / "dispatch" / "dispatch_prompts.py"

    probe = _run_capture(
        stage="outer_retry_probe",
        command=[
            sys.executable,
            str(validator_path),
            "wait-done",
            "--run-id",
            run_id,
            "--timeout-seconds",
            "1",
            "--poll-seconds",
            "0.2",
        ],
        cwd=repo_root,
        logger=logger,
        records=records,
    )
    payload: dict[str, Any]
    try:
        payload = _parse_json(probe.stdout)
    except Exception:
        payload = {}
    pending_workers = _pending_workers_from_wait_payload(payload)

    if len(pending_workers) != 1:
        result["note"] = (
            "outer retry skipped; pending workers count is not exactly one: "
            + (",".join(pending_workers) if pending_workers else "<none>")
        )
        return result

    worker = pending_workers[0]
    result["attempted"] = True
    result["worker"] = worker
    logger.log("outer_retry", f"re-dispatching single worker: {worker}")

    dispatch = _run_capture(
        stage=f"outer_retry_dispatch_{worker}",
        command=[
            sys.executable,
            str(dispatch_script),
            "--run-id",
            run_id,
            "--workers",
            worker,
        ],
        cwd=repo_root,
        logger=logger,
        records=records,
    )
    if dispatch.returncode != 0:
        result["note"] = f"re-dispatch failed for worker {worker}"
        return result

    wait_timeout = _int_from_env("FACTORY_WORKER_DONE_TIMEOUT", 3600)
    wait_result = _run_capture(
        stage=f"outer_retry_wait_done_{worker}",
        command=[
            sys.executable,
            str(validator_path),
            "wait-done",
            "--run-id",
            run_id,
            "--workers",
            worker,
            "--timeout-seconds",
            str(wait_timeout),
            "--poll-seconds",
            "2",
        ],
        cwd=repo_root,
        logger=logger,
        records=records,
    )
    if wait_result.returncode != 0:
        result["note"] = f"DONE.marker still missing for worker {worker} after retry"
        return result

    workers_csv = ",".join(WORKERS)
    for stage, command in (
        (
            "outer_retry_bundle_validate",
            [sys.executable, "-m", "tools.codex.factory", "bundle-validate", "--run-id", run_id, "--workers", workers_csv],
        ),
        (
            "outer_retry_integrate",
            [sys.executable, "-m", "tools.codex.factory", "integrate", "--run-id", run_id, "--workers", workers_csv],
        ),
        (
            "outer_retry_guardrails",
            [sys.executable, str(validator_path), "validate-guardrails", "--run-id", run_id],
        ),
    ):
        completed = _run_capture(
            stage=stage,
            command=command,
            cwd=repo_root,
            logger=logger,
            records=records,
        )
        if completed.returncode != 0:
            result["note"] = f"retry post-stage failed: {stage}"
            return result

    result["succeeded"] = True
    result["note"] = f"single-worker retry succeeded for {worker}"
    return result

def _preflight_validate(repo_root: Path, shared_paths: SharedPaths) -> dict[str, str]:
    if shutil.which("git") is None:
        raise PreflightError("git is not available in PATH")

    if _resolve_code_command() is None:
        raise PreflightError("VS Code command was not found (code/code.cmd/Code.exe)")

    if len(set(WORKERS)) != len(WORKERS):
        raise PreflightError("worker set contains duplicates")

    if tuple(WORKERS) != ("A_core", "B_tooling", "C_features", "D_validation", "Z_aggregator"):
        raise PreflightError("worker set/order is invalid and must remain A_core,B_tooling,C_features,D_validation,Z_aggregator")

    required_paths = [
        repo_root / "scripts" / "OPEN_HOS_FACTORY.ps1",
        repo_root / "tools" / "codex" / "dispatch" / "run_iter.ps1",
        repo_root / "tools" / "codex" / "dispatch" / "validator.py",
        repo_root / "tools" / "codex" / "dispatch" / "dispatch_prompts.py",
    ]
    for item in required_paths:
        if not item.exists():
            raise PreflightError(f"required path is missing: {item.as_posix()}")

    if not shared_paths.base.exists():
        raise PreflightError(f"shared base path is missing: {shared_paths.base.as_posix()}")

    return {
        "git": shutil.which("git") or "",
        "code": _resolve_code_command() or "",
        "python": sys.executable,
    }


def _build_summary_payload(
    *,
    status: str,
    exit_code: int,
    started_at_utc: str,
    ended_at_utc: str,
    repo_root: Path | None,
    run_id: str | None,
    shared_paths: SharedPaths | None,
    run_paths: RunPaths | None,
    dry_run: bool,
    outer_retry_enabled: bool,
    outer_retry_result: dict[str, Any] | None,
    archived_pack_path: Path | None,
    error: str,
    command_records: list[CommandRecord],
    mirrored_logs: dict[str, Any] | None,
    tools_detected: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "status": status,
        "exit_code": int(exit_code),
        "started_at_utc": started_at_utc,
        "ended_at_utc": ended_at_utc,
        "repo_root": repo_root.as_posix() if repo_root else "",
        "run_id": run_id or "",
        "dry_run": bool(dry_run),
        "outer_retry": {
            "enabled": bool(outer_retry_enabled),
            "result": outer_retry_result or {},
        },
        "shared_paths": {
            "base": shared_paths.base.as_posix() if shared_paths else "",
            "inbox": shared_paths.inbox.as_posix() if shared_paths else "",
            "runs": shared_paths.runs.as_posix() if shared_paths else "",
            "archive": shared_paths.archive.as_posix() if shared_paths else "",
            "run_dir": run_paths.run_dir.as_posix() if run_paths else "",
            "raw_pack": run_paths.raw_pack.as_posix() if run_paths else "",
            "debug_dir": run_paths.debug_dir.as_posix() if run_paths else "",
            "archived_pack": archived_pack_path.as_posix() if archived_pack_path else "",
        },
        "tools_detected": tools_detected or {},
        "commands": [
            {
                "stage": entry.stage,
                "rc": entry.rc,
                "command": entry.command,
                "output_tail": entry.output_tail,
            }
            for entry in command_records
        ],
        "mirrored_logs": mirrored_logs or {},
        "error": error,
    }


def run_executor(*, dry_run: bool, outer_retry: bool) -> int:
    logger = ExecutorLogger()
    command_records: list[CommandRecord] = []
    repo_root: Path | None = None
    shared_paths: SharedPaths | None = None
    run_paths: RunPaths | None = None
    run_id: str | None = None
    archived_pack: Path | None = None
    mirrored_logs: dict[str, Any] | None = None
    tools_detected: dict[str, str] | None = None
    outer_retry_result: dict[str, Any] | None = None

    status = "PASS"
    exit_code = EXIT_SUCCESS
    error = ""
    started_at = _now_utc()

    try:
        repo_root = _resolve_repo_root()
        logger.log("init", f"repo_root={repo_root.as_posix()}")
        _resolve_powershell()

        shared_paths = _ensure_shared_paths(OFFICIAL_SHARED_BASE)
        logger.log("init", f"shared_base={shared_paths.base.as_posix()}")

        tools_detected = _preflight_validate(repo_root=repo_root, shared_paths=shared_paths)

        inbox_pack = _resolve_inbox_pack(shared_paths.inbox)
        run_id = _generate_run_id(repo_root=repo_root, logger=logger, records=command_records)
        logger.log("init", f"run_id={run_id}")

        run_paths = _create_run_paths(shared_paths.runs, run_id)
        logger.bind(run_paths.debug_dir / "EXECUTOR.log")
        logger.log("init", f"run_dir={run_paths.run_dir.as_posix()}")

        shutil.copy2(inbox_pack, run_paths.raw_pack)
        logger.log("pack", f"copied raw pack to {run_paths.raw_pack.as_posix()}")

        _materialize_pack_precheck(
            repo_root=repo_root,
            run_id=run_id,
            pack_path=run_paths.raw_pack,
            materialized_mirror_dir=run_paths.materialized_dir,
            logger=logger,
            records=command_records,
        )

        if dry_run:
            logger.log("pack", "dry-run enabled: inbox pack archive move skipped")
        else:
            archived_pack = _archive_inbox_pack(inbox_pack, shared_paths.archive, run_id)
            logger.log("pack", f"archived inbox pack to {archived_pack.as_posix()}")

        canonical_run = _canonical_run_root(repo_root, run_id)
        (canonical_run / "_debug").mkdir(parents=True, exist_ok=True)
        for worker in WORKERS:
            _ensure_worker_junction(
                link_path=run_paths.workers_dir / worker,
                target_path=canonical_run / worker,
                repo_root=repo_root,
                logger=logger,
                records=command_records,
            )
        _validate_workers_dir_shape(run_paths.workers_dir)

        if dry_run:
            logger.log("dry_run", "dry-run preflight completed")
            print("Dry run preflight completed successfully.")
        else:
            powershell = _resolve_powershell()
            launcher_command = [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(repo_root / "scripts" / "OPEN_HOS_FACTORY.ps1"),
                "-RunId",
                run_id,
            ]
            launcher_rc = _run_stream(
                stage="launcher",
                command=launcher_command,
                cwd=repo_root,
                logger=logger,
                records=command_records,
            )
            if launcher_rc != 0:
                raise PipelineError(f"launcher failed with rc={launcher_rc}")

            run_iter_command = [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(repo_root / "tools" / "codex" / "dispatch" / "run_iter.ps1"),
                "-RunId",
                run_id,
                "-PromptsPackPath",
                str(run_paths.raw_pack),
            ]
            run_iter_rc = _run_stream(
                stage="run_iter",
                command=run_iter_command,
                cwd=repo_root,
                logger=logger,
                records=command_records,
            )
            if run_iter_rc != 0:
                if outer_retry:
                    outer_retry_result = _attempt_outer_retry(
                        repo_root=repo_root,
                        run_id=run_id,
                        logger=logger,
                        records=command_records,
                    )
                    if not bool(outer_retry_result.get("succeeded", False)):
                        raise PipelineError(
                            "run_iter failed and outer retry did not recover pipeline; "
                            + str(outer_retry_result.get("note", "no detail"))
                        )
                else:
                    raise PipelineError(f"run_iter failed with rc={run_iter_rc}")

            logger.log("executor", "factory run completed")
            print("Factory run completed successfully.")

    except PreflightError as exc:
        status = "FAIL"
        exit_code = EXIT_PREFLIGHT_FAILURE
        error = str(exc)
        logger.log("fatal", error, level="ERROR")
    except PipelineError as exc:
        status = "FAIL"
        exit_code = EXIT_PIPELINE_FAILURE
        error = str(exc)
        logger.log("fatal", error, level="ERROR")
    except Exception as exc:
        status = "FAIL"
        exit_code = EXIT_PIPELINE_FAILURE if run_id else EXIT_PREFLIGHT_FAILURE
        error = f"unexpected executor error: {exc!r}"
        logger.log("fatal", error, level="ERROR")
    finally:
        if repo_root and run_id and run_paths:
            try:
                mirrored_logs = _mirror_logs(repo_root=repo_root, run_paths=run_paths, run_id=run_id)
            except Exception as mirror_exc:
                logger.log("mirror_logs", f"failed to mirror logs: {mirror_exc}", level="WARN")
            summary = _build_summary_payload(
                status=status,
                exit_code=exit_code,
                started_at_utc=started_at,
                ended_at_utc=_now_utc(),
                repo_root=repo_root,
                run_id=run_id,
                shared_paths=shared_paths,
                run_paths=run_paths,
                dry_run=dry_run,
                outer_retry_enabled=outer_retry,
                outer_retry_result=outer_retry_result,
                archived_pack_path=archived_pack,
                error=error,
                command_records=command_records,
                mirrored_logs=mirrored_logs,
                tools_detected=tools_detected,
            )
            _write_json(run_paths.debug_dir / "EXECUTOR_SUMMARY.json", summary)
            logger.log("summary", f"wrote {run_paths.debug_dir.joinpath('EXECUTOR_SUMMARY.json').as_posix()}")

    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HITECH-OS one-button prompt-pack executor")
    parser.add_argument("--dry-run", action="store_true", help="Preflight mode only; no launcher/run_iter dispatch")
    parser.add_argument("--outer-retry", action="store_true", help="Enable single-worker outer retry flow on run_iter failure")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dry_run = bool(args.dry_run or _truthy(os.environ.get("DRY_RUN")))
    outer_retry = bool(args.outer_retry or _truthy(os.environ.get("OUTER_RETRY")))

    return run_executor(dry_run=dry_run, outer_retry=outer_retry)


if __name__ == "__main__":
    raise SystemExit(main())

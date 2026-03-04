from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .validator import BLOCKED, CODEX_IDS, PASS, PROMPTS_ROOT, _apply_prompt_contract, expected_prompt_files, validate_prompt_folder
except Exception:  # pragma: no cover - script mode
    from validator import BLOCKED, CODEX_IDS, PASS, PROMPTS_ROOT, _apply_prompt_contract, expected_prompt_files, validate_prompt_folder

DEFAULT_FALLBACK_REPO = Path(r"F:\repos\hitech-os")


def _git_toplevel(start_dir: Path) -> Path | None:
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
    value = completed.stdout.strip()
    if not value:
        return None
    return Path(value).resolve()


def _resolve_repo_root() -> Path:
    script_hint = Path(__file__).resolve().parents[3]
    for probe in (script_hint, Path.cwd()):
        detected = _git_toplevel(probe)
        if detected:
            return detected
    if DEFAULT_FALLBACK_REPO.exists():
        return DEFAULT_FALLBACK_REPO.resolve()
    return script_hint


REPO_ROOT = _resolve_repo_root()
CODEX_DIR = REPO_ROOT / "tools" / "codex"
DISPATCH_DIR = CODEX_DIR / "dispatch"
RUNS_ROOT = CODEX_DIR / "runs"

DEFAULT_WINDOW_READY_TIMEOUT = 120
DEFAULT_READINESS_TIMEOUT = 25
DEFAULT_BETWEEN_WORKERS_DELAY_MS = 700
MIN_WINDOW_READY_TIMEOUT = 5
MAX_WINDOW_READY_TIMEOUT = 900
MIN_READINESS_TIMEOUT = 5
MAX_READINESS_TIMEOUT = 300
DISPATCH_HARD_TIMEOUT_MIN_SECONDS = 180
DISPATCH_HARD_TIMEOUT_MAX_SECONDS = 7200
DISPATCH_HARD_TIMEOUT_BUFFER_SECONDS = 30
DISPATCH_PER_WORKER_ACTION_SECONDS = 50
HEARTBEAT_FILE_NAME = "DISPATCH_HEARTBEAT.json"
TIMEOUT_REPORT_FILE_NAME = "TIMEOUT_REPORT.json"


@dataclass(frozen=True)
class DispatchConfig:
    run_id: str
    workers: tuple[str, ...]
    window_ready_timeout: int
    readiness_timeout: int
    between_workers_delay_ms: int
    ahk_exe: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _status_code(status: str) -> int:
    return 0 if str(status).upper() == PASS else 2


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(path.name + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    temp_path.replace(path)


def _heartbeat_path(run_id: str) -> Path:
    return RUNS_ROOT / run_id / "_debug" / HEARTBEAT_FILE_NAME


def _timeout_report_path(run_id: str) -> Path:
    return RUNS_ROOT / run_id / "_debug" / TIMEOUT_REPORT_FILE_NAME


def _first_env(*names: str) -> str | None:
    for name in names:
        raw = os.getenv(name)
        if raw is not None and raw.strip():
            return raw.strip()
    return None


def _coerce_int(raw: str | None, default: int) -> int:
    if raw is None:
        return int(default)
    try:
        return int(raw)
    except ValueError:
        return int(default)


def _resolve_ahk_exe(explicit: str | None) -> str | None:
    if explicit:
        return explicit

    env_value = _first_env("FACTORY_AHK_EXE", "FACTORY_DISPATCH__AHK_EXE")
    if env_value:
        return env_value

    for candidate in ("AutoHotkey64.exe", "AutoHotkey.exe", "autohotkey"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    return None


def _parse_workers(raw: str | None) -> tuple[tuple[str, ...] | None, list[str]]:
    if raw is None or not raw.strip():
        return tuple(CODEX_IDS), []

    parsed = [item.strip() for item in raw.split(",") if item.strip()]
    if not parsed:
        return tuple(CODEX_IDS), []

    unknown = [item for item in parsed if item not in CODEX_IDS]
    if unknown:
        return None, [f"unknown worker ids: {','.join(sorted(set(unknown)))}"]

    ordered: list[str] = []
    for worker in parsed:
        if worker not in ordered:
            ordered.append(worker)
    return tuple(ordered), []


def _ahk_escape(text: str) -> str:
    return text.replace('"', '""')


def _compute_hard_timeout_seconds(config: DispatchConfig) -> int:
    worker_count = max(1, len(config.workers))
    per_worker = max(
        60,
        int(config.window_ready_timeout) + int(config.readiness_timeout) + DISPATCH_PER_WORKER_ACTION_SECONDS,
    )
    computed = (worker_count * per_worker) + DISPATCH_HARD_TIMEOUT_BUFFER_SECONDS
    return max(DISPATCH_HARD_TIMEOUT_MIN_SECONDS, min(DISPATCH_HARD_TIMEOUT_MAX_SECONDS, computed))


def _build_jobs_block(run_id: str, workers: tuple[str, ...]) -> str:
    expected = expected_prompt_files(run_id)
    lines: list[str] = []
    for worker in workers:
        prompt_path = (PROMPTS_ROOT / run_id / expected[worker]).as_posix()
        worktree_path = (CODEX_DIR / "worktrees" / worker).as_posix()
        lines.extend(
            [
                f'    if !DispatchWorker("{_ahk_escape(worker)}", "{_ahk_escape(worktree_path)}", "{_ahk_escape(prompt_path)}") {{',
                "        failures += 1",
                "    }",
                "    Sleep(betweenWorkersDelayMs)",
            ]
        )
    return "\n".join(lines)


def _render_script(template_text: str, config: DispatchConfig, run_logs_dir: Path, debug_dir: Path) -> str:
    substitutions = {
        "{{RUN_ID}}": _ahk_escape(config.run_id),
        "{{LOG_PATH}}": _ahk_escape((debug_dir / "AHK_DISPATCH.log").as_posix()),
        "{{RESULT_PATH}}": _ahk_escape((debug_dir / "AHK_WORKER_RESULTS.log").as_posix()),
        "{{WINDOW_READY_TIMEOUT_MS}}": str(max(1000, config.window_ready_timeout * 1000)),
        "{{READINESS_TIMEOUT_MS}}": str(max(1000, config.readiness_timeout * 1000)),
        "{{BETWEEN_WORKERS_DELAY_MS}}": str(max(0, config.between_workers_delay_ms)),
        "{{JOBS_BLOCK}}": _build_jobs_block(config.run_id, config.workers),
    }

    rendered = template_text
    for key, value in substitutions.items():
        rendered = rendered.replace(key, value)
    return rendered


def _parse_worker_results(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    parsed: dict[str, dict[str, str]] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        worker, status, detail = parts
        parsed[str(worker)] = {
            "worker": str(worker),
            "status": str(status),
            "detail": str(detail),
        }
    return parsed


def _ensure_worker_worktree_dirs(workers: tuple[str, ...]) -> None:
    for worker in workers:
        target = CODEX_DIR / "worktrees" / worker
        target.mkdir(parents=True, exist_ok=True)


def run_dispatch(config: DispatchConfig) -> dict[str, Any]:
    run_logs_dir = PROMPTS_ROOT / config.run_id / "logs"
    run_logs_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = RUNS_ROOT / config.run_id / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    heartbeat_path = _heartbeat_path(config.run_id)
    timeout_report_path = _timeout_report_path(config.run_id)
    hard_timeout_seconds = _compute_hard_timeout_seconds(config)

    heartbeat_seq = 0

    def write_heartbeat(state: str, last_step: str) -> None:
        nonlocal heartbeat_seq
        heartbeat_seq += 1
        _atomic_write_json(
            heartbeat_path,
            {
                "last_step": str(last_step),
                "run_id": config.run_id,
                "seq": int(heartbeat_seq),
                "stage": "dispatch_prompts",
                "state": str(state),
                "workers": list(config.workers),
            },
        )

    write_heartbeat("STARTING", "validate_prompt_folder")
    prompt_validation = validate_prompt_folder(config.run_id)
    if str(prompt_validation.get("status", BLOCKED)).upper() != PASS:
        write_heartbeat("BLOCKED", "prompt_validation_failed")
        return {
            "status": BLOCKED,
            "run_id": config.run_id,
            "workers": list(config.workers),
            "error": "prompt validation failed before dispatch",
            "prompt_validation": prompt_validation,
        }

    _ensure_worker_worktree_dirs(config.workers)
    expected = expected_prompt_files(config.run_id)
    missing_prompt_files: list[str] = []
    for worker in config.workers:
        prompt_path = PROMPTS_ROOT / config.run_id / expected[worker]
        if not prompt_path.exists() or not prompt_path.is_file():
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            placeholder = "AUTOFIX_PROMPT_PLACEHOLDER: worker prompt was missing and auto-generated.\n"
            prompt_path.write_text(
                _apply_prompt_contract(config.run_id, worker, placeholder),
                encoding="utf-8",
                newline="\n",
            )
            missing_prompt_files.append(prompt_path.as_posix())
    if missing_prompt_files:
        write_heartbeat("RUNNING", "missing_prompt_files_autofixed")

    template_path = DISPATCH_DIR / "ahk_template.ahk"
    if not template_path.exists():
        write_heartbeat("BLOCKED", "missing_ahk_template")
        return {
            "status": BLOCKED,
            "run_id": config.run_id,
            "workers": list(config.workers),
            "error": f"missing AHK template: {template_path.as_posix()}",
        }

    ahk_exe_path = Path(config.ahk_exe)
    if not ahk_exe_path.exists():
        resolved = shutil.which(config.ahk_exe)
        if resolved:
            ahk_exe_path = Path(resolved)
    if not ahk_exe_path.exists():
        write_heartbeat("BLOCKED", "missing_ahk_executable")
        return {
            "status": BLOCKED,
            "run_id": config.run_id,
            "workers": list(config.workers),
            "error": f"AutoHotkey executable not found: {config.ahk_exe}",
        }

    script_path = run_logs_dir / "DISPATCH_RUNTIME.ahk"
    stdout_path = run_logs_dir / "AHK_STDOUT.log"
    stderr_path = run_logs_dir / "AHK_STDERR.log"
    results_path = debug_dir / "AHK_WORKER_RESULTS.log"
    ahk_log_path = debug_dir / "AHK_DISPATCH.log"

    if ahk_log_path.exists():
        ahk_log_path.unlink()
    if results_path.exists():
        results_path.unlink()
    if timeout_report_path.exists():
        timeout_report_path.unlink()

    template_text = template_path.read_text(encoding="utf-8")
    script_text = _render_script(template_text, config, run_logs_dir, debug_dir)
    script_path.write_text(script_text, encoding="utf-8", newline="\n")

    started_at = _now_iso()
    write_heartbeat("RUNNING", "launch_ahk")
    proc: subprocess.Popen[str] | None = None
    ahk_rc = 255
    timed_out = False
    deadline = time.monotonic() + hard_timeout_seconds
    next_heartbeat_at = time.monotonic()

    with stdout_path.open("w", encoding="utf-8", newline="\n") as stdout_handle, stderr_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as stderr_handle:
        try:
            proc = subprocess.Popen(
                [str(ahk_exe_path), str(script_path)],
                cwd=str(REPO_ROOT),
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
            )
        except Exception as exc:
            ended_at = _now_iso()
            write_heartbeat("BLOCKED", "ahk_launch_failed")
            return {
                "status": BLOCKED,
                "run_id": config.run_id,
                "workers": list(config.workers),
                "started_at": started_at,
                "ended_at": ended_at,
                "error": f"failed to launch AutoHotkey: {exc!r}",
                "failures": [f"failed to launch AutoHotkey: {exc!r}"],
                "ahk_rc": 127,
                "config": {
                    "workers": list(config.workers),
                    "window_ready_timeout": config.window_ready_timeout,
                    "readiness_timeout": config.readiness_timeout,
                    "between_workers_delay_ms": config.between_workers_delay_ms,
                    "ahk_exe": str(ahk_exe_path),
                    "computed_hard_timeout_seconds": hard_timeout_seconds,
                },
                "artifacts": {
                    "script": script_path.as_posix(),
                    "stdout": stdout_path.as_posix(),
                    "stderr": stderr_path.as_posix(),
                    "worker_results": results_path.as_posix(),
                    "ahk_log": ahk_log_path.as_posix(),
                    "heartbeat": heartbeat_path.as_posix(),
                },
                "workers_results": [],
            }

        while True:
            assert proc is not None
            rc = proc.poll()
            if rc is not None:
                ahk_rc = int(rc)
                break

            now = time.monotonic()
            if now >= deadline:
                timed_out = True
                write_heartbeat("TIMEOUT_HARD", "hard_timeout_reached")
                proc.kill()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                ahk_rc = int(proc.returncode if proc.returncode is not None else 124)
                break

            if now >= next_heartbeat_at:
                write_heartbeat("RUNNING", "waiting_for_ahk_exit")
                next_heartbeat_at = now + 1.0
            time.sleep(0.2)

    ended_at = _now_iso()

    if timed_out:
        _atomic_write_json(
            timeout_report_path,
            {
                "cause": "TIMEOUT_HARD",
                "hard_timeout_seconds": hard_timeout_seconds,
                "last_step": "waiting_for_ahk_exit",
                "run_id": config.run_id,
                "stage": "dispatch_prompts",
                "workers": list(config.workers),
            },
        )
        write_heartbeat("TIMEOUT_HARD", "timeout_report_written")
        return {
            "status": BLOCKED,
            "run_id": config.run_id,
            "workers": list(config.workers),
            "cause": "TIMEOUT_HARD",
            "error": f"dispatch_prompts exceeded hard timeout ({hard_timeout_seconds}s)",
            "started_at": started_at,
            "ended_at": ended_at,
            "failures": [f"TIMEOUT_HARD: dispatch_prompts exceeded {hard_timeout_seconds}s"],
            "workers_results": [],
            "ahk_rc": int(ahk_rc),
            "config": {
                "workers": list(config.workers),
                "window_ready_timeout": config.window_ready_timeout,
                "readiness_timeout": config.readiness_timeout,
                "between_workers_delay_ms": config.between_workers_delay_ms,
                "ahk_exe": str(ahk_exe_path),
                "computed_hard_timeout_seconds": hard_timeout_seconds,
            },
            "artifacts": {
                "script": script_path.as_posix(),
                "stdout": stdout_path.as_posix(),
                "stderr": stderr_path.as_posix(),
                "worker_results": results_path.as_posix(),
                "ahk_log": ahk_log_path.as_posix(),
                "heartbeat": heartbeat_path.as_posix(),
                "timeout_report": timeout_report_path.as_posix(),
            },
        }

    write_heartbeat("RUNNING", "parse_worker_results")
    worker_map = _parse_worker_results(results_path)
    workers_results: list[dict[str, Any]] = []
    failures: list[str] = []

    for worker in config.workers:
        record = worker_map.get(worker)
        if record is None:
            workers_results.append(
                {
                    "worker": worker,
                    "status": BLOCKED,
                    "detail": "missing dispatch result line",
                }
            )
            failures.append(f"missing dispatch result for {worker}")
            continue

        raw_status = str(record.get("status", "")).upper()
        detail = str(record.get("detail", ""))
        mapped_status = PASS if raw_status == PASS else BLOCKED
        workers_results.append(
            {
                "worker": worker,
                "status": mapped_status,
                "raw_status": raw_status,
                "detail": detail,
            }
        )
        if mapped_status != PASS:
            failures.append(f"{worker}: {detail or 'dispatch failed'}")

    if ahk_rc != 0:
        failures.append(f"AutoHotkey exited with rc={ahk_rc}")

    status = PASS if not failures else BLOCKED
    write_heartbeat("PASS" if status == PASS else "BLOCKED", "dispatch_complete")
    return {
        "status": status,
        "run_id": config.run_id,
        "workers": list(config.workers),
        "started_at": started_at,
        "ended_at": ended_at,
        "config": {
            "workers": list(config.workers),
            "window_ready_timeout": config.window_ready_timeout,
            "readiness_timeout": config.readiness_timeout,
            "between_workers_delay_ms": config.between_workers_delay_ms,
            "ahk_exe": str(ahk_exe_path),
            "computed_hard_timeout_seconds": hard_timeout_seconds,
        },
        "artifacts": {
            "script": script_path.as_posix(),
            "stdout": stdout_path.as_posix(),
            "stderr": stderr_path.as_posix(),
            "worker_results": results_path.as_posix(),
            "ahk_log": ahk_log_path.as_posix(),
            "heartbeat": heartbeat_path.as_posix(),
        },
        "workers_results": workers_results,
        "failures": failures,
        "ahk_rc": int(ahk_rc),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dispatch RUN_ID prompts to Codex windows via AutoHotkey")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", default=None, help="Comma-separated worker IDs in dispatch order")
    parser.add_argument("--window-ready-timeout", type=int, default=None)
    parser.add_argument("--readiness-timeout", type=int, default=None)
    parser.add_argument("--between-workers-delay-ms", type=int, default=None)
    parser.add_argument("--ahk-exe", default=None)
    return parser


def _build_config(args: argparse.Namespace) -> tuple[DispatchConfig | None, list[str]]:
    errors: list[str] = []

    workers_value = args.workers or _first_env("FACTORY_DISPATCH__WORKERS")
    workers, workers_errors = _parse_workers(workers_value)
    if workers_errors:
        errors.extend(workers_errors)

    window_ready_timeout = (
        args.window_ready_timeout
        if args.window_ready_timeout is not None
        else _coerce_int(
            _first_env("FACTORY_WINDOW_READY_TIMEOUT", "FACTORY_DISPATCH__WINDOW_READY_TIMEOUT"),
            DEFAULT_WINDOW_READY_TIMEOUT,
        )
    )
    readiness_timeout = (
        args.readiness_timeout
        if args.readiness_timeout is not None
        else _coerce_int(
            _first_env("FACTORY_READINESS_TIMEOUT", "FACTORY_DISPATCH__READINESS_TIMEOUT"),
            DEFAULT_READINESS_TIMEOUT,
        )
    )
    worker_delay = (
        args.between_workers_delay_ms
        if args.between_workers_delay_ms is not None
        else _coerce_int(
            _first_env("FACTORY_BETWEEN_WORKERS_DELAY_MS", "FACTORY_DISPATCH__BETWEEN_WORKERS_DELAY_MS"),
            DEFAULT_BETWEEN_WORKERS_DELAY_MS,
        )
    )

    ahk_exe = _resolve_ahk_exe(args.ahk_exe)
    if not ahk_exe:
        errors.append("AutoHotkey executable could not be resolved")

    if window_ready_timeout < MIN_WINDOW_READY_TIMEOUT or window_ready_timeout > MAX_WINDOW_READY_TIMEOUT:
        errors.append(
            f"window_ready_timeout must be between {MIN_WINDOW_READY_TIMEOUT} and {MAX_WINDOW_READY_TIMEOUT} seconds"
        )
    if readiness_timeout < MIN_READINESS_TIMEOUT or readiness_timeout > MAX_READINESS_TIMEOUT:
        errors.append(f"readiness_timeout must be between {MIN_READINESS_TIMEOUT} and {MAX_READINESS_TIMEOUT} seconds")
    if worker_delay < 0:
        errors.append("between_workers_delay_ms must be >= 0")
    if workers is None or len(workers) == 0:
        errors.append("workers list resolved to empty")

    if errors:
        return None, errors

    config = DispatchConfig(
        run_id=str(args.run_id),
        workers=tuple(workers),
        window_ready_timeout=int(window_ready_timeout),
        readiness_timeout=int(readiness_timeout),
        between_workers_delay_ms=int(worker_delay),
        ahk_exe=str(ahk_exe),
    )
    return config, []


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config, errors = _build_config(args)
    if errors:
        payload = {
            "status": BLOCKED,
            "run_id": args.run_id,
            "errors": errors,
        }
        _emit(payload)
        return _status_code(payload["status"])

    assert config is not None
    payload = run_dispatch(config)

    report_json = PROMPTS_ROOT / config.run_id / "logs" / "DISPATCH_PROMPTS.json"
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    _emit(payload)
    return _status_code(str(payload.get("status", BLOCKED)))


if __name__ == "__main__":
    raise SystemExit(main())

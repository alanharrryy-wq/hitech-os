from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import shutil
import string
import subprocess
import sys
import time
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

RUN_ID_OLD_RE = re.compile(r"^\d{8}_\d+$")
RUN_ID_NEW_RE = re.compile(r"^\d{8}_\d{6}_[A-Z0-9]{4}$")

RECOVERABLE_ERROR_CLASSES: set[str] = {
    "LOCK_STALE",
    "WORKTREE_DIRTY",
    "GIT_TRANSIENT",
    "AHK_TRANSIENT_IF_DETECTABLE",
}

MAX_ATTEMPTS_PER_WORKER = 2
DEFAULT_WORKER_DONE_TIMEOUT = 7200
DEFAULT_FALLBACK_REPO = Path(r"F:\repos\hitech-os")
SNAPSHOT_REF_PREFIX = "refs/hos/snapshots/"

WORKTREE_ROOT_REL = Path("tools") / "codex" / "worktrees"
RUNS_ROOT_REL = Path("tools") / "codex" / "runs"
DEBUG_ROOT_REL = Path("tools") / "codex" / "_debug"
DISPATCHER_REL = Path("tools") / "codex" / "dispatch" / "run_iter.ps1"
VALIDATOR_REL = Path("tools") / "codex" / "dispatch" / "validator.py"

PASS_STATE = "PASS"
FAIL_STATE = "FAIL"
PARTIAL_STATE = "PARTIAL"
RUNNING_STATE = "RUNNING"

EXIT_SUCCESS = 0
EXIT_FAILURE = 2


class ExecutorFailure(RuntimeError):
    def __init__(self, message: str, *, error_class: str | None = None) -> None:
        super().__init__(message)
        self.error_class = error_class


@dataclass
class CommandRecord:
    stage: str
    command: list[str]
    cwd: str
    rc: int
    output_tail: str


class RuntimeLogger:
    def __init__(self) -> None:
        self._log_path: Path | None = None

    def bind(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._log_path = path
        self.log("init", f"log_path={path.as_posix()}")

    def log(self, stage: str, message: str, *, level: str = "INFO") -> None:
        stamp = _now_utc_iso()
        line = f"{stamp} [{level}] [{stage}] {message.rstrip()}"
        print(line, flush=True)
        if self._log_path is not None:
            with self._log_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(line + "\n")


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _now_utc_iso() -> str:
    return _now_utc().replace(microsecond=0).isoformat()


def _tail_lines(text: str, max_lines: int = 80) -> str:
    stripped = str(text or "").strip()
    if not stripped:
        return ""
    lines = stripped.splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[-max_lines:])


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def _truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


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
    script_hint = Path(__file__).resolve().parents[3]
    for probe in (script_hint, Path.cwd()):
        detected = _git_toplevel(probe)
        if detected:
            return detected
    if DEFAULT_FALLBACK_REPO.exists():
        return DEFAULT_FALLBACK_REPO.resolve()
    raise ExecutorFailure("unable to resolve repository root via git and fallback path")


def _run_id_valid(run_id: str) -> bool:
    return bool(RUN_ID_NEW_RE.fullmatch(run_id) or RUN_ID_OLD_RE.fullmatch(run_id))


def _parse_run_id_timestamp(run_id: str) -> dt.datetime | None:
    match_new = RUN_ID_NEW_RE.fullmatch(run_id)
    if match_new:
        day = run_id[0:8]
        time_part = run_id[9:15]
        try:
            return dt.datetime.strptime(day + time_part, "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return None

    match_old = RUN_ID_OLD_RE.fullmatch(run_id)
    if match_old:
        day = run_id[0:8]
        try:
            return dt.datetime.strptime(day, "%Y%m%d").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return None

    return None


def _detect_error_class(text: str) -> str | None:
    probe = str(text or "").lower()

    lock_markers = (
        "stale lock",
        "lock held",
        "lock exists",
        ".hos_lock",
        "run.lock",
    )
    if any(marker in probe for marker in lock_markers):
        return "LOCK_STALE"

    dirty_markers = (
        "worktree dirty",
        "reset-clean left dirty",
        "left dirty tree",
        "please commit or stash",
    )
    if any(marker in probe for marker in dirty_markers):
        return "WORKTREE_DIRTY"

    ahk_markers = ("autohotkey",)
    ahk_transient_markers = ("timeout", "window", "focus", "ready", "transient")
    if any(marker in probe for marker in ahk_markers) and any(marker in probe for marker in ahk_transient_markers):
        return "AHK_TRANSIENT_IF_DETECTABLE"

    git_transient_markers = (
        "index.lock",
        "could not resolve host",
        "connection reset",
        "failed to connect",
        "unable to access",
        "remote end hung up",
        "resource temporarily unavailable",
    )
    if any(marker in probe for marker in git_transient_markers):
        return "GIT_TRANSIENT"

    return None


class TxnExecutor:
    def __init__(
        self,
        *,
        dry_run: bool,
        resume_run_id: str | None,
        torture_mode: bool,
    ) -> None:
        self.dry_run = bool(dry_run)
        self.resume_run_id = str(resume_run_id).strip() if resume_run_id else None
        self.torture_mode = bool(torture_mode)

        self.logger = RuntimeLogger()
        self.command_records: list[CommandRecord] = []

        self.repo_root: Path | None = None
        self.run_id: str = ""
        self.run_root: Path | None = None
        self.run_debug_dir: Path | None = None
        self.global_debug_dir: Path | None = None

        self.dispatcher_path: Path | None = None
        self.validator_path: Path | None = None

        self.started_at_utc = _now_utc_iso()
        self.ended_at_utc = ""
        self.status = RUNNING_STATE
        self.error = ""
        self.exit_code = EXIT_SUCCESS

        self.timeline: list[dict[str, Any]] = []
        self.worker_done: dict[str, bool] = {worker: False for worker in WORKERS}
        self.worker_attempts: dict[str, int] = {worker: 0 for worker in WORKERS}

        self.branch_before: dict[str, Any] = {}
        self.branch_after: dict[str, Any] = {}
        self.worktree_before: list[str] = []
        self.worktree_after: list[str] = []
        self.ref_map_before: dict[str, str] = {}
        self.ref_map_after: dict[str, str] = {}

        self.prompt_pack_path: Path | None = None

    def _require_paths(self) -> tuple[Path, Path, Path, Path, Path]:
        if (
            self.repo_root is None
            or self.run_root is None
            or self.run_debug_dir is None
            or self.global_debug_dir is None
            or self.dispatcher_path is None
            or self.validator_path is None
        ):
            raise ExecutorFailure("runtime paths are not initialized")
        return (
            self.repo_root,
            self.run_root,
            self.run_debug_dir,
            self.global_debug_dir,
            self.dispatcher_path,
        )

    def _record_timeline(self, stage: str, status: str, detail: str = "", **extra: Any) -> None:
        payload: dict[str, Any] = {
            "ts_utc": _now_utc_iso(),
            "stage": stage,
            "status": status,
            "detail": detail,
        }
        payload.update(extra)
        self.timeline.append(payload)
        self._write_status_file()

    def _record_command(self, *, stage: str, command: list[str], cwd: Path, rc: int, output_tail: str) -> None:
        self.command_records.append(
            CommandRecord(
                stage=stage,
                command=list(command),
                cwd=str(cwd),
                rc=int(rc),
                output_tail=output_tail,
            )
        )

    def _run_capture(
        self,
        *,
        stage: str,
        command: list[str],
        cwd: Path,
        timeout_seconds: float = 300.0,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        self.logger.log(stage, "CMD: " + " ".join(command))
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=max(1.0, float(timeout_seconds)),
            )
        except subprocess.TimeoutExpired as exc:
            output_tail = _tail_lines((exc.stdout or "") + "\n" + (exc.stderr or ""))
            self._record_command(stage=stage, command=command, cwd=cwd, rc=124, output_tail=output_tail)
            raise ExecutorFailure(f"command timeout in stage '{stage}'") from exc
        except OSError as exc:
            self._record_command(stage=stage, command=command, cwd=cwd, rc=127, output_tail=str(exc))
            raise ExecutorFailure(f"command launch failed in stage '{stage}': {exc}") from exc

        output_tail = _tail_lines(completed.stdout + ("\n" + completed.stderr if completed.stderr else ""))
        self._record_command(stage=stage, command=command, cwd=cwd, rc=completed.returncode, output_tail=output_tail)
        self.logger.log(stage, f"RC={completed.returncode}")
        if output_tail:
            self.logger.log(stage, "OUTPUT_TAIL:\n" + output_tail, level="CMD")
        if check and completed.returncode != 0:
            raise ExecutorFailure(f"command failed in stage '{stage}'")
        return completed

    def _collect_heads(self) -> dict[str, Any]:
        repo_root, _, _, _, _ = self._require_paths()
        completed = self._run_capture(
            stage="collect_heads",
            command=["git", "-C", str(repo_root), "for-each-ref", "--format=%(refname)", "refs/heads"],
            cwd=repo_root,
            timeout_seconds=30,
            check=True,
        )
        refs = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        codex_factory = [ref for ref in refs if ref.startswith("refs/heads/codex/factory/")]
        return {
            "refs_heads_count": len(refs),
            "refs_heads": refs,
            "codex_factory_heads": codex_factory,
            "codex_factory_present": bool(codex_factory),
        }

    def _collect_refs_map(self) -> dict[str, str]:
        repo_root, _, _, _, _ = self._require_paths()
        completed = self._run_capture(
            stage="collect_refs_map",
            command=["git", "-C", str(repo_root), "for-each-ref", "--format=%(refname) %(objectname)"],
            cwd=repo_root,
            timeout_seconds=30,
            check=True,
        )
        mapping: dict[str, str] = {}
        for raw in completed.stdout.splitlines():
            line = raw.strip()
            if not line:
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            mapping[parts[0]] = parts[1]
        return mapping

    def _worktree_root(self) -> Path:
        repo_root, _, _, _, _ = self._require_paths()
        return repo_root / WORKTREE_ROOT_REL

    def _allowed_worktree_dirs(self) -> list[Path]:
        root = self._worktree_root()
        return [root / worker for worker in WORKERS]

    def _collect_worktree_dirs(self) -> list[str]:
        repo_root, _, _, _, _ = self._require_paths()
        root = self._worktree_root().resolve()
        completed = self._run_capture(
            stage="worktree_list",
            command=["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
            cwd=repo_root,
            timeout_seconds=30,
            check=True,
        )
        entries: list[str] = []
        current_worktree: str | None = None
        for raw in completed.stdout.splitlines():
            line = raw.strip()
            if not line:
                if current_worktree is not None:
                    current_worktree = None
                continue
            if line.startswith("worktree "):
                current_worktree = line.split(" ", 1)[1].strip()
                candidate = Path(current_worktree).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    continue
                entries.append(candidate.as_posix())
        return sorted(set(entries))

    def _write_branch_guard_report(self) -> None:
        _, _, _, global_debug_dir, _ = self._require_paths()
        before = self.branch_before or {
            "refs_heads_count": 0,
            "refs_heads": [],
            "codex_factory_heads": [],
            "codex_factory_present": False,
        }
        after = self.branch_after or {
            "refs_heads_count": 0,
            "refs_heads": [],
            "codex_factory_heads": [],
            "codex_factory_present": False,
        }

        codex_factory_heads = sorted(set(before.get("codex_factory_heads", [])) | set(after.get("codex_factory_heads", [])))
        payload = {
            "run_id": self.run_id,
            "generated_at_utc": _now_utc_iso(),
            "refs_heads_count_before": int(before.get("refs_heads_count", 0)),
            "refs_heads_count_after": int(after.get("refs_heads_count", 0)),
            "refs_heads": {
                "before": list(before.get("refs_heads", [])),
                "after": list(after.get("refs_heads", [])),
            },
            "codex_factory_heads_present": bool(codex_factory_heads),
            "codex_factory_heads": codex_factory_heads,
        }
        _write_json(global_debug_dir / "branch_guard_report.json", payload)

    def _write_worktree_guard_report(self, unexpected_paths: list[str]) -> None:
        _, _, _, global_debug_dir, _ = self._require_paths()
        payload = {
            "run_id": self.run_id,
            "generated_at_utc": _now_utc_iso(),
            "worktree_directories_before": list(self.worktree_before),
            "worktree_directories_after": list(self.worktree_after),
            "unexpected_paths": sorted(set(unexpected_paths)),
        }
        _write_json(global_debug_dir / "worktree_guard_report.json", payload)

    def _assert_refs_changes_scoped(self) -> None:
        before = self.ref_map_before
        after = self.ref_map_after
        changed: list[str] = []
        for ref in sorted(set(before.keys()) | set(after.keys())):
            if before.get(ref) != after.get(ref):
                changed.append(ref)
        forbidden = [ref for ref in changed if not ref.startswith(SNAPSHOT_REF_PREFIX)]
        if forbidden:
            raise ExecutorFailure(
                "snapshot scope guard failed; changed refs outside refs/hos/snapshots/: " + ",".join(forbidden)
            )

    def _assert_branch_guard(self) -> None:
        before_count = int(self.branch_before.get("refs_heads_count", 0))
        after_count = int(self.branch_after.get("refs_heads_count", 0))
        codex_factory_present = bool(self.branch_before.get("codex_factory_present")) or bool(
            self.branch_after.get("codex_factory_present")
        )

        if codex_factory_present:
            raise ExecutorFailure("branch guard failed: refs/heads/codex/factory/* is present")
        if before_count != after_count:
            raise ExecutorFailure(f"branch guard failed: refs/heads count changed ({before_count} -> {after_count})")

    def _ensure_fixed_worktrees(self) -> None:
        repo_root, _, _, _, _ = self._require_paths()
        root = self._worktree_root()
        root.mkdir(parents=True, exist_ok=True)

        allowed = {path.resolve().as_posix() for path in self._allowed_worktree_dirs()}
        self.worktree_before = self._collect_worktree_dirs()
        unexpected_before = [path for path in self.worktree_before if path not in allowed]

        if len(self.worktree_before) > len(WORKERS):
            self.worktree_after = list(self.worktree_before)
            self._write_worktree_guard_report(unexpected_before)
            raise ExecutorFailure("worktree guard failed: more than 5 worktree directories exist")
        if unexpected_before:
            self.worktree_after = list(self.worktree_before)
            self._write_worktree_guard_report(unexpected_before)
            raise ExecutorFailure("worktree guard failed: unexpected worktree directory exists")

        baseline_sha = self._run_capture(
            stage="baseline_sha",
            command=["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            cwd=repo_root,
            timeout_seconds=20,
            check=True,
        ).stdout.strip()

        for target in self._allowed_worktree_dirs():
            target_norm = target.resolve().as_posix()
            if target_norm in self.worktree_before:
                continue
            if target.exists():
                raise ExecutorFailure(
                    "worktree guard failed: expected worktree path exists but is not registered: "
                    + target.as_posix()
                )
            self._run_capture(
                stage=f"worktree_add_{target.name}",
                command=["git", "-C", str(repo_root), "worktree", "add", "--detach", str(target), baseline_sha],
                cwd=repo_root,
                timeout_seconds=180,
                check=True,
            )

        self.worktree_after = self._collect_worktree_dirs()
        unexpected_after = [path for path in self.worktree_after if path not in allowed]
        missing_after = [path for path in sorted(allowed) if path not in self.worktree_after]
        self._write_worktree_guard_report(unexpected_after)

        if len(self.worktree_after) > len(WORKERS):
            raise ExecutorFailure("worktree guard failed: more than 5 worktree directories exist after ensure")
        if unexpected_after:
            raise ExecutorFailure("worktree guard failed: unexpected worktree directory exists after ensure")
        if missing_after:
            raise ExecutorFailure("worktree guard failed: one or more fixed worktree directories are missing")

    def _validate_run_id_or_fail(self) -> None:
        if not _run_id_valid(self.run_id):
            raise ExecutorFailure("RUN_ID is invalid; expected old or new factory format")

    def _generate_run_id(self) -> str:
        if self.repo_root is None:
            raise ExecutorFailure("repo root is not initialized")
        repo_root = self.repo_root
        runs_root = repo_root / RUNS_ROOT_REL
        prompts_root = repo_root / "tools" / "codex" / "prompts"
        zip_root = repo_root / "tools" / "codex" / "prompt_zips"

        for _ in range(1024):
            stamp = _now_utc().strftime("%Y%m%d_%H%M%S")
            rand4 = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            candidate = f"{stamp}_{rand4}"
            probes = [
                runs_root / candidate,
                prompts_root / candidate,
                zip_root / f"{candidate}.zip",
            ]
            if any(path.exists() for path in probes):
                continue
            return candidate
        raise ExecutorFailure("unable to generate collision-safe RUN_ID")

    def _done_marker_path(self, worker: str) -> Path:
        _, run_root, _, _, _ = self._require_paths()
        return run_root / worker / "DONE.marker"

    def _done_marker_ok(self, worker: str) -> bool:
        path = self._done_marker_path(worker)
        if not path.exists():
            return False
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return False
        token = f"DONE {self.run_id} {worker}"
        return token in text

    def _refresh_done_markers(self) -> None:
        for worker in WORKERS:
            self.worker_done[worker] = self._done_marker_ok(worker)

    def _all_done(self) -> bool:
        return all(bool(self.worker_done.get(worker, False)) for worker in WORKERS)

    def _pending_workers(self) -> list[str]:
        return [worker for worker in WORKERS if not self.worker_done.get(worker, False)]

    def _build_prompt_pack_text(self) -> str:
        blocks: list[str] = []
        for worker in WORKERS:
            blocks.extend(
                [
                    f"=== {worker} PROMPT ===",
                    "RUN_ID: {{RUN_ID}}",
                    f"CODEX_ID: {worker}",
                    "MODE: FACTORY_AUTOGEN",
                    "TASK: Complete your assigned worker scope for this run with deterministic outputs.",
                    f"DONE_MARKER_PATH: tools/codex/runs/{{{{RUN_ID}}}}/{worker}/DONE.marker",
                    f"DONE_MARKER_TOKEN: DONE {{{{RUN_ID}}}} {worker}",
                    "After finishing your scope, write the DONE marker token exactly as specified.",
                    "",
                ]
            )
        return "\n".join(blocks).rstrip() + "\n"

    def _ensure_prompt_pack(self) -> Path:
        _, run_root, _, _, _ = self._require_paths()
        pack_dir = run_root / "pack"
        pack_dir.mkdir(parents=True, exist_ok=True)

        pack_path = pack_dir / "raw_pack.txt"
        if self.resume_run_id and pack_path.exists():
            return pack_path

        pack_text = self._build_prompt_pack_text()
        pack_path.write_text(pack_text, encoding="utf-8", newline="\n")
        return pack_path

    def _write_status_file(self) -> None:
        if self.run_root is None:
            return
        payload = {
            "run_id": self.run_id,
            "status": self.status,
            "error": self.error,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc or "",
            "timeline": list(self.timeline),
            "worker_attempts": dict(self.worker_attempts),
            "worker_done": dict(self.worker_done),
            "artifacts": {
                "run_root": self.run_root.as_posix(),
                "report": (self.run_root / "TXN_EXECUTOR_REPORT.md").as_posix(),
                "branch_guard_report": ((self.global_debug_dir or Path(".")) / "branch_guard_report.json").as_posix(),
                "worktree_guard_report": ((self.global_debug_dir or Path(".")) / "worktree_guard_report.json").as_posix(),
            },
        }
        _write_json(self.run_root / "STATUS.json", payload)

    def _write_report(self) -> None:
        if self.run_root is None or self.global_debug_dir is None:
            return

        done_a = self._done_marker_path("A_core")

        lines: list[str] = [
            "# TXN Executor Report",
            "",
            f"- run_id: {self.run_id}",
            f"- status: {self.status}",
            f"- started_at_utc: {self.started_at_utc}",
            f"- ended_at_utc: {self.ended_at_utc}",
            f"- dry_run: {str(self.dry_run).lower()}",
            f"- resume_mode: {str(bool(self.resume_run_id)).lower()}",
            f"- torture_mode: {str(self.torture_mode).lower()}",
            "",
            "## Artifacts",
            "",
            f"- status_json: {(self.run_root / 'STATUS.json').as_posix()}",
            f"- branch_guard_report: {(self.global_debug_dir / 'branch_guard_report.json').as_posix()}",
            f"- worktree_guard_report: {(self.global_debug_dir / 'worktree_guard_report.json').as_posix()}",
            f"- done_marker_a_core: {done_a.as_posix()}",
            "",
            "## Worker State",
            "",
        ]

        for worker in WORKERS:
            lines.append(
                f"- {worker}: done={str(bool(self.worker_done.get(worker, False))).lower()} attempts={int(self.worker_attempts.get(worker, 0))}"
            )

        lines.extend(["", "## Timeline", ""])
        for item in self.timeline:
            detail = str(item.get("detail", "")).strip()
            stage = str(item.get("stage", ""))
            state = str(item.get("status", ""))
            ts = str(item.get("ts_utc", ""))
            suffix = f" :: {detail}" if detail else ""
            lines.append(f"- {ts} [{state}] {stage}{suffix}")

        lines.extend(["", "## Error", "", f"- {self.error or '<none>'}"])

        (self.run_root / "TXN_EXECUTOR_REPORT.md").write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def _write_last_result_pointer(self) -> None:
        if self.repo_root is None or self.run_root is None:
            return
        pointer = {
            "run_id": self.run_id,
            "status": self.status,
            "error": self.error,
            "run_root": self.run_root.as_posix(),
            "status_path": (self.run_root / "STATUS.json").as_posix(),
            "report_path": (self.run_root / "TXN_EXECUTOR_REPORT.md").as_posix(),
            "ended_at_utc": self.ended_at_utc or _now_utc_iso(),
        }
        _write_json((self.repo_root / DEBUG_ROOT_REL) / "last_runtime_result.json", pointer)

    def _run_validator_wait_done(self) -> None:
        repo_root, _, _, _, _ = self._require_paths()
        timeout_seconds = int(
            os.environ.get("FACTORY_WORKER_DONE_TIMEOUT", str(DEFAULT_WORKER_DONE_TIMEOUT))
            or str(DEFAULT_WORKER_DONE_TIMEOUT)
        )
        cmd = [
            sys.executable,
            str(self.validator_path),
            "wait-done",
            "--run-id",
            self.run_id,
            "--workers",
            ",".join(WORKERS),
            "--timeout-seconds",
            str(timeout_seconds),
            "--poll-seconds",
            "2",
        ]
        completed = self._run_capture(
            stage="validate_done_markers",
            command=cmd,
            cwd=repo_root,
            timeout_seconds=max(120.0, timeout_seconds + 120.0),
            check=False,
        )
        if completed.returncode != 0:
            raise ExecutorFailure("DONE marker validation failed")

    def _run_integrate_and_guardrails(self) -> None:
        repo_root, _, _, _, _ = self._require_paths()
        workers_csv = ",".join(WORKERS)

        steps = [
            (
                "factory_bundle_validate",
                [
                    sys.executable,
                    "-m",
                    "tools.codex.factory",
                    "bundle-validate",
                    "--run-id",
                    self.run_id,
                    "--workers",
                    workers_csv,
                ],
                900.0,
            ),
            (
                "factory_integrate",
                [
                    sys.executable,
                    "-m",
                    "tools.codex.factory",
                    "integrate",
                    "--run-id",
                    self.run_id,
                    "--workers",
                    workers_csv,
                ],
                1800.0,
            ),
            (
                "factory_guardrails",
                [sys.executable, str(self.validator_path), "validate-guardrails", "--run-id", self.run_id],
                900.0,
            ),
        ]

        for stage, cmd, timeout in steps:
            completed = self._run_capture(
                stage=stage,
                command=cmd,
                cwd=repo_root,
                timeout_seconds=timeout,
                check=False,
            )
            if completed.returncode != 0:
                raise ExecutorFailure(f"{stage} failed")

    def _run_iter_once(self, *, attempt_number: int) -> subprocess.CompletedProcess[str]:
        repo_root, _, _, _, dispatcher_path = self._require_paths()
        if self.prompt_pack_path is None:
            raise ExecutorFailure("prompt pack path is not prepared")

        cmd = [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(dispatcher_path),
            "-RunId",
            self.run_id,
            "-PromptsPackPath",
            str(self.prompt_pack_path),
        ]
        return self._run_capture(
            stage=f"run_iter_attempt_{attempt_number}",
            command=cmd,
            cwd=repo_root,
            timeout_seconds=14400.0,
            check=False,
        )

    def _execute_full_run(self) -> None:
        while True:
            self._refresh_done_markers()
            pending = self._pending_workers()
            if not pending:
                self._record_timeline("dispatch", PASS_STATE, "all workers already DONE")
                return

            for worker in pending:
                next_attempt = int(self.worker_attempts.get(worker, 0)) + 1
                if next_attempt > MAX_ATTEMPTS_PER_WORKER:
                    raise ExecutorFailure(
                        f"retry limit reached for worker {worker} (max {MAX_ATTEMPTS_PER_WORKER})"
                    )
                self.worker_attempts[worker] = next_attempt
                if next_attempt > 1:
                    self._record_timeline(
                        "outer_retry",
                        RUNNING_STATE,
                        f"retry attempt {next_attempt} for {worker}",
                        worker=worker,
                        attempt=next_attempt,
                    )

            highest_attempt = max(self.worker_attempts[worker] for worker in pending)
            self._record_timeline(
                "dispatch",
                RUNNING_STATE,
                f"run_iter attempt {highest_attempt} for pending workers: {','.join(pending)}",
                pending_workers=pending,
                attempt=highest_attempt,
            )

            completed = self._run_iter_once(attempt_number=highest_attempt)
            self._refresh_done_markers()

            if completed.returncode == 0:
                self._record_timeline("dispatch", PASS_STATE, f"run_iter attempt {highest_attempt} completed")
                if not self._all_done():
                    missing = ",".join(self._pending_workers())
                    raise ExecutorFailure(f"run_iter returned success but DONE markers missing: {missing}")
                return

            merged_output = (completed.stdout or "") + "\n" + (completed.stderr or "")
            error_class = _detect_error_class(merged_output)
            pending_after = self._pending_workers()
            has_retry_budget = any(
                int(self.worker_attempts.get(worker, 0)) < MAX_ATTEMPTS_PER_WORKER for worker in pending_after
            )

            self._record_timeline(
                "dispatch",
                FAIL_STATE,
                f"run_iter attempt {highest_attempt} failed (rc={completed.returncode})",
                attempt=highest_attempt,
                rc=completed.returncode,
                error_class=error_class or "NON_RECOVERABLE",
                pending_workers=pending_after,
            )

            if error_class in RECOVERABLE_ERROR_CLASSES and has_retry_budget:
                self._record_timeline(
                    "retry_decision",
                    RUNNING_STATE,
                    f"recoverable class {error_class}; scheduling outer retry",
                    error_class=error_class,
                )
                continue

            if error_class is None:
                raise ExecutorFailure("run_iter failed with non-recoverable error class")
            raise ExecutorFailure(
                f"run_iter failed with non-recoverable class: {error_class}",
                error_class=error_class,
            )

    def _execute_torture_mode(self) -> None:
        repo_root, _, run_debug_dir, _, dispatcher_path = self._require_paths()
        if self.prompt_pack_path is None:
            raise ExecutorFailure("prompt pack path is not prepared")

        marker_timeout = int(os.environ.get("HOS_FACTORY_FIRST_MARKER_TIMEOUT", "7200") or "7200")

        for attempt in range(1, MAX_ATTEMPTS_PER_WORKER + 1):
            self.worker_attempts["A_core"] = attempt
            if attempt > 1:
                self._record_timeline(
                    "outer_retry",
                    RUNNING_STATE,
                    f"retry attempt {attempt} for A_core in torture mode",
                    worker="A_core",
                    attempt=attempt,
                )

            out_path = run_debug_dir / f"RUN_ITER_TORTURE_ATTEMPT_{attempt}_STDOUT.log"
            err_path = run_debug_dir / f"RUN_ITER_TORTURE_ATTEMPT_{attempt}_STDERR.log"
            cmd = [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(dispatcher_path),
                "-RunId",
                self.run_id,
                "-PromptsPackPath",
                str(self.prompt_pack_path),
            ]
            self.logger.log("torture_dispatch", "CMD: " + " ".join(cmd))
            self._record_timeline(
                "torture_dispatch",
                RUNNING_STATE,
                f"attempt {attempt} started",
                attempt=attempt,
            )

            with out_path.open("w", encoding="utf-8", newline="\n") as stdout_handle, err_path.open(
                "w",
                encoding="utf-8",
                newline="\n",
            ) as stderr_handle:
                try:
                    proc = subprocess.Popen(
                        cmd,
                        cwd=str(repo_root),
                        stdout=stdout_handle,
                        stderr=stderr_handle,
                        text=True,
                    )
                except OSError as exc:
                    raise ExecutorFailure(f"unable to launch run_iter in torture mode: {exc}") from exc

                deadline = time.monotonic() + marker_timeout
                found_a_done = False

                while True:
                    if self._done_marker_ok("A_core"):
                        found_a_done = True
                        self.worker_done["A_core"] = True
                        self._record_timeline(
                            "torture_dispatch",
                            RUNNING_STATE,
                            "A_core DONE marker detected; stopping run intentionally",
                            attempt=attempt,
                            done_marker=self._done_marker_path("A_core").as_posix(),
                        )
                        proc.terminate()
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=5)
                        break

                    rc = proc.poll()
                    if rc is not None:
                        break

                    if time.monotonic() >= deadline:
                        proc.terminate()
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=5)
                        rc = proc.returncode if proc.returncode is not None else 124
                        self._record_timeline(
                            "torture_dispatch",
                            FAIL_STATE,
                            f"timeout waiting for first DONE marker (attempt {attempt})",
                            attempt=attempt,
                            rc=rc,
                        )
                        break

                    time.sleep(1.0)

                if found_a_done:
                    return

            stdout_text = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else ""
            stderr_text = err_path.read_text(encoding="utf-8", errors="replace") if err_path.exists() else ""
            merged = stdout_text + "\n" + stderr_text
            error_class = _detect_error_class(merged)
            self._record_timeline(
                "torture_dispatch",
                FAIL_STATE,
                f"attempt {attempt} failed before A_core DONE marker",
                attempt=attempt,
                error_class=error_class or "NON_RECOVERABLE",
            )

            if error_class in RECOVERABLE_ERROR_CLASSES and attempt < MAX_ATTEMPTS_PER_WORKER:
                self._record_timeline(
                    "retry_decision",
                    RUNNING_STATE,
                    f"recoverable class {error_class}; retrying torture attempt",
                    attempt=attempt,
                    error_class=error_class,
                )
                continue

            if error_class is None:
                raise ExecutorFailure("torture mode failed with non-recoverable error class")
            raise ExecutorFailure(
                f"torture mode failed with non-recoverable class: {error_class}",
                error_class=error_class,
            )

        raise ExecutorFailure("torture mode exhausted retries without A_core DONE marker")

    def _setup(self) -> None:
        self.repo_root = _resolve_repo_root()
        repo_root = self.repo_root

        self.dispatcher_path = repo_root / DISPATCHER_REL
        self.validator_path = repo_root / VALIDATOR_REL
        if not self.dispatcher_path.exists():
            raise ExecutorFailure(f"dispatcher path is missing: {self.dispatcher_path.as_posix()}")
        if not self.validator_path.exists():
            raise ExecutorFailure(f"validator path is missing: {self.validator_path.as_posix()}")

        self.global_debug_dir = repo_root / DEBUG_ROOT_REL
        self.global_debug_dir.mkdir(parents=True, exist_ok=True)

        if self.resume_run_id:
            self.run_id = self.resume_run_id
        else:
            self.run_id = self._generate_run_id()

        self.run_root = repo_root / RUNS_ROOT_REL / self.run_id
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.run_debug_dir = self.run_root / "_debug"
        self.run_debug_dir.mkdir(parents=True, exist_ok=True)

        self.logger.bind(self.run_debug_dir / "TXN_EXECUTOR.log")
        self.logger.log("init", f"repo_root={repo_root.as_posix()}")
        self.logger.log("init", f"run_id={self.run_id}")

    def _finalize(self, *, status: str, error: str) -> int:
        self.status = status
        self.error = error
        self.ended_at_utc = _now_utc_iso()

        if status == FAIL_STATE:
            self.exit_code = EXIT_FAILURE
        else:
            self.exit_code = EXIT_SUCCESS

        self._write_status_file()
        self._write_report()
        self._write_last_result_pointer()
        return self.exit_code

    def execute(self) -> int:
        try:
            self._setup()
            self._record_timeline("runtime", RUNNING_STATE, "initializing execution")
            self._validate_run_id_or_fail()

            self.branch_before = self._collect_heads()
            self.branch_after = dict(self.branch_before)
            self._write_branch_guard_report()
            if bool(self.branch_before.get("codex_factory_present", False)):
                raise ExecutorFailure("branch guard failed before execution: refs/heads/codex/factory/* exists")

            self.ref_map_before = self._collect_refs_map()

            self._ensure_fixed_worktrees()
            self.prompt_pack_path = self._ensure_prompt_pack()
            self._record_timeline(
                "prompt_pack",
                PASS_STATE,
                f"prompt pack ready: {self.prompt_pack_path.as_posix()}",
            )

            if self.dry_run:
                self._record_timeline("runtime", PASS_STATE, "dry-run completed; dispatch skipped")
            elif self.torture_mode:
                self._execute_torture_mode()
                self._refresh_done_markers()
                if not self.worker_done.get("A_core", False):
                    raise ExecutorFailure("torture mode ended without A_core DONE marker")
                self._record_timeline(
                    "runtime",
                    PARTIAL_STATE,
                    "PARTIAL-SANITY-PASS after first worker DONE marker",
                    done_marker=self._done_marker_path("A_core").as_posix(),
                )
            else:
                self._execute_full_run()
                self._run_validator_wait_done()
                self._run_integrate_and_guardrails()
                self._refresh_done_markers()
                if not self._all_done():
                    raise ExecutorFailure("full run completed but one or more DONE markers are missing")
                self._record_timeline("runtime", PASS_STATE, "full run completed")

            self.branch_after = self._collect_heads()
            self._write_branch_guard_report()

            self.worktree_after = self._collect_worktree_dirs()
            allowed = {path.resolve().as_posix() for path in self._allowed_worktree_dirs()}
            unexpected_after = [path for path in self.worktree_after if path not in allowed]
            self._write_worktree_guard_report(unexpected_after)

            self.ref_map_after = self._collect_refs_map()
            self._assert_refs_changes_scoped()
            self._assert_branch_guard()

            if len(self.worktree_after) > len(WORKERS):
                raise ExecutorFailure("worktree guard failed after execution: more than 5 worktree directories exist")
            if unexpected_after:
                raise ExecutorFailure("worktree guard failed after execution: unexpected worktree directory exists")

            if self.torture_mode and not self.dry_run:
                return self._finalize(status=PARTIAL_STATE, error="")

            return self._finalize(status=PASS_STATE, error="")

        except ExecutorFailure as exc:
            self.logger.log("fatal", str(exc), level="ERROR")
            try:
                if self.repo_root is not None and self.dispatcher_path is not None:
                    self.branch_after = self._collect_heads()
                    self._write_branch_guard_report()
            except Exception:
                pass
            return self._finalize(status=FAIL_STATE, error=str(exc))
        except Exception as exc:
            self.logger.log("fatal", f"unexpected runtime failure: {exc!r}", level="ERROR")
            try:
                if self.repo_root is not None and self.dispatcher_path is not None:
                    self.branch_after = self._collect_heads()
                    self._write_branch_guard_report()
            except Exception:
                pass
            return self._finalize(status=FAIL_STATE, error=f"unexpected runtime failure: {exc!r}")


def run_snapshot_gc(*, keep_days: int, keep_count: int) -> int:
    try:
        repo_root = _resolve_repo_root()
    except ExecutorFailure as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_FAILURE

    now = _now_utc()
    report_root = repo_root / RUNS_ROOT_REL / "_gc"
    report_root.mkdir(parents=True, exist_ok=True)

    try:
        listed = subprocess.run(
            ["git", "-C", str(repo_root), "for-each-ref", "--format=%(refname)", f"{SNAPSHOT_REF_PREFIX}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except Exception as exc:
        print(f"gc failed listing refs: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    refs = [line.strip() for line in listed.stdout.splitlines() if line.strip()]
    pattern = re.compile(r"^refs/hos/snapshots/(?P<worker>[^/]+)/(?P<run_id>[^/]+)/(?P<phase>[^/]+)$")

    run_to_refs: dict[str, list[str]] = {}
    run_to_stamp: dict[str, dt.datetime] = {}

    for ref in refs:
        match = pattern.fullmatch(ref)
        if not match:
            continue
        run_id = str(match.group("run_id"))
        run_to_refs.setdefault(run_id, []).append(ref)
        stamp = _parse_run_id_timestamp(run_id) or dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)
        run_to_stamp[run_id] = stamp

    ordered_runs = sorted(run_to_stamp.keys(), key=lambda item: (run_to_stamp[item], item), reverse=True)

    keep_set = set(ordered_runs[: max(0, int(keep_count))])
    for run_id in ordered_runs:
        age_days = (now - run_to_stamp[run_id]).total_seconds() / 86400.0
        if age_days <= float(keep_days):
            keep_set.add(run_id)

    delete_refs: list[str] = []
    for run_id, ref_list in run_to_refs.items():
        if run_id in keep_set:
            continue
        delete_refs.extend(ref_list)
    delete_refs = sorted(set(delete_refs))

    deleted: list[str] = []
    failed: list[dict[str, Any]] = []

    for ref in delete_refs:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "update-ref", "-d", ref],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=20,
        )
        if proc.returncode == 0:
            deleted.append(ref)
        else:
            failed.append({"ref": ref, "rc": proc.returncode, "stderr": proc.stderr.strip()})

    status = PASS_STATE if not failed else FAIL_STATE
    stamp = _now_utc().strftime("%Y%m%d_%H%M%S")
    payload = {
        "status": status,
        "timestamp_utc": _now_utc_iso(),
        "keep_days": int(keep_days),
        "keep_count": int(keep_count),
        "total_snapshot_refs": len(refs),
        "runs_considered": len(ordered_runs),
        "deleted_refs": deleted,
        "failed_deletes": failed,
    }
    _write_json(report_root / f"GC_{stamp}.json", payload)

    lines: list[str] = [
        "# Snapshot GC Report",
        "",
        f"- status: {status}",
        f"- keep_days: {int(keep_days)}",
        f"- keep_count: {int(keep_count)}",
        f"- total_snapshot_refs: {len(refs)}",
        f"- deleted_refs: {len(deleted)}",
        f"- failed_deletes: {len(failed)}",
        "",
        "## Deleted Refs",
        "",
    ]
    if deleted:
        lines.extend(f"- {ref}" for ref in deleted)
    else:
        lines.append("- <none>")
    lines.extend(["", "## Failed Deletes", ""])
    if failed:
        lines.extend(f"- {item['ref']} (rc={item['rc']}) {item['stderr']}" for item in failed)
    else:
        lines.append("- <none>")

    (report_root / f"GC_{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return EXIT_SUCCESS if status == PASS_STATE else EXIT_FAILURE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HITECH-OS fortress transactional runtime")
    parser.add_argument("--dry-run", action="store_true", help="Run preflight/guards only.")
    parser.add_argument("--resume-run-id", help="Resume existing run id.")
    parser.add_argument("--outer-retry", action="store_true", help="Compatibility flag; behavior is built-in.")
    parser.add_argument("--torture-mode", action="store_true", help="Stop intentionally after first A_core DONE marker.")
    parser.add_argument("--gc", action="store_true", help="Run snapshot reference GC only.")
    parser.add_argument("--keep-days", type=int, default=14, help="GC retention in days.")
    parser.add_argument("--keep-count", type=int, default=20, help="GC retention by latest run count.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gc:
        return run_snapshot_gc(keep_days=int(args.keep_days), keep_count=int(args.keep_count))

    torture_mode = bool(args.torture_mode or _truthy(os.environ.get("HOS_FACTORY_TORTURE_MODE")))
    executor = TxnExecutor(
        dry_run=bool(args.dry_run or _truthy(os.environ.get("DRY_RUN"))),
        resume_run_id=str(args.resume_run_id).strip() if args.resume_run_id else None,
        torture_mode=torture_mode,
    )
    rc = executor.execute()

    summary = {
        "run_id": executor.run_id,
        "status": executor.status,
        "error": executor.error,
        "run_root": executor.run_root.as_posix() if executor.run_root else "",
        "status_path": (executor.run_root / "STATUS.json").as_posix() if executor.run_root else "",
        "report_path": (executor.run_root / "TXN_EXECUTOR_REPORT.md").as_posix() if executor.run_root else "",
        "branch_guard_report": ((executor.global_debug_dir / "branch_guard_report.json").as_posix() if executor.global_debug_dir else ""),
        "worktree_guard_report": ((executor.global_debug_dir / "worktree_guard_report.json").as_posix() if executor.global_debug_dir else ""),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

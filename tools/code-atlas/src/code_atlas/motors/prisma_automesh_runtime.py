#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared runtime primitives for PRISMA AutoMesh/Smart AllMesh.

The module is intentionally dependency-free and Windows-safe. It provides:
- collision-proof run IDs;
- structured/live progress with heartbeat and ETA;
- a cross-process 18-slot worker governor;
- streamed child-process output;
- atomic, CRC-validated ZIP publication.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import os
import queue
import random
import shutil
import signal
import subprocess
import threading
import time
import traceback
import uuid
import zipfile
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

DEFAULT_GLOBAL_BUDGET_ROOT = Path(
    os.environ.get(
        "PRISMA_AUTOMESH_BUDGET_ROOT",
        r"F:\descargasf\.prisma_automesh_worker_budget",
    )
)


def make_run_id(prefix: str = "automesh") -> str:
    now = dt.datetime.now()
    nonce = uuid.uuid4().hex[:8]
    return f"{prefix}_{now:%Y%m%dT%H%M%S%f}_{os.getpid()}_{nonce}"


def short_run_id(run_id: str, length: int = 12) -> str:
    cleaned = "".join(ch for ch in run_id if ch.isalnum())
    return cleaned[-length:] if cleaned else uuid.uuid4().hex[:length]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _duration(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "n/d"
    seconds_i = int(seconds)
    hours, remainder = divmod(seconds_i, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class ProgressReporter:
    """Thread-safe console + JSONL progress reporter with heartbeat."""

    def __init__(
        self,
        *,
        run_id: str,
        jsonl_path: Path | None = None,
        width: int = 30,
        component: str = "automesh",
    ) -> None:
        self.run_id = run_id
        self.jsonl_path = jsonl_path
        self.width = max(10, width)
        self.component = component
        self.started_monotonic = time.monotonic()
        self.started_at = dt.datetime.now().isoformat()
        self._lock = threading.RLock()
        self._last_emit_monotonic = 0.0
        self._last_event: dict[str, Any] = {
            "percent": 0,
            "label": "iniciando",
            "done": None,
            "total": None,
            "details": {},
            "status": "RUNNING",
        }
        self._stop_event = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None
        if self.jsonl_path is not None:
            self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def elapsed_seconds(self) -> float:
        return max(0.0, time.monotonic() - self.started_monotonic)

    def emit(
        self,
        percent: int | float,
        label: str,
        *,
        done: int | None = None,
        total: int | None = None,
        status: str = "RUNNING",
        details: Mapping[str, Any] | None = None,
        heartbeat: bool = False,
        force: bool = True,
    ) -> dict[str, Any]:
        now_monotonic = time.monotonic()
        pct = max(0, min(100, int(percent)))
        elapsed = self.elapsed_seconds
        eta: float | None = None
        if 0 < pct < 100:
            eta = max(0.0, elapsed * (100 - pct) / pct)

        event: dict[str, Any] = {
            "kind": "PRISMA_AUTOMESH_PROGRESS",
            "run_id": self.run_id,
            "component": self.component,
            "timestamp": dt.datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 3),
            "eta_seconds": round(eta, 3) if eta is not None else None,
            "percent": pct,
            "label": str(label),
            "done": done,
            "total": total,
            "status": status,
            "heartbeat": bool(heartbeat),
            "details": dict(details or {}),
        }

        with self._lock:
            if not force and now_monotonic - self._last_emit_monotonic < 0.5:
                return event
            self._last_emit_monotonic = now_monotonic
            self._last_event = {
                "percent": pct,
                "label": str(label),
                "done": done,
                "total": total,
                "details": dict(details or {}),
                "status": status,
            }

            fill = int(self.width * pct / 100)
            bar = "█" * fill + "░" * (self.width - fill)
            count = ""
            if done is not None:
                count = f" | {done}"
                if total is not None:
                    count += f"/{total}"
            suffix = " | heartbeat" if heartbeat else ""
            print(
                f"[{bar}] {pct:3d}% | lleva {_duration(elapsed)} | "
                f"falta {_duration(eta)} | {label}{count}{suffix}",
                flush=True,
            )

            if self.jsonl_path is not None:
                with self.jsonl_path.open("a", encoding="utf-8", errors="replace") as stream:
                    stream.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event

    def start_heartbeat(self, interval_seconds: float = 5.0) -> None:
        if self._heartbeat_thread is not None:
            return

        def worker() -> None:
            while not self._stop_event.wait(max(1.0, interval_seconds)):
                with self._lock:
                    last_age = time.monotonic() - self._last_emit_monotonic
                    snapshot = dict(self._last_event)
                if last_age < interval_seconds:
                    continue
                self.emit(
                    snapshot.get("percent", 0),
                    snapshot.get("label", "trabajando"),
                    done=snapshot.get("done"),
                    total=snapshot.get("total"),
                    status=snapshot.get("status", "RUNNING"),
                    details=snapshot.get("details") or {},
                    heartbeat=True,
                    force=True,
                )

        self._heartbeat_thread = threading.Thread(
            target=worker,
            name=f"{self.component}-heartbeat",
            daemon=True,
        )
        self._heartbeat_thread.start()

    def stop_heartbeat(self) -> None:
        self._stop_event.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=2.0)




def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


class GlobalWorkerBudget:
    """Cross-process 18-worker governor.

    Windows uses 18 named mutexes. A mutex is owned by the worker thread and
    becomes abandoned automatically if its process dies, so a crashed worker
    cannot permanently consume capacity. This avoids the previous token-file
    race where contending readers could prevent a live owner from deleting its
    ``slot_*.lock`` file.

    Non-Windows platforms retain atomic token files for portability. Telemetry
    files are never used as locks and therefore cannot block execution.
    """

    WAIT_OBJECT_0 = 0x00000000
    WAIT_ABANDONED = 0x00000080
    WAIT_TIMEOUT = 0x00000102

    def __init__(
        self,
        root: Path | str | None = None,
        *,
        slots: int = 18,
        run_id: str,
    ) -> None:
        self.root = Path(root) if root else DEFAULT_GLOBAL_BUDGET_ROOT
        self.slots = max(1, min(18, int(slots)))
        self.run_id = run_id
        self.root.mkdir(parents=True, exist_ok=True)
        self._windows_handles: list[Any] = []
        self._kernel32 = None

        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CreateMutexW.argtypes = [
                wintypes.LPVOID,
                wintypes.BOOL,
                wintypes.LPCWSTR,
            ]
            kernel32.CreateMutexW.restype = wintypes.HANDLE
            kernel32.WaitForSingleObject.argtypes = [
                wintypes.HANDLE,
                wintypes.DWORD,
            ]
            kernel32.WaitForSingleObject.restype = wintypes.DWORD
            kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
            kernel32.ReleaseMutex.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            self._kernel32 = kernel32

            budget_key = hashlib.sha256(
                str(self.root.resolve()).lower().encode("utf-8", errors="replace")
            ).hexdigest()[:20]
            for index in range(self.slots):
                name = f"Local\\PRISMA_AUTOMESH_{budget_key}_SLOT_{index:02d}"
                handle = kernel32.CreateMutexW(None, False, name)
                if not handle:
                    error_code = ctypes.get_last_error()
                    self.close()
                    raise OSError(
                        error_code,
                        f"CreateMutexW failed for AutoMesh slot {index}",
                    )
                self._windows_handles.append(handle)

    def close(self) -> None:
        if self._kernel32 is None:
            return
        handles, self._windows_handles = self._windows_handles, []
        for handle in handles:
            try:
                self._kernel32.CloseHandle(handle)
            except Exception:
                pass

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def _token_path(self, index: int) -> Path:
        return self.root / f"slot_{index:02d}.lock"

    def _cleanup_stale_token(self, path: Path) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            pid = int(payload.get("pid", 0))
            if not _pid_alive(pid):
                path.unlink(missing_ok=True)
                return
        except Exception:
            try:
                if time.time() - path.stat().st_mtime > 300:
                    path.unlink(missing_ok=True)
            except Exception:
                pass

    def _telemetry_path(self, lease_id: str) -> Path:
        digest = hashlib.sha256(lease_id.encode("utf-8")).hexdigest()[:20]
        return self.root / (
            f"active_{os.getpid()}_{threading.get_ident()}_{digest}.json"
        )

    def _write_telemetry(
        self,
        path: Path,
        *,
        lease_id: str,
        task_id: str,
        slot_index: int,
        mechanism: str,
    ) -> None:
        payload = {
            "kind": "PRISMA_AUTOMESH_ACTIVE_WORKER",
            "lease_id": lease_id,
            "run_id": self.run_id,
            "task_id": task_id,
            "pid": os.getpid(),
            "thread_id": threading.get_ident(),
            "slot_index": slot_index,
            "mechanism": mechanism,
            "created_at": dt.datetime.now().isoformat(),
        }
        try:
            path.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            # Telemetry is observational only. It must never become a lock.
            pass

    @staticmethod
    def _remove_telemetry(path: Path) -> None:
        for delay in (0.0, 0.01, 0.03, 0.08, 0.15):
            if delay:
                time.sleep(delay)
            try:
                path.unlink(missing_ok=True)
                return
            except Exception:
                continue

    @contextlib.contextmanager
    def lease(
        self,
        task_id: str,
        *,
        cancel_event: threading.Event | None = None,
        poll_seconds: float = 0.05,
    ) -> Iterator[int]:
        lease_id = (
            f"{self.run_id}:{task_id}:{threading.get_ident()}:{uuid.uuid4().hex}"
        )
        seed = int(
            hashlib.sha256(lease_id.encode("utf-8")).hexdigest()[:8],
            16,
        )
        order = list(range(self.slots))
        random.Random(seed).shuffle(order)

        if os.name == "nt":
            if self._kernel32 is None or len(self._windows_handles) != self.slots:
                raise RuntimeError("AUTOMESH_WINDOWS_MUTEX_POOL_NOT_INITIALIZED")

            claimed_index = -1
            while claimed_index < 0:
                if cancel_event is not None and cancel_event.is_set():
                    raise RuntimeError(
                        "AUTOMESH_CANCELLED_WHILE_WAITING_FOR_GLOBAL_WORKER"
                    )

                for index in order:
                    result = int(
                        self._kernel32.WaitForSingleObject(
                            self._windows_handles[index],
                            0,
                        )
                    )
                    if result in (self.WAIT_OBJECT_0, self.WAIT_ABANDONED):
                        claimed_index = index
                        break
                    if result != self.WAIT_TIMEOUT:
                        raise OSError(
                            result,
                            f"WaitForSingleObject failed for AutoMesh slot {index}",
                        )

                if claimed_index < 0:
                    time.sleep(max(0.01, poll_seconds))

            telemetry = self._telemetry_path(lease_id)
            self._write_telemetry(
                telemetry,
                lease_id=lease_id,
                task_id=task_id,
                slot_index=claimed_index,
                mechanism="windows_named_mutex",
            )
            try:
                yield claimed_index
            finally:
                self._remove_telemetry(telemetry)
                if not self._kernel32.ReleaseMutex(
                    self._windows_handles[claimed_index]
                ):
                    import ctypes
                    raise OSError(
                        ctypes.get_last_error(),
                        f"ReleaseMutex failed for AutoMesh slot {claimed_index}",
                    )
            return

        claimed_path: Path | None = None
        claimed_index = -1
        while claimed_path is None:
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError(
                    "AUTOMESH_CANCELLED_WHILE_WAITING_FOR_GLOBAL_WORKER"
                )

            for index in order:
                path = self._token_path(index)
                try:
                    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                except FileExistsError:
                    self._cleanup_stale_token(path)
                    continue
                except OSError:
                    continue

                payload = {
                    "kind": "PRISMA_AUTOMESH_WORKER_LEASE",
                    "lease_id": lease_id,
                    "run_id": self.run_id,
                    "task_id": task_id,
                    "pid": os.getpid(),
                    "thread_id": threading.get_ident(),
                    "created_at": dt.datetime.now().isoformat(),
                }
                try:
                    os.write(
                        fd,
                        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    )
                except BaseException:
                    os.close(fd)
                    path.unlink(missing_ok=True)
                    raise
                else:
                    os.close(fd)

                claimed_path = path
                claimed_index = index
                break

            if claimed_path is None:
                time.sleep(max(0.01, poll_seconds))

        try:
            yield claimed_index
        finally:
            # On non-Windows this owner-created path is the lock. Retry removal
            # to tolerate transient scanners without allowing an eternal wait.
            for delay in (0.0, 0.01, 0.03, 0.08, 0.15, 0.30):
                if delay:
                    time.sleep(delay)
                try:
                    current = json.loads(
                        claimed_path.read_text(
                            encoding="utf-8",
                            errors="replace",
                        )
                    )
                    if current.get("lease_id") == lease_id:
                        claimed_path.unlink(missing_ok=True)
                    break
                except FileNotFoundError:
                    break
                except Exception:
                    continue


def atomic_zip_dir(
    source_dir: Path,
    destination_zip: Path,
    *,
    include_root: bool = False,
    compression_level: int = 8,
) -> dict[str, Any]:
    source_dir = source_dir.resolve()
    destination_zip.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_zip.with_name(
        f".{destination_zip.name}.{uuid.uuid4().hex}.tmp"
    )
    temporary.unlink(missing_ok=True)

    with zipfile.ZipFile(
        temporary,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=max(0, min(9, compression_level)),
    ) as archive:
        for path in sorted(source_dir.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file():
                continue
            relative = path.relative_to(source_dir)
            archive_name = (
                (Path(source_dir.name) / relative).as_posix()
                if include_root
                else relative.as_posix()
            )
            archive.write(path, archive_name)

    with zipfile.ZipFile(temporary, "r") as archive:
        bad_entry = archive.testzip()
        entry_count = len(archive.infolist())

    if bad_entry:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"ZIP_CRC_FAILURE: {bad_entry}")
    if entry_count < 1:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("ZIP_EMPTY")

    os.replace(temporary, destination_zip)
    return {
        "path": str(destination_zip),
        "entries": entry_count,
        "size": destination_zip.stat().st_size,
        "sha256": sha256(destination_zip),
    }


def extract_zip_verified(source_zip: Path, destination_dir: Path) -> dict[str, Any]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source_zip, "r") as archive:
        bad_entry = archive.testzip()
        if bad_entry:
            raise RuntimeError(f"SOURCE_ZIP_CRC_FAILURE: {bad_entry}")
        archive.extractall(destination_dir)
        entries = len(archive.infolist())
    return {
        "source": str(source_zip),
        "entries": entries,
        "sha256": sha256(source_zip),
    }


def _terminate_process_tree(proc: subprocess.Popen[str], grace_seconds: float = 5.0) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.send_signal(signal.SIGINT)
        proc.wait(timeout=grace_seconds)
        return
    except Exception:
        pass
    try:
        proc.terminate()
        proc.wait(timeout=3.0)
        return
    except Exception:
        pass
    try:
        proc.kill()
    except Exception:
        pass


def stream_command(
    command: Sequence[str],
    *,
    cwd: Path | None,
    log_path: Path,
    reporter: ProgressReporter | None = None,
    heartbeat_label: str = "motor hijo trabajando",
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run a child process while streaming merged stdout/stderr live."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    creationflags = 0
    if os.name == "nt":
        creationflags |= int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))

    child_env = os.environ.copy()
    child_env["PYTHONUNBUFFERED"] = "1"
    if env:
        child_env.update({str(key): str(value) for key, value in env.items()})

    line_queue: queue.Queue[str | None] = queue.Queue()
    markers: dict[str, str] = {}
    tail: list[str] = []

    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        log.write("\n\n$ " + " ".join(map(str, command)) + "\n")
        log.flush()

        proc = subprocess.Popen(
            list(command),
            cwd=str(cwd) if cwd else None,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            bufsize=1,
            shell=False,
            env=child_env,
            creationflags=creationflags,
        )

        def reader() -> None:
            try:
                assert proc.stdout is not None
                for raw_line in iter(proc.stdout.readline, ""):
                    line_queue.put(raw_line)
            finally:
                line_queue.put(None)

        reader_thread = threading.Thread(
            target=reader,
            name="automesh-child-output",
            daemon=True,
        )
        reader_thread.start()

        last_output = time.monotonic()
        reader_done = False
        try:
            while True:
                try:
                    item = line_queue.get(timeout=0.25)
                except queue.Empty:
                    item = ""

                if item is None:
                    reader_done = True
                elif item:
                    last_output = time.monotonic()
                    print(item, end="", flush=True)
                    log.write(item)
                    log.flush()
                    stripped = item.strip()
                    tail.append(stripped)
                    tail = tail[-200:]
                    for prefix in (
                        "OK_RESULT_ZIP=",
                        "FAIL_ZIP=",
                        "FINAL_RESULT_ZIP=",
                        "FINAL_FAIL_ZIP=",
                    ):
                        if stripped.startswith(prefix):
                            markers[prefix.rstrip("=")] = stripped[len(prefix):].strip()

                if reporter is not None and time.monotonic() - last_output >= 5.0:
                    snapshot = reporter._last_event  # guarded by reporter internally on emit
                    reporter.emit(
                        snapshot.get("percent", 0),
                        heartbeat_label,
                        done=snapshot.get("done"),
                        total=snapshot.get("total"),
                        details={"child_pid": proc.pid},
                        heartbeat=True,
                    )
                    last_output = time.monotonic()

                if proc.poll() is not None and reader_done and line_queue.empty():
                    break
        except KeyboardInterrupt:
            log.write("\n[controller] KeyboardInterrupt: cancelling child\n")
            log.flush()
            _terminate_process_tree(proc)
            raise
        finally:
            reader_thread.join(timeout=2.0)

        returncode = proc.wait()
        log.write(f"\n[returncode] {returncode}\n")
        log.flush()

    return {
        "returncode": returncode,
        "markers": markers,
        "tail": tail,
        "cmd": list(command),
        "pid": proc.pid,
    }


def capture_exception(exc: BaseException) -> dict[str, Any]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "repr": repr(exc),
        "traceback": "".join(traceback.format_exception(exc)),
    }


def safe_rmtree(path: Path) -> None:
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

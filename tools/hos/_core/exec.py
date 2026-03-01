#!/usr/bin/env python3
from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    elapsed_ms: int
    timed_out: bool
    classification: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def _classify(returncode: int, timed_out: bool, stderr: str) -> str:
    if timed_out:
        return "timeout"
    if returncode == 0:
        return "ok"
    if returncode < 0:
        return "signal"
    lower = stderr.lower()
    if "not found" in lower or "is not recognized" in lower:
        return "not_found"
    return "non_zero"


def _normalize_argv(argv: Sequence[str] | str) -> tuple[str, ...]:
    if isinstance(argv, str):
        return tuple(shlex.split(argv, posix=False))
    return tuple(str(part) for part in argv)


def run_command(
    argv: Sequence[str] | str,
    cwd: Path | None = None,
    timeout_seconds: float | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = False,
) -> CommandResult:
    normalized = _normalize_argv(argv)
    if not normalized:
        raise ValueError("argv must not be empty")

    run_cwd = str(cwd.resolve()) if cwd is not None else str(Path.cwd().resolve())
    started = time.perf_counter()
    timed_out = False

    try:
        completed = subprocess.run(
            normalized,
            cwd=run_cwd,
            env=dict(env) if env is not None else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or f"command timed out after {timeout_seconds} seconds"
    except FileNotFoundError as exc:
        returncode = 127
        stdout = ""
        stderr = str(exc)

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    classification = _classify(returncode=returncode, timed_out=timed_out, stderr=stderr)

    result = CommandResult(
        argv=normalized,
        cwd=run_cwd,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        elapsed_ms=elapsed_ms,
        timed_out=timed_out,
        classification=classification,
    )
    if check and not result.ok:
        command_text = " ".join(result.argv)
        raise RuntimeError(f"command failed ({result.classification}): {command_text}\n{result.stderr}".rstrip())
    return result


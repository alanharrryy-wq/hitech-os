from __future__ import annotations

import pathlib
import subprocess
from datetime import datetime, timedelta, timezone

from .constants import TIMEZONE_NAME


def detect_repo_root(explicit_root: str | None = None) -> pathlib.Path:
    if explicit_root:
        root = pathlib.Path(explicit_root).expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(f"repo root does not exist: {root}")
        return root

    git_root = _git_toplevel()
    if git_root is not None:
        return git_root

    script_guess = pathlib.Path(__file__).resolve().parents[2]
    if (script_guess / ".git").exists():
        return script_guess

    raise RuntimeError("unable to detect repo root; use --repo-root")


def _git_toplevel() -> pathlib.Path | None:
    try:
        cp = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    if cp.returncode != 0:
        return None

    path = cp.stdout.strip()
    if not path:
        return None

    return pathlib.Path(path).resolve()


def now_local_timestamp() -> tuple[str, str]:
    now_local = _now_mexico_city()
    iso = now_local.isoformat(timespec="seconds")
    run_id = now_local.strftime("RUN_%Y%m%d_%H%M%S")
    return run_id, iso


def _now_mexico_city() -> datetime:
    try:
        from zoneinfo import ZoneInfo

        zone = ZoneInfo(TIMEZONE_NAME)
        return datetime.now(zone)
    except Exception:
        # Deterministic fallback when tz database is unavailable.
        fixed = timezone(timedelta(hours=-6), name=TIMEZONE_NAME)
        return datetime.now(fixed)


def as_posix(path: pathlib.Path | str) -> str:
    return str(path).replace("\\", "/")

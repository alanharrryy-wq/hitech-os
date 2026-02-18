from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_DIR = REPO_ROOT / "tools" / "codex"
RUNS_DIR = CODEX_DIR / "runs"
FACTORY_DIR = CODEX_DIR / "factory"
SCHEMAS_DIR = CODEX_DIR / "schemas"
CONTRACTS_DIR = CODEX_DIR / "contracts" / "factory"
TEMPLATES_DIR = CODEX_DIR / "templates" / "factory"

WORKERS: tuple[str, ...] = ("A_worker", "B_worker", "C_worker", "D_worker")
INTEGRATOR = "Z_integrator"
DEFAULT_BRANCH_PREFIX = "codex/factory"
UTC = dt.timezone.utc


def now_utc() -> dt.datetime:
    return dt.datetime.now(UTC)


def iso_utc(value: dt.datetime | None = None) -> str:
    stamp = value or now_utc()
    return stamp.replace(microsecond=0).isoformat()


def compact_utc(value: dt.datetime | None = None) -> str:
    stamp = value or now_utc()
    return stamp.strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def stable_sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_rel(path: Path | str, start: Path | None = None) -> str:
    root = start or REPO_ROOT
    candidate = Path(path)
    if candidate.is_absolute():
        rel = candidate.relative_to(root)
    else:
        rel = candidate
    return rel.as_posix()


def sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values})


def bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def run_command(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 600,
) -> dict[str, Any]:
    run_cwd = cwd or REPO_ROOT
    proc = subprocess.run(
        list(command),
        cwd=str(run_cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "cmd": list(command),
        "cwd": str(run_cwd),
        "rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "combined": f"{proc.stdout}{proc.stderr}",
    }


def append_log(path: Path, line: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")


def deep_sort_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: deep_sort_json(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        if all(isinstance(item, dict) and "path" in item for item in value):
            ordered = sorted(value, key=lambda item: str(item.get("path", "")))
        else:
            ordered = value
        return [deep_sort_json(item) for item in ordered]
    return value


def render_command_log(entry: Mapping[str, Any]) -> str:
    cmd = " ".join(entry.get("cmd", []))
    return (
        f"# cmd: {cmd}\n"
        f"# cwd: {entry.get('cwd', '')}\n"
        f"# rc: {entry.get('rc', '')}\n\n"
        f"{entry.get('stdout', '')}"
        f"{entry.get('stderr', '')}"
    )


def load_json_or_default(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return read_json(path)

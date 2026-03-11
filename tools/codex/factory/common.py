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

CANONICAL_BUILD_WORKERS: tuple[str, ...] = ("A_core", "B_tooling", "C_features")
CANONICAL_VALIDATION_WORKERS: tuple[str, ...] = ("D_validation",)
CANONICAL_POST_RUN_WORKERS: tuple[str, ...] = ("R_reviewer", "E_planner")
PRE_INTEGRATION_WORKERS: tuple[str, ...] = (*CANONICAL_BUILD_WORKERS, *CANONICAL_VALIDATION_WORKERS)
CANONICAL_EXECUTION_WORKERS: tuple[str, ...] = (*PRE_INTEGRATION_WORKERS, "Z_aggregator")
CANONICAL_WORKERS: tuple[str, ...] = (*PRE_INTEGRATION_WORKERS, *CANONICAL_POST_RUN_WORKERS)
CANONICAL_INTEGRATOR = "Z_aggregator"
RUNTIME_WORKERS: tuple[str, ...] = (*PRE_INTEGRATION_WORKERS, CANONICAL_INTEGRATOR, *CANONICAL_POST_RUN_WORKERS)
WORKER_PHASE_BY_CANONICAL: dict[str, str] = {
    **{worker: "build" for worker in CANONICAL_BUILD_WORKERS},
    **{worker: "validation" for worker in CANONICAL_VALIDATION_WORKERS},
    CANONICAL_INTEGRATOR: "integration",
    **{worker: "post_run" for worker in CANONICAL_POST_RUN_WORKERS},
}
LEGACY_WORKER_ALIASES: dict[str, str] = {
    "A_worker": "A_core",
    "B_worker": "B_tooling",
    "C_worker": "C_features",
    "D_worker": "D_validation",
    "E_worker": "E_planner",
    "R_worker": "R_reviewer",
    "Z_integrator": "Z_aggregator",
}
LEGACY_ALIAS_BY_CANONICAL: dict[str, str] = {value: key for key, value in LEGACY_WORKER_ALIASES.items()}
KNOWN_WORKER_IDS: tuple[str, ...] = (
    *RUNTIME_WORKERS,
    *sorted(LEGACY_WORKER_ALIASES.keys()),
)

# Backward-compatible exports used by the rest of the factory runtime.
WORKERS: tuple[str, ...] = PRE_INTEGRATION_WORKERS
INTEGRATOR = CANONICAL_INTEGRATOR
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


def canonical_worker_id(worker: str) -> str:
    value = str(worker).strip()
    if not value:
        return value
    return LEGACY_WORKER_ALIASES.get(value, value)


def canonical_workers_for_phase(phase: str) -> tuple[str, ...]:
    key = str(phase).strip().lower()
    if key == "build":
        return CANONICAL_BUILD_WORKERS
    if key == "validation":
        return CANONICAL_VALIDATION_WORKERS
    if key == "integration":
        return (CANONICAL_INTEGRATOR,)
    if key in {"post_run", "postrun"}:
        return CANONICAL_POST_RUN_WORKERS
    return ()


def worker_phase(worker: str) -> str:
    canonical = canonical_worker_id(worker)
    return WORKER_PHASE_BY_CANONICAL.get(canonical, "")


def is_known_worker_id(
    worker: str,
    *,
    include_integrator: bool = True,
    include_post_run: bool = True,
) -> bool:
    canonical = canonical_worker_id(worker)
    if canonical in PRE_INTEGRATION_WORKERS:
        return True
    if include_post_run and canonical in CANONICAL_POST_RUN_WORKERS:
        return True
    if include_integrator and canonical == INTEGRATOR:
        return True
    return False


def worker_aliases(worker: str) -> tuple[str, ...]:
    canonical = canonical_worker_id(worker)
    values: list[str] = []
    if canonical:
        values.append(canonical)
    legacy = LEGACY_ALIAS_BY_CANONICAL.get(canonical, "")
    if legacy:
        values.append(legacy)
    if str(worker).strip() and str(worker).strip() not in values:
        values.append(str(worker).strip())
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return tuple(deduped)


def canonicalize_workers(
    workers: Iterable[str] | None,
    *,
    include_integrator: bool = False,
    include_post_run: bool = False,
    keep_unknown: bool = False,
) -> list[str]:
    ordered = [
        *PRE_INTEGRATION_WORKERS,
        *([INTEGRATOR] if include_integrator else []),
        *([*CANONICAL_POST_RUN_WORKERS] if include_post_run else []),
    ]
    allowed = set(ordered)

    if workers is None:
        return list(ordered)

    seen: set[str] = set()
    normalized: list[str] = []
    unknown: list[str] = []
    for item in workers:
        raw = str(item).strip()
        if not raw:
            continue
        canonical = canonical_worker_id(raw)
        if canonical in allowed:
            if canonical not in seen:
                seen.add(canonical)
                normalized.append(canonical)
            continue
        if keep_unknown and raw not in unknown:
            unknown.append(raw)

    if not normalized:
        normalized = [worker for worker in ordered if worker in allowed]
    normalized.sort(key=lambda value: ordered.index(value) if value in ordered else len(ordered))
    return [*normalized, *sorted(unknown)]


def bundle_path_candidates(run_id: str, worker: str) -> list[Path]:
    run_root = RUNS_DIR / str(run_id).strip()
    canonical = canonical_worker_id(worker)
    candidates: list[Path] = []
    for value in worker_aliases(canonical):
        if value:
            candidate = run_root / value
            if candidate not in candidates:
                candidates.append(candidate)
    return candidates


def resolve_bundle_dir(run_id: str, worker: str, *, prefer_existing: bool = True) -> Path:
    candidates = bundle_path_candidates(run_id, worker)
    if prefer_existing:
        for candidate in candidates:
            if candidate.exists():
                return candidate
    return candidates[0] if candidates else RUNS_DIR / str(run_id).strip() / canonical_worker_id(worker)


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

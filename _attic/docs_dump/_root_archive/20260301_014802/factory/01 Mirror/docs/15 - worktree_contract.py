from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .common import CODEX_DIR, REPO_ROOT

FIXED_WORKTREE_MODE = "fixed"
FACTORY_WORKTREE_MODE_ENV = "FACTORY_WORKTREE_MODE"
CONTRACT_PATH = REPO_ROOT / "tools" / "hos" / "factory" / "config.json"
RUN_ID_SEGMENT_RE = re.compile(r"^\d{8}(?:_\d+|_\d{6}_[A-Z0-9]{4})$")


def is_run_scoped_worktree_segment(value: str) -> bool:
    return bool(RUN_ID_SEGMENT_RE.fullmatch(str(value).strip()))


def fixed_worktrees_root() -> Path:
    return CODEX_DIR / "worktrees"


def fixed_worker_path(worker: str) -> Path:
    return fixed_worktrees_root() / str(worker).strip()


def _read_contract_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"missing unified worktree contract: {path.as_posix()}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"invalid unified worktree contract JSON: {path.as_posix()} :: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"unified worktree contract must be an object: {path.as_posix()}")
    return payload


def resolve_unified_worktree_mode(
    *,
    env: Mapping[str, str] | None = None,
    contract_path: Path | None = None,
) -> dict[str, Any]:
    path = contract_path or CONTRACT_PATH
    payload = _read_contract_payload(path)

    if "worktree_mode" not in payload:
        raise ValueError(f"missing required key 'worktree_mode' in {path.as_posix()}")

    contract_mode_raw = str(payload.get("worktree_mode", "")).strip().lower()
    if contract_mode_raw != FIXED_WORKTREE_MODE:
        raise ValueError(
            f"unsupported worktree_mode in contract: {contract_mode_raw!r} (expected '{FIXED_WORKTREE_MODE}')"
        )

    environment = dict(env or os.environ)
    env_override_raw = str(environment.get(FACTORY_WORKTREE_MODE_ENV, "")).strip()
    env_override = env_override_raw.lower() if env_override_raw else ""
    if env_override and env_override != FIXED_WORKTREE_MODE:
        raise ValueError(
            f"{FACTORY_WORKTREE_MODE_ENV} must be '{FIXED_WORKTREE_MODE}' when set (got {env_override_raw!r})"
        )

    return {
        "worktree_mode": FIXED_WORKTREE_MODE,
        "contract_mode": contract_mode_raw,
        "env_override": env_override if env_override else "",
        "contract_path": path.as_posix(),
    }

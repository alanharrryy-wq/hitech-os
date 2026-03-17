from __future__ import annotations

import datetime as dt
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .common import REPO_ROOT, UTC, compact_utc
from .ledger import query_run_ids


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    kind: str
    stamp: str
    base_ref: str
    base_ref_hash: str
    sequence: int


def _parse_timestamp(value: str | None) -> dt.datetime:
    if value:
        return dt.datetime.strptime(value, "%Y%m%d_%H%M%S").replace(tzinfo=UTC)
    return dt.datetime.now(UTC)


def _resolve_base_ref_hash(base_ref: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", base_ref],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        proc = None
    token_source = base_ref
    if proc is not None and proc.returncode == 0 and proc.stdout.strip():
        token_source = proc.stdout.strip()
    import hashlib

    return hashlib.sha256(token_source.encode("utf-8")).hexdigest()[:8]


def next_run_identity(
    kind: str,
    stamp: str | None = None,
    *,
    base_ref: str = "HEAD",
    ledger_path: Path | None = None,
) -> RunIdentity:
    dt_value = _parse_timestamp(stamp)
    compact = compact_utc(dt_value)
    base_ref_hash = _resolve_base_ref_hash(base_ref)
    prefix = f"{kind}_{compact}_{base_ref_hash}"

    current = query_run_ids(path=ledger_path)
    matching = [item for item in current if str(item).startswith(prefix)]
    sequence = 1
    if matching:
        last = sorted(matching)[-1]
        tail = last.rsplit("_", 1)[-1]
        if tail.isdigit():
            sequence = int(tail) + 1

    run_id = f"{prefix}_{sequence:03d}"
    return RunIdentity(
        run_id=run_id,
        kind=kind,
        stamp=compact,
        base_ref=base_ref,
        base_ref_hash=base_ref_hash,
        sequence=sequence,
    )

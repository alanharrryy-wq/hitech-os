"""JSONL-backed session ledger for one-button idempotency and reuse."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class LedgerEntry:
    session_id: str
    created_at_utc: str
    session_mode: str
    policy: str
    project_id: str
    run_id: str
    round_id: str
    idempotency_key: str
    status: str
    session_zip_path: str
    handoff_copy_path: Optional[str]
    lock_id: Optional[str]

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> 'LedgerEntry':
        return cls(
            session_id=str(payload.get('session_id', '')),
            created_at_utc=str(payload.get('created_at_utc', '')),
            session_mode=str(payload.get('session_mode', '')),
            policy=str(payload.get('policy', '')),
            project_id=str(payload.get('project_id', '')),
            run_id=str(payload.get('run_id', '')),
            round_id=str(payload.get('round_id', '')),
            idempotency_key=str(payload.get('idempotency_key', '')),
            status=str(payload.get('status', '')),
            session_zip_path=str(payload.get('session_zip_path', '')),
            handoff_copy_path=payload.get('handoff_copy_path'),
            lock_id=payload.get('lock_id'),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'created_at_utc': self.created_at_utc,
            'session_mode': self.session_mode,
            'policy': self.policy,
            'project_id': self.project_id,
            'run_id': self.run_id,
            'round_id': self.round_id,
            'idempotency_key': self.idempotency_key,
            'status': self.status,
            'session_zip_path': self.session_zip_path,
            'handoff_copy_path': self.handoff_copy_path,
            'lock_id': self.lock_id,
        }


class SessionLedger:
    def __init__(self, ledger_path: Path) -> None:
        self.ledger_path = ledger_path

    def read_entries(self) -> List[LedgerEntry]:
        if not self.ledger_path.exists():
            return []
        entries: List[LedgerEntry] = []
        with self.ledger_path.open('r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                entries.append(LedgerEntry.from_dict(json.loads(line)))
        return entries

    def append(self, entry: LedgerEntry) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')

    def find_reusable(self, idempotency_key: str) -> Optional[LedgerEntry]:
        reusable_statuses = {'ready_for_dispatch', 'reused'}
        for entry in reversed(self.read_entries()):
            if entry.idempotency_key != idempotency_key:
                continue
            if entry.status not in reusable_statuses:
                continue
            if entry.session_zip_path and Path(entry.session_zip_path).exists():
                return entry
        return None

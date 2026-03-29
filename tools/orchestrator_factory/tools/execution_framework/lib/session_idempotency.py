"""Idempotency helpers for one-button sessions."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from session_ledger import LedgerEntry, SessionLedger


@dataclass(frozen=True)
class IdempotencyContext:
    key: str
    decision: str
    reusable_entry: Optional[LedgerEntry]
    context_hashes: Dict[str, str]


class SessionIdempotencyManager:
    def __init__(self, ledger: SessionLedger, sentinel_none_value: str = 'none') -> None:
        self.ledger = ledger
        self.sentinel_none_value = sentinel_none_value

    def compute(
        self,
        *,
        session_mode: str,
        policy: str,
        project_id: str,
        normalized_intent: str,
        target_run_id: Optional[str],
        target_round_id: Optional[str],
        project_manifest_path: Path,
        run_manifest_path: Path,
        round_manifest_path: Path,
    ) -> IdempotencyContext:
        context_hashes = {
            'project_manifest_sha256': self._sha256_or_none(project_manifest_path),
            'run_manifest_sha256': self._sha256_or_none(run_manifest_path),
            'round_manifest_sha256': self._sha256_or_none(round_manifest_path),
        }
        key_material = [
            session_mode,
            policy,
            project_id,
            normalized_intent.strip(),
            target_run_id or self.sentinel_none_value,
            target_round_id or self.sentinel_none_value,
            context_hashes['project_manifest_sha256'],
            context_hashes['run_manifest_sha256'],
            context_hashes['round_manifest_sha256'],
        ]
        digest = hashlib.sha256('|'.join(key_material).encode('utf-8')).hexdigest()
        reusable_entry = self.ledger.find_reusable(digest)
        return IdempotencyContext(
            key=digest,
            decision='reused' if reusable_entry else 'new_session',
            reusable_entry=reusable_entry,
            context_hashes=context_hashes,
        )

    def _sha256_or_none(self, path: Path) -> str:
        if not path.exists():
            return self.sentinel_none_value
        digest = hashlib.sha256()
        with path.open('rb') as fh:
            while True:
                chunk = fh.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

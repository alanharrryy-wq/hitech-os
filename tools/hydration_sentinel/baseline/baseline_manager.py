from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ..engine.context import Finding


@dataclass(slots=True)
class Baseline:
    version: int
    fingerprints: frozenset[str]
    source_path: Path

    def contains(self, fingerprint: str) -> bool:
        return fingerprint in self.fingerprints


class BaselineManager:
    def __init__(self, path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / 'baseline.json'
        self.path = Path(path).resolve() if path else default_path

    def load(self) -> Baseline:
        if not self.path.exists():
            return Baseline(version=1, fingerprints=frozenset(), source_path=self.path)
        payload = json.loads(self.path.read_text(encoding='utf-8'))
        fps = frozenset(str(item) for item in payload.get('fingerprints', []))
        return Baseline(version=int(payload.get('version', 1)), fingerprints=fps, source_path=self.path)

    def save_from_findings(self, findings: Iterable[Finding], notes: str = '') -> Path:
        unique = sorted({finding.fingerprint for finding in findings})
        payload = {
            'version': 1,
            'fingerprints': unique,
            'notes': notes,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        return self.path

    def apply(self, findings: Iterable[Finding], baseline: Baseline) -> tuple[list[Finding], int]:
        active: list[Finding] = []
        ignored = 0
        for finding in findings:
            if baseline.contains(finding.fingerprint):
                ignored += 1
                active.append(finding.clone_with(ignored=True))
            else:
                active.append(finding)
        return active, ignored

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class VerifierResultRow:
    verifier_id: str
    ok: bool
    title: str
    detail: str
    source_plugin: str = 'capatch_verify'
    checked_at: str | None = None
    evidence_refs: list[str] | None = None
    metrics: dict[str, Any] | None = None
    severity_if_failed: str = 'error'
    verification_class: str = 'builtin'

    def to_dict(self) -> dict[str, Any]:
        return {
            'verifier_id': self.verifier_id,
            'ok': self.ok,
            'title': self.title,
            'detail': self.detail,
            'source_plugin': self.source_plugin,
            'checked_at': self.checked_at,
            'evidence_refs': list(self.evidence_refs or []),
            'metrics': dict(self.metrics or {}),
            'severity_if_failed': self.severity_if_failed,
            'verification_class': self.verification_class,
        }


def existing_target_files(target_files: list[str], ctx: dict[str, Any]) -> list[Path]:
    root_dir = Path(str((ctx or {}).get('root_dir') or '.')).resolve()
    resolved: list[Path] = []
    for item in list(target_files or []):
        path = Path(item)
        if not path.is_absolute():
            path = root_dir / path
        if path.exists() and path.is_file():
            resolved.append(path.resolve())
    return resolved

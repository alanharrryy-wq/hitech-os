from __future__ import annotations

import re

from ..engine.context import Finding
from ..rules_engine.registry import RuleContext

_STORAGE_RE = re.compile(r'(localStorage|sessionStorage)')
_STATE_INIT_RE = re.compile(r'useState\s*\(')
_HYDRATE_RE = re.compile(r'hydrat')


class StorageHydrationRule:
    rule_id = 'storage_hydration'
    description = 'Detect storage-backed hydration and state bootstrapping patterns.'

    def evaluate(self, context: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for relpath, file_facts in context.inventory_map.items():
            text = file_facts.text
            if not _STORAGE_RE.search(text):
                continue
            indicators = []
            if _STATE_INIT_RE.search(text):
                indicators.append('useState')
            if _HYDRATE_RE.search(text.lower()):
                indicators.append('hydrate')
            if file_facts.probable_serverish_path and not file_facts.has_use_client:
                indicators.append('serverish-storage')
            if not indicators:
                continue
            severity = 'medium' if file_facts.probable_tooling_path else 'high'
            for line_number, line in enumerate(file_facts.lines, start=1):
                lowered = line.lower()
                if 'localstorage' not in lowered and 'sessionstorage' not in lowered:
                    continue
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity=severity,
                        relpath=relpath,
                        line_number=line_number,
                        column_number=max(1, lowered.find('storage') + 1),
                        message='Storage-backed render or hydration state detected. Verify deterministic SSR fallback and post-mount hydration flow.',
                        snippet=line.strip()[:500],
                        excerpt=self._excerpt(file_facts.lines, line_number),
                        tags=('storage', 'hydration', 'state'),
                        details={'indicators': indicators, 'tooling_path': file_facts.probable_tooling_path},
                    ).ensure_fingerprint()
                )
        return findings

    @staticmethod
    def _excerpt(lines: list[str], line_number: int) -> str:
        start = max(1, line_number - 1)
        end = min(len(lines), line_number + 1)
        return '\n'.join(f"{'>' if current == line_number else ' '} {current:04d}: {lines[current - 1]}" for current in range(start, end + 1))

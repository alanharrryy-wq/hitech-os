from __future__ import annotations

from ..engine.context import Finding
from ..rules_engine.registry import RuleContext


TOKEN_MAP = {
    'window': ('window.', 'window['),
    'document': ('document.', 'document['),
    'navigator': ('navigator.',),
    'location': ('location.',),
    'history': ('history.',),
    'localStorage': ('localstorage',),
    'sessionStorage': ('sessionstorage',),
    'matchMedia': ('matchmedia',),
    'ResizeObserver': ('resizeobserver',),
    'MutationObserver': ('mutationobserver',),
}


class BrowserApiNonClientRule:
    rule_id = 'browser_api_non_client'
    description = 'Escalate browser API usage outside explicit client boundaries.'

    def evaluate(self, context: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for relpath, file_facts in context.inventory_map.items():
            if file_facts.has_use_client:
                continue
            for line_number, line in enumerate(file_facts.lines, start=1):
                lowered = line.lower()
                if 'typeof window' in lowered or 'typeof document' in lowered:
                    continue
                token = self._match_token(lowered)
                if not token:
                    continue
                severity = 'medium' if file_facts.probable_serverish_path else 'low'
                if any(marker in relpath.lower() for marker in ('/app/', '/layout.', '/page.', '/route.')):
                    severity = 'high' if token in {'localStorage', 'sessionStorage', 'document'} else severity
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity=severity,
                        relpath=relpath,
                        line_number=line_number,
                        column_number=max(1, lowered.find(token.lower()) + 1),
                        message=f'Browser API {token} is used outside an explicit client file.',
                        snippet=line.strip()[:500],
                        excerpt=self._excerpt(file_facts.lines, line_number),
                        tags=('browser-api', 'boundary', 'rule-engine'),
                        details={'token': token, 'serverish_path': file_facts.probable_serverish_path},
                    ).ensure_fingerprint()
                )
        return findings

    @staticmethod
    def _match_token(lowered: str) -> str | None:
        for token, signatures in TOKEN_MAP.items():
            if any(signature in lowered for signature in signatures):
                return token
        return None

    @staticmethod
    def _excerpt(lines: list[str], line_number: int) -> str:
        start = max(1, line_number - 1)
        end = min(len(lines), line_number + 1)
        return '\n'.join(f"{'>' if current == line_number else ' '} {current:04d}: {lines[current - 1]}" for current in range(start, end + 1))

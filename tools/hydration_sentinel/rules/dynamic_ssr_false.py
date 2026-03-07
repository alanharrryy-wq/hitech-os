from __future__ import annotations

from ..engine.context import Finding
from ..rules_engine.registry import RuleContext


class DynamicSSRFalseRule:
    rule_id = 'dynamic_ssr_false'
    description = 'Review dynamic import boundaries that disable SSR.'

    def evaluate(self, context: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for relpath, file_facts in context.inventory_map.items():
            for line_number, line in enumerate(file_facts.lines, start=1):
                lowered = line.lower().replace(' ', '')
                if 'ssr:false' not in lowered:
                    continue
                severity = 'medium' if file_facts.probable_tooling_path else 'high'
                message = 'dynamic(..., { ssr: false }) detected. Confirm this is a narrow client-only boundary.'
                if not file_facts.probable_tooling_path:
                    message = 'dynamic(..., { ssr: false }) appears outside tooling-only paths. Review scope carefully.'
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity=severity,
                        relpath=relpath,
                        line_number=line_number,
                        column_number=max(1, line.lower().find('ssr') + 1),
                        message=message,
                        snippet=line.strip()[:500],
                        excerpt=self._excerpt(file_facts.lines, line_number),
                        tags=('ssr', 'dynamic-import', 'boundary'),
                        details={'tooling_path': file_facts.probable_tooling_path},
                    ).ensure_fingerprint()
                )
        return findings

    @staticmethod
    def _excerpt(lines: list[str], line_number: int) -> str:
        start = max(1, line_number - 1)
        end = min(len(lines), line_number + 1)
        return '\n'.join(f"{'>' if current == line_number else ' '} {current:04d}: {lines[current - 1]}" for current in range(start, end + 1))

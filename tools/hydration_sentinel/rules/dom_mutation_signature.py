from __future__ import annotations

from ..engine.context import Finding
from ..rules_engine.registry import RuleContext


PATTERNS = {
    'innerHTML': 'innerHTML',
    'appendChild': 'appendChild(',
    'insertBefore': 'insertBefore(',
    'MutationObserver': 'MutationObserver',
    'createElement': 'document.createElement(',
}


class DomMutationSignatureRule:
    rule_id = 'dom_mutation_signature'
    description = 'Detect DOM mutation signatures that often correlate with hydration drift.'

    def evaluate(self, context: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for relpath, file_facts in context.inventory_map.items():
            for line_number, line in enumerate(file_facts.lines, start=1):
                for label, signature in PATTERNS.items():
                    if signature not in line:
                        continue
                    severity = 'medium' if file_facts.probable_tooling_path else 'high'
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity=severity,
                            relpath=relpath,
                            line_number=line_number,
                            column_number=max(1, line.find(signature) + 1),
                            message=f'DOM mutation signature detected via {label}. Validate pre-hydration mutation safety.',
                            snippet=line.strip()[:500],
                            excerpt=self._excerpt(file_facts.lines, line_number),
                            tags=('dom', 'mutation', 'hydration'),
                            details={'signature': signature, 'tooling_path': file_facts.probable_tooling_path},
                        ).ensure_fingerprint()
                    )
        return findings

    @staticmethod
    def _excerpt(lines: list[str], line_number: int) -> str:
        start = max(1, line_number - 1)
        end = min(len(lines), line_number + 1)
        return '\n'.join(f"{'>' if current == line_number else ' '} {current:04d}: {lines[current - 1]}" for current in range(start, end + 1))

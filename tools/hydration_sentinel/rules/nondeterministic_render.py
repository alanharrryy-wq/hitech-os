from __future__ import annotations

from ..engine.context import Finding
from ..rules_engine.registry import RuleContext


PATTERNS = {
    'Date.now': 'Date.now()',
    'new Date': 'new Date(',
    'Math.random': 'Math.random()',
    'randomUUID': 'randomUUID(',
}


class NondeterministicRenderRule:
    rule_id = 'nondeterministic_render'
    description = 'Detect unstable render-time values that can drift between server and client.'

    def evaluate(self, context: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for relpath, file_facts in context.inventory_map.items():
            if file_facts.probable_tooling_path:
                continue
            if not any(fragment in file_facts.text for fragment in ('<', 'return (', 'return <')):
                continue
            for line_number, line in enumerate(file_facts.lines, start=1):
                for label, signature in PATTERNS.items():
                    if signature not in line:
                        continue
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity='high',
                            relpath=relpath,
                            line_number=line_number,
                            column_number=max(1, line.find(signature) + 1),
                            message=f'Render-time nondeterminism detected via {label}. Prefer stable server data or post-mount calculation.',
                            snippet=line.strip()[:500],
                            excerpt=self._excerpt(file_facts.lines, line_number),
                            tags=('determinism', 'render', 'hydration'),
                            details={'signature': signature},
                        ).ensure_fingerprint()
                    )
        return findings

    @staticmethod
    def _excerpt(lines: list[str], line_number: int) -> str:
        start = max(1, line_number - 1)
        end = min(len(lines), line_number + 1)
        return '\n'.join(f"{'>' if current == line_number else ' '} {current:04d}: {lines[current - 1]}" for current in range(start, end + 1))

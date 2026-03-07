from __future__ import annotations

from ..engine.context import Finding
from ..rules_engine.registry import RuleContext


class ServerClientImportRule:
    rule_id = 'server_client_import'
    description = 'Identify serverish files importing explicit client modules.'

    def evaluate(self, context: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for relpath, file_facts in context.inventory_map.items():
            if file_facts.has_use_client:
                continue
            targets = context.client_index.imports_client(relpath)
            if not targets:
                continue
            severity = 'low' if file_facts.probable_tooling_path else 'medium'
            for target in targets[:20]:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity=severity,
                        relpath=relpath,
                        line_number=1,
                        column_number=1,
                        message=f'Serverish file imports explicit client module: {target}',
                        snippet=target,
                        excerpt=target,
                        tags=('boundary', 'imports', 'client'),
                        details={'target': target, 'tooling_path': file_facts.probable_tooling_path},
                    ).ensure_fingerprint()
                )
        return findings

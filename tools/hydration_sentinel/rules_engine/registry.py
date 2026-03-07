from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..engine.client_index import ClientBoundaryIndex
from ..engine.context import FileFacts, Finding, ScanOutput


@dataclass(slots=True)
class RuleContext:
    repo_root: Path
    scan_output: ScanOutput
    inventory_map: dict[str, FileFacts]
    client_index: ClientBoundaryIndex
    base_findings_by_path: dict[str, list[Finding]] = field(default_factory=dict)

    def findings_for_path(self, relpath: str) -> list[Finding]:
        return self.base_findings_by_path.get(relpath, [])


class Rule(Protocol):
    rule_id: str
    description: str

    def evaluate(self, context: RuleContext) -> list[Finding]:
        ...


class RuleRegistry:
    def default_rules(self) -> list[Rule]:
        from ..rules.browser_api_non_client import BrowserApiNonClientRule
        from ..rules.dom_mutation_signature import DomMutationSignatureRule
        from ..rules.dynamic_ssr_false import DynamicSSRFalseRule
        from ..rules.nondeterministic_render import NondeterministicRenderRule
        from ..rules.server_client_import import ServerClientImportRule
        from ..rules.storage_hydration import StorageHydrationRule
        from ..rules.suppress_hydration_warning import SuppressHydrationWarningRule

        return [
            BrowserApiNonClientRule(),
            DynamicSSRFalseRule(),
            SuppressHydrationWarningRule(),
            ServerClientImportRule(),
            StorageHydrationRule(),
            NondeterministicRenderRule(),
            DomMutationSignatureRule(),
        ]

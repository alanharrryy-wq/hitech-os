from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from ..baseline.baseline_manager import BaselineManager
from ..engine.client_index import ClientIndexBuilder
from ..engine.context import Finding, ScanOutput
from .registry import RuleContext, RuleRegistry


REPLACED_RAW_RULE_IDS = {
    'browser_api_in_non_client',
    'dynamic_ssr_false',
    'suppress_hydration_warning',
    'server_to_client_import_hint',
    'client_boundary_hint',
}


@dataclass(slots=True)
class RuleExecutionResult:
    scan_output: ScanOutput
    replaced_rule_ids: list[str]
    executed_rule_ids: list[str]


class RulesExecutor:
    def __init__(self, repo_root: str | Path, *, baseline_path: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.baseline_manager = BaselineManager(baseline_path)
        self.registry = RuleRegistry()

    def execute(self, scan_output: ScanOutput) -> RuleExecutionResult:
        inventory_map = {facts.relpath: facts for facts in scan_output.inventory}
        client_index = ClientIndexBuilder(str(self.repo_root)).build(scan_output.inventory)
        base_findings_by_path: dict[str, list[Finding]] = defaultdict(list)
        for finding in scan_output.findings:
            base_findings_by_path[finding.relpath].append(finding)

        context = RuleContext(
            repo_root=self.repo_root,
            scan_output=scan_output,
            inventory_map=inventory_map,
            client_index=client_index,
            base_findings_by_path=dict(base_findings_by_path),
        )

        enhanced: list[Finding] = []
        executed_rule_ids: list[str] = []
        for rule in self.registry.default_rules():
            executed_rule_ids.append(rule.rule_id)
            enhanced.extend(rule.evaluate(context))

        baseline = self.baseline_manager.load()
        enhanced, ignored_count = self.baseline_manager.apply(enhanced, baseline)

        kept_base = [finding for finding in scan_output.findings if finding.rule_id not in REPLACED_RAW_RULE_IDS]
        merged = self._dedupe_findings([*kept_base, *enhanced])
        scan_output.findings = merged
        scan_output.stats.findings_total = len(merged)
        scan_output.stats.baseline_ignored = sum(1 for item in merged if item.ignored)
        scan_output.stats.findings_active = sum(1 for item in merged if not item.ignored)
        scan_output.meta['rule_engine'] = {
            'executed_rules': executed_rule_ids,
            'replaced_raw_rule_ids': sorted(REPLACED_RAW_RULE_IDS),
            'enhanced_findings': len(enhanced),
            'enhanced_ignored_by_baseline': ignored_count,
        }
        return RuleExecutionResult(
            scan_output=scan_output,
            replaced_rule_ids=sorted(REPLACED_RAW_RULE_IDS),
            executed_rule_ids=executed_rule_ids,
        )

    @staticmethod
    def _dedupe_findings(findings: list[Finding]) -> list[Finding]:
        seen: set[str] = set()
        unique: list[Finding] = []
        for finding in findings:
            finding.ensure_fingerprint()
            if finding.fingerprint in seen:
                continue
            seen.add(finding.fingerprint)
            unique.append(finding)
        return sorted(unique, key=lambda item: (item.relpath, item.line_number, item.rule_id, item.fingerprint))

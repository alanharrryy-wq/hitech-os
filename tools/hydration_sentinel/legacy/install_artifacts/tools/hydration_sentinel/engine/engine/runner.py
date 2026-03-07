from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

from ..baseline.baseline_manager import BaselineManager
from ..config.config_loader import load_config
from ..diff.git_diff_scanner import GitDiffScanner
from .client_index import ClientIndexBuilder
from .context import FileFacts, Finding, ScanOutput, ScanStats
from .scanner import RepoScanner


class ScanRunner:
    def __init__(
        self,
        repo_root: str | Path,
        *,
        config_path: str | Path | None = None,
        baseline_path: str | Path | None = None,
        force_diff_enabled: bool | None = None,
        force_diff_base_ref: str | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        config_result = load_config(config_path)
        self.config = config_result.config
        if force_diff_enabled is not None:
            self.config = replace(self.config, diff_enabled=force_diff_enabled)
        if force_diff_base_ref is not None:
            self.config = replace(self.config, diff_base_ref=force_diff_base_ref)
        self.config_source = config_result.source_path
        self.baseline_manager = BaselineManager(baseline_path)
        self.scanner = RepoScanner(self.repo_root, self.config)

    def run(self) -> ScanOutput:
        baseline = self.baseline_manager.load()
        diff_selection = GitDiffScanner(self.repo_root).build_selection(
            enabled=self.config.diff_enabled,
            base_ref=self.config.diff_base_ref,
            include_untracked=self.config.diff_include_untracked,
            staged_only=self.config.diff_staged_only,
        )

        discovered_paths = self.scanner.discover_files()
        inventory: list[FileFacts] = []
        stats = ScanStats(files_discovered=len(discovered_paths))
        for abs_path in discovered_paths:
            relpath = str(abs_path.relative_to(self.repo_root)).replace('\\', '/')
            if not diff_selection.allows(relpath):
                stats.files_skipped += 1
                continue
            file_facts = self.scanner.build_file_facts(abs_path)
            if file_facts is None:
                stats.files_skipped += 1
                continue
            inventory.append(file_facts)
            stats.files_scanned += 1

        client_index = ClientIndexBuilder(str(self.repo_root)).build(inventory)
        findings: list[Finding] = []
        for file_facts in inventory:
            findings.extend(self.scanner.scan_file(file_facts, client_index))

        findings, ignored_count = self.baseline_manager.apply(findings, baseline)
        stats.findings_total = len(findings)
        stats.baseline_ignored = ignored_count
        stats.findings_active = sum(1 for finding in findings if not finding.ignored)

        meta = {
            'config_path': str(self.config_source),
            'baseline_exists': baseline.source_path.exists(),
            'client_file_count': len(client_index.client_files),
            'serverish_file_count': len(client_index.serverish_files),
            'top_import_hubs': self._top_import_hubs(client_index.reverse_import_graph),
            'inventory_extensions': dict(Counter(f.extension for f in inventory)),
        }

        return ScanOutput(
            repo_root=str(self.repo_root),
            config_version=self.config.version,
            baseline_path=str(baseline.source_path),
            diff_mode={
                'enabled': diff_selection.enabled,
                'git_available': diff_selection.git_available,
                'base_ref': diff_selection.base_ref,
                'mode': diff_selection.mode,
                'changed_files': len(diff_selection.changed_files),
                'untracked_files': len(diff_selection.untracked_files),
                'error': diff_selection.error,
            },
            stats=stats,
            findings=findings,
            inventory=inventory,
            meta=meta,
        )

    def write_baseline(self, findings: list[Finding], notes: str = '') -> Path:
        return self.baseline_manager.save_from_findings(findings, notes=notes)

    @staticmethod
    def _top_import_hubs(reverse_graph: dict[str, list[str]], limit: int = 10) -> list[dict[str, Any]]:
        ranked = sorted(reverse_graph.items(), key=lambda item: (-len(item[1]), item[0]))[:limit]
        return [{'relpath': path, 'imported_by': len(referrers)} for path, referrers in ranked]

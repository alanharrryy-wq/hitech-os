from __future__ import annotations

import json
from pathlib import Path

from tools.hydration_sentinel.cli.sentinel_cli import main
from tools.hydration_sentinel.reporting.report_builder import ReportBuilder


SAMPLE_CONFIG = {
    'exclude_dir_names': ['.git', '.next', 'dist', 'node_modules'],
    'exclude_path_substrings': [],
    'finding_limit_per_rule_per_file': 50,
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + '\n', encoding='utf-8')


def seed_repo(repo: Path) -> None:
    write(repo / 'package.json', '{"name":"sample"}')
    write(
        repo / 'apps/web/app/page.tsx',
        """
        import { Shell } from '../shared/Shell'
        export default function Page() {
            return <Shell />
        }
        """,
    )
    write(
        repo / 'apps/web/shared/Shell.tsx',
        """
        import { ClientPanel } from '../components/ClientPanel'
        export function Shell() {
            return <ClientPanel />
        }
        """,
    )
    write(
        repo / 'apps/web/components/ClientPanel.tsx',
        """
        'use client'
        export function ClientPanel() {
            const seed = localStorage.getItem('seed')
            const unstable = Math.random()
            document.body.appendChild(document.createElement('div'))
            return <div suppressHydrationWarning>{seed}:{unstable}</div>
        }
        """,
    )


def test_graph_history_smoke(tmp_path: Path) -> None:
    repo = tmp_path / 'repo'
    seed_repo(repo)
    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(SAMPLE_CONFIG), encoding='utf-8')

    report_root = tmp_path / 'reports'
    builder = ReportBuilder(repo, config_path=config_path, report_root=report_root)
    first = builder.build()
    first_written = builder.write_latest(first)

    assert first.graph_payload['node_count'] >= 3
    assert first.graph_payload['path_counts']['storage_api'] >= 1
    assert first.graph_payload['path_counts']['nondeterministic'] >= 1
    assert first.graph_payload['trend']['has_previous'] is False
    assert first_written['graph_summary'].exists()
    assert first_written['history_snapshot'].exists()

    write(
        repo / 'apps/web/components/ClientPanel.tsx',
        """
        'use client'
        export function ClientPanel() {
            const seed = localStorage.getItem('seed')
            return <div suppressHydrationWarning>{seed}</div>
        }
        """,
    )

    second = builder.build()
    second_written = builder.write_latest(second)
    assert second.graph_payload['trend']['has_previous'] is True
    assert second.graph_payload['trend']['resolved_findings'] >= 1
    assert second_written['trend_summary'].exists()


def test_cli_build_report(tmp_path: Path) -> None:
    repo = tmp_path / 'repo'
    seed_repo(repo)
    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(SAMPLE_CONFIG), encoding='utf-8')
    report_root = tmp_path / 'reports'

    exit_code = main([
        '--repo-root', str(repo),
        '--config', str(config_path),
        '--build-report',
        '--write-report',
        '--report-root', str(report_root),
    ])
    assert exit_code == 0
    assert (report_root / 'latest' / 'report.md').exists()
    assert (report_root / 'latest' / 'graph_summary.json').exists()
    assert (report_root / 'latest' / 'history_snapshot.json').exists()

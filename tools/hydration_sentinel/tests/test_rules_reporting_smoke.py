from __future__ import annotations

import json
from pathlib import Path

from tools.hydration_sentinel.reporting.report_builder import ReportBuilder


SAMPLE_CONFIG = {
    'exclude_dir_names': ['.git', '.next', 'dist', 'node_modules'],
    'exclude_path_substrings': [],
    'finding_limit_per_rule_per_file': 50,
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + '\n', encoding='utf-8')


def test_rules_reporting_smoke(tmp_path: Path) -> None:
    repo = tmp_path / 'repo'
    write(repo / 'package.json', '{"name":"sample"}')
    write(
        repo / 'apps/web/app/page.tsx',
        '''
        import { ClientThing } from '../components/ClientThing'
        export default function Page() {
            const now = Date.now()
            const fromStorage = localStorage.getItem('foo')
            return <ClientThing value={`${now}:${fromStorage}`} />
        }
        ''',
    )
    write(
        repo / 'apps/web/components/ClientThing.tsx',
        '''
        'use client'
        export function ClientThing(props: { value: string | null }) {
            return <div suppressHydrationWarning>{props.value}</div>
        }
        ''',
    )
    write(
        repo / 'apps/web/app/dev/panel.tsx',
        '''
        import dynamic from 'next/dynamic'
        const DebugPanel = dynamic(() => import('../components/ClientThing'), { ssr: false })
        export default function Panel() {
            document.body.appendChild(document.createElement('div'))
            return <DebugPanel />
        }
        ''',
    )

    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(SAMPLE_CONFIG), encoding='utf-8')

    report_builder = ReportBuilder(repo, config_path=config_path)
    built = report_builder.build()
    written = report_builder.write_latest(built)

    findings = built.findings_payload['findings']
    categories = {item['rule_id'] for item in findings if not item.get('ignored', False)}

    assert 'storage_hydration' in categories
    assert 'nondeterministic_render' in categories
    assert 'dom_mutation_signature' in categories
    assert 'dynamic_ssr_false' in categories
    assert 'suppress_hydration_warning' in categories
    assert built.summary_payload['risk']['total_score'] > 0
    assert written['report'].exists()
    assert written['findings'].exists()

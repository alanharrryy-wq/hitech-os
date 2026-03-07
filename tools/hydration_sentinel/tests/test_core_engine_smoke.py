from __future__ import annotations

import json
from pathlib import Path

from tools.hydration_sentinel.engine.runner import ScanRunner


SAMPLE_CONFIG = {
    'exclude_dir_names': ['.git', '.next', 'dist', 'node_modules'],
    'exclude_path_substrings': ['/snapshots/'],
    'finding_limit_per_rule_per_file': 50,
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + '\n', encoding='utf-8')


def test_core_engine_smoke(tmp_path: Path) -> None:
    repo = tmp_path / 'repo'
    write(repo / 'package.json', '{"name":"sample"}')
    write(
        repo / 'apps/web/app/page.tsx',
        """
        import { ClientThing } from '../components/ClientThing'
        export default function Page() {
            const fromStorage = localStorage.getItem('foo')
            return <ClientThing value={fromStorage} />
        }
        """,
    )
    write(
        repo / 'apps/web/components/ClientThing.tsx',
        """
        'use client'
        export function ClientThing(props: { value: string | null }) {
            return <div suppressHydrationWarning>{props.value}</div>
        }
        """,
    )
    write(
        repo / 'apps/web/app/dev/panel.tsx',
        """
        import dynamic from 'next/dynamic'
        const DebugPanel = dynamic(() => import('../components/ClientThing'), { ssr: false })
        export default function Panel() { return <DebugPanel /> }
        """,
    )
    write(repo / 'apps/web/.next/chunks/compiled.js', 'suppressHydrationWarning localStorage hydrate')

    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(SAMPLE_CONFIG), encoding='utf-8')

    output = ScanRunner(repo, config_path=config_path).run()
    active = [finding for finding in output.findings if not finding.ignored]
    categories = {finding.rule_id for finding in active}

    assert output.stats.files_scanned == 3
    assert 'browser_api_in_non_client' in categories
    assert 'suppress_hydration_warning' in categories
    assert 'dynamic_ssr_false' in categories
    assert 'client_boundary_hint' in categories
    assert 'server_to_client_import_hint' in categories

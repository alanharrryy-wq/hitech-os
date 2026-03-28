
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'tools/execution_framework'))

from lib.readiness import build_readiness_report


class ReadinessTests(unittest.TestCase):
    def test_install_readiness_passes_with_clean_minimal_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            for rel in [
                '00-governance-core/docs/control',
                '00-governance-core/docs/contracts',
                '01-identity-access-and-trust',
                '02-domain-data-and-persistence',
                '03-service-contracts-and-orchestration',
                '04-experience-clients-and-interactions',
                '05-platform-infrastructure-and-delivery',
                '06-quality-release-and-operations',
                'configs/execution_framework',
                'docs/parallel_execution',
                'prompts/execution_framework',
                'schemas/execution_framework',
                'tools/execution_framework',
                'tests/execution_framework',
                'templates/execution_framework',
                'ops/projects',
                'ops/runs',
            ]:
                (repo / rel).mkdir(parents=True, exist_ok=True)
            (repo / 'README.md').write_text('x', encoding='utf-8')
            (repo / 'OPERATOR_ONE_PAGE_FLOW.md').write_text('x', encoding='utf-8')
            (repo / 'STARTER_INDEX.md').write_text('x', encoding='utf-8')
            (repo / 'MASTER_INDEX.md').write_text('x', encoding='utf-8')
            (repo / 'parallel_manifest.json').write_text('{}', encoding='utf-8')
            (repo / 'parallel_launch_order.md').write_text('x', encoding='utf-8')
            (repo / 'master_chat_routing.md').write_text('x', encoding='utf-8')
            (repo / 'universal_execution_starter_kit_v1.zip').write_text('zip', encoding='utf-8')
            (repo / '00-governance-core/docs/control/framework_readiness_gates.md').write_text('x', encoding='utf-8')
            (repo / '00-governance-core/docs/control/inter_chat_communication_policy.md').write_text('x', encoding='utf-8')
            (repo / '00-governance-core/docs/control/waiver_and_exception_policy.md').write_text('x', encoding='utf-8')
            (repo / '00-governance-core/docs/contracts/contract_versioning_policy.md').write_text('x', encoding='utf-8')
            (repo / 'docs/parallel_execution/21_one_page_operator_flow.md').write_text('x', encoding='utf-8')
            (repo / 'docs/parallel_execution/22_install_bootstrap_run_boundaries.md').write_text('x', encoding='utf-8')
            (repo / 'docs/parallel_execution/23_inter_chat_communication_policy.md').write_text('x', encoding='utf-8')
            (repo / 'docs/parallel_execution/24_exception_and_waiver_policy.md').write_text('x', encoding='utf-8')
            (repo / 'docs/parallel_execution/25_contract_versioning_policy.md').write_text('x', encoding='utf-8')
            (repo / 'docs/parallel_execution/26_go_live_readiness_gates.md').write_text('x', encoding='utf-8')
            (repo / 'schemas/execution_framework/waiver_request.schema.json').write_text(json.dumps({'name': 'waiver_request', 'required_fields': {}}), encoding='utf-8')
            (repo / 'templates/execution_framework/run').mkdir(parents=True, exist_ok=True)
            (repo / 'templates/execution_framework/run/waiver_request.template.json').write_text(json.dumps({'schema_version': '1.0'}), encoding='utf-8')
            (repo / 'configs/execution_framework/system_config.json').write_text(json.dumps({
                'projects_root': 'ops/projects',
                'tree_hygiene_config': 'configs/execution_framework/canonical_tree_excludes.json',
                'runs_root': 'ops/runs',
                'rounds_dir_name': 'rounds',
                'decisions_dir_name': 'decisions',
                'incoming_dir_name': 'incoming',
                'reports_dir_name': 'reports',
                'packets_dir_name': 'packets',
                'prompts_dir_name': 'prompts',
                'active_package_ids': []
            }), encoding='utf-8')
            (repo / 'configs/execution_framework/repo_target_layout.json').write_text(json.dumps({'required_directories': [
                '00-governance-core', '01-identity-access-and-trust', '02-domain-data-and-persistence', '03-service-contracts-and-orchestration', '04-experience-clients-and-interactions', '05-platform-infrastructure-and-delivery', '06-quality-release-and-operations', 'configs/execution_framework', 'docs/parallel_execution', 'prompts/execution_framework', 'schemas/execution_framework', 'tools/execution_framework', 'tests/execution_framework', 'templates/execution_framework', 'ops/projects', 'ops/runs'
            ]}), encoding='utf-8')
            (repo / 'configs/execution_framework/path_policies.json').write_text('{}', encoding='utf-8')
            (repo / 'configs/execution_framework/canonical_tree_excludes.json').write_text(json.dumps({'excluded_paths': ['**/__pycache__/**', '**/*.pyc'], 'excluded_names': ['__pycache__']}), encoding='utf-8')
            report = build_readiness_report(repo)
            self.assertEqual(report['stages']['install']['status'], 'ready')


if __name__ == '__main__':
    unittest.main()

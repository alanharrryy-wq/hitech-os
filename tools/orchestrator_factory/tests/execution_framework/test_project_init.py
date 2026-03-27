
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'tools/execution_framework'))

from lib.projects import initialize_project_baseline


class ProjectInitTests(unittest.TestCase):
    def test_initialize_project_baseline_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / 'configs/execution_framework').mkdir(parents=True, exist_ok=True)
            (repo / 'ops/projects').mkdir(parents=True, exist_ok=True)
            (repo / 'configs/execution_framework/system_config.json').write_text(json.dumps({
                'projects_root': 'ops/projects',
                'active_package_ids': ['01-a', '02-b']
            }), encoding='utf-8')
            result = initialize_project_baseline('prj-demo', 'Demo', 'greenfield', 'Ship one thing', repo)
            project_root = repo / 'ops/projects/prj-demo'
            self.assertTrue((project_root / 'project_manifest.json').exists())
            self.assertTrue((project_root / 'idea_intake.md').exists())
            self.assertTrue((project_root / 'homologation_record.md').exists())
            self.assertEqual(result['project_id'], 'prj-demo')


if __name__ == '__main__':
    unittest.main()

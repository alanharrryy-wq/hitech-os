from __future__ import annotations

import json
from pathlib import Path

from ..engine.context import ScanOutput


class RegressionDetector:
    def compare_with_previous(self, output: ScanOutput, report_root: str | Path) -> dict:
        report_root = Path(report_root)
        latest_findings = report_root / 'latest' / 'findings.json'
        current_fps = {finding.fingerprint for finding in output.findings if not finding.ignored}
        if not latest_findings.exists():
            return {
                'has_previous': False,
                'new_findings': len(current_fps),
                'resolved_findings': 0,
                'unchanged_findings': 0,
            }
        payload = json.loads(latest_findings.read_text(encoding='utf-8'))
        previous_fps = {
            str(item.get('fingerprint'))
            for item in payload.get('findings', [])
            if not item.get('ignored', False)
        }
        return {
            'has_previous': True,
            'new_findings': len(current_fps - previous_fps),
            'resolved_findings': len(previous_fps - current_fps),
            'unchanged_findings': len(current_fps & previous_fps),
        }

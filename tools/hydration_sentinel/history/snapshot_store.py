from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..engine.context import ScanOutput
from ..react_graph.models import GraphSummary


class SnapshotStore:
    def __init__(self, report_root: str | Path) -> None:
        self.report_root = Path(report_root)

    def build_snapshot(self, output: ScanOutput, graph_summary: GraphSummary) -> dict:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        active = [finding for finding in output.findings if not finding.ignored]
        return {
            'created_at': timestamp,
            'repo_root': output.repo_root,
            'config_version': output.config_version,
            'stats': output.to_summary()['stats'],
            'findings_by_rule': output.findings_by_rule(),
            'findings_by_severity': output.findings_by_severity(),
            'active_fingerprints': sorted(finding.fingerprint for finding in active),
            'graph_summary': graph_summary.to_dict(),
        }

    def read_latest_snapshot(self) -> dict | None:
        latest = self.report_root / 'latest' / 'history_snapshot.json'
        if not latest.exists():
            return None
        return json.loads(latest.read_text(encoding='utf-8'))

    def write(self, snapshot: dict) -> dict[str, Path]:
        latest_dir = self.report_root / 'latest'
        history_dir = self.report_root / 'history'
        latest_dir.mkdir(parents=True, exist_ok=True)
        history_dir.mkdir(parents=True, exist_ok=True)
        stamp = snapshot['created_at'].replace(':', '').replace('-', '')
        dated = history_dir / f'{stamp}.json'
        latest = latest_dir / 'history_snapshot.json'
        payload = json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n'
        dated.write_text(payload, encoding='utf-8')
        latest.write_text(payload, encoding='utf-8')
        return {'dated': dated, 'latest': latest}

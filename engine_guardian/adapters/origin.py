from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from ..health import probe_url
from ..paths import GuardianPaths
from ..policy import GuardianPolicy
from ..state_store import StateStore, utc_now_iso


class OriginAdapter:
    def __init__(self, paths: GuardianPaths, policy: GuardianPolicy, state_store: StateStore) -> None:
        self.paths = paths
        self.policy = policy
        self.state_store = state_store

    def _python(self) -> str:
        tools = self.state_store.read_json(self.state_store.resolved_tools_path, {})
        return tools.get('python', {}).get('path') or sys.executable

    def _run(self, cmd: List[str], timeout: int) -> Dict[str, Any]:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            'command': cmd,
            'returncode': completed.returncode,
            'stdout_tail': completed.stdout[-4000:],
            'stderr_tail': completed.stderr[-4000:],
        }

    def _invoke_repair(self) -> Dict[str, Any]:
        script = self.paths.ensure_origin_script
        if not script.exists():
            return {
                'attempted': False,
                'applied': False,
                'reason': 'ensure_origin.py is unavailable',
                'script_path': str(script),
            }
        cmd = [self._python(), str(script), '--apply']
        try:
            result = self._run(cmd, timeout=self.policy.repair_script_timeout_seconds)
        except Exception as exc:
            result = {
                'command': cmd,
                'returncode': 1,
                'stdout_tail': '',
                'stderr_tail': str(exc),
            }
        result['attempted'] = True
        result['applied'] = result.get('returncode') == 0
        return result

    def ensure(self, repair: bool = False) -> Dict[str, Any]:
        probe = probe_url(self.paths.origin_url, self.policy.origin_probe_timeout_seconds)
        result: Dict[str, Any] = {
            'component': 'origin',
            'timestamp_utc': utc_now_iso(),
            'url': self.paths.origin_url,
            'healthy': bool(probe.get('healthy')),
            'status_code': probe.get('status_code'),
            'probe': probe,
            'repair': None,
        }
        if repair and not result['healthy']:
            result['repair'] = self._invoke_repair()
            result['probe_after_repair'] = probe_url(self.paths.origin_url, self.policy.origin_probe_timeout_seconds)
            result['healthy'] = bool(result['probe_after_repair'].get('healthy'))
            result['status_code'] = result['probe_after_repair'].get('status_code')
        self.state_store.write_json(self.paths.reports_dir / 'origin_status_latest.json', result)
        return result

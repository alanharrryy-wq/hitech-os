from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from ..paths import GuardianPaths
from ..policy import GuardianPolicy
from ..state_store import StateStore, utc_now_iso


class RepoAnalyzerAdapter:
    def __init__(self, paths: GuardianPaths, policy: GuardianPolicy, state_store: StateStore) -> None:
        self.paths = paths
        self.policy = policy
        self.state_store = state_store

    def _python(self) -> str:
        tools = self.state_store.read_json(self.state_store.resolved_tools_path, {})
        return tools.get('python', {}).get('path') or sys.executable

    def _run(self, cmd: List[str], timeout: int) -> Dict[str, Any]:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(self.paths.repo_analyzer_dir))
        return {
            'command': cmd,
            'returncode': completed.returncode,
            'stdout_tail': completed.stdout[-4000:],
            'stderr_tail': completed.stderr[-4000:],
        }

    def validate(self) -> Dict[str, Any]:
        checks = {
            'repo_analyzer_dir_exists': self.paths.repo_analyzer_dir.exists(),
            'main_exists': self.paths.repo_analyzer_main.exists(),
            'self_test_exists': self.paths.repo_analyzer_self_test.exists(),
        }
        validation: Dict[str, Any]
        if self.paths.repo_analyzer_self_test.exists():
            cmd = [self._python(), str(self.paths.repo_analyzer_self_test)]
            validation = self._run(cmd, timeout=self.policy.repo_analyzer_self_test_timeout_seconds)
        elif self.paths.repo_analyzer_main.exists():
            cmd = [self._python(), str(self.paths.repo_analyzer_main), '--help']
            validation = self._run(cmd, timeout=self.policy.repo_analyzer_cli_timeout_seconds)
        else:
            validation = {
                'command': [],
                'returncode': 1,
                'stdout_tail': '',
                'stderr_tail': 'Repo Analyzer entrypoints are missing.',
            }
        healthy = all(checks.values()) and validation.get('returncode') == 0
        payload = {
            'status': 'healthy' if healthy else 'degraded',
            'healthy': healthy,
            'checks': checks,
            'validation': validation,
            'timestamp_utc': utc_now_iso(),
        }
        self.state_store.write_json(self.state_store.repo_analyzer_status_path, payload)
        self.state_store.append_log_line(self.state_store.repo_analyzer_log_path, f"repo_analyzer validate healthy={healthy}")
        return payload

    def ensure(self, repair: bool = False) -> Dict[str, Any]:
        payload = self.validate()
        payload['mode'] = 'heal' if repair else 'validate'
        self.state_store.write_json(self.state_store.repo_analyzer_status_path, payload)
        return payload

    def status(self) -> Dict[str, Any]:
        payload = self.state_store.read_json(self.state_store.repo_analyzer_status_path, {})
        if payload:
            return payload
        return self.validate()

    def open(self) -> Dict[str, Any]:
        if not self.paths.repo_analyzer_main.exists():
            payload = {
                'status': 'missing',
                'healthy': False,
                'timestamp_utc': utc_now_iso(),
                'error': f'Missing {self.paths.repo_analyzer_main}',
            }
            self.state_store.write_json(self.state_store.repo_analyzer_status_path, payload)
            return payload
        cmd = [self._python(), str(self.paths.repo_analyzer_main)]
        try:
            process = subprocess.Popen(cmd, cwd=str(self.paths.repo_analyzer_dir))
            payload = {
                'status': 'launched',
                'healthy': True,
                'timestamp_utc': utc_now_iso(),
                'pid': process.pid,
                'command': cmd,
            }
        except Exception as exc:
            payload = {
                'status': 'launch_failed',
                'healthy': False,
                'timestamp_utc': utc_now_iso(),
                'error': str(exc),
                'command': cmd,
            }
        self.state_store.write_json(self.state_store.repo_analyzer_status_path, payload)
        self.state_store.append_log_line(self.state_store.repo_analyzer_log_path, f"repo_analyzer open status={payload.get('status')}")
        return payload

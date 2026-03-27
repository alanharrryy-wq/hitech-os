from __future__ import annotations

import json
import platform
import subprocess
import sys
from typing import Any, Dict, List

from ..health import probe_url
from ..paths import GuardianPaths
from ..policy import GuardianPolicy
from ..state_store import StateStore, utc_now_iso


class CloudflareAdapter:
    def __init__(self, paths: GuardianPaths, policy: GuardianPolicy, state_store: StateStore) -> None:
        self.paths = paths
        self.policy = policy
        self.state_store = state_store

    def _resolved_tools(self) -> Dict[str, Any]:
        return self.state_store.read_json(self.state_store.resolved_tools_path, {})

    def _python(self) -> str:
        return self._resolved_tools().get('python', {}).get('path') or sys.executable

    def _powershell(self) -> str | None:
        tools = self._resolved_tools()
        return tools.get('pwsh', {}).get('path') or tools.get('powershell', {}).get('path')

    def _cloudflared(self) -> str | None:
        return self._resolved_tools().get('cloudflared', {}).get('path')

    def _run(self, cmd: List[str], timeout: int) -> Dict[str, Any]:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            'command': cmd,
            'returncode': completed.returncode,
            'stdout_tail': completed.stdout[-4000:],
            'stderr_tail': completed.stderr[-4000:],
        }

    def _extract_json(self, text: str) -> Dict[str, Any] | None:
        text = text.strip()
        if not text:
            return None
        candidates = [text]
        if '\n' in text:
            candidates.append(text.splitlines()[-1])
        for candidate in candidates:
            try:
                payload = json.loads(candidate)
                if isinstance(payload, dict):
                    return payload
            except Exception:
                continue
        return None

    def _service_status(self) -> Dict[str, Any]:
        shell = self._powershell()
        base = {
            'component': 'cloudflared_service',
            'timestamp_utc': utc_now_iso(),
            'healthy': False,
            'installed': False,
            'running': False,
            'repair': None,
        }
        if platform.system() != 'Windows' or not shell:
            base['mode'] = 'preview_only'
            base['healthy'] = self.paths.cloudflared_config_path.exists()
            return base
        cmd = [
            shell,
            '-NoProfile',
            '-Command',
            (
                "$svc = Get-CimInstance Win32_Service -Filter \"Name='cloudflared'\" -ErrorAction SilentlyContinue; "
                "if ($null -eq $svc) { exit 1 }; $svc | ConvertTo-Json -Depth 5"
            ),
        ]
        try:
            result = self._run(cmd, timeout=30)
        except Exception as exc:
            base['error'] = str(exc)
            return base
        base['query'] = result
        if result.get('returncode') == 0:
            payload = self._extract_json(result.get('stdout_tail', '')) or {}
            state = str(payload.get('State') or payload.get('Status') or '')
            base.update(
                {
                    'installed': True,
                    'running': state.lower() == 'running',
                    'state': state,
                    'service_name': payload.get('Name') or 'cloudflared',
                    'path_name': payload.get('PathName'),
                }
            )
            base['healthy'] = base['running']
        return base

    def _repair_service(self) -> Dict[str, Any]:
        script = self.paths.ensure_service_script
        if not script.exists():
            return {
                'attempted': False,
                'applied': False,
                'reason': 'ensure_service.py is unavailable',
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

    def _validate_tunnel_via_script(self) -> Dict[str, Any]:
        script = self.paths.validate_tunnel_script
        if not script.exists():
            return {
                'component': 'tunnel',
                'timestamp_utc': utc_now_iso(),
                'healthy': False,
                'mode': 'missing_script',
                'script_path': str(script),
            }
        cmd = [self._python(), str(script)]
        try:
            result = self._run(cmd, timeout=self.policy.tunnel_validation_timeout_seconds)
        except Exception as exc:
            return {
                'component': 'tunnel',
                'timestamp_utc': utc_now_iso(),
                'healthy': False,
                'mode': 'script_error',
                'error': str(exc),
            }
        payload = self._extract_json(result.get('stdout_tail', '')) or {}
        healthy = bool(
            payload.get('healthy')
            or payload.get('public_edge_reachable')
            or (
                payload.get('tunnel_connected')
                and payload.get('hostname_bound')
                and payload.get('ingress_ok')
            )
        )
        return {
            'component': 'tunnel',
            'timestamp_utc': utc_now_iso(),
            'healthy': healthy,
            'mode': 'validate_tunnel_script',
            'details': payload,
            'command_result': result,
        }

    def _validate_tunnel_via_cli(self) -> Dict[str, Any]:
        cloudflared = self._cloudflared()
        if not cloudflared:
            return {
                'component': 'tunnel',
                'timestamp_utc': utc_now_iso(),
                'healthy': False,
                'mode': 'missing_cloudflared',
            }
        cmd = [cloudflared, 'tunnel', 'info', 'engine']
        try:
            result = self._run(cmd, timeout=self.policy.tunnel_validation_timeout_seconds)
        except Exception as exc:
            return {
                'component': 'tunnel',
                'timestamp_utc': utc_now_iso(),
                'healthy': False,
                'mode': 'cli_error',
                'error': str(exc),
            }
        stdout = result.get('stdout_tail', '')
        return {
            'component': 'tunnel',
            'timestamp_utc': utc_now_iso(),
            'healthy': result.get('returncode') == 0 and ('ID:' in stdout or 'NAME:' in stdout),
            'mode': 'cloudflared_cli',
            'command_result': result,
        }

    def _tunnel_status(self) -> Dict[str, Any]:
        script_result = self._validate_tunnel_via_script()
        if script_result.get('healthy') or script_result.get('mode') == 'validate_tunnel_script':
            return script_result
        return self._validate_tunnel_via_cli()

    def ensure(self, repair: bool = False) -> Dict[str, Any]:
        service = self._service_status()
        if repair and not service.get('healthy'):
            service['repair'] = self._repair_service()
            service = self._service_status() | {'repair': service.get('repair')}
        tunnel = self._tunnel_status()
        public_status = probe_url(self.paths.public_url, self.policy.public_probe_timeout_seconds)
        public_status['truth_model'] = 'public_2xx_or_3xx_required'
        payload = {
            'service': service,
            'tunnel': tunnel,
            'public': public_status,
            'timestamp_utc': utc_now_iso(),
        }
        self.state_store.write_json(self.paths.reports_dir / 'cloudflare_status_latest.json', payload)
        return payload

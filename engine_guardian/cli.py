from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from engine_guardian.orchestrator import EngineGuardianOrchestrator
    from engine_guardian.paths import build_paths
    from engine_guardian.preflight import run_preflight
else:
    from .orchestrator import EngineGuardianOrchestrator
    from .paths import build_paths
    from .preflight import run_preflight



def _emit(payload: Dict[str, Any], *, json_only: bool = False) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    print(text)



def _log_cli_result(orchestrator: EngineGuardianOrchestrator, command_name: str, payload: Dict[str, Any]) -> None:
    healthy = payload.get('engine_public_healthy')
    if healthy is None:
        healthy = payload.get('healthy')
    orchestrator.state_store.append_log_line(
        orchestrator.state_store.engine_log_path,
        f'command={command_name} healthy={healthy} status={payload.get("status")}',
    )



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='engine_guardian', description='Engine Guardian v3 CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('bootstrap', help='Seed runtime and write preflight outputs')

    cycle = sub.add_parser('cycle', help='Run a unified guardian cycle')
    cycle.add_argument('--reason', choices=['boot', 'pulse', 'manual'], default='manual')
    cycle.add_argument('--repair', action='store_true')

    sub.add_parser('validate', help='Run validation without forced repair')
    sub.add_parser('heal', help='Run validation with repair enabled')

    status = sub.add_parser('status', help='Print current engine status')
    status.add_argument('--json-only', action='store_true')

    preflight = sub.add_parser('preflight', help='Run preflight only')
    preflight.add_argument('--json-only', action='store_true')

    sched = sub.add_parser('install-scheduler', help='Install the official scheduler tasks')
    sched.add_argument('--dry-run', action='store_true')
    sched.add_argument('--json-only', action='store_true')

    legacy = sub.add_parser('disable-legacy-cloudflare-tasks', help='Export and optionally disable legacy tasks')
    legacy.add_argument('--apply', action='store_true')
    legacy.add_argument('--json-only', action='store_true')

    ra_open = sub.add_parser('repo-analyzer-open', help='Launch Repo Analyzer entrypoint')
    ra_open.add_argument('--json-only', action='store_true')

    ra_validate = sub.add_parser('repo-analyzer-validate', help='Validate Repo Analyzer wrapper')
    ra_validate.add_argument('--json-only', action='store_true')

    ra_heal = sub.add_parser('repo-analyzer-heal', help='Heal Repo Analyzer wrapper')
    ra_heal.add_argument('--json-only', action='store_true')

    ra_status = sub.add_parser('repo-analyzer-status', help='Read Repo Analyzer status')
    ra_status.add_argument('--json-only', action='store_true')

    return parser



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    orchestrator = EngineGuardianOrchestrator()

    try:
        if args.command == 'bootstrap':
            payload = orchestrator.bootstrap()
            _log_cli_result(orchestrator, 'bootstrap', payload)
            _emit(payload)
            return 0

        if args.command == 'cycle':
            payload = orchestrator.cycle(reason=args.reason, repair=args.repair)
            _log_cli_result(orchestrator, f'cycle:{args.reason}', payload)
            _emit(payload)
            return 0

        if args.command == 'validate':
            payload = orchestrator.validate()
            _log_cli_result(orchestrator, 'validate', payload)
            _emit(payload)
            return 0

        if args.command == 'heal':
            payload = orchestrator.heal()
            _log_cli_result(orchestrator, 'heal', payload)
            _emit(payload)
            return 0

        if args.command == 'status':
            payload = orchestrator.status()
            _log_cli_result(orchestrator, 'status', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        if args.command == 'preflight':
            payload = run_preflight(orchestrator.paths, orchestrator.state_store)
            _log_cli_result(orchestrator, 'preflight', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        if args.command == 'install-scheduler':
            payload = orchestrator.install_scheduler(apply=not args.dry_run)
            _log_cli_result(orchestrator, 'install-scheduler', payload)
            _emit(payload, json_only=args.json_only)
            if not args.dry_run and not bool(payload.get('ok', True)):
                return 1
            return 0

        if args.command == 'disable-legacy-cloudflare-tasks':
            payload = orchestrator.disable_legacy_cloudflare_tasks(apply=args.apply)
            _log_cli_result(orchestrator, 'disable-legacy-cloudflare-tasks', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        if args.command == 'repo-analyzer-open':
            payload = orchestrator.repo_analyzer.open()
            _log_cli_result(orchestrator, 'repo-analyzer-open', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        if args.command == 'repo-analyzer-validate':
            payload = orchestrator.repo_analyzer.validate()
            _log_cli_result(orchestrator, 'repo-analyzer-validate', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        if args.command == 'repo-analyzer-heal':
            payload = orchestrator.repo_analyzer.ensure(repair=True)
            _log_cli_result(orchestrator, 'repo-analyzer-heal', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        if args.command == 'repo-analyzer-status':
            payload = orchestrator.repo_analyzer.status()
            _log_cli_result(orchestrator, 'repo-analyzer-status', payload)
            _emit(payload, json_only=args.json_only)
            return 0

        parser.error(f'Unsupported command: {args.command}')
        return 2
    except Exception as exc:
        error_payload = {
            'status': 'error',
            'command': args.command,
            'error': str(exc),
        }
        try:
            _log_cli_result(orchestrator, f'error:{args.command}', error_payload)
        except Exception:
            pass
        print(json.dumps(error_payload, indent=2, sort_keys=True, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

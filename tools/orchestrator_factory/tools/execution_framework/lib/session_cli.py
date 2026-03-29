"""CLI and interactive operator UX for the one-button runtime core."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

SESSION_MODES = ('existing_project', 'new_project')
POLICIES = ('resume_latest_round', 'open_new_round', 'upgrade')


class CLIValidationError(Exception):
    pass


@dataclass(frozen=True)
class RuntimeContext:
    framework_root: Path
    session_mode: str
    policy: str
    project_id: str
    project_name: Optional[str]
    initiative_type: Optional[str]
    intent: str
    dry_run: bool
    non_interactive: bool
    emit_json: bool
    force_lock_steal: bool = False


@dataclass(frozen=True)
class RuntimeResult:
    status: str
    message: str
    session_mode: str
    policy: str
    dry_run: bool
    framework_root: str
    project_id: str
    project_name: str
    initiative_type: str
    run_id: str
    round_id: str
    session_id: str
    created_at_utc: str
    canonical_zip_path: str
    project_manifest_path: str
    run_manifest_path: str
    round_manifest_path: str
    handoff_copy_filename: str
    handoff_copy_path: Optional[str]
    lock_path: str
    ledger_path: str
    idempotency_key: Optional[str]
    notes: List[str]
    touched_paths: Dict[str, str]
    issues: List[Dict[str, Any]] = field(default_factory=list)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='One-button runtime launcher (wave 4).')
    parser.add_argument('--framework-root', default=None, help='Override the framework root path.')
    parser.add_argument('--session-mode', choices=SESSION_MODES, default=None)
    parser.add_argument('--policy', choices=POLICIES, default=None)
    parser.add_argument('--project-id', default=None)
    parser.add_argument('--project-name', default=None)
    parser.add_argument('--initiative-type', default=None)
    parser.add_argument('--intent', default=None, help='Single-line operator intent for the session.')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--emit-json', action='store_true', help='Emit JSON payload instead of decorated text output.')
    parser.add_argument('--force-lock-steal', action='store_true', help='Allow stealing a stale or stale-safe lock only.')
    return parser.parse_args(argv)


def build_runtime_context(args: argparse.Namespace) -> RuntimeContext:
    framework_root = _detect_framework_root(args.framework_root)

    if args.non_interactive:
        missing = [
            name
            for name, value in (
                ('session_mode', args.session_mode),
                ('policy', args.policy),
                ('project_id', args.project_id),
                ('intent', args.intent),
            )
            if not value
        ]
        if missing:
            raise CLIValidationError('The following arguments are required in --non-interactive mode: ' + ', '.join(missing))
        if args.session_mode == 'new_project':
            missing_new = [
                name
                for name, value in (
                    ('project_name', args.project_name),
                    ('initiative_type', args.initiative_type),
                )
                if not value
            ]
            if missing_new:
                raise CLIValidationError(
                    'The following arguments are required for new_project in --non-interactive mode: ' + ', '.join(missing_new)
                )
        return RuntimeContext(
            framework_root=framework_root,
            session_mode=args.session_mode,
            policy=args.policy,
            project_id=args.project_id,
            project_name=args.project_name,
            initiative_type=args.initiative_type,
            intent=args.intent,
            dry_run=bool(args.dry_run),
            non_interactive=True,
            emit_json=bool(args.emit_json),
            force_lock_steal=bool(args.force_lock_steal),
        )

    interactive_values = _collect_interactive_values(
        session_mode=args.session_mode,
        policy=args.policy,
        project_id=args.project_id,
        project_name=args.project_name,
        initiative_type=args.initiative_type,
        intent=args.intent,
        framework_root=framework_root,
    )
    return RuntimeContext(
        framework_root=framework_root,
        session_mode=interactive_values['session_mode'],
        policy=interactive_values['policy'],
        project_id=interactive_values['project_id'],
        project_name=interactive_values.get('project_name'),
        initiative_type=interactive_values.get('initiative_type'),
        intent=interactive_values['intent'],
        dry_run=bool(args.dry_run),
        non_interactive=False,
        emit_json=bool(args.emit_json),
        force_lock_steal=bool(args.force_lock_steal),
    )


def format_console_result(result: RuntimeResult) -> str:
    payload = asdict(result)
    if payload.get('status') in {'ready_for_dispatch', 'reused'}:
        payload['operator_next_step'] = 'Provide the ZIP back to ChatGPT for prompt generation or review the issues list if warnings were emitted.'
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _collect_interactive_values(
    *,
    session_mode: Optional[str],
    policy: Optional[str],
    project_id: Optional[str],
    project_name: Optional[str],
    initiative_type: Optional[str],
    intent: Optional[str],
    framework_root: Path,
) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    values['session_mode'] = session_mode or _prompt_choice('Modo de sesión', [('1', 'existing_project'), ('2', 'new_project')])
    policy_choices = [('2', 'open_new_round')] if values['session_mode'] == 'new_project' else [('1', 'resume_latest_round'), ('2', 'open_new_round'), ('3', 'upgrade')]
    values['policy'] = policy or _prompt_choice('Política', policy_choices)
    values['project_id'] = project_id or _prompt_text('Project ID', required=True)
    if values['session_mode'] == 'new_project':
        values['project_name'] = project_name or _prompt_text('Project name', required=True)
        values['initiative_type'] = initiative_type or _prompt_text('Initiative type', required=True)
    else:
        values['project_name'] = project_name
        values['initiative_type'] = initiative_type
    values['intent'] = intent or _prompt_text('Objetivo de esta sesión', required=True)

    preview = {
        'framework_root': str(framework_root),
        'session_mode': values['session_mode'],
        'policy': values['policy'],
        'project_id': values['project_id'],
        'project_name': values.get('project_name'),
        'initiative_type': values.get('initiative_type'),
        'intent': values['intent'],
    }
    print(json.dumps(preview, indent=2, ensure_ascii=False))
    confirm = _prompt_text('Confirmar [Y/N]', required=True).strip().lower()
    if confirm not in {'y', 'yes', 's', 'si'}:
        raise CLIValidationError('Operator aborted before launching the runtime core.')
    return values


def _prompt_choice(label: str, choices: Sequence[tuple[str, str]]) -> str:
    print(f'{label}:')
    mapping = {key: value for key, value in choices}
    for key, value in choices:
        print(f'[{key}] {value}')
    while True:
        raw = input('> ').strip()
        if raw in mapping:
            return mapping[raw]
        if raw in mapping.values():
            return raw
        print('Selecciona una opción válida.')


def _prompt_text(label: str, required: bool) -> str:
    while True:
        raw = input(f'{label}: ').strip()
        if raw or not required:
            return raw
        print('Este campo es obligatorio.')


def _detect_framework_root(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).resolve()
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if candidate.name == 'orchestrator_factory' and candidate.parent.name == 'tools':
            return candidate
    env_value = os.environ.get('HITECH_ORCHESTRATOR_FRAMEWORK_ROOT')
    if env_value:
        return Path(env_value).resolve()
    raise CLIValidationError('Could not detect framework root. Pass --framework-root explicitly.')

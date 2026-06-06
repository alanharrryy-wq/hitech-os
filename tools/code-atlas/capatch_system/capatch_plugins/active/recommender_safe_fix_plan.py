#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Autofix recommender for safe, declarative fix proposals."""

from pathlib import Path
from typing import Any

from plugin_lib.fixer_utils import (
    CONFIG_SIGNAL_TERMS,
    DB_SIGNAL_TERMS,
    NODE_SIGNAL_TERMS,
    PORT_SIGNAL_TERMS,
    PYTHON_SIGNAL_TERMS,
    TEXTUAL_CONFIG_SIGNAL_TERMS,
    build_fix_proposal_v2,
    build_restore_recipe,
    build_verification_recipe,
    collect_signal_text,
    detect_package_manager,
    extract_port,
    file_exists_any,
    find_candidate_config,
    next_port,
    runtime_python_command,
    signal_contains,
)

PLUGIN_ID = 'recommender.safe-fix-plan'
PLUGIN_VERSION = '6.0.0'
PLUGIN_DESCRIPTION = 'Construye FixProposalV2 declarativos, reversibles y con recetas de verificación.'
PLUGIN_MIN_RUNTIME = '6.0.0'
PLUGIN_KIND = 'recommender'
PLUGIN_PHASE = 'recommend'
PLUGIN_OUTPUTS = [
    'reports/findings/fix_execution.json',
    'reports/findings/fix_execution.md',
    'reports/verification/before_after_verification.json',
    'reports/verification/before_after_verification.md',
]


def register(api):
    api.register_recommender(recommend)



def _proposal_node_deps(root_dir: Path, signal_text: str, evidence_refs: list[str]) -> dict[str, Any] | None:
    package_json = file_exists_any(root_dir, ['package.json'])
    if not package_json or not signal_contains(signal_text, NODE_SIGNAL_TERMS):
        return None
    manager = detect_package_manager(root_dir)
    command = 'npm install --ignore-scripts --no-audit --no-fund'
    lock_path = 'package-lock.json'
    if manager == 'pnpm':
        command = 'pnpm install --ignore-scripts'
        lock_path = 'pnpm-lock.yaml'
    elif manager == 'yarn':
        command = 'yarn install --ignore-scripts'
        lock_path = 'yarn.lock'
    affected = [package_json]
    if (root_dir / lock_path).exists():
        affected.append(lock_path)
    rollback_recipe = build_restore_recipe(affected, family='node-deps', delete_paths=['node_modules'])
    verification_recipe = build_verification_recipe(affected, family='node-deps', extra=[
        {'kind': 'command-exit', 'verifier_id': 'command-exit-zero', 'family': 'node-deps'},
        {'kind': 'builtin-verifier', 'verifier_id': 'git-clean', 'family': 'node-deps'},
    ])
    return build_fix_proposal_v2(
        proposal_id='autofix.node-deps.install-safe',
        title='Reparar dependencias Node con install allowlisted',
        rationale='Se detectaron señales de módulos faltantes o árbol de dependencias roto y existe package.json.',
        family='node-deps',
        affected_paths=affected,
        commands=[command],
        risk_level='medium',
        reversible=True,
        metadata={
            'evidence_refs': evidence_refs,
            'cross_signal_support': ['runtime.log-tail-sample'],
            'package_manager': manager,
            'confidence_score': 0.61,
        },
        applicability_predicates=[
            {'type': 'session_mode', 'modes': ['fix-plan', 'apply-fixes']},
            {'type': 'any_file_exists', 'paths': ['package.json']},
            {'type': 'signal_contains', 'terms': NODE_SIGNAL_TERMS},
        ],
        rollback_recipe=rollback_recipe,
        verification_recipe=verification_recipe,
        verification_steps=['command exit == 0', 'json parse on package manifest if touched', 'git status capture'],
        confidence_reason='node manifest present + missing dependency signals + reversible rollback on manifests/node_modules',
    )



def _proposal_python_venv(root_dir: Path, signal_text: str, evidence_refs: list[str]) -> dict[str, Any] | None:
    manifest = file_exists_any(root_dir, ['requirements.txt', 'pyproject.toml', 'requirements-dev.txt'])
    if not manifest or not signal_contains(signal_text, PYTHON_SIGNAL_TERMS):
        return None
    py = runtime_python_command()
    commands = [f'{py} -m venv .venv']
    if manifest.endswith('.txt'):
        commands.append(f'{py} -m pip install -r {manifest}')
    rollback_recipe = build_restore_recipe([manifest], family='python-venv', delete_paths=['.venv'])
    verification_recipe = build_verification_recipe([manifest], family='python-venv', extra=[
        {'kind': 'command-exit', 'verifier_id': 'command-exit-zero', 'family': 'python-venv'},
        {'kind': 'builtin-verifier', 'verifier_id': 'git-clean', 'family': 'python-venv'},
    ])
    return build_fix_proposal_v2(
        proposal_id='autofix.python-venv.rebuild-safe',
        title='Reconstruir venv local de forma reversible',
        rationale='Se detectaron señales de entorno Python roto y existe un manifiesto instalable.',
        family='python-venv',
        affected_paths=[manifest],
        commands=commands,
        risk_level='medium',
        reversible=True,
        metadata={
            'evidence_refs': evidence_refs,
            'cross_signal_support': ['runtime.environment-summary'],
            'confidence_score': 0.58,
        },
        applicability_predicates=[
            {'type': 'session_mode', 'modes': ['fix-plan', 'apply-fixes']},
            {'type': 'any_file_exists', 'paths': ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml']},
            {'type': 'signal_contains', 'terms': PYTHON_SIGNAL_TERMS},
        ],
        rollback_recipe=rollback_recipe,
        verification_recipe=verification_recipe,
        verification_steps=['command exit == 0', 'toml/json parse on touched manifests if needed'],
        confidence_reason='python manifest present + module/venv signals + rollback can drop .venv',
    )



def _proposal_port_conflict(root_dir: Path, signal_text: str, evidence_refs: list[str]) -> dict[str, Any] | None:
    config_path = find_candidate_config(root_dir)
    if not config_path or not signal_contains(signal_text, PORT_SIGNAL_TERMS):
        return None
    current_port = extract_port(signal_text, default=3000)
    replacement_port = next_port(current_port)
    suffix = Path(config_path).suffix.lower()
    if suffix == '.json':
        ops = [{
            'type': 'SetJsonValue',
            'label': 'set-port-json',
            'file': config_path,
            'json_pointer': '/port',
            'value': replacement_port,
        }]
    elif suffix in {'.yaml', '.yml'}:
        ops = [{
            'type': 'SetYamlValue',
            'label': 'set-port-yaml',
            'file': config_path,
            'yaml_path': 'port',
            'value': replacement_port,
        }]
    elif suffix == '.toml':
        ops = [{
            'type': 'SetTomlValue',
            'label': 'set-port-toml',
            'file': config_path,
            'toml_path': 'port',
            'value': replacement_port,
        }]
    else:
        ops = [{
            'type': 'ReplaceRegexOnce',
            'label': 'set-port-textual',
            'file': config_path,
            'pattern': r'(?im)^(\s*(?:port|PORT)\s*[=:]\s*)(\d{2,5})(\s*)$',
            'new_text': rf'\g<1>{replacement_port}\g<3>',
        }]
    return build_fix_proposal_v2(
        proposal_id='autofix.port-conflict.bump-port',
        title='Mover puerto a un valor libre cercano',
        rationale='Se detectó conflicto de puerto y existe un archivo de configuración editable de forma declarativa.',
        family='port-conflict',
        affected_paths=[config_path],
        ops_payload=ops,
        risk_level='low',
        reversible=True,
        metadata={
            'evidence_refs': evidence_refs,
            'current_port': current_port,
            'replacement_port': replacement_port,
            'confidence_score': 0.74,
        },
        applicability_predicates=[
            {'type': 'session_mode', 'modes': ['fix-plan', 'apply-fixes']},
            {'type': 'any_file_exists', 'paths': [config_path]},
            {'type': 'signal_contains', 'terms': PORT_SIGNAL_TERMS},
        ],
        rollback_recipe=build_restore_recipe([config_path], family='port-conflict'),
        verification_recipe=build_verification_recipe([config_path], family='port-conflict'),
        verification_steps=[f'Actualizar port de {current_port} a {replacement_port} y validar parser del archivo'],
        confidence_reason='port conflict signal + config candidate exists + parser-backed patch path',
    )



def _proposal_db_reconnect(root_dir: Path, signal_text: str, evidence_refs: list[str]) -> dict[str, Any] | None:
    config_path = file_exists_any(root_dir, ['config.json', 'settings.json', 'appsettings.json', 'config.yaml', 'config.yml', 'settings.yaml', 'settings.yml', 'config.toml', 'settings.toml'])
    if not config_path or not signal_contains(signal_text, DB_SIGNAL_TERMS):
        return None
    suffix = Path(config_path).suffix.lower()
    if suffix == '.json':
        ops = [
            {'type': 'SetJsonValue', 'label': 'db-reconnect-enabled', 'file': config_path, 'json_pointer': '/database/reconnect', 'value': True},
            {'type': 'SetJsonValue', 'label': 'db-retry-count', 'file': config_path, 'json_pointer': '/database/retryAttempts', 'value': 3},
        ]
    elif suffix in {'.yaml', '.yml'}:
        ops = [
            {'type': 'SetYamlValue', 'label': 'db-reconnect-enabled', 'file': config_path, 'yaml_path': 'database.reconnect', 'value': True},
            {'type': 'SetYamlValue', 'label': 'db-retry-count', 'file': config_path, 'yaml_path': 'database.retryAttempts', 'value': 3},
        ]
    elif suffix == '.toml':
        ops = [
            {'type': 'SetTomlValue', 'label': 'db-reconnect-enabled', 'file': config_path, 'toml_path': 'database.reconnect', 'value': True},
            {'type': 'SetTomlValue', 'label': 'db-retry-count', 'file': config_path, 'toml_path': 'database.retryAttempts', 'value': 3},
        ]
    else:
        ops = [{
            'type': 'EnsureInsertAfterExact',
            'label': 'db-reconnect-text',
            'file': config_path,
            'anchor': '[database]',
            'insert_text': 'reconnect=true\nretryAttempts=3\n',
        }]
    return build_fix_proposal_v2(
        proposal_id='autofix.db-reconnect.enable-retries',
        title='Activar reconnect/retries de base de datos',
        rationale='Se detectaron señales de conexión inestable a DB y existe configuración candidata para endurecer el runtime.',
        family='db-reconnect',
        affected_paths=[config_path],
        ops_payload=ops,
        risk_level='low',
        reversible=True,
        metadata={
            'evidence_refs': evidence_refs,
            'confidence_score': 0.67,
        },
        applicability_predicates=[
            {'type': 'session_mode', 'modes': ['fix-plan', 'apply-fixes']},
            {'type': 'any_file_exists', 'paths': [config_path]},
            {'type': 'signal_contains', 'terms': DB_SIGNAL_TERMS},
        ],
        rollback_recipe=build_restore_recipe([config_path], family='db-reconnect'),
        verification_recipe=build_verification_recipe([config_path], family='db-reconnect'),
        verification_steps=['Validar parser del config y confirmar presencia de reconnect/retryAttempts'],
        confidence_reason='db instability signals + config candidate exists + reversible semantic patch',
    )



def _proposal_textual_config(root_dir: Path, signal_text: str, evidence_refs: list[str]) -> dict[str, Any] | None:
    env_path = file_exists_any(root_dir, ['.env', '.env.local', '.env.development'])
    example_path = file_exists_any(root_dir, ['.env.example'])
    if not env_path or not example_path or not signal_contains(signal_text, TEXTUAL_CONFIG_SIGNAL_TERMS + CONFIG_SIGNAL_TERMS):
        return None
    example_text = (root_dir / example_path).read_text(encoding='utf-8', errors='replace')
    env_text = (root_dir / env_path).read_text(encoding='utf-8', errors='replace')
    missing_anchor = None
    missing_line = None
    for raw_line in example_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key = line.split('=', 1)[0].strip()
        if f'{key}=' not in env_text:
            missing_anchor = env_text.splitlines()[-1] if env_text.splitlines() else ''
            missing_line = line
            break
    if not missing_line:
        return None
    ops = [{
        'type': 'EnsureInsertAfterExact',
        'label': 'repair-env-missing-key',
        'file': env_path,
        'anchor': missing_anchor or env_text.splitlines()[-1],
        'insert_text': f'\n{missing_line}\n' if missing_anchor else f'{missing_line}\n',
    }]
    return build_fix_proposal_v2(
        proposal_id='autofix.textual-config.repair-env',
        title='Completar configuración textual faltante desde ejemplo',
        rationale='Se detectó config textual incompleta y existe .env.example como fuente reversible de reparación.',
        family='textual-config-repair',
        affected_paths=[env_path],
        ops_payload=ops,
        risk_level='low',
        reversible=True,
        metadata={
            'evidence_refs': evidence_refs,
            'missing_line': missing_line,
            'confidence_score': 0.69,
        },
        applicability_predicates=[
            {'type': 'session_mode', 'modes': ['fix-plan', 'apply-fixes']},
            {'type': 'any_file_exists', 'paths': [env_path, example_path]},
            {'type': 'signal_contains', 'terms': TEXTUAL_CONFIG_SIGNAL_TERMS + CONFIG_SIGNAL_TERMS},
        ],
        rollback_recipe=build_restore_recipe([env_path], family='textual-config-repair'),
        verification_recipe=build_verification_recipe([env_path], family='textual-config-repair'),
        verification_steps=['Confirmar que la clave faltante existe después del parche'],
        confidence_reason='example-backed textual repair + env target exists + missing key detected concretely',
    )



def _proposal_config_patch(root_dir: Path, signal_text: str, evidence_refs: list[str]) -> dict[str, Any] | None:
    config_path = file_exists_any(root_dir, ['config.json', 'settings.json', 'appsettings.json', 'config.yaml', 'config.yml', 'settings.yaml', 'settings.yml', 'config.toml', 'settings.toml'])
    if not config_path or not signal_contains(signal_text, CONFIG_SIGNAL_TERMS):
        return None
    suffix = Path(config_path).suffix.lower()
    if suffix == '.json':
        ops = [{'type': 'SetJsonValue', 'label': 'config-patch-json', 'file': config_path, 'json_pointer': '/autofix/lastAppliedBy', 'value': 'autofix-bridge'}]
    elif suffix in {'.yaml', '.yml'}:
        ops = [{'type': 'SetYamlValue', 'label': 'config-patch-yaml', 'file': config_path, 'yaml_path': 'autofix.lastAppliedBy', 'value': 'autofix-bridge'}]
    elif suffix == '.toml':
        ops = [{'type': 'SetTomlValue', 'label': 'config-patch-toml', 'file': config_path, 'toml_path': 'autofix.lastAppliedBy', 'value': 'autofix-bridge'}]
    else:
        return None
    return build_fix_proposal_v2(
        proposal_id='autofix.config-patch.annotate-safe-fix',
        title='Aplicar patch declarativo de config compatible con parser',
        rationale='Existe un config estructurado y conviene dejar una marca controlada para reparar/configurar sin tocar internals privados.',
        family='config-patch',
        affected_paths=[config_path],
        ops_payload=ops,
        risk_level='low',
        reversible=True,
        metadata={'evidence_refs': evidence_refs, 'confidence_score': 0.56},
        applicability_predicates=[
            {'type': 'session_mode', 'modes': ['fix-plan', 'apply-fixes']},
            {'type': 'any_file_exists', 'paths': [config_path]},
            {'type': 'signal_contains', 'terms': CONFIG_SIGNAL_TERMS},
        ],
        rollback_recipe=build_restore_recipe([config_path], family='config-patch'),
        verification_recipe=build_verification_recipe([config_path], family='config-patch'),
        verification_steps=['Parser del config debe seguir pasando después del patch'],
        confidence_reason='structured config exists + semantic op available + reversible single-file patch',
    )



def recommend(session, artifacts, findings, recommendations, **kwargs):
    root_dir = Path(getattr(session, 'target_path', getattr(session, 'root_dir', '.'))).resolve()
    signal_text = collect_signal_text(artifacts=artifacts, findings=findings, recommendations=recommendations)
    evidence_refs = [str(getattr(item, 'artifact_id', '')) for item in list(artifacts or []) if getattr(item, 'artifact_id', None)]
    proposals = []
    for builder in (
        _proposal_node_deps,
        _proposal_python_venv,
        _proposal_config_patch,
        _proposal_port_conflict,
        _proposal_db_reconnect,
        _proposal_textual_config,
    ):
        payload = builder(root_dir, signal_text, evidence_refs)
        if payload:
            proposals.append(payload)
    summary = f'Autofix Bridge generó {len(proposals)} propuesta(s) declarativa(s).' if proposals else 'Autofix Bridge no encontró propuestas aplicables todavía.'
    return {
        'fixes': proposals,
        'summary': summary,
    }

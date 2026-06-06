#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from capatch_ai_apply_common import (  # noqa: E402
    ChangePlanEntry,
    PhaseError,
    build_config_from_args,
    build_phase_output_dir,
    capture_backups,
    default_test_command,
    emit_json_summary,
    ensure_dir,
    iso_now,
    parse_common_args,
    relpath,
    render_manifest_md,
    restore_from_manifest,
    run_subprocess_logged,
    safe_slug,
    sha256_file,
    transaction_id_for,
    write_json,
    write_rollback_instructions,
    write_text,
)

PHASE_NAME = 'phase6_planner_foundation'
ROOT_EXPORT_NAME = 'capatch_ai_controlled_fix'

PLANNER_INPUT_CONTENT = '''from __future__ import annotations

from typing import Any


def build_planner_input(preflight_report: Any, risk_summary: dict[str, Any], operations: list[Any]) -> dict[str, Any]:
    target_files = list(getattr(preflight_report, 'target_files', []) or [])
    anchor_diagnostics = dict(getattr(preflight_report, 'anchor_diagnostics', {}) or {})
    surface_summary = dict(getattr(preflight_report, 'surface_summary', {}) or {})
    operation_types: list[str] = []
    for item in list(operations or []):
        value = getattr(item, 'type', None)
        if value is None and isinstance(item, dict):
            value = item.get('type')
        if value:
            operation_types.append(str(value))
    return {
        'target_files': target_files,
        'target_file_count': len(target_files),
        'risk_level': str((risk_summary or {}).get('risk_level') or 'low').lower(),
        'blocked_reasons': list((risk_summary or {}).get('blocked_reasons') or []),
        'fragile_anchor_count': int(anchor_diagnostics.get('fragile_anchor_operation_count', 0) or 0),
        'exact_anchor_count': int(anchor_diagnostics.get('exact_anchor_operation_count', 0) or 0),
        'structural_candidate_files': list(surface_summary.get('structural_candidate_files') or []),
        'operation_types': operation_types,
    }
'''

PLANNER_RUNTIME_CONTENT = '''from __future__ import annotations

from typing import Any

from .planner_input import build_planner_input

_ALLOWED = ('exact', 'structural', 'guarded', 'transactional', 'probe-only')


def run_planner_runtime(ctx: Any, preflight_report: Any, risk_summary: dict[str, Any], operations: list[Any]) -> dict[str, Any]:
    planner_mode = str(getattr(ctx, 'planner_mode', 'off') or 'off').lower()
    planner_input = build_planner_input(preflight_report, risk_summary, operations)
    blocked_reasons = list(planner_input.get('blocked_reasons') or [])
    if planner_mode not in {'off', 'advisory'}:
        planner_mode = 'off'
    if planner_mode == 'off':
        return {
            'planner_mode': 'off',
            'enabled': False,
            'preferred_strategy': None,
            'confidence_delta': {},
            'source_of_decision': 'planner:off',
            'planner_input': planner_input,
            'notes': ['planner disabled'],
        }

    target_file_count = int(planner_input.get('target_file_count', 0) or 0)
    fragile_anchor_count = int(planner_input.get('fragile_anchor_count', 0) or 0)
    exact_anchor_count = int(planner_input.get('exact_anchor_count', 0) or 0)
    structural_candidate_files = list(planner_input.get('structural_candidate_files') or [])
    risk_level = str(planner_input.get('risk_level') or 'low').lower()

    preferred = 'guarded'
    notes: list[str] = []
    if blocked_reasons:
        preferred = 'probe-only'
        notes.append('planner saw blockers and suggested probe-only')
    elif target_file_count > 1:
        preferred = 'transactional'
        notes.append('planner prefers transactional for multi-file change sets')
    elif structural_candidate_files:
        preferred = 'structural'
        notes.append('planner detected structural surface candidates')
    elif exact_anchor_count > 0 and fragile_anchor_count == 0:
        preferred = 'exact'
        notes.append('planner saw exact anchors with low fragility')
    elif fragile_anchor_count > 0 or risk_level in {'medium', 'high', 'critical'}:
        preferred = 'guarded'
        notes.append('planner prefers guarded mode for fragile anchors or elevated risk')

    confidence_delta = {key: 0.0 for key in _ALLOWED}
    if preferred in confidence_delta:
        confidence_delta[preferred] = 0.07
    return {
        'planner_mode': 'advisory',
        'enabled': True,
        'preferred_strategy': preferred,
        'confidence_delta': confidence_delta,
        'source_of_decision': 'planner:advisory',
        'planner_input': planner_input,
        'notes': notes,
    }
'''

STRATEGY_FUSION_CONTENT = '''from __future__ import annotations

from typing import Any

_ALLOWED = ('exact', 'structural', 'guarded', 'transactional', 'probe-only')


def fuse_strategy_signals(candidate_scores: dict[str, float], planner_decision: dict[str, Any] | None) -> dict[str, Any]:
    planner_decision = dict(planner_decision or {})
    fused: dict[str, float] = {}
    base_scores = dict(candidate_scores or {})
    delta = dict(planner_decision.get('confidence_delta') or {})
    for strategy in _ALLOWED:
        base = float(base_scores.get(strategy, 0.0) or 0.0)
        boost = float(delta.get(strategy, 0.0) or 0.0)
        fused[strategy] = round(max(0.01, min(0.99, base + boost)), 3)
    preferred = str(planner_decision.get('preferred_strategy') or '').strip().lower() or None
    source = str(planner_decision.get('source_of_decision') or 'confidence-only')
    return {
        'candidate_scores': fused,
        'preferred_strategy': preferred,
        'source_of_decision': source,
        'planner_mode': str(planner_decision.get('planner_mode') or 'off'),
        'planner_enabled': bool(planner_decision.get('enabled', False)),
        'planner_notes': list(planner_decision.get('notes') or []),
    }
'''


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8', newline='\n')


def _replace_exact_once(content: str, old: str, new: str, *, label: str) -> str:
    if old not in content:
        if new in content:
            return content
        raise PhaseError(f'No encontre ancla para {label}')
    return content.replace(old, new, 1)


def _upsert_file(root_dir: Path, relative_path: str, content: str, *, apply: bool) -> dict[str, Any]:
    target = root_dir / relative_path
    before_exists = target.exists()
    before_sha = sha256_file(target) if before_exists else None
    status = 'unchanged'
    if not before_exists or _read(target) != content:
        status = 'create' if not before_exists else 'update'
        if apply:
            ensure_dir(target.parent)
            _write(target, content)
    after_sha = sha256_file(target) if apply and target.exists() else None
    return {
        'relative_path': relative_path,
        'status': status,
        'before_sha256': before_sha,
        'after_sha256': after_sha,
    }


def _patch_file(root_dir: Path, relative_path: str, transform, *, apply: bool) -> dict[str, Any]:
    target = root_dir / relative_path
    if not target.exists():
        raise PhaseError(f'Archivo esperado no existe: {relative_path}')
    before = _read(target)
    after = transform(before)
    status = 'unchanged' if after == before else 'update'
    if apply and after != before:
        _write(target, after)
    return {
        'relative_path': relative_path,
        'status': status,
        'before_sha256': sha256_file(target) if target.exists() else None,
    }


def _transform_context(content: str) -> str:
    old = "    force_dry_run_on_high_risk: bool = True\n"
    new = "    force_dry_run_on_high_risk: bool = True\n    planner_mode: str = \"off\"\n"
    return _replace_exact_once(content, old, new, label='context planner_mode')


def _transform_parser(content: str) -> str:
    anchor = "    parser.add_argument('--strategy', choices=['auto', 'exact', 'guarded', 'transactional', 'structural', 'probe-only'], default='auto', help='Fuerza o sugiere estrategia de patch. auto deja decidir al selector.')\n"
    addition = anchor + "    parser.add_argument('--planner-mode', choices=['off', 'advisory'], default='off', help='Activa planner foundation heuristico sin ceder control de ejecucion.')\n"
    return _replace_exact_once(content, anchor, addition, label='parser planner-mode')


def _transform_commands_patch(content: str) -> str:
    old = "        force_dry_run_on_high_risk=bool(getattr(args, 'force_dry_run_on_high_risk', False)),\n    )\n"
    new = "        force_dry_run_on_high_risk=bool(getattr(args, 'force_dry_run_on_high_risk', False)),\n        planner_mode=str(getattr(args, 'planner_mode', 'off') or 'off'),\n    )\n"
    return _replace_exact_once(content, old, new, label='commands_patch planner_mode')


def _transform_confidence(content: str) -> str:
    content = content.replace('\nimport os\n', '\n')
    old = '''def _normalize_strategy_hint(planner_hint: Any | None) -> dict[str, Any]:\n    if planner_hint is None:\n        planner_hint = os.environ.get('CAPATCH_PLANNER_HINT')\n    hint = str(planner_hint or '').strip().lower()\n    if hint not in _ALLOWED_STRATEGIES:\n        hint = ''\n    return {\n        'enabled': bool(hint),\n        'hint': hint or None,\n        'source': 'env:CAPATCH_PLANNER_HINT' if hint and planner_hint == os.environ.get('CAPATCH_PLANNER_HINT') else 'callsite' if hint else None,\n    }\n'''
    new = '''def _normalize_strategy_hint(planner_hint: Any | None) -> dict[str, Any]:\n    hint = str(planner_hint or '').strip().lower()\n    if hint not in _ALLOWED_STRATEGIES:\n        hint = ''\n    return {\n        'enabled': bool(hint),\n        'hint': hint or None,\n        'source': 'callsite' if hint else None,\n    }\n'''
    return _replace_exact_once(content, old, new, label='confidence no env planner hint')


def _transform_strategy_selector(content: str) -> str:
    content = _replace_exact_once(
        content,
        "from capatch_ops.registry import strategy_capabilities, summarize_operation_families\nfrom capatch_policy.confidence import score_patch_strategy\n",
        "from capatch_ops.registry import strategy_capabilities, summarize_operation_families\nfrom capatch_policy.confidence import score_patch_strategy\nfrom capatch_policy.strategy_fusion import fuse_strategy_signals\n\nfrom .planner_runtime import run_planner_runtime\n",
        label='selector imports',
    )
    old_func = '''def _planner_hint_from_ctx(ctx: Any) -> Any | None:\n    for attr in ('planner_hint', 'ai_strategy_hint', 'strategy_hint'):\n        value = getattr(ctx, attr, None)\n        if value:\n            return value\n    return None\n\n\n'''
    new_func = '''def _planner_hint_from_ctx(ctx: Any) -> Any | None:\n    for attr in ('planner_hint', 'ai_strategy_hint', 'strategy_hint'):\n        value = getattr(ctx, attr, None)\n        if value:\n            return value\n    return None\n\n\ndef _planner_mode_from_ctx(ctx: Any) -> str:\n    return str(getattr(ctx, 'planner_mode', 'off') or 'off').lower()\n\n\n'''
    content = _replace_exact_once(content, old_func, new_func, label='selector planner mode helper')
    old_body = '''def select_patch_strategy(ctx: Any, preflight_report: Any, operations: list[Any], risk_summary: dict[str, Any]) -> dict[str, Any]:\n    planner_hint = _planner_hint_from_ctx(ctx)\n    confidence = score_patch_strategy(preflight_report, risk_summary, list(operations or []), planner_hint=planner_hint)\n    candidate_scores = dict(confidence.get('candidate_scores') or {})\n    strategy_hints = dict(getattr(preflight_report, 'strategy_hints', {}) or {})\n    blockers = list((risk_summary or {}).get('blocked_reasons') or [])\n    reasons: list[str] = []\n\n    if blockers or strategy_hints.get('force_probe_only'):\n        selected = 'probe-only'\n        reasons.append('preflight reported blockers or path violations')\n    else:\n        selected = _choose_strategy(candidate_scores)\n\n    if selected == 'exact':\n        reasons.append('single-file anchor-driven patch remains stable enough for literal execution')\n    elif selected == 'structural':\n        reasons.append('typescript/javascript surface and anchor fragility suggest structural handling next')\n    elif selected == 'guarded':\n        reasons.append('risk or anchor fragility suggests guarded execution with review')\n    elif selected == 'transactional':\n        reasons.append('multi-file or batch-heavy change deserves transactional coordination')\n    else:\n        reasons.append('inspect only before mutating because confidence is too low or blockers exist')\n\n    if confidence.get('planner_stub', {}).get('enabled'):\n        reasons.append(f"planner stub bias applied: {confidence['planner_stub'].get('hint')}")\n\n    capabilities = strategy_capabilities().get(selected, {'advisory_only': False, 'families': []})\n    operation_families = summarize_operation_families(operations)\n    ordered_candidates = [\n        {'strategy': key, 'score': value}\n        for key, value in sorted(candidate_scores.items(), key=lambda item: (-float(item[1]), _TIE_BREAK_ORDER.get(item[0], 99)))\n    ]\n    return {\n        'selected_strategy': selected,\n        'selected_score': float(candidate_scores.get(selected, 0.0) or 0.0),\n        'candidate_ranking': ordered_candidates,\n        'operation_families': operation_families,\n        'planner_stub': dict(confidence.get('planner_stub') or {}),\n        'anchor_confidence': float(confidence.get('anchor_confidence', 0.0) or 0.0),\n        'syntax_confidence': float(confidence.get('syntax_confidence', 0.0) or 0.0),\n        'semantic_confidence': float(confidence.get('semantic_confidence', 0.0) or 0.0),\n        'batch_risk': float(confidence.get('batch_risk', 0.0) or 0.0),\n        'rollback_readiness': float(confidence.get('rollback_readiness', 0.0) or 0.0),\n        'overall_confidence': float(confidence.get('overall_confidence', 0.0) or 0.0),\n        'recommended_guardrails': list(confidence.get('recommended_guardrails') or []),\n        'requires_future_executor': bool(capabilities.get('advisory_only', False)),\n        'executor_capabilities': capabilities,\n        'advisory_only': bool(capabilities.get('advisory_only', False)),\n        'reasons': reasons,\n    }\n'''
    new_body = '''def select_patch_strategy(ctx: Any, preflight_report: Any, operations: list[Any], risk_summary: dict[str, Any]) -> dict[str, Any]:\n    planner_hint = _planner_hint_from_ctx(ctx)\n    planner_mode = _planner_mode_from_ctx(ctx)\n    confidence = score_patch_strategy(preflight_report, risk_summary, list(operations or []), planner_hint=planner_hint)\n    planner_decision = run_planner_runtime(ctx, preflight_report, risk_summary, list(operations or []))\n    fusion = fuse_strategy_signals(dict(confidence.get('candidate_scores') or {}), planner_decision)\n    candidate_scores = dict(fusion.get('candidate_scores') or confidence.get('candidate_scores') or {})\n    strategy_hints = dict(getattr(preflight_report, 'strategy_hints', {}) or {})\n    blockers = list((risk_summary or {}).get('blocked_reasons') or [])\n    reasons: list[str] = []\n\n    if blockers or strategy_hints.get('force_probe_only'):\n        selected = 'probe-only'\n        reasons.append('preflight reported blockers or path violations')\n    else:\n        selected = _choose_strategy(candidate_scores)\n\n    if selected == 'exact':\n        reasons.append('single-file anchor-driven patch remains stable enough for literal execution')\n    elif selected == 'structural':\n        reasons.append('typescript/javascript surface and anchor fragility suggest structural handling next')\n    elif selected == 'guarded':\n        reasons.append('risk or anchor fragility suggests guarded execution with review')\n    elif selected == 'transactional':\n        reasons.append('multi-file or batch-heavy change deserves transactional coordination')\n    else:\n        reasons.append('inspect only before mutating because confidence is too low or blockers exist')\n\n    if fusion.get('planner_enabled'):\n        reasons.append(f\"planner foundation advisory nudged strategy toward: {fusion.get('preferred_strategy')}\")\n\n    capabilities = strategy_capabilities().get(selected, {'advisory_only': False, 'families': []})\n    operation_families = summarize_operation_families(operations)\n    ordered_candidates = [\n        {'strategy': key, 'score': value}\n        for key, value in sorted(candidate_scores.items(), key=lambda item: (-float(item[1]), _TIE_BREAK_ORDER.get(item[0], 99)))\n    ]\n    return {\n        'selected_strategy': selected,\n        'selected_score': float(candidate_scores.get(selected, 0.0) or 0.0),\n        'candidate_ranking': ordered_candidates,\n        'operation_families': operation_families,\n        'planner_stub': {'enabled': False, 'hint': None, 'source': None},\n        'planner_mode': planner_mode,\n        'planner_decision': dict(planner_decision or {}),\n        'source_of_decision': str(fusion.get('source_of_decision') or 'confidence-only'),\n        'anchor_confidence': float(confidence.get('anchor_confidence', 0.0) or 0.0),\n        'syntax_confidence': float(confidence.get('syntax_confidence', 0.0) or 0.0),\n        'semantic_confidence': float(confidence.get('semantic_confidence', 0.0) or 0.0),\n        'batch_risk': float(confidence.get('batch_risk', 0.0) or 0.0),\n        'rollback_readiness': float(confidence.get('rollback_readiness', 0.0) or 0.0),\n        'overall_confidence': float(confidence.get('overall_confidence', 0.0) or 0.0),\n        'recommended_guardrails': list(confidence.get('recommended_guardrails') or []),\n        'requires_future_executor': bool(capabilities.get('advisory_only', False)),\n        'executor_capabilities': capabilities,\n        'advisory_only': bool(capabilities.get('advisory_only', False)),\n        'reasons': reasons,\n    }\n'''
    content = _replace_exact_once(content, old_body, new_body, label='selector phase6 body')
    return content


def _build_plan() -> list[ChangePlanEntry]:
    return [
        ChangePlanEntry(kind='upsert', relative_path='capatch_engine/planner_input.py', content=PLANNER_INPUT_CONTENT, notes=['new planner input builder']),
        ChangePlanEntry(kind='upsert', relative_path='capatch_engine/planner_runtime.py', content=PLANNER_RUNTIME_CONTENT, notes=['new planner runtime foundation']),
        ChangePlanEntry(kind='upsert', relative_path='capatch_policy/strategy_fusion.py', content=STRATEGY_FUSION_CONTENT, notes=['new fusion layer for confidence + planner']),
        ChangePlanEntry(kind='patch', relative_path='capatch_engine/context.py', notes=['add planner_mode to PatchContext']),
        ChangePlanEntry(kind='patch', relative_path='capatch_cli/parser.py', notes=['add --planner-mode']),
        ChangePlanEntry(kind='patch', relative_path='capatch_cli/commands_patch.py', notes=['pass planner_mode to PatchContext']),
        ChangePlanEntry(kind='patch', relative_path='capatch_policy/confidence.py', notes=['remove env planner hint dependency']),
        ChangePlanEntry(kind='patch', relative_path='capatch_engine/strategy_selector.py', notes=['use planner runtime + strategy fusion']),
    ]


def _apply_plan(root_dir: Path, plan: list[ChangePlanEntry], *, apply: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in plan:
        if item.kind == 'upsert':
            results.append(_upsert_file(root_dir, item.relative_path, str(item.content or ''), apply=apply))
            continue
        if item.relative_path == 'capatch_engine/context.py':
            results.append(_patch_file(root_dir, item.relative_path, _transform_context, apply=apply))
        elif item.relative_path == 'capatch_cli/parser.py':
            results.append(_patch_file(root_dir, item.relative_path, _transform_parser, apply=apply))
        elif item.relative_path == 'capatch_cli/commands_patch.py':
            results.append(_patch_file(root_dir, item.relative_path, _transform_commands_patch, apply=apply))
        elif item.relative_path == 'capatch_policy/confidence.py':
            results.append(_patch_file(root_dir, item.relative_path, _transform_confidence, apply=apply))
        elif item.relative_path == 'capatch_engine/strategy_selector.py':
            results.append(_patch_file(root_dir, item.relative_path, _transform_strategy_selector, apply=apply))
        else:
            raise PhaseError(f'Patch no implementado para {item.relative_path}')
    return results


def _collect_abs_paths(root_dir: Path, plan: list[ChangePlanEntry]) -> list[Path]:
    return [(root_dir / item.relative_path).resolve() for item in plan]


def _build_summary(config, output_dir: Path, transaction_id: str, plan: list[ChangePlanEntry], results: list[dict[str, Any]], tests_result: dict[str, Any] | None) -> dict[str, Any]:
    touched_files = [item.relative_path for item in plan]
    changed = [row['relative_path'] for row in results if row.get('status') in {'create', 'update'}]
    return {
        'phase_name': config.phase_name,
        'mode': config.mode,
        'run_id': safe_slug(config.checkpoint_label, fallback=config.phase_name),
        'transaction_id': transaction_id,
        'root_dir': str(config.root_dir),
        'export_dir': str(config.export_dir),
        'checkpoint_label': config.checkpoint_label,
        'requested_by': config.requested_by,
        'created_at': iso_now(),
        'touched_files': touched_files,
        'changed_files': changed,
        'notes': [
            'phase6 injector uses deterministic text patches and new planner foundation modules',
            'dry-run does not write repo files; apply captures backups before mutation',
        ],
        'tests': tests_result or {},
        'output_dir': str(output_dir),
    }


def _run_tests(config, output_dir: Path) -> dict[str, Any]:
    tests = [
        'tests/test_engine_golden.py',
        'tests/test_patch_pipeline.py',
        'tests/test_commands_patch_hardening.py',
        'tests/test_contracts.py',
    ]
    command = default_test_command(root_dir=config.root_dir, tests=tests)
    return run_subprocess_logged(command, cwd=config.root_dir, log_path=output_dir / 'phase_tests.log')


def _find_transaction_file(config, output_dir: Path) -> Path:
    if config.transaction_file is not None:
        return config.transaction_file
    return output_dir / 'last_transaction.json'


def _rollback(config) -> dict[str, Any]:
    output_dir = build_phase_output_dir(export_dir=config.export_dir, phase_name=config.phase_name, mode='rollback')
    ensure_dir(output_dir)
    transaction_file = _find_transaction_file(config, build_phase_output_dir(export_dir=config.export_dir, phase_name=config.phase_name, mode='apply'))
    if not transaction_file.exists():
        raise PhaseError(f'No existe transaction_file para rollback: {transaction_file}')
    transaction = json.loads(transaction_file.read_text(encoding='utf-8'))
    result = restore_from_manifest(transaction)
    payload = {
        'phase_name': config.phase_name,
        'mode': 'rollback',
        'transaction_file': str(transaction_file),
        'restored': result,
        'created_at': iso_now(),
    }
    write_json(output_dir / 'rollback_result.json', payload)
    write_text(output_dir / 'rollback_result.log', json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    emit_json_summary(payload, enabled=config.json_output)
    return payload


def main() -> int:
    args = parse_common_args(phase_name=PHASE_NAME)
    config = build_config_from_args(args, phase_name=PHASE_NAME)
    if config.mode == 'rollback':
        _rollback(config)
        return 0

    output_dir = build_phase_output_dir(export_dir=config.export_dir, phase_name=config.phase_name, mode=config.mode)
    ensure_dir(output_dir)
    plan = _build_plan()
    transaction_id = transaction_id_for(config.phase_name)
    touched_files = [item.relative_path for item in plan]
    write_json(output_dir / 'touched_files.json', touched_files)

    if config.mode == 'dry-run':
        results = _apply_plan(config.root_dir, plan, apply=False)
        tests_result = _run_tests(config, output_dir) if config.run_tests and not config.skip_smoke else None
        summary = _build_summary(config, output_dir, transaction_id, plan, results, tests_result)
        manifest = dict(summary)
        manifest['notes'] = list(summary.get('notes') or []) + ['dry-run only; repo files unchanged']
        write_json(output_dir / 'phase_manifest.json', manifest)
        write_text(output_dir / 'phase_manifest.md', render_manifest_md(manifest))
        write_json(output_dir / 'phase_summary.json', summary)
        write_text(output_dir / 'phase_apply.log', 'dry-run: no file mutations were applied\n')
        tx_file = output_dir / 'last_transaction.json'
        dry_tx = {
            'transaction_id': transaction_id,
            'phase_name': config.phase_name,
            'mode': config.mode,
            'created_at': iso_now(),
            'root_dir': str(config.root_dir),
            'checkpoint_label': config.checkpoint_label,
            'requested_by': config.requested_by,
            'backups': [],
            'touched_files': touched_files,
        }
        write_json(tx_file, dry_tx)
        write_rollback_instructions(output_dir / 'rollback_instructions.txt', transaction_file=tx_file, script_path=Path(__file__).resolve(), root_dir=config.root_dir)
        emit_json_summary(summary, enabled=config.json_output)
        return 0

    backups_dir = ensure_dir(output_dir / 'backups')
    abs_paths = _collect_abs_paths(config.root_dir, plan)
    backups = capture_backups(abs_paths, root_dir=config.root_dir, backups_dir=backups_dir)
    transaction = {
        'transaction_id': transaction_id,
        'phase_name': config.phase_name,
        'mode': config.mode,
        'created_at': iso_now(),
        'root_dir': str(config.root_dir),
        'export_dir': str(config.export_dir),
        'checkpoint_label': config.checkpoint_label,
        'requested_by': config.requested_by,
        'backups': backups,
        'touched_files': touched_files,
    }
    tx_file = output_dir / 'last_transaction.json'
    write_json(tx_file, transaction)
    write_rollback_instructions(output_dir / 'rollback_instructions.txt', transaction_file=tx_file, script_path=Path(__file__).resolve(), root_dir=config.root_dir)

    try:
        results = _apply_plan(config.root_dir, plan, apply=True)
        write_text(output_dir / 'phase_apply.log', json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        tests_result = _run_tests(config, output_dir) if config.run_tests and not config.skip_smoke else None
        if tests_result and int(tests_result.get('returncode', 0)) != 0:
            restored = restore_from_manifest(transaction)
            write_json(output_dir / 'rollback_result.json', restored)
            raise PhaseError('Tests fallaron despues del apply; se ejecutó rollback automático.')
        summary = _build_summary(config, output_dir, transaction_id, plan, results, tests_result)
        manifest = dict(summary)
        manifest['notes'] = list(summary.get('notes') or []) + ['apply completed successfully']
        write_json(output_dir / 'phase_manifest.json', manifest)
        write_text(output_dir / 'phase_manifest.md', render_manifest_md(manifest))
        write_json(output_dir / 'phase_summary.json', summary)
        emit_json_summary(summary, enabled=config.json_output)
        return 0
    except Exception as exc:
        restored = restore_from_manifest(transaction)
        failure = {
            'phase_name': config.phase_name,
            'mode': config.mode,
            'transaction_id': transaction_id,
            'error': f'{type(exc).__name__}: {exc}',
            'rollback': restored,
            'created_at': iso_now(),
        }
        write_json(output_dir / 'phase_summary.json', failure)
        write_text(output_dir / 'phase_apply.log', json.dumps(failure, indent=2, ensure_ascii=False) + '\n')
        emit_json_summary(failure, enabled=config.json_output)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

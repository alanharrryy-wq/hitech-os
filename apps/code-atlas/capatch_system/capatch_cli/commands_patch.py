#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from capatch_contracts.constants import BACKUP_DIR_NAME
from capatch_engine import PatchContext, load_operations_from_file, load_operations_from_stdin, run_patch_pipeline
from capatch_ops.base import CapatchError

from .exit_codes import (
    EXIT_BLOCKED,
    EXIT_DRY_RUN,
    EXIT_GENERAL_ERROR,
    EXIT_OK,
    EXIT_VERIFICATION_ROLLED_BACK,
    EXIT_VERIFICATION_ROLLBACK_FAILED,
)
from .patch_compat import emit_ok, emit_warn, print_self_test, run_smoke_tests, sanitize_checkpoint_label


def _default_external_export_dir(root_dir: Path) -> Path:
    override = os.environ.get('CAPATCH_AUDIT_EXPORT_DIR', '').strip()
    if override:
        return Path(override).expanduser()
    if os.name == 'nt':
        return Path(r'F:\descargasf')
    return root_dir / '.capatch' / 'external_audit'


def _safe_output_token(value: str) -> str:
    raw = str(value or '').strip() or 'capatch'
    safe = ''.join(char if char.isalnum() or char in {' ', '-', '_'} else ' ' for char in raw)
    return ' '.join(safe.split())[:64] or 'capatch'


def _default_run_label() -> str:
    return _safe_output_token(os.environ.get('CAPATCH_RUN_LABEL', 'capatch run1'))


def _capatch_timestamp() -> str:
    return datetime.now().strftime('%d%m %H%M%S')


def _ensure_unique_path(path_value: Path) -> Path:
    if not path_value.exists():
        return path_value
    stem = path_value.stem
    suffix = path_value.suffix
    parent = path_value.parent
    for index in range(2, 1000):
        candidate = parent / f'{stem} {index:02d}{suffix}'
        if not candidate.exists():
            return candidate
    return parent / f'{stem} {datetime.now().strftime("%H%M%S%f")}{suffix}'


def _ensure_run_workspace(args: Any, root_dir: Path) -> Path:
    existing = str(getattr(args, '_capatch_run_workspace', '') or '').strip()
    if existing:
        path_value = Path(existing).expanduser().resolve()
        path_value.mkdir(parents=True, exist_ok=True)
        return path_value
    export_dir = _default_external_export_dir(root_dir).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    run_name = f'{_default_run_label()} {_capatch_timestamp()}'
    run_dir = _ensure_unique_path(export_dir / '_capatch_runtime' / run_name).resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    setattr(args, '_capatch_run_name', run_dir.name)
    setattr(args, '_capatch_run_workspace', str(run_dir))
    setattr(args, '_capatch_export_dir', str(export_dir))
    return run_dir


def _copy_file_best_effort(source: Path, destination: Path) -> dict[str, Any]:
    row = {'source': str(source), 'destination': str(destination), 'ok': False, 'reason': ''}
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        row['ok'] = True
    except Exception as exc:
        row['reason'] = f'{type(exc).__name__}: {exc}'
    return row


def _copy_target_file_snapshot(root_dir: Path, relative_path: str, destination_root: Path) -> dict[str, Any]:
    normalized = _normalize_target_path(relative_path, root_dir=root_dir) or str(relative_path)
    candidate = Path(normalized)
    source = candidate if candidate.is_absolute() else (root_dir / candidate).resolve()
    safe_relative = normalized.replace('\\', '/')
    if Path(safe_relative).is_absolute() or safe_relative.startswith('..'):
        safe_relative = safe_relative.replace(':', '').replace('/', '__')
    destination = destination_root / safe_relative
    row = {'relative_path': normalized, 'source': str(source), 'destination': str(destination), 'exists': source.exists(), 'copied': False}
    try:
        if source.exists() and source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            row['copied'] = True
        else:
            marker = destination.with_suffix(destination.suffix + '.missing.txt') if destination.suffix else destination.with_name(destination.name + '.missing.txt')
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(f'{normalized} missing at export time\n', encoding='utf-8', newline='')
            row['destination'] = str(marker)
    except Exception as exc:
        row['error'] = f'{type(exc).__name__}: {exc}'
    return row


def _zip_directory(source_dir: Path, zip_path: Path) -> Path:
    zip_path = _ensure_unique_path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path_value in sorted(source_dir.rglob('*')):
            if path_value.is_file():
                zf.write(path_value, path_value.relative_to(source_dir).as_posix())
    return zip_path


def _cleanup_run_workspace(run_dir: Path) -> None:
    if os.environ.get('CAPATCH_KEEP_RUN_DIR', '').strip() in {'1', 'true', 'TRUE', 'yes'}:
        return
    try:
        shutil.rmtree(run_dir, ignore_errors=True)
        parent = run_dir.parent
        if parent.name == '_capatch_runtime' and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    except Exception:
        return


def _normalize_target_path(path_value: Any, *, root_dir: Path) -> str | None:
    raw = str(path_value or '').strip()
    if not raw:
        return None
    parsed = Path(raw)
    if parsed.is_absolute():
        try:
            return parsed.resolve().relative_to(root_dir.resolve()).as_posix()
        except Exception:
            return str(parsed.resolve())
    return parsed.as_posix()


def _iter_operation_paths(operations: list[Any]) -> list[str]:
    rows: list[str] = []
    for operation in list(operations or []):
        file_value = str(getattr(operation, 'file', '') or '').strip()
        if file_value:
            rows.append(file_value)
        payload = getattr(operation, 'payload', None)
        if isinstance(payload, dict):
            nested = payload.get('operations')
            if isinstance(nested, list) and nested:
                rows.extend(_iter_operation_paths(list(nested)))
    return rows


def _collect_target_files(pipeline: Any, operations: list[Any], *, root_dir: Path) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    def _append(path_value: Any) -> None:
        normalized = _normalize_target_path(path_value, root_dir=root_dir)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        ordered.append(normalized)

    preflight = getattr(pipeline, 'preflight_report', None) if pipeline is not None else None
    for item in list(getattr(preflight, 'target_files', []) or []):
        _append(item)
    run_record = getattr(pipeline, 'run_record', None) if pipeline is not None else None
    for item in list(getattr(run_record, 'target_files', []) or []):
        _append(item)
    preview_payload = getattr(pipeline, 'preview_payload', None) if pipeline is not None else None
    if isinstance(preview_payload, dict):
        preview_map = preview_payload.get('preview_content_by_target')
        if isinstance(preview_map, dict):
            for key in preview_map.keys():
                _append(key)
    for row in list(getattr(pipeline, 'operation_results', []) or []):
        if isinstance(row, dict):
            _append(row.get('target_path'))
        else:
            _append(getattr(row, 'target_path', None))
    for item in _iter_operation_paths(list(operations or [])):
        _append(item)
    return ordered


def _looks_binary(raw: bytes) -> bool:
    if not raw:
        return False
    sample = raw[:8192]
    if b'\x00' in sample:
        return True
    text_bytes = set(range(32, 127)) | {9, 10, 13}
    non_text = sum(1 for value in sample if value not in text_bytes)
    return (non_text / max(1, len(sample))) > 0.35


def _render_target_snapshot(root_dir: Path, relative_path: str) -> str:
    normalized = _normalize_target_path(relative_path, root_dir=root_dir) or str(relative_path)
    candidate = Path(normalized)
    file_path = candidate if candidate.is_absolute() else (root_dir / candidate).resolve()
    title = f'===== FILE: {normalized} ====='
    if not file_path.exists():
        return '\n'.join([title, 'file does not exist at export time', ''])
    if not file_path.is_file():
        return '\n'.join([title, 'path is not a regular file at export time', ''])
    try:
        raw = file_path.read_bytes()
    except Exception as exc:
        return '\n'.join([title, f'could not read file at export time: {type(exc).__name__}: {exc}', ''])
    if _looks_binary(raw):
        return '\n'.join([title, 'binary-looking content detected', ''])
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return '\n'.join([title, 'binary-looking content detected (non-utf8)', ''])
    return '\n'.join([title, text, f'===== END FILE: {normalized} =====', ''])


def _operation_result_row_text(row: Any, index: int) -> str:
    if isinstance(row, dict):
        label = row.get('operation_label')
        status = row.get('patch_status')
        target = row.get('target_path')
        message = row.get('message')
    else:
        label = getattr(row, 'operation_label', None)
        status = getattr(row, 'patch_status', None)
        target = getattr(row, 'target_path', None)
        message = getattr(row, 'message', None)
    return f"{index}. label={label} status={status} target={target} message={message}"


def _build_external_log_text(
    args: Any,
    pipeline: Any,
    operations: list[Any],
    *,
    reason_override: str | None = None,
    target_files: list[str] | None = None,
) -> str:
    root_dir = Path(_resolved_root_dir(args)).resolve()
    outcome = str(getattr(pipeline, 'outcome', 'error')) if pipeline is not None else 'error'
    run_record = getattr(pipeline, 'run_record', None) if pipeline is not None else None
    run_id = getattr(run_record, 'run_id', None) if run_record is not None else None
    reason = str(reason_override or (getattr(pipeline, 'error', None) if pipeline is not None else None) or outcome)
    targets = list(target_files or _collect_target_files(pipeline, operations, root_dir=root_dir))
    lines = [
        'capatch external audit log',
        f"generated_at={datetime.now().isoformat(timespec='seconds')}",
        f'outcome={outcome}',
        f'reason={reason}',
        f'run_id={run_id}',
        f"dry_run={bool(getattr(args, 'dry_run', False))}",
        f'root_dir={root_dir}',
        '',
        'target_files:',
    ]
    if targets:
        lines.extend([f'- {item}' for item in targets])
    else:
        lines.append('- (none)')

    lines.extend(['', 'preview_diff:'])
    preview_payload = getattr(pipeline, 'preview_payload', {}) if pipeline is not None else {}
    diff_summary = list(preview_payload.get('diff_summary', []) if isinstance(preview_payload, dict) else [])
    if diff_summary:
        lines.extend([f'- {item}' for item in diff_summary])
    else:
        lines.append('- (none)')

    lines.extend(['', 'operation_results:'])
    operation_results = list(getattr(pipeline, 'operation_results', []) or []) if pipeline is not None else []
    if operation_results:
        lines.extend([_operation_result_row_text(row, index + 1) for index, row in enumerate(operation_results)])
    else:
        lines.append('- (none)')

    lines.extend(['', 'verifier_results:'])
    required = list(getattr(pipeline, 'required_verifiers', []) or []) if pipeline is not None else []
    lines.append(f"required={','.join(required) if required else 'none'}")
    verifier_results = list(getattr(pipeline, 'verifier_results', []) or []) if pipeline is not None else []
    if verifier_results:
        for row in verifier_results:
            lines.append(f"- verifier_id={row.get('verifier_id')} ok={row.get('ok')} title={row.get('title')} detail={row.get('detail')}")
    else:
        lines.append('- (none)')

    rollback_decision = getattr(pipeline, 'rollback_decision', None) if pipeline is not None else None
    rollback_event = getattr(pipeline, 'rollback_event', None) if pipeline is not None else None
    lines.extend(
        [
            '',
            f'rollback_decision={json.dumps(rollback_decision, ensure_ascii=False, sort_keys=True)}' if rollback_decision else 'rollback_decision=null',
            f'rollback_event={json.dumps(rollback_event, ensure_ascii=False, sort_keys=True)}' if rollback_event else 'rollback_event=null',
            f'error={getattr(pipeline, "error", None) if pipeline is not None else reason}',
            '',
        ]
    )
    return '\n'.join(lines)


def _export_attempt_artifacts(
    args: Any,
    pipeline: Any,
    operations: list[Any],
    *,
    reason_override: str | None = None,
) -> dict[str, Any]:
    # CAPATCH_READY1_ENRICHED_EXPORT
    import zipfile
    from capatch_runtime.run_dir_policy import keep_run_dir_default, keep_run_dir_reason
    from capatch_plan.patch_plan import build_patch_plan, render_patch_plan_md
    root_dir = Path(_resolved_root_dir(args)).resolve()
    export_dir = _default_external_export_dir(root_dir).resolve()
    outcome = str(getattr(pipeline, 'outcome', '') or '') if pipeline is not None else ''
    status = 'result' if outcome in {'verified','applied-no-verifiers','dry-run'} or pipeline is None else 'fail'
    run_dir = export_dir / '_capatch_runtime' / f"capatch patch {datetime.now().strftime('%d%m %H%M%S')} {status}"
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
        targets = _collect_target_files(pipeline, operations, root_dir=root_dir)
        (run_dir / 'capatch_log.txt').write_text(_build_external_log_text(args, pipeline, operations, reason_override=reason_override, target_files=targets) + '\n', encoding='utf-8', newline='')
        (run_dir / 'capatch_sources.txt').write_text('\n'.join([_render_target_snapshot(root_dir, x) for x in targets]) + '\n', encoding='utf-8', newline='')
        plan = build_patch_plan(root_dir=root_dir, target_files=targets, operations=operations, pipeline=pipeline)
        (run_dir / 'PATCH_PLAN.md').write_text(render_patch_plan_md(plan), encoding='utf-8', newline='')
        (run_dir / 'PATCH_PLAN.json').write_text(json.dumps(plan, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='')
        (run_dir / 'RUN_SUMMARY.json').write_text(json.dumps({'status':status,'outcome':outcome,'root_dir':str(root_dir),'target_files':targets,'keep_run_dir':keep_run_dir_default(),'keep_run_dir_reason':keep_run_dir_reason()}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='')
        zip_path = export_dir / f'{run_dir.name}.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for item in sorted(run_dir.rglob('*')):
                if item.is_file(): zf.write(item, item.relative_to(run_dir).as_posix())
        if not keep_run_dir_default(): shutil.rmtree(run_dir, ignore_errors=True)
        return {'export_dir': str(export_dir), 'run_dir': str(run_dir), 'bundle_zip': str(zip_path), 'log_path': str(run_dir / 'capatch_log.txt'), 'sources_path': str(run_dir / 'capatch_sources.txt')}
    except Exception as exc:
        return {'export_dir': str(export_dir), 'log_path': None, 'sources_path': None, 'export_error': f'{type(exc).__name__}: {exc}'}

def _print_export_paths(paths: dict[str, Any]) -> None:
    error = str(paths.get('export_error') or '').strip()
    if error:
        print(f'[WARN] external audit export failed: {error}')
        return
    print(f"[AUDIT] export_dir={paths.get('export_dir')}")
    print(f"[AUDIT] log_path={paths.get('log_path')}")
    print(f"[AUDIT] sources_path={paths.get('sources_path')}")
    if paths.get('zip_path'):
        print(f"[AUDIT] zip_path={paths.get('zip_path')}")


def _print_preflight_report(report: Any) -> None:
    if report.path_violations:
        print('[ERROR] path violations:')
        for row in report.path_violations:
            print(f'  - {row}')
    if report.conflicts:
        print('[ERROR] conflicts:')
        for row in report.conflicts:
            print(f'  - {row}')
    if report.schema_violations:
        print('[ERROR] schema violations:')
        for row in report.schema_violations:
            print(f'  - {row}')


def _print_preview(preview_payload: dict[str, Any]) -> None:
    for line in preview_payload.get('diff_summary', []):
        print(f'[PREVIEW] {line}')


def _print_apply_summary(results: list[Any]) -> None:
    counts: dict[str, int] = {}
    for row in results:
        status = getattr(row, 'patch_status', None)
        label = getattr(row, 'operation_label', 'op')
        target = getattr(row, 'target_path', '')
        counts[str(status)] = counts.get(str(status), 0) + 1
        print(f'[PATCH] {label} :: {status} :: {target}')
    if counts:
        print('[SUMMARY] ' + ', '.join(f'{key}={value}' for key, value in sorted(counts.items())))


def _print_verifier_summary(required_verifiers: list[str], verifier_results: list[dict[str, Any]]) -> None:
    if required_verifiers:
        print('[VERIFY] required=' + ', '.join(required_verifiers))
    else:
        print('[VERIFY] required=none')
    for row in verifier_results:
        print(f"[VERIFY] {row.get('verifier_id')} :: ok={row.get('ok')} :: {row.get('title')}")




def _map_outcome_to_exit_code(outcome: str) -> int:
    mapping = {
        'verified': EXIT_OK,
        'applied-no-verifiers': EXIT_OK,
        'dry-run': EXIT_DRY_RUN,
        'blocked': EXIT_BLOCKED,
        'apply-failed': EXIT_GENERAL_ERROR,
        'verification-failed': EXIT_GENERAL_ERROR,
        'rolled-back': EXIT_VERIFICATION_ROLLED_BACK,
        'rollback-failed': EXIT_VERIFICATION_ROLLBACK_FAILED,
    }
    return int(mapping.get(str(outcome or ''), EXIT_GENERAL_ERROR))


def _resolved_root_dir(args: Any) -> str:
    return str(Path(getattr(args, 'root_dir')).expanduser().resolve())


def _status_from_outcome(outcome: str) -> str:
    normalized = str(outcome or '')
    if normalized in {'verified', 'applied-no-verifiers', 'dry-run'}:
        return 'ok'
    if normalized == 'rolled-back':
        return 'rolled_back'
    return 'failed'


def _checkpoint_id_from_pipeline(pipeline: Any) -> str | None:
    run_record = getattr(pipeline, 'run_record', None)
    rollback_target = getattr(run_record, 'rollback_target', None) if run_record is not None else None
    if rollback_target:
        return Path(str(rollback_target)).name
    rollback_event = getattr(pipeline, 'rollback_event', None)
    if isinstance(rollback_event, dict):
        checkpoint_id = rollback_event.get('checkpoint_id')
        if checkpoint_id is not None:
            return str(checkpoint_id)
    return None


def _emit_json_summary(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def _patch_json_payload(args: Any, pipeline: Any, *, reason_override: str | None = None) -> dict[str, Any]:
    outcome = str(getattr(pipeline, 'outcome', 'failed'))
    run_record = getattr(pipeline, 'run_record', None)
    payload = {
        'status': _status_from_outcome(outcome),
        'reason': str(reason_override or getattr(pipeline, 'error', None) or outcome),
        'outcome': outcome,
        'dry_run': bool(getattr(args, 'dry_run', False)),
        'root_dir': _resolved_root_dir(args),
        'checkpoint_id': _checkpoint_id_from_pipeline(pipeline),
        'run_id': getattr(run_record, 'run_id', None) if run_record is not None else None,
        'patch_status': getattr(run_record, 'patch_status', None) if run_record is not None else None,
        'system_status': getattr(run_record, 'system_status', None) if run_record is not None else None,
        'verification_outcome': getattr(run_record, 'verification_outcome', None) if run_record is not None else None,
        'rollback_applied': bool(getattr(pipeline, 'rollback_event', None)),
        'selected_strategy': (getattr(pipeline, 'strategy_decision', None) or {}).get('selected_strategy'),
    }
    return payload


def _non_patch_json_payload(args: Any, *, operation: str, returncode: int, reason: str) -> dict[str, Any]:
    payload = {
        'status': 'ok' if int(returncode) == 0 else 'failed',
        'reason': str(reason),
        'outcome': str(operation),
        'dry_run': bool(getattr(args, 'dry_run', False)),
        'root_dir': _resolved_root_dir(args),
        'checkpoint_id': None,
        'verification_outcome': None,
        'returncode': int(returncode),
    }
    return payload


def handle(args: Any, parser: Any) -> int | None:
    json_output = bool(getattr(args, 'json_output', False))
    operations: list[Any] = []
    pipeline: Any | None = None
    if getattr(args, 'self_test', False):
        returncode = int(print_self_test())
        audit_refs = _export_attempt_artifacts(args, None, operations, reason_override='self-test completed')
        _print_export_paths(audit_refs)
        if json_output:
            payload = _non_patch_json_payload(args, operation='self-test', returncode=returncode, reason='self-test completed')
            payload['external_audit_refs'] = audit_refs
            _emit_json_summary(payload)
        return returncode
    if getattr(args, 'smoke_test', False):
        returncode = int(run_smoke_tests())
        audit_refs = _export_attempt_artifacts(args, None, operations, reason_override='smoke-test completed')
        _print_export_paths(audit_refs)
        if json_output:
            payload = _non_patch_json_payload(args, operation='smoke-test', returncode=returncode, reason='smoke-test completed')
            payload['external_audit_refs'] = audit_refs
            _emit_json_summary(payload)
        return returncode

    if not args.ops_file and not args.ops_stdin:
        return None

    root_dir = Path(args.root_dir).expanduser().resolve()
    run_workspace = _ensure_run_workspace(args, root_dir)
    backup_dir = run_workspace / 'backups_before_changes'
    checkpoint_label = sanitize_checkpoint_label(args.checkpoint_label)
    checkpoint_dir = backup_dir / checkpoint_label
    strategy_hint = None if str(getattr(args, 'strategy', 'auto') or 'auto') == 'auto' else str(getattr(args, 'strategy'))
    if bool(getattr(args, 'probe_only', False)):
        strategy_hint = 'probe-only'
    ctx = PatchContext(
        root_dir=root_dir,
        backup_dir=backup_dir,
        checkpoint_dir=checkpoint_dir,
        dry_run=bool(args.dry_run),
        auto_support=not bool(args.no_auto_support),
        requested_by='capatch-cli',
        invocation_mode='patch-run',
        strategy_hint=strategy_hint,
        allow_advisory_strategy=bool(getattr(args, 'allow_advisory_strategy', False)),
        force_dry_run_on_high_risk=bool(getattr(args, 'force_dry_run_on_high_risk', False)),
        planner_mode=str(getattr(args, 'planner_mode', 'off') or 'off'),
    )

    try:
        operations = (
            load_operations_from_file(Path(args.ops_file).expanduser().resolve())
            if args.ops_file
            else load_operations_from_stdin()
        )
        pipeline = run_patch_pipeline(ctx, operations)
        strategy = dict(getattr(pipeline, 'strategy_decision', None) or {})
        if strategy:
            selected = strategy.get('selected_strategy')
            advisory = strategy.get('advisory_only')
            print(f"[STRATEGY] selected={selected} advisory_only={advisory} score={strategy.get('selected_score')}")
            for reason in list(strategy.get('reasons') or []):
                print(f"[STRATEGY] reason={reason}")
        _print_preflight_report(pipeline.preflight_report)
        _print_preview(pipeline.preview_payload)
        _print_apply_summary(pipeline.operation_results)
        _print_verifier_summary(pipeline.required_verifiers, pipeline.verifier_results)

        if pipeline.rollback_decision.get('should_rollback'):
            print(f"[ROLLBACK] auto={pipeline.rollback_decision.get('should_rollback')} reason={pipeline.rollback_decision.get('rollback_reason')}")
        if pipeline.rollback_event:
            print(f"[ROLLBACK] status={pipeline.rollback_event.get('status')} checkpoint={pipeline.rollback_event.get('checkpoint_id')}")
        if pipeline.run_record is not None:
            print(
                f"[RUN] run_id={pipeline.run_record.run_id} patch_status={pipeline.run_record.patch_status} system_status={pipeline.run_record.system_status}"
            )
        if pipeline.outcome == 'blocked' and strategy.get('selected_strategy') == 'probe-only':
            emit_warn('Selector dejÃ³ el cambio en probe-only. Se requiere --dry-run o una estrategia explÃ­cita mÃ¡s segura.')
        elif pipeline.outcome == 'dry-run':
            emit_ok('Preview listo. No se escribieron cambios.')
        elif pipeline.outcome == 'verified':
            emit_ok('Patch aplicado y verificado.')
        elif pipeline.outcome == 'applied-no-verifiers':
            emit_warn('Patch aplicado, pero no hubo verifiers obligatorios para confirmar salud final.')
        elif pipeline.outcome == 'rolled-back':
            emit_warn('Patch aplicado, verificaciÃ³n fallÃ³ y se hizo auto rollback.')
        elif pipeline.outcome == 'rollback-failed':
            emit_warn('Patch aplicado, verificaciÃ³n fallÃ³ y el auto rollback tambiÃ©n fallÃ³.')
        returncode = _map_outcome_to_exit_code(pipeline.outcome)
        audit_refs = _export_attempt_artifacts(args, pipeline, operations)
        _print_export_paths(audit_refs)
        if json_output:
            payload = _patch_json_payload(args, pipeline)
            payload['external_audit_refs'] = audit_refs
            _emit_json_summary(payload)
        return returncode
    except CapatchError as exc:
        print(f'[ERROR] {exc}', file=sys.stderr)
        audit_refs = _export_attempt_artifacts(args, pipeline, operations, reason_override=str(exc))
        _print_export_paths(audit_refs)
        if json_output:
            payload = {
                'status': 'failed',
                'reason': str(exc),
                'outcome': 'error',
                'dry_run': bool(getattr(args, 'dry_run', False)),
                'root_dir': _resolved_root_dir(args),
                'checkpoint_id': None,
                'verification_outcome': None,
                'external_audit_refs': audit_refs,
            }
            _emit_json_summary(payload)
        return EXIT_GENERAL_ERROR
    except json.JSONDecodeError as exc:
        print(f'[ERROR] JSON invalido: {exc}', file=sys.stderr)
        reason = f'JSON invalido: {exc}'
        audit_refs = _export_attempt_artifacts(args, pipeline, operations, reason_override=reason)
        _print_export_paths(audit_refs)
        if json_output:
            payload = {
                'status': 'failed',
                'reason': reason,
                'outcome': 'error',
                'dry_run': bool(getattr(args, 'dry_run', False)),
                'root_dir': _resolved_root_dir(args),
                'checkpoint_id': None,
                'verification_outcome': None,
                'external_audit_refs': audit_refs,
            }
            _emit_json_summary(payload)
        return EXIT_GENERAL_ERROR
    except Exception as exc:
        print(f'[ERROR] Error inesperado: {exc}', file=sys.stderr)
        reason = f'Error inesperado: {exc}'
        audit_refs = _export_attempt_artifacts(args, pipeline, operations, reason_override=reason)
        _print_export_paths(audit_refs)
        if json_output:
            payload = {
                'status': 'failed',
                'reason': reason,
                'outcome': 'error',
                'dry_run': bool(getattr(args, 'dry_run', False)),
                'root_dir': _resolved_root_dir(args),
                'checkpoint_id': None,
                'verification_outcome': None,
                'external_audit_refs': audit_refs,
            }
            _emit_json_summary(payload)
        return EXIT_GENERAL_ERROR

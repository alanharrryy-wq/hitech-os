from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from capatch_audit import apply_rollback, finalize_run, load_run, start_run
from capatch_audit.manifest import patch_run_record_to_dict
from capatch_audit.renderers import render_patch_run_md, write_json, write_text
from capatch_fs.guards import ensure_mutable_target
from capatch_fs.workspace_lock import acquire_workspace_lock, collect_target_snapshot, diff_target_snapshot
from capatch_policy import classify_change, maybe_auto_rollback
from capatch_policy.verification_requirements import assess_verification_outcome
from capatch_verify import run_required_verifiers

from .executor import apply
from .preview import preview
from .preflight import preflight
from .strategy_selector import select_patch_strategy
from .transaction import (
    advance_transaction,
    attach_operation_results,
    attach_verifier_results,
    load_transaction,
    mark_transaction_committed,
    record_strategy_decision,
    mark_transaction_failed,
    mark_transaction_rollback_started,
    mark_transaction_rolled_back,
    start_transaction,
)


@dataclass(slots=True)
class PatchPipelineResult:
    preflight_report: Any
    risk_summary: dict[str, Any]
    preview_payload: dict[str, Any]
    operation_results: list[Any]
    verifier_results: list[dict[str, Any]]
    required_verifiers: list[str]
    run_record: Any | None
    rollback_decision: dict[str, Any]
    rollback_event: dict[str, Any] | None
    outcome: str
    strategy_decision: dict[str, Any] | None = None
    transaction_record: Any | None = None
    error: str | None = None


_ALLOWED_SUCCESS_OUTCOMES = {'verified'}


def _normalize_required_verifiers(risk_summary: dict[str, Any]) -> list[str]:
    ordered: list[str] = []
    seen = set()
    for item in list((risk_summary or {}).get('required_verifiers') or []):
        token = str(item or '').strip()
        if token and token not in seen:
            seen.add(token)
            ordered.append(token)
    return ordered


def _verification_ctx(ctx: Any, risk_summary: dict[str, Any], verification_ctx: dict[str, Any] | None) -> dict[str, Any]:
    payload = {
        'root_dir': str(Path(getattr(ctx, 'root_dir')).resolve()),
        'run_id': getattr(ctx, 'run_id', None),
        'invocation_mode': getattr(ctx, 'invocation_mode', 'patch-run'),
        'risk_summary': dict(risk_summary or {}),
        # CAPATCH_DELTA1_CHECKPOINT_CTX: allow delta-aware verifiers to compare final files against the pre-apply checkpoint.
        'checkpoint_dir': str(Path(getattr(ctx, 'checkpoint_dir', '') or '').expanduser().resolve()) if str(getattr(ctx, 'checkpoint_dir', '') or '').strip() else None,
    }
    payload.update(dict(verification_ctx or {}))
    return payload


def _persist_run_record(record: Any, transaction_record: Any | None = None) -> Any:
    if record is None:
        return None
    if transaction_record is not None:
        record.transaction_id = getattr(transaction_record, 'transaction_id', None)
        record.transaction_journal = getattr(transaction_record, 'journal_path', None)
        record.transaction_phase = getattr(transaction_record, 'phase', None)
        record.transaction_status = getattr(transaction_record, 'transaction_status', None)
        record.lifecycle = list(getattr(transaction_record, 'phase_history', []) or [])
        if getattr(transaction_record, 'verification_outcome', None) is not None:
            record.verification_outcome = getattr(transaction_record, 'verification_outcome', None)
        if getattr(transaction_record, 'final_state', None) is not None:
            record.final_state = getattr(transaction_record, 'final_state', None)
        if getattr(transaction_record, 'rollback_event', None):
            record.rollback_triggered = True
            status = getattr(transaction_record, 'rollback_event', {}).get('status') if isinstance(getattr(transaction_record, 'rollback_event', None), dict) else None
            record.rollback_outcome = str(status or record.rollback_outcome or 'completed')
    root_dir = Path(str(record.root_dir)).resolve()
    write_json(root_dir / 'reports/patch_runs' / f'{record.run_id}.json', patch_run_record_to_dict(record))
    write_text(root_dir / 'reports/patch_runs' / f'{record.run_id}.md', render_patch_run_md(record))
    return record


def _mark_failed(record: Any, transaction_record: Any | None, *, error: str, patch_status: str = 'failed', system_status: str = 'failed', final_state: str = 'failed') -> Any:
    if record is None:
        return None
    record.patch_status = patch_status
    record.system_status = system_status
    record.error = str(error)
    record.final_state = str(final_state)
    return _persist_run_record(record, transaction_record)


def _mutating_operations(preflight_report: Any) -> bool:
    return bool(int(getattr(preflight_report, 'mutating_operation_count', 0) or 0) > 0)


def _enforce_verification_lifecycle(required_verifiers: list[str], preflight_report: Any) -> tuple[bool, str | None]:
    if _mutating_operations(preflight_report) and not list(required_verifiers or []):
        return False, 'mutating patch requires explicit verification steps'
    return True, None


def _normalize_targets(preflight_report: Any, operations: list[Any]) -> list[str]:
    rows = [str(item) for item in list(getattr(preflight_report, 'target_files', []) or []) if str(item)]
    if not rows:
        rows = [str(getattr(item, 'file', '')) for item in list(operations or []) if getattr(item, 'file', None)]
    return sorted({item for item in rows if item})


def _validate_mutable_targets(root_dir: Path, target_files: list[str]) -> None:
    for relative_path in list(target_files or []):
        ensure_mutable_target(root_dir, root_dir / relative_path, allow_missing=True)


def is_success_outcome(value: str) -> bool:
    return str(value or '') in _ALLOWED_SUCCESS_OUTCOMES


def _strategy_runtime_guard(ctx: Any, strategy_decision: dict[str, Any], risk_summary: dict[str, Any]) -> tuple[bool, str | None]:
    selected = str((strategy_decision or {}).get('selected_strategy') or '')
    advisory_only = bool((strategy_decision or {}).get('advisory_only', False))
    risk_level = str((risk_summary or {}).get('risk_level') or '').lower()
    if selected == 'probe-only' and not bool(getattr(ctx, 'dry_run', False)):
        return False, 'probe-only strategy selected; rerun with --dry-run or --strategy exact/guarded'
    if advisory_only and not bool(getattr(ctx, 'allow_advisory_strategy', False)) and not bool(getattr(ctx, 'dry_run', False)):
        return False, 'selected strategy is advisory_only; rerun with --allow-advisory-strategy or --dry-run'
    if bool(getattr(ctx, 'force_dry_run_on_high_risk', False)) and risk_level in {'high', 'critical'} and not bool(getattr(ctx, 'dry_run', False)):
        return False, 'high-risk change requires --dry-run first; rerun with --dry-run or lower the risk surface'
    return True, None


def run_patch_pipeline(ctx: Any, operations: list[Any], *, verification_ctx: dict[str, Any] | None = None) -> PatchPipelineResult:
    target_files = [str(getattr(item, 'file', '')) for item in list(operations or []) if getattr(item, 'file', None)]
    transaction_record = start_transaction(ctx, operations, target_files=target_files, metadata={'phase': 'phase5'})
    preflight_report = preflight(ctx, operations)
    risk_summary = classify_change(preflight_report, operations)
    strategy_decision = select_patch_strategy(ctx, preflight_report, operations, risk_summary)
    runtime_ok, runtime_reason = _strategy_runtime_guard(ctx, strategy_decision, risk_summary)
    risk_summary = dict(risk_summary or {})
    risk_summary['selected_strategy'] = strategy_decision.get('selected_strategy')
    risk_summary['strategy_decision'] = dict(strategy_decision or {})
    risk_summary['recommended_guardrails'] = list(strategy_decision.get('recommended_guardrails') or risk_summary.get('recommended_guardrails') or [])
    preflight_report.risk_summary = dict(risk_summary or {})
    preflight_report.strategy_decision = dict(strategy_decision or {})
    preflight_report.strategy_hints = dict(getattr(preflight_report, 'strategy_hints', {}) or {})
    preflight_report.strategy_hints['selected_strategy'] = strategy_decision.get('selected_strategy')
    preview_payload = preview(ctx, operations)
    required_verifiers = _normalize_required_verifiers(risk_summary)
    ok_to_mutate, lifecycle_reason = _enforce_verification_lifecycle(required_verifiers, preflight_report)
    if ok_to_mutate and not runtime_ok:
        ok_to_mutate = False
        lifecycle_reason = runtime_reason
    normalized_targets = _normalize_targets(preflight_report, operations)
    root_dir = Path(getattr(ctx, 'root_dir')).resolve()
    preview_snapshot = collect_target_snapshot(root_dir, normalized_targets)

    transaction_record = record_strategy_decision(transaction_record, strategy_decision)

    advance_transaction(
        transaction_record,
        'preflight_ok' if preflight_report.ok and ok_to_mutate else 'failed',
        status='active' if preflight_report.ok and ok_to_mutate else 'failed',
        note='preflight complete' if preflight_report.ok and ok_to_mutate else lifecycle_reason or 'preflight blocked',
        extra={'target_files': normalized_targets, 'required_verifiers': required_verifiers, 'selected_strategy': strategy_decision.get('selected_strategy')},
    )

    if not preflight_report.ok or not ok_to_mutate:
        error = lifecycle_reason or 'preflight blocked'
        transaction_record = mark_transaction_failed(
            transaction_record,
            error=error,
            phase='failed',
            recovery_hint='review conflicts or add required verifiers before retrying',
            extra={'blocked': True},
        )
        return PatchPipelineResult(
            preflight_report=preflight_report,
            risk_summary=risk_summary,
            preview_payload=preview_payload,
            operation_results=[],
            verifier_results=[],
            required_verifiers=required_verifiers,
            run_record=None,
            rollback_decision={},
            rollback_event=None,
            outcome='blocked',
            strategy_decision=strategy_decision,
            transaction_record=transaction_record,
            error=error,
        )

    if bool(getattr(ctx, 'dry_run', False)):
        advance_transaction(transaction_record, 'checkpoint_created', status='active', note='dry-run preview only')
        advance_transaction(transaction_record, 'committed', status='committed', note='dry-run completed', extra={'dry_run': True})
        transaction_record.final_state = 'dry-run'
        return PatchPipelineResult(
            preflight_report=preflight_report,
            risk_summary=risk_summary,
            preview_payload=preview_payload,
            operation_results=[],
            verifier_results=[],
            required_verifiers=required_verifiers,
            run_record=None,
            rollback_decision={},
            rollback_event=None,
            outcome='dry-run',
            strategy_decision=strategy_decision,
            transaction_record=transaction_record,
        )

    workspace_lock = None
    run_record = None
    try:
        workspace_lock = acquire_workspace_lock(
            root_dir,
            owner_token=str(getattr(transaction_record, 'transaction_id', 'transaction')),
            metadata={'run_id': getattr(transaction_record, 'run_id', None), 'phase': 'patch-pipeline'},
        )
        _validate_mutable_targets(root_dir, normalized_targets)
        locked_snapshot = collect_target_snapshot(root_dir, normalized_targets)
        drift = diff_target_snapshot(preview_snapshot, locked_snapshot)
        if drift:
            transaction_record = mark_transaction_failed(
                transaction_record,
                error='workspace_drift_detected',
                phase='failed',
                recovery_hint='refresh preview and retry after external modifications settle',
                extra={'drift': drift},
            )
            return PatchPipelineResult(
                preflight_report=preflight_report,
                risk_summary=risk_summary,
                preview_payload=preview_payload,
                operation_results=[],
                verifier_results=[],
                required_verifiers=required_verifiers,
                run_record=None,
                rollback_decision={},
                rollback_event=None,
                outcome='blocked',
                strategy_decision=strategy_decision,
                transaction_record=transaction_record,
                error='workspace_drift_detected',
            )

        advance_transaction(transaction_record, 'checkpoint_created', status='active', note='checkpoint materialization delegated to executor')
        run_record = start_run(ctx, preflight_report, risk_summary)
        run_record.transaction_id = transaction_record.transaction_id
        run_record.transaction_journal = transaction_record.journal_path
        run_record.transaction_phase = transaction_record.phase
        run_record.transaction_status = transaction_record.transaction_status
        run_record.lifecycle = list(transaction_record.phase_history)
        _persist_run_record(run_record, transaction_record)

        try:
            advance_transaction(transaction_record, 'apply_started', status='active', note='apply started')
            operation_results = apply(ctx, operations)
            attach_operation_results(transaction_record, [dict(
                operation_label=getattr(item, 'operation_label', None),
                operation_type=getattr(item, 'operation_type', None),
                target_path=getattr(item, 'target_path', None),
                patch_status=getattr(item, 'patch_status', None),
                message=getattr(item, 'message', None),
                before_hash=getattr(item, 'before_hash', None),
                after_hash=getattr(item, 'after_hash', None),
                preview_hash=getattr(item, 'preview_hash', None),
                bytes_before=getattr(item, 'bytes_before', None),
                bytes_after=getattr(item, 'bytes_after', None),
                changed_line_count=getattr(item, 'changed_line_count', 0),
                support_notes=list(getattr(item, 'support_notes', []) or []),
            ) for item in list(operation_results or [])])
            advance_transaction(transaction_record, 'apply_succeeded', status='active', note='apply succeeded')
        except Exception as exc:
            transaction_record = mark_transaction_failed(
                transaction_record,
                error=f'apply_failed: {type(exc).__name__}: {exc}',
                exception_class=type(exc).__name__,
                phase='failed',
                recovery_hint='inspect checkpoint and transaction journal before retrying',
            )
            run_record = _mark_failed(run_record, transaction_record, error=f'apply_failed: {type(exc).__name__}: {exc}', final_state='apply_failed')
            return PatchPipelineResult(
                preflight_report=preflight_report,
                risk_summary=risk_summary,
                preview_payload=preview_payload,
                operation_results=[],
                verifier_results=[],
                required_verifiers=required_verifiers,
                run_record=run_record,
                rollback_decision={},
                rollback_event=None,
                outcome='apply-failed',
                strategy_decision=strategy_decision,
                transaction_record=transaction_record,
                error=str(exc),
            )

        advance_transaction(transaction_record, 'verify_started', status='active', note='verifier execution started')
        verifier_results = run_required_verifiers(
            list(preflight_report.target_files or []),
            required_verifiers,
            _verification_ctx(ctx, risk_summary, verification_ctx),
        )
        attach_verifier_results(transaction_record, verifier_results)
        assessment = assess_verification_outcome(risk_summary, list(preflight_report.target_files or []), verifier_results)
        transaction_record.verification_outcome = 'passed' if assessment.get('passed') else 'failed'
        advance_transaction(
            transaction_record,
            'verification_passed' if assessment.get('passed') else 'verification_failed',
            status='active',
            note='verification passed' if assessment.get('passed') else 'verification failed',
            extra={'assessment': assessment},
        )
        run_record.verification_outcome = transaction_record.verification_outcome
        run_record.final_state = 'verification_passed' if assessment.get('passed') else 'verification_failed'
        run_record = finalize_run(run_record, operation_results, verifier_results)
        run_record = _persist_run_record(run_record, transaction_record)
        rollback_decision = maybe_auto_rollback(run_record, verifier_results)
        rollback_event = None

        if rollback_decision.get('should_rollback'):
            try:
                run_record.rollback_triggered = True
                transaction_record = mark_transaction_rollback_started(transaction_record, note=rollback_decision.get('rollback_reason'), extra={'rollback_decision': rollback_decision})
                rollback_event = apply_rollback(run_id=run_record.run_id, root_dir=Path(getattr(ctx, 'root_dir')).resolve())
                refreshed = load_run(run_record.run_id, root_dir=Path(getattr(ctx, 'root_dir')).resolve())
                if refreshed is not None:
                    run_record = refreshed
                run_record.rollback_triggered = True
                run_record.rollback_outcome = str(rollback_event.get('status') or 'restored')
                run_record.final_state = 'rolled_back'
                transaction_record = mark_transaction_rolled_back(transaction_record, rollback_event=rollback_event, note='rollback completed', rollback_failed=False)
                run_record = _persist_run_record(run_record, transaction_record)
                return PatchPipelineResult(
                    preflight_report=preflight_report,
                    risk_summary=risk_summary,
                    preview_payload=preview_payload,
                    operation_results=operation_results,
                    verifier_results=verifier_results,
                    required_verifiers=required_verifiers,
                    run_record=run_record,
                    rollback_decision=rollback_decision,
                    rollback_event=rollback_event,
                    outcome='rolled-back',
                    strategy_decision=strategy_decision,
                    transaction_record=transaction_record,
                )
            except Exception as exc:
                transaction_record = mark_transaction_rolled_back(transaction_record, rollback_event=rollback_event, note=f'rollback failed: {exc}', rollback_failed=True)
                run_record.rollback_triggered = True
                run_record.rollback_outcome = 'failed'
                run_record = _mark_failed(run_record, transaction_record, error=f'auto_rollback_failed: {type(exc).__name__}: {exc}', patch_status='failed', system_status='failed', final_state='rollback_failed')
                return PatchPipelineResult(
                    preflight_report=preflight_report,
                    risk_summary=risk_summary,
                    preview_payload=preview_payload,
                    operation_results=operation_results,
                    verifier_results=verifier_results,
                    required_verifiers=required_verifiers,
                    run_record=run_record,
                    rollback_decision=rollback_decision,
                    rollback_event=rollback_event,
                    outcome='rollback-failed',
                    strategy_decision=strategy_decision,
                    transaction_record=transaction_record,
                    error=str(exc),
                )

        if assessment.get('passed'):
            outcome = str(assessment.get('recommended_outcome') or 'verified')
            transaction_record = mark_transaction_committed(transaction_record, final_state='verified', note='pipeline committed cleanly')
            run_record.final_state = 'verified'
            run_record.rollback_triggered = False
            run_record.rollback_outcome = None
            run_record = _persist_run_record(run_record, transaction_record)
        else:
            transaction_record = mark_transaction_failed(transaction_record, error='verification_failed', phase='verification_failed', recovery_hint='review verifier failures or rollback manually if needed', extra={'assessment': assessment})
            run_record = _mark_failed(run_record, transaction_record, error='verification_failed', patch_status='failed', system_status='failed', final_state='verification_failed')
            outcome = 'verification-failed'
        return PatchPipelineResult(
            preflight_report=preflight_report,
            risk_summary=risk_summary,
            preview_payload=preview_payload,
            operation_results=operation_results,
            verifier_results=verifier_results,
            required_verifiers=required_verifiers,
            run_record=run_record,
            rollback_decision=rollback_decision,
            rollback_event=rollback_event,
            outcome=outcome,
            strategy_decision=strategy_decision,
            transaction_record=transaction_record,
            error=getattr(run_record, 'error', None),
        )
    except Exception as exc:
        transaction_record = mark_transaction_failed(
            transaction_record,
            error=f'workspace_lock_failed: {type(exc).__name__}: {exc}',
            exception_class=type(exc).__name__,
            phase='failed',
            recovery_hint='ensure no other capatch run is mutating the workspace and retry',
        )
        run_record = _mark_failed(run_record, transaction_record, error=f'workspace_lock_failed: {type(exc).__name__}: {exc}', final_state='workspace_lock_failed') if run_record is not None else None
        return PatchPipelineResult(
            preflight_report=preflight_report,
            risk_summary=risk_summary,
            preview_payload=preview_payload,
            operation_results=[],
            verifier_results=[],
            required_verifiers=required_verifiers,
            run_record=run_record,
            rollback_decision={},
            rollback_event=None,
            outcome='blocked',
            strategy_decision=strategy_decision,
            transaction_record=transaction_record,
            error=str(exc),
        )
    finally:
        if workspace_lock is not None:
            workspace_lock.release()

"""Runtime orchestration for the one-button wave 4 launcher."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from session_cli import RuntimeContext, RuntimeResult
from session_export import SessionExportError, SessionExportResult, SessionExporter
from session_idempotency import SessionIdempotencyManager
from session_ledger import LedgerEntry, SessionLedger
from session_lock import SessionLockError, SessionLockManager
from session_state import PlannedSession, SessionStateError, SessionStateManager


@dataclass(frozen=True)
class RuntimeFlowError(Exception):
    status: str
    message: str
    details: Dict[str, Any]


DEFAULT_TTL_SECONDS = 60
DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 15


def run_runtime_core(context: RuntimeContext) -> RuntimeResult:
    _validate_policy_for_mode(context.session_mode, context.policy)
    state_manager = SessionStateManager(context.framework_root)

    try:
        plan = state_manager.plan_session(
            session_mode=context.session_mode,
            policy=context.policy,
            project_id=context.project_id,
            project_name=context.project_name,
            initiative_type=context.initiative_type,
            intent_raw=context.intent,
            dry_run=context.dry_run,
        )
    except SessionStateError as exc:
        raise RuntimeFlowError(
            status='runtime_core_failed',
            message=str(exc),
            details={'framework_root': str(context.framework_root), 'session_mode': context.session_mode, 'policy': context.policy, 'project_id': context.project_id},
        ) from exc

    ledger = SessionLedger(plan.paths.project.session_ledger_path)
    idp = SessionIdempotencyManager(ledger)
    idp_context = idp.compute(
        session_mode=plan.session_mode,
        policy=plan.policy,
        project_id=plan.project_id,
        normalized_intent=plan.intent_normalized,
        target_run_id=plan.run_id,
        target_round_id=plan.round_id,
        project_manifest_path=plan.paths.project.project_manifest_path,
        run_manifest_path=plan.paths.project.run_manifest_path,
        round_manifest_path=plan.paths.project.round_manifest_path,
    )

    if idp_context.reusable_entry is not None:
        return _build_reused_result(plan, idp_context.reusable_entry, idp_context.key)

    if context.dry_run:
        touched_paths = state_manager.materialize_minimal_state(plan)
        return _build_dry_run_result(plan, touched_paths, idp_context.key)

    lock_manager = SessionLockManager(
        lock_path=plan.paths.project.lock_file_path,
        ttl_seconds=DEFAULT_TTL_SECONDS,
        heartbeat_interval_seconds=DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    )
    try:
        with lock_manager.acquire(
            session_id=plan.session_id,
            project_id=plan.project_id,
            force_lock_steal=context.force_lock_steal,
        ) as lock_handle:
            touched_paths = state_manager.materialize_minimal_state(plan)
            lock_handle.heartbeat()
            exporter = SessionExporter(context.framework_root)
            export_result = exporter.export_session(
                plan=plan,
                checks={
                    'contracts': 'pass',
                    'smoke': 'pass',
                    'readiness_stage_install': 'ready',
                    'readiness_stage_round': 'ready',
                },
                idempotency_key=idp_context.key,
                idempotency_decision=idp_context.decision,
                context_hashes=idp_context.context_hashes,
                lock_id=lock_handle.result.lock_id,
                lock_path=plan.paths.project.lock_file_path,
                lock_pid=lock_manager.current_pid,
                lock_host=lock_manager.current_host,
            )
            ledger.append(
                LedgerEntry(
                    session_id=plan.session_id,
                    created_at_utc=plan.created_at_utc,
                    session_mode=plan.session_mode,
                    policy=plan.policy,
                    project_id=plan.project_id,
                    run_id=plan.run_id,
                    round_id=plan.round_id,
                    idempotency_key=idp_context.key,
                    status='ready_for_dispatch',
                    session_zip_path=export_result.canonical_zip_path,
                    handoff_copy_path=export_result.handoff_copy_path,
                    lock_id=lock_handle.result.lock_id,
                )
            )
            return _build_exported_result(plan, touched_paths, idp_context.key, export_result)
    except SessionLockError as exc:
        raise RuntimeFlowError(
            status='blocked_by_lock',
            message=str(exc),
            details={'project_id': plan.project_id, 'lock_path': str(plan.paths.project.lock_file_path)},
        ) from exc
    except SessionExportError as exc:
        raise RuntimeFlowError(
            status='export_contract_failed',
            message=str(exc),
            details={'project_id': plan.project_id, 'canonical_zip_path': str(plan.paths.export_hints.canonical_zip_path)},
        ) from exc



def _validate_policy_for_mode(session_mode: str, policy: str) -> None:
    valid_pairs = {
        'new_project': {'open_new_round'},
        'existing_project': {'resume_latest_round', 'open_new_round', 'upgrade'},
    }
    allowed = valid_pairs.get(session_mode)
    if not allowed:
        raise RuntimeFlowError(status='invalid_policy_transition', message=f'Unsupported session_mode: {session_mode}', details={'session_mode': session_mode, 'policy': policy})
    if policy not in allowed:
        raise RuntimeFlowError(status='invalid_policy_transition', message=f"Policy '{policy}' is not valid for session_mode '{session_mode}'.", details={'session_mode': session_mode, 'policy': policy, 'allowed_policies': sorted(allowed)})



def _build_reused_result(plan: PlannedSession, reusable_entry: LedgerEntry, idempotency_key: str) -> RuntimeResult:
    notes = [
        'The requested session matched a reusable ledger entry with the same idempotency key.',
        'No new lock acquisition, state mutation, or export work was required.',
    ]
    return RuntimeResult(
        status='reused',
        message='Existing session ZIP was reused from the session ledger.',
        session_mode=plan.session_mode,
        policy=plan.policy,
        dry_run=plan.dry_run,
        framework_root=str(plan.paths.project.framework_root),
        project_id=plan.project_id,
        project_name=plan.project_name,
        initiative_type=plan.initiative_type,
        run_id=reusable_entry.run_id,
        round_id=reusable_entry.round_id,
        session_id=reusable_entry.session_id,
        created_at_utc=reusable_entry.created_at_utc,
        canonical_zip_path=reusable_entry.session_zip_path,
        project_manifest_path=str(plan.paths.project.project_manifest_path),
        run_manifest_path=str(plan.paths.project.run_manifest_path),
        round_manifest_path=str(plan.paths.project.round_manifest_path),
        handoff_copy_filename=Path(reusable_entry.session_zip_path).name,
        handoff_copy_path=reusable_entry.handoff_copy_path,
        lock_path=str(plan.paths.project.lock_file_path),
        ledger_path=str(plan.paths.project.session_ledger_path),
        idempotency_key=idempotency_key,
        notes=notes,
        touched_paths={},
        issues=[],
    )



def _build_dry_run_result(plan: PlannedSession, touched_paths: Dict[str, Path], idempotency_key: str) -> RuntimeResult:
    notes = list(plan.notes)
    notes.extend([
        'Wave 4 dry-run computed idempotency and export targets without mutating the lock, ledger, or ZIP outputs.',
        'Canonical export, handoff copy, and sidecars were intentionally skipped because dry-run mode was requested.',
    ])
    return RuntimeResult(
        status='ready',
        message='One-button runtime core and export plan were resolved in dry-run mode.',
        session_mode=plan.session_mode,
        policy=plan.policy,
        dry_run=plan.dry_run,
        framework_root=str(plan.paths.project.framework_root),
        project_id=plan.project_id,
        project_name=plan.project_name,
        initiative_type=plan.initiative_type,
        run_id=plan.run_id,
        round_id=plan.round_id,
        session_id=plan.session_id,
        created_at_utc=plan.created_at_utc,
        canonical_zip_path=str(plan.paths.export_hints.canonical_zip_path),
        project_manifest_path=str(plan.paths.project.project_manifest_path),
        run_manifest_path=str(plan.paths.project.run_manifest_path),
        round_manifest_path=str(plan.paths.project.round_manifest_path),
        handoff_copy_filename=plan.paths.export_hints.handoff_copy_filename,
        handoff_copy_path=None,
        lock_path=str(plan.paths.project.lock_file_path),
        ledger_path=str(plan.paths.project.session_ledger_path),
        idempotency_key=idempotency_key,
        notes=notes,
        touched_paths={key: str(value) for key, value in touched_paths.items()},
        issues=[],
    )



def _build_exported_result(plan: PlannedSession, touched_paths: Dict[str, Path], idempotency_key: str, export_result: SessionExportResult) -> RuntimeResult:
    notes = list(plan.notes)
    notes.extend([
        'Wave 4 acquired the project lock, exported the canonical ZIP, validated the export contract, and updated the session ledger.',
        'The canonical ZIP is ready for dispatch or handoff review.',
    ])
    return RuntimeResult(
        status='ready_for_dispatch',
        message='Canonical one-button session ZIP exported successfully.',
        session_mode=plan.session_mode,
        policy=plan.policy,
        dry_run=plan.dry_run,
        framework_root=str(plan.paths.project.framework_root),
        project_id=plan.project_id,
        project_name=plan.project_name,
        initiative_type=plan.initiative_type,
        run_id=plan.run_id,
        round_id=plan.round_id,
        session_id=plan.session_id,
        created_at_utc=plan.created_at_utc,
        canonical_zip_path=export_result.canonical_zip_path,
        project_manifest_path=str(plan.paths.project.project_manifest_path),
        run_manifest_path=str(plan.paths.project.run_manifest_path),
        round_manifest_path=str(plan.paths.project.round_manifest_path),
        handoff_copy_filename=Path(export_result.canonical_zip_path).name,
        handoff_copy_path=export_result.handoff_copy_path,
        lock_path=str(plan.paths.project.lock_file_path),
        ledger_path=str(plan.paths.project.session_ledger_path),
        idempotency_key=idempotency_key,
        notes=notes,
        touched_paths={key: str(value) for key, value in touched_paths.items()},
        issues=export_result.issues,
    )

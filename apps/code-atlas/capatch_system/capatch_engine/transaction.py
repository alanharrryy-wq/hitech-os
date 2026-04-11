from __future__ import annotations

import json
import tempfile
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from capatch_contracts.operations import OperationSpec
from capatch_fs.atomic_io import read_file_utf8, write_file_if_changed
from capatch_fs.paths import resolve_target_file, resolve_target_path
from capatch_ops.registry import execute_operation

from .normalization import preserve_file_style
from .support_resolution import materialize_support_payload

TRANSACTION_SCHEMA_VERSION = '2.0.0'
TRANSACTION_PHASES = (
    'planned',
    'preflight_ok',
    'checkpoint_created',
    'apply_started',
    'apply_succeeded',
    'verify_started',
    'verification_passed',
    'verification_failed',
    'rollback_started',
    'rollback_succeeded',
    'rollback_failed',
    'committed',
    'failed',
)
TRANSACTION_STATUSES = ('active', 'committed', 'rolled_back', 'failed', 'abandoned')


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def _normalize_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _normalize_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _normalize_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_jsonable(item) for item in value]
    return value


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n', delete=False, dir=str(path.parent), suffix='.tmp') as handle:
        json.dump(_normalize_jsonable(payload), handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _phase_entry(phase: str, *, status: str, note: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        'timestamp': utc_now_iso(),
        'phase': str(phase),
        'status': str(status),
        'note': str(note) if note else None,
        'extra': _normalize_jsonable(dict(extra or {})),
    }
    return payload


@dataclass(slots=True)
class TransactionRecord:
    schema_version: str
    transaction_id: str
    run_id: str
    root_dir: str
    journal_path: str
    checkpoint_dir: str | None
    invocation_mode: str
    execution_mode: str
    started_at: str
    updated_at: str
    finished_at: str | None
    phase: str
    transaction_status: str
    target_files: list[str] = field(default_factory=list)
    operation_count: int = 0
    attempts: int = 1
    operation_results: list[dict[str, Any]] = field(default_factory=list)
    verifier_results: list[dict[str, Any]] = field(default_factory=list)
    rollback_event: dict[str, Any] | None = None
    verification_outcome: str | None = None
    final_state: str | None = None
    error: str | None = None
    last_exception_class: str | None = None
    recovery_hint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    phase_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _normalize_jsonable(self)


def transaction_dir(root_dir: Path) -> Path:
    return Path(root_dir).resolve() / 'reports' / 'patch_transactions'


def transaction_journal_path(root_dir: Path, transaction_id: str) -> Path:
    return transaction_dir(root_dir) / f'{transaction_id}.json'


def _transaction_id(ctx: object) -> str:
    run_id = str(getattr(ctx, 'run_id', '') or '').strip()
    if run_id:
        return f'txn_{run_id}'
    return f'txn_{datetime.now().strftime("%Y%m%d_%H%M%S")}'


def start_transaction(ctx: object, operations: list[OperationSpec], *, target_files: list[str] | None = None, metadata: dict[str, Any] | None = None) -> TransactionRecord:
    root_dir = Path(getattr(ctx, 'root_dir')).expanduser().resolve()
    tx_id = _transaction_id(ctx)
    journal = transaction_journal_path(root_dir, tx_id)
    record = TransactionRecord(
        schema_version=TRANSACTION_SCHEMA_VERSION,
        transaction_id=tx_id,
        run_id=str(getattr(ctx, 'run_id', tx_id)),
        root_dir=str(root_dir),
        journal_path=str(journal),
        checkpoint_dir=str(getattr(ctx, 'checkpoint_dir', '') or '') or None,
        invocation_mode=str(getattr(ctx, 'invocation_mode', 'patch-run') or 'patch-run'),
        execution_mode=str(getattr(ctx, 'invocation_mode', 'patch-run') or 'patch-run'),
        started_at=utc_now_iso(),
        updated_at=utc_now_iso(),
        finished_at=None,
        phase='planned',
        transaction_status='active',
        target_files=[str(item) for item in list(target_files or [])],
        operation_count=len(list(operations or [])),
        attempts=1,
        metadata=_normalize_jsonable(dict(metadata or {})),
        phase_history=[_phase_entry('planned', status='active', note='transaction created')],
    )
    _write_json_atomic(journal, record.to_dict())
    return record


def persist_transaction(record: TransactionRecord) -> TransactionRecord:
    record.updated_at = utc_now_iso()
    _write_json_atomic(Path(record.journal_path), record.to_dict())
    return record


def advance_transaction(record: TransactionRecord, phase: str, *, status: str | None = None, note: str | None = None, extra: dict[str, Any] | None = None) -> TransactionRecord:
    record.phase = str(phase)
    if status:
        record.transaction_status = str(status)
    record.phase_history.append(_phase_entry(phase, status=record.transaction_status, note=note, extra=extra))
    return persist_transaction(record)


def attach_operation_results(record: TransactionRecord, operation_results: list[dict[str, Any]]) -> TransactionRecord:
    record.operation_results = [_normalize_jsonable(dict(item)) for item in list(operation_results or [])]
    return persist_transaction(record)


def attach_verifier_results(record: TransactionRecord, verifier_results: list[dict[str, Any]]) -> TransactionRecord:
    record.verifier_results = [_normalize_jsonable(dict(item)) for item in list(verifier_results or [])]
    return persist_transaction(record)


def mark_transaction_failed(record: TransactionRecord, *, error: str, exception_class: str | None = None, phase: str = 'failed', recovery_hint: str | None = None, extra: dict[str, Any] | None = None) -> TransactionRecord:
    record.error = str(error)
    record.last_exception_class = str(exception_class) if exception_class else None
    record.recovery_hint = str(recovery_hint) if recovery_hint else record.recovery_hint
    record.final_state = 'failed'
    record.finished_at = utc_now_iso()
    record.transaction_status = 'failed'
    record.phase = str(phase)
    record.phase_history.append(_phase_entry(phase, status='failed', note=error, extra=extra))
    return persist_transaction(record)


def mark_transaction_committed(record: TransactionRecord, *, final_state: str = 'verified', note: str | None = None, extra: dict[str, Any] | None = None) -> TransactionRecord:
    record.final_state = str(final_state)
    record.phase = 'committed'
    record.transaction_status = 'committed'
    record.finished_at = utc_now_iso()
    record.phase_history.append(_phase_entry('committed', status='committed', note=note, extra=extra))
    return persist_transaction(record)


def mark_transaction_rollback_started(record: TransactionRecord, *, note: str | None = None, extra: dict[str, Any] | None = None) -> TransactionRecord:
    return advance_transaction(record, 'rollback_started', status='active', note=note, extra=extra)


def mark_transaction_rolled_back(record: TransactionRecord, *, rollback_event: dict[str, Any] | None = None, note: str | None = None, rollback_failed: bool = False, extra: dict[str, Any] | None = None) -> TransactionRecord:
    record.rollback_event = _normalize_jsonable(dict(rollback_event or {})) if rollback_event is not None else None
    record.finished_at = utc_now_iso()
    record.final_state = 'rollback_failed' if rollback_failed else 'rolled_back'
    record.phase = 'rollback_failed' if rollback_failed else 'rollback_succeeded'
    record.transaction_status = 'failed' if rollback_failed else 'rolled_back'
    record.phase_history.append(_phase_entry(record.phase, status=record.transaction_status, note=note, extra=extra))
    return persist_transaction(record)


def load_transaction(root_dir: Path | str, *, transaction_id: str | None = None, run_id: str | None = None) -> TransactionRecord | None:
    root_path = Path(root_dir).expanduser().resolve()
    if transaction_id:
        journal = transaction_journal_path(root_path, str(transaction_id))
    elif run_id:
        journal = transaction_journal_path(root_path, f'txn_{run_id}')
    else:
        return None
    if not journal.exists():
        return None
    payload = json.loads(journal.read_text(encoding='utf-8'))
    return TransactionRecord(**payload)


def list_recoverable_transactions(root_dir: Path | str) -> list[dict[str, Any]]:
    root_path = Path(root_dir).expanduser().resolve()
    rows: list[dict[str, Any]] = []
    for path in sorted(transaction_dir(root_path).glob('*.json')):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        status = str(payload.get('transaction_status') or '')
        phase = str(payload.get('phase') or '')
        if status == 'active' or phase in {'apply_started', 'apply_succeeded', 'verify_started', 'verification_failed', 'rollback_started'}:
            rows.append(payload)
    rows.sort(key=lambda item: str(item.get('updated_at') or ''), reverse=True)
    return rows


def execute_with_state(ctx: object, operations: list[OperationSpec], base_state: dict[Path, str] | None = None):
    state: dict[Path, str] = {} if base_state is None else dict(base_state)
    executions = []
    root_dir = Path(getattr(ctx, 'root_dir'))

    def run_one(operation: OperationSpec):
        if operation.type == 'ApplySet':
            for child in operation.payload.get('operations') or []:
                run_one(child)
            return
        if operation.type in {'AssertFileExists', 'AssertFileNotExists'}:
            target = resolve_target_path(root_dir, operation.file)
            execution = execute_operation(target, None, operation)
            executions.append((operation, execution, []))
            return
        target = resolve_target_file(root_dir, operation.file)
        content = state.get(target)
        if content is None:
            content = read_file_utf8(target)
        operation_to_run = operation
        support_notes: list[str] = []
        payload, support_notes = materialize_support_payload(ctx, target, content, operation)
        if payload != operation.payload:
            operation_to_run = OperationSpec(
                type=operation.type,
                label=operation.label,
                file=operation.file,
                payload=payload,
                schema_version=operation.schema_version,
                idempotency_class=operation.idempotency_class,
                reversibility=operation.reversibility,
            )
        execution = execute_operation(target, content, operation_to_run)
        if execution.final_text is not None:
            normalized = preserve_file_style(content, execution.final_text, operation_to_run.type)
            execution = type(execution)(
                target=execution.target,
                original_content=execution.original_content,
                final_text=normalized,
                message=execution.message,
                mutates_file=execution.mutates_file,
            )
            state[target] = normalized
        executions.append((operation, execution, support_notes))

    for operation in operations:
        run_one(operation)
    return executions, state


def apply_writes(executions) -> None:
    for _operation, execution, _notes in executions:
        if execution.mutates_file and execution.original_content is not None and execution.final_text is not None:
            write_file_if_changed(execution.target, execution.original_content, execution.final_text)



def build_transaction_batch_profile(target_files: list[str], strategy_decision: dict[str, Any] | None = None) -> dict[str, Any]:
    decision = dict(strategy_decision or {})
    normalized_targets = sorted({str(item) for item in list(target_files or []) if str(item)})
    return {
        'target_count': len(normalized_targets),
        'targets': normalized_targets,
        'selected_strategy': decision.get('selected_strategy'),
        'advisory_only': bool(decision.get('advisory_only', False)),
        'guardrails': list(decision.get('recommended_guardrails') or []),
    }


def record_strategy_decision(record: TransactionRecord, strategy_decision: dict[str, Any] | None = None) -> TransactionRecord:
    decision = dict(strategy_decision or {})
    if not decision:
        return persist_transaction(record)
    metadata = dict(record.metadata or {})
    metadata['strategy_decision'] = decision
    metadata['batch_profile'] = build_transaction_batch_profile(record.target_files, decision)
    record.metadata = metadata
    return persist_transaction(record)

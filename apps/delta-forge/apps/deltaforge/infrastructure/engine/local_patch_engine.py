from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

from application.contracts.engine_adapter import EngineIoResult
from domain.models import (
    ApplyChange,
    ApplyResult,
    DiffHunk,
    DiffPreview,
    FileDiff,
    FilePlan,
    OpsDocument,
    PlanResult,
    PlanStep,
    RefreshResult,
    RollbackResult,
    SessionWorkspace,
    ValidationIssue,
    ValidationResult,
)
from domain.models.plan_preview import PlanFilePreview, PlanStepPreview
from domain.models.process_report import ProcessReport
from infrastructure.engine.backup_store import BackupStore
from infrastructure.engine.operation_validator import OperationValidator, ResolvedOperation


class LocalPatchEngine:
    engine_name = "local_patch_engine"

    def __init__(
        self,
        root_dir: str | Path | None = None,
        *,
        backup_store_cls: type[BackupStore] = BackupStore,
        validator: OperationValidator | None = None,
    ) -> None:
        self._default_root_dir = None if root_dir is None else Path(root_dir).expanduser().resolve()
        self._backup_store_cls = backup_store_cls
        self._validator = validator or OperationValidator()

    def load_ops(self, path: str) -> OpsDocument:
        source = Path(path).expanduser().resolve()
        text = source.read_text(encoding="utf-8")
        stat = source.stat()
        metadata = {
            "size_bytes": stat.st_size,
            "modified_at": datetime.utcfromtimestamp(stat.st_mtime).isoformat(),
        }
        return OpsDocument(text=text, source_path=str(source), loaded_at=datetime.utcnow(), metadata=metadata)

    def save_ops(self, path: str, document: OpsDocument) -> EngineIoResult:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document.content, encoding="utf-8")
        return EngineIoResult(ok=True, message="Ops document saved", path=str(target))

    def validate(self, session: SessionWorkspace) -> ValidationResult:
        start = time.perf_counter()
        report = self._validator.validate(session, fallback_root_dir=self._default_root_dir)

        issues: list[ValidationIssue] = []
        for warning in report.warnings:
            issues.append(ValidationIssue(severity="warning", message=warning))
        for error in report.errors:
            issues.append(ValidationIssue(severity="error", message=error))

        ok = report.ok
        status = "ok" if ok else "invalid"
        summary = "Validation passed" if ok else f"Validation failed with {len(report.errors)} error(s)"
        duration_ms = int((time.perf_counter() - start) * 1000)

        return ValidationResult(
            ok=ok,
            status=status,
            summary=summary,
            warnings=list(report.warnings),
            errors=list(report.errors),
            touched_files=list(report.touched_files),
            duration_ms=duration_ms,
            process=ProcessReport(engine_name=self.engine_name, mode="validate"),
            payload={
                "operations_count": len(report.operations),
                "root_dir": "" if report.root_dir is None else str(report.root_dir),
            },
            issues=issues,
            operations_count=len(report.operations),
        )

    def plan(self, session: SessionWorkspace) -> PlanResult:
        start = time.perf_counter()
        report = self._validator.validate(session, fallback_root_dir=self._default_root_dir)

        if report.errors:
            return PlanResult(
                ok=False,
                status="invalid",
                summary=f"Plan blocked by {len(report.errors)} validation error(s)",
                warnings=list(report.warnings),
                errors=list(report.errors),
                touched_files=list(report.touched_files),
                duration_ms=int((time.perf_counter() - start) * 1000),
                process=ProcessReport(engine_name=self.engine_name, mode="plan"),
            )

        plan_steps: list[PlanStep] = []
        previews_by_file: dict[str, list[PlanStepPreview]] = {}

        for operation in report.operations:
            preview_text = self._build_preview(operation)
            risk = self._risk_for_operation(operation.operation_type)
            step = PlanStep(
                step_id=f"op-{operation.index:03d}",
                title=operation.label,
                detail=f"{operation.operation_type} -> {operation.file}",
                preview=preview_text,
                risk=risk,
                file_path=str(operation.target_path),
                operation_type=operation.operation_type,
            )
            plan_steps.append(step)

            preview = PlanStepPreview(
                step_id=step.step_id,
                label=step.title,
                operation_type=step.operation_type,
                file_path=step.file_path,
                preview=step.preview,
                risk=step.risk,
            )
            previews_by_file.setdefault(str(operation.target_path), []).append(preview)

        file_plans: list[FilePlan] = []
        diff_files: list[FileDiff] = []
        file_previews: list[PlanFilePreview] = []

        for path_value, previews in previews_by_file.items():
            operations = [
                step
                for step in plan_steps
                if step.file_path == path_value
            ]
            summary = f"{len(operations)} operation(s) planned"
            file_plans.append(
                FilePlan(
                    path=path_value,
                    summary=summary,
                    operations=operations,
                    risk=self._aggregate_risk(operations),
                    diff_summary=summary,
                )
            )
            file_previews.append(
                PlanFilePreview(
                    file_path=path_value,
                    operations_count=len(previews),
                    summary=summary,
                    steps=previews,
                )
            )
            diff_files.append(
                FileDiff(
                    path=path_value,
                    change_type="modify",
                    hunks=[DiffHunk(header="planned", before="", after="\n".join(item.preview for item in previews))],
                )
            )

        duration_ms = int((time.perf_counter() - start) * 1000)
        summary = f"Plan generated for {len(plan_steps)} operation(s) across {len(file_plans)} file(s)"

        return PlanResult(
            ok=True,
            status="ok",
            summary=summary,
            files=file_plans,
            diff_preview=DiffPreview(summary=summary, files=diff_files),
            warnings=list(report.warnings),
            errors=[],
            touched_files=list(report.touched_files),
            duration_ms=duration_ms,
            process=ProcessReport(engine_name=self.engine_name, mode="plan"),
        )

    def apply(self, session: SessionWorkspace) -> ApplyResult:
        start = time.perf_counter()
        report = self._validator.validate(session, fallback_root_dir=self._default_root_dir)

        if report.errors or report.root_dir is None:
            return ApplyResult(
                ok=False,
                status="invalid",
                summary=f"Apply blocked by {len(report.errors)} validation error(s)",
                warnings=list(report.warnings),
                errors=list(report.errors),
                touched_files=list(report.touched_files),
                duration_ms=int((time.perf_counter() - start) * 1000),
                process=ProcessReport(engine_name=self.engine_name, mode="apply"),
            )

        store = self._backup_store_cls(report.root_dir)
        rollback_token = store.create_token()
        manifest = store.start_manifest(
            rollback_token=rollback_token,
            operations_count=len(report.operations),
            touched_files=list(report.touched_files),
        )

        changes: list[ApplyChange] = []

        try:
            for operation in report.operations:
                store.backup_file(manifest, operation.target_path)
                original = operation.target_path.read_text(encoding="utf-8")
                updated = self._apply_operation(operation, original)
                operation.target_path.write_text(updated, encoding="utf-8", newline="")
                changes.append(
                    ApplyChange(
                        path=str(operation.target_path),
                        status="applied",
                        detail=f"{operation.operation_type}::{operation.label}",
                    )
                )

            store.write_manifest(manifest)
            duration_ms = int((time.perf_counter() - start) * 1000)
            summary = f"Applied {len(changes)} operation(s) across {len(report.touched_files)} file(s)"
            return ApplyResult(
                ok=True,
                status="applied",
                summary=summary,
                warnings=list(report.warnings),
                errors=[],
                touched_files=list(report.touched_files),
                backups=[entry.as_dict() for entry in manifest.backup_entries],
                rollback_token=rollback_token,
                duration_ms=duration_ms,
                process=ProcessReport(engine_name=self.engine_name, mode="apply"),
                payload={"manifest_path": str(store.manifest_path(rollback_token))},
                changes=changes,
            )
        except Exception as exc:
            restored, restore_errors = store.restore(manifest)
            duration_ms = int((time.perf_counter() - start) * 1000)
            errors = [f"Apply failed: {exc}"]
            errors.extend(restore_errors)
            return ApplyResult(
                ok=False,
                status="failed",
                summary="Apply failed and rollback restore was attempted",
                warnings=list(report.warnings),
                errors=errors,
                touched_files=list(report.touched_files),
                backups=[entry.as_dict() for entry in manifest.backup_entries],
                rollback_token=rollback_token,
                duration_ms=duration_ms,
                process=ProcessReport(engine_name=self.engine_name, mode="apply"),
                payload={"restored_paths": restored},
                changes=changes,
            )

    def rollback(self, session: SessionWorkspace, rollback_token: str = "") -> RollbackResult:
        start = time.perf_counter()
        token = self._select_rollback_token(session, rollback_token)
        if not token:
            return RollbackResult(
                ok=False,
                status="invalid",
                summary="No rollback token available",
                errors=["Rollback token was not provided and session has no recorded token."],
                duration_ms=int((time.perf_counter() - start) * 1000),
                process=ProcessReport(engine_name=self.engine_name, mode="rollback"),
            )

        root_dir = self._resolve_root_for_session(session)
        if root_dir is None:
            return RollbackResult(
                ok=False,
                status="invalid",
                summary="Cannot resolve root_dir for rollback",
                errors=["Session root_dir is missing."],
                rollback_token=token,
                duration_ms=int((time.perf_counter() - start) * 1000),
                process=ProcessReport(engine_name=self.engine_name, mode="rollback"),
            )

        store = self._backup_store_cls(root_dir)

        try:
            manifest = store.read_manifest(token)
        except Exception as exc:
            return RollbackResult(
                ok=False,
                status="missing_manifest",
                summary="Rollback manifest not found",
                errors=[str(exc)],
                rollback_token=token,
                duration_ms=int((time.perf_counter() - start) * 1000),
                process=ProcessReport(engine_name=self.engine_name, mode="rollback"),
            )

        restored, restore_errors = store.restore(manifest)
        ok = not restore_errors
        duration_ms = int((time.perf_counter() - start) * 1000)

        return RollbackResult(
            ok=ok,
            status="rolled_back" if ok else "failed",
            summary=(
                f"Rollback restored {len(restored)} file(s)"
                if ok
                else f"Rollback restored {len(restored)} file(s) with errors"
            ),
            warnings=[],
            errors=list(restore_errors),
            touched_files=list(manifest.touched_files),
            backups=[entry.as_dict() for entry in manifest.backup_entries],
            rollback_token=manifest.rollback_token,
            duration_ms=duration_ms,
            process=ProcessReport(engine_name=self.engine_name, mode="rollback"),
            restored_paths=restored,
        )

    def refresh(self, session: SessionWorkspace) -> RefreshResult:
        start = time.perf_counter()
        payload = session.ops_document.summary_payload()
        root_dir = self._resolve_root_for_session(session)
        payload["root_dir"] = "" if root_dir is None else str(root_dir)

        return RefreshResult(
            ok=True,
            status="ok",
            summary="Session backend state refreshed",
            warnings=[],
            errors=[],
            touched_files=[],
            duration_ms=int((time.perf_counter() - start) * 1000),
            process=ProcessReport(engine_name=self.engine_name, mode="refresh"),
            metadata=payload,
            payload=payload,
        )

    def _resolve_root_for_session(self, session: SessionWorkspace) -> Path | None:
        scope_root = str(getattr(getattr(session, "scope", None), "root_dir", "") or "").strip()
        if scope_root:
            return Path(scope_root).expanduser().resolve()
        if self._default_root_dir is not None:
            return self._default_root_dir
        return None

    def _select_rollback_token(self, session: SessionWorkspace, rollback_token: str) -> str:
        token = str(rollback_token or "").strip()
        if token:
            return token
        if getattr(session, "rollback_token", ""):
            return str(session.rollback_token)
        tokens = list(getattr(session, "rollback_tokens", []) or [])
        if tokens:
            return str(tokens[-1])
        return ""

    def _build_preview(self, operation: ResolvedOperation) -> str:
        if operation.operation_type == "ReplaceLineRange":
            return (
                f"replace lines {operation.payload.get('start_line')}..{operation.payload.get('end_line')} "
                f"in {operation.file}"
            )
        if operation.operation_type == "ReplaceExactOnce":
            old_text = str(operation.payload.get("old_text", ""))
            return f"replace exact block ({len(old_text)} chars) in {operation.file}"
        anchor = str(operation.payload.get("anchor", ""))
        return f"insert after anchor ({len(anchor)} chars) in {operation.file}"

    def _risk_for_operation(self, operation_type: str) -> str:
        if operation_type == "ReplaceLineRange":
            return "medium"
        return "low"

    def _aggregate_risk(self, operations: list[PlanStep]) -> str:
        if any(item.risk == "high" for item in operations):
            return "high"
        if any(item.risk == "medium" for item in operations):
            return "medium"
        return "low"

    def _apply_operation(self, operation: ResolvedOperation, content: str) -> str:
        payload = operation.payload
        if operation.operation_type == "ReplaceLineRange":
            return self._apply_replace_line_range(
                content,
                int(payload["start_line"]),
                int(payload["end_line"]),
                str(payload.get("new_text", "")),
            )
        if operation.operation_type == "ReplaceExactOnce":
            return self._apply_replace_exact_once(
                content,
                str(payload["old_text"]),
                str(payload.get("new_text", "")),
            )
        if operation.operation_type == "InsertAfterExact":
            return self._apply_insert_after_exact(
                content,
                str(payload["anchor"]),
                str(payload.get("insert_text", "")),
            )
        raise ValueError(f"Unsupported operation type: {operation.operation_type}")

    def _apply_replace_line_range(self, content: str, start_line: int, end_line: int, new_text: str) -> str:
        lines = content.splitlines()
        before = lines[: start_line - 1]
        after = lines[end_line:]
        replacement = new_text.splitlines()
        final_lines = before + replacement + after
        final_text = "\n".join(final_lines)
        if content.endswith("\n"):
            final_text += "\n"
        return final_text

    def _apply_replace_exact_once(self, content: str, old_text: str, new_text: str) -> str:
        first = content.find(old_text)
        if first < 0:
            raise ValueError("old_text was not found during apply")
        second = content.find(old_text, first + len(old_text))
        if second >= 0:
            raise ValueError("old_text appears more than once during apply")
        return content.replace(old_text, new_text, 1)

    def _apply_insert_after_exact(self, content: str, anchor: str, insert_text: str) -> str:
        first = content.find(anchor)
        if first < 0:
            raise ValueError("anchor was not found during apply")
        second = content.find(anchor, first + len(anchor))
        if second >= 0:
            raise ValueError("anchor appears more than once during apply")
        position = first + len(anchor)
        return content[:position] + insert_text + content[position:]

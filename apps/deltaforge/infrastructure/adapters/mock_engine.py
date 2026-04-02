from __future__ import annotations

from datetime import datetime
from pathlib import Path

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


class MockEngineAdapter:
    def validate(self, session: SessionWorkspace) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if session.scope.is_empty:
            issues.append(ValidationIssue(severity="error", message="No hay scope cargado."))
        if not session.ops_document.is_loaded:
            issues.append(ValidationIssue(severity="warning", message="No hay Ops Document cargado."))

        ok = not any(item.severity == "error" for item in issues)
        summary = "Validacion OK" if ok else "Validacion con observaciones"
        return ValidationResult(ok=ok, summary=summary, issues=issues)

    def plan(self, session: SessionWorkspace) -> PlanResult:
        lines = [line.strip() for line in session.ops_document.text.splitlines() if line.strip()]
        if not lines:
            lines = ["noop:review"]

        file_plans: list[FilePlan] = []
        file_diffs: list[FileDiff] = []

        for index, target in enumerate(session.scope.targets, start=1):
            operations = [
                PlanStep(
                    step_id=f"{index}-{line_idx}",
                    title=f"Operacion {line_idx + 1}",
                    detail=line,
                )
                for line_idx, line in enumerate(lines)
            ]
            file_plans.append(
                FilePlan(
                    path=target,
                    summary=f"{len(operations)} operaciones propuestas",
                    operations=operations,
                )
            )

            file_diffs.append(
                FileDiff(
                    path=target,
                    change_type="modify",
                    hunks=[
                        DiffHunk(
                            header="@@ -1,2 +1,3 @@",
                            before="linea_original = true",
                            after="linea_original = true\nlinea_nueva = true",
                        )
                    ],
                )
            )

        summary = f"Plan generado para {len(file_plans)} archivos"
        diff_preview = DiffPreview(summary=summary, files=file_diffs)
        return PlanResult(ok=bool(file_plans), summary=summary, files=file_plans, diff_preview=diff_preview)

    def apply(self, session: SessionWorkspace) -> ApplyResult:
        changes = [
            ApplyChange(path=target, status="applied", detail="Cambio aplicado en mock engine")
            for target in session.scope.targets
        ]
        rollback_token = datetime.utcnow().strftime("rbk-%Y%m%d-%H%M%S")
        return ApplyResult(
            ok=bool(changes),
            summary=f"Apply ejecutado en {len(changes)} archivos",
            changes=changes,
            rollback_token=rollback_token,
        )

    def rollback(self, session: SessionWorkspace, rollback_token: str = "") -> RollbackResult:
        token = rollback_token or (session.rollback_tokens[-1] if session.rollback_tokens else "")
        if not token:
            return RollbackResult(ok=False, summary="No hay rollback disponible", restored_paths=[])

        restored = list(session.scope.targets)
        return RollbackResult(ok=True, summary=f"Rollback {token} completado", restored_paths=restored)

    def refresh(self, session: SessionWorkspace) -> RefreshResult:
        return RefreshResult(ok=True, summary=f"Scope refrescado ({session.scope.count} targets)")

    def load_ops(self, path: str) -> OpsDocument:
        source = Path(path).expanduser().resolve()
        text = source.read_text(encoding="utf-8")
        return OpsDocument(text=text, source_path=str(source), loaded_at=datetime.utcnow())

    def save_ops(self, path: str, document: OpsDocument) -> EngineIoResult:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document.text, encoding="utf-8")
        return EngineIoResult(ok=True, message="Ops guardado", path=str(target))

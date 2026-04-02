from __future__ import annotations

from PySide6.QtWidgets import QListWidget, QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget

from domain.events import AppEvent
from domain.models import ApplyResult, PlanResult, RollbackResult, ValidationResult
from ui.primitives import SectionCard


class BottomPane(QWidget):
    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.card = SectionCard("Execution Surface", "Events, validacion y resultados", alt=True)
        self.tabs = QTabWidget()

        self.events_list = QListWidget()
        self.validation_text = QPlainTextEdit()
        self.plan_text = QPlainTextEdit()
        self.apply_text = QPlainTextEdit()
        self.rollback_text = QPlainTextEdit()

        for widget in (self.validation_text, self.plan_text, self.apply_text, self.rollback_text):
            widget.setReadOnly(True)

        self.tabs.addTab(self.events_list, "Events")
        self.tabs.addTab(self.validation_text, "Validation")
        self.tabs.addTab(self.plan_text, "Plan")
        self.tabs.addTab(self.apply_text, "Apply")
        self.tabs.addTab(self.rollback_text, "Rollback")

        self.card.content_layout.addWidget(self.tabs)
        outer.addWidget(self.card)

    def append_event(self, event: AppEvent) -> None:
        stamp = event.created_at.strftime("%H:%M:%S")
        summary = f"[{stamp}] {event.name}"
        if event.session_id:
            summary += f" ({event.session_id})"
        self.events_list.insertItem(0, summary)

    def set_validation(self, result: ValidationResult | None) -> None:
        if result is None:
            self.validation_text.setPlainText("Sin validacion")
            return
        lines = [result.summary, ""]
        for issue in result.issues:
            lines.append(f"- [{issue.severity}] {issue.message} {issue.path}".strip())
        self.validation_text.setPlainText("\n".join(lines))

    def set_plan(self, result: PlanResult | None) -> None:
        if result is None:
            self.plan_text.setPlainText("Sin plan")
            return
        lines = [result.summary, ""]
        for file_plan in result.files:
            lines.append(f"- {file_plan.path}: {file_plan.summary}")
        self.plan_text.setPlainText("\n".join(lines))

    def set_apply(self, result: ApplyResult | None) -> None:
        if result is None:
            self.apply_text.setPlainText("Sin apply")
            return
        lines = [result.summary, ""]
        for change in result.changes:
            lines.append(f"- {change.path}: {change.status} ({change.detail})")
        if result.rollback_token:
            lines.extend(["", f"rollback token: {result.rollback_token}"])
        self.apply_text.setPlainText("\n".join(lines))

    def set_rollback(self, result: RollbackResult | None) -> None:
        if result is None:
            self.rollback_text.setPlainText("Sin rollback")
            return
        lines = [result.summary, ""]
        for path in result.restored_paths:
            lines.append(f"- {path}")
        self.rollback_text.setPlainText("\n".join(lines))

    def focus_panel(self) -> None:
        self.tabs.setFocus()

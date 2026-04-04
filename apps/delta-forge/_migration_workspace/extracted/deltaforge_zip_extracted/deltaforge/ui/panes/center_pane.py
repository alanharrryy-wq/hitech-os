from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from domain.models import DiffPreview, PlanResult
from ui.primitives import DiffBlockContainer, SectionCard


class CenterPane(QWidget):
    plan_item_selected = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical)
        outer.addWidget(splitter)

        self.plan_card = SectionCard("Plan", "Vista agrupada por archivo")
        self.plan_tree = QTreeWidget()
        self.plan_tree.setHeaderLabels(["Archivo / Operacion", "Detalle"])
        self.plan_tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.plan_card.content_layout.addWidget(self.plan_tree)
        splitter.addWidget(self.plan_card)

        self.diff_card = SectionCard("Diff Preview", "Preview mock del resultado", alt=True)
        self.diff_block = DiffBlockContainer()
        self.diff_card.content_layout.addWidget(self.diff_block)
        splitter.addWidget(self.diff_card)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

    def set_plan_result(self, plan: PlanResult | None) -> None:
        self.plan_tree.clear()
        if plan is None:
            self.diff_block.set_diff_text("Sin plan")
            return

        for file_plan in plan.files:
            root = QTreeWidgetItem([file_plan.path, file_plan.summary])
            root.setData(0, Qt.UserRole, {"kind": "file", "path": file_plan.path, "summary": file_plan.summary})
            self.plan_tree.addTopLevelItem(root)

            for step in file_plan.operations:
                child = QTreeWidgetItem([step.title, step.detail])
                child.setData(
                    0,
                    Qt.UserRole,
                    {
                        "kind": "step",
                        "path": file_plan.path,
                        "step_id": step.step_id,
                        "title": step.title,
                        "detail": step.detail,
                    },
                )
                root.addChild(child)

            root.setExpanded(True)

    def set_diff_preview(self, diff: DiffPreview | None) -> None:
        if diff is None or not diff.files:
            self.diff_block.set_diff_text("Sin diff")
            return

        chunks: list[str] = [diff.summary, ""]
        for file_diff in diff.files:
            chunks.append(f"# {file_diff.path} [{file_diff.change_type}]")
            for hunk in file_diff.hunks:
                chunks.append(hunk.header)
                chunks.append(f"- {hunk.before}")
                chunks.append(f"+ {hunk.after}")
            chunks.append("")
        self.diff_block.set_diff_text("\n".join(chunks))

    def focus_panel(self) -> None:
        self.plan_tree.setFocus()

    def _on_selection_changed(self) -> None:
        items = self.plan_tree.selectedItems()
        if not items:
            return

        payload = items[0].data(0, Qt.UserRole)
        if isinstance(payload, dict):
            self.plan_item_selected.emit(payload)

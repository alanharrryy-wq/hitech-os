from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QSplitter, QVBoxLayout, QWidget

from .bottom_results_tabs import BottomResultsTabs
from .detail_stack import DetailStack
from .ops_list import OpsList
from .plan_diff_stack import PlanDiffStack
from .target_list import TargetList


class SessionWorkspace(QWidget):
    targetSelected = Signal(object)
    opSelected = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        vertical = QSplitter(Qt.Vertical, self)
        top = QSplitter(Qt.Horizontal, vertical)

        self.left_surface = self._make_surface('Scope / Ops')
        left_layout = self.left_surface.layout()
        self.target_list = TargetList(self.left_surface)
        self.ops_list = OpsList(self.left_surface)
        self.target_list.selectionChangedByUser.connect(self.targetSelected.emit)
        self.ops_list.selectionChangedByUser.connect(self.opSelected.emit)
        left_layout.addWidget(self.target_list, 1)
        left_layout.addWidget(self.ops_list, 1)

        self.center_surface = self._make_surface('Center Preview')
        center_layout = self.center_surface.layout()
        self.plan_diff_stack = PlanDiffStack(self.center_surface)
        center_layout.addWidget(self.plan_diff_stack, 1)

        self.right_surface = self._make_surface('Detail')
        right_layout = self.right_surface.layout()
        self.detail_stack = DetailStack(self.right_surface)
        right_layout.addWidget(self.detail_stack, 1)

        top.addWidget(self.left_surface)
        top.addWidget(self.center_surface)
        top.addWidget(self.right_surface)
        top.setSizes([260, 520, 340])

        self.bottom_surface = self._make_surface('Results Stream')
        bottom_layout = self.bottom_surface.layout()
        self.bottom_results_tabs = BottomResultsTabs(self.bottom_surface)
        bottom_layout.addWidget(self.bottom_results_tabs, 1)

        vertical.addWidget(top)
        vertical.addWidget(self.bottom_surface)
        vertical.setSizes([540, 220])
        layout.addWidget(vertical, 1)

    def _make_surface(self, title_text: str) -> QFrame:
        frame = QFrame(self)
        frame.setProperty('role', 'surface')
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        title = QLabel(title_text, frame)
        title.setProperty('role', 'surface-title')
        layout.addWidget(title)
        return frame

    def set_projection(self, projection: dict | None) -> None:
        projection = projection or {}
        self.target_list.set_items(projection.get('targets', []))
        self.ops_list.set_items(projection.get('ops', []))
        self.plan_diff_stack.set_groups(projection.get('grouped_preview', []))
        self.detail_stack.set_detail(projection.get('detail'))
        self.bottom_results_tabs.set_payloads(projection.get('results', {}))

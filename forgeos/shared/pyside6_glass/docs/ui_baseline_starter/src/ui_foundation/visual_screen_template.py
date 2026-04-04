"""
Reusable screen scaffold for visually capable internal tools.

Key idea:
- the developer declares intent
- the template wires structure
- the runtime applies sensible defaults
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .ui_runtime import get_visual_runtime


class VisualScreenTemplate(QMainWindow):
    """Base window for new tools and internal screens."""

    visual_role = "workspace"
    visual_variant = "default"
    visual_emphasis = "medium"
    visual_fx_level = "standard"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.runtime = get_visual_runtime()
        self.fx = self.runtime.describe_fx(self.visual_fx_level)
        self.tone = self.runtime.tone_for_role(self.visual_role, self.visual_variant)

        self.setWindowTitle(self.title_text())
        self.resize(1320, 820)

        root = QWidget()
        root.setObjectName("root")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(12)

        self.header = self._build_header()
        self.toolbar = self._build_toolbar()
        self.body = self._build_body()
        self.status = self._build_status_strip()

        root_layout.addWidget(self.header)
        root_layout.addWidget(self.toolbar)
        root_layout.addWidget(self.body, 1)
        root_layout.addWidget(self.status)

        self.setCentralWidget(root)
        self._apply_styles()

    # -------- developer extension points --------

    def title_text(self) -> str:
        return self.__class__.__name__.replace("Screen", "").replace("_", " ")

    def subtitle_text(self) -> str:
        return "Governed scaffold for fast, decent-looking UI."

    def build_main_content(self) -> QWidget:
        return self._placeholder("Main content")

    def build_side_panel(self) -> Optional[QWidget]:
        return None

    def build_primary_actions(self) -> list[QPushButton]:
        return []

    # -------- scaffold implementation --------

    def _build_header(self) -> QFrame:
        frame = self._surface_frame("headerSurface")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        title = QLabel(self.title_text())
        title.setObjectName("pageTitle")

        subtitle = QLabel(self.subtitle_text())
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return frame

    def _build_toolbar(self) -> QFrame:
        frame = self._surface_frame("toolbarSurface")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        role_badge = QLabel(
            f"role={self.visual_role} | variant={self.visual_variant} | emphasis={self.visual_emphasis} | fx={self.visual_fx_level}"
        )
        role_badge.setObjectName("metaBadge")
        layout.addWidget(role_badge)
        layout.addStretch(1)

        actions = self.build_primary_actions()
        if actions:
            for button in actions:
                button.setProperty("primaryAction", True)
                layout.addWidget(button)
        else:
            action = QPushButton("Primary action")
            action.setProperty("primaryAction", True)
            layout.addWidget(action)

        return frame

    def _build_body(self) -> QWidget:
        body = QWidget()
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        main = self._surface_frame(self.tone["surface_class"])
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.addWidget(self.build_main_content(), 1)

        layout.addWidget(main, 1)

        side_panel = self.build_side_panel()
        if side_panel is not None:
            side = self._surface_frame("sideSurface")
            side.setMinimumWidth(320)
            side.setMaximumWidth(420)
            side_layout = QVBoxLayout(side)
            side_layout.setContentsMargins(16, 16, 16, 16)
            side_layout.addWidget(side_panel, 1)
            layout.addWidget(side)

        return body

    def _build_status_strip(self) -> QFrame:
        frame = self._surface_frame("statusSurface")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        status = QLabel("Ready")
        status.setObjectName("statusLabel")
        layout.addWidget(status)

        layout.addStretch(1)

        stack = []
        if self.runtime.capabilities.qtawesome:
            stack.append("QtAwesome")
        if self.runtime.capabilities.pyqtgraph:
            stack.append("pyqtgraph")
        if self.runtime.capabilities.fluent_widgets:
            stack.append("Fluent")
        if self.runtime.capabilities.frameless_window:
            stack.append("Frameless")

        enabled = QLabel("Enabled: " + (", ".join(stack) if stack else "core only"))
        enabled.setObjectName("metaBadge")
        layout.addWidget(enabled)

        return frame

    # -------- utility helpers --------

    def loading_state(self, message: str = "Loading...") -> QWidget:
        return self._placeholder(message)

    def empty_state(self, message: str = "No data yet") -> QWidget:
        return self._placeholder(message)

    def error_state(self, message: str = "Something went wrong") -> QWidget:
        return self._placeholder(message)

    def _placeholder(self, message: str) -> QWidget:
        frame = self._surface_frame("placeholderSurface")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(8)

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)
        return frame

    def _surface_frame(self, class_name: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setObjectName(class_name)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return frame

    def _apply_styles(self) -> None:
        radius = self.fx["radius"]
        border_alpha = self.fx["border_alpha"]

        self.setStyleSheet(
            f"""
            QWidget#root {{
                background: #0f1115;
                color: #eef2f7;
            }}
            QFrame#headerSurface, QFrame#toolbarSurface, QFrame#statusSurface,
            QFrame#dataSurface, QFrame#defaultSurface, QFrame#formSurface,
            QFrame#sideSurface, QFrame#placeholderSurface {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, {border_alpha});
                border-radius: {radius}px;
            }}
            QLabel#pageTitle {{
                font-size: 24px;
                font-weight: 700;
            }}
            QLabel#pageSubtitle {{
                color: rgba(238, 242, 247, 0.72);
            }}
            QLabel#metaBadge {{
                color: rgba(238, 242, 247, 0.72);
                font-size: 11px;
            }}
            QLabel#statusLabel {{
                font-weight: 600;
            }}
            QPushButton[primaryAction="true"] {{
                padding: 8px 14px;
                border-radius: {max(8, radius - 4)}px;
                background: #2f6fed;
                color: white;
                border: none;
                font-weight: 600;
            }}
            QPushButton[primaryAction="true"]:hover {{
                background: #4d82ef;
            }}
            """
        )

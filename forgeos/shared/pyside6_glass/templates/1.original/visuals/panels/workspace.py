from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from ..controls.chips import create_chip
from ..controls.inputs import create_combo, create_line_edit
from ..effects.polish import enable_card_hover
from ..effects.shadow import apply_shadow
from ..widgets.primitives import make_placeholder, make_separator


@dataclass(slots=True)
class WorkspaceRefs:
    root_layout: QHBoxLayout
    panels: dict[str, QFrame]
    slot_layouts: dict[str, QVBoxLayout]
    workspace_entry: QLineEdit | None
    mode_combo: QComboBox | None
    view_combo: QComboBox | None


def _build_sidebar(parent: QWidget) -> tuple[QFrame, QVBoxLayout, QLineEdit, QComboBox, QComboBox]:
    frame = QFrame(parent)
    frame.setProperty("card", "true")
    apply_shadow(frame, blur=22.0, y_offset=8.0, alpha=18, color=QColor(7, 18, 28, 54))
    enable_card_hover(frame)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    section = QLabel("Workspace", frame)
    section.setProperty("role", "section")
    layout.addWidget(section)

    path_label = QLabel("Path", frame)
    path_label.setProperty("role", "field")
    layout.addWidget(path_label)
    workspace_entry = create_line_edit("Paste workspace path or identifier", parent=frame)
    layout.addWidget(workspace_entry)

    layout.addWidget(make_separator())

    mode_label = QLabel("Mode", frame)
    mode_label.setProperty("role", "field")
    layout.addWidget(mode_label)
    mode_combo = create_combo(["Overview", "Focus", "Automation", "Diagnostics"], parent=frame)
    layout.addWidget(mode_combo)

    view_label = QLabel("View", frame)
    view_label.setProperty("role", "field")
    layout.addWidget(view_label)
    view_combo = create_combo(["Split", "Columns", "Compact"], parent=frame)
    layout.addWidget(view_combo)

    chip_row = QHBoxLayout()
    chip_row.setSpacing(8)
    chip_row.addWidget(create_chip("Status", tone="accent", icon="status", parent=frame), 0)
    chip_row.addWidget(create_chip("Live", tone="neutral", icon="spark", parent=frame), 0)
    chip_row.addStretch(1)
    layout.addLayout(chip_row)

    hint = QLabel(
        "This sidebar is intentionally generic: keep, reorder, or replace controls per project.",
        frame,
    )
    hint.setProperty("role", "hint")
    hint.setWordWrap(True)
    layout.addWidget(hint)

    layout.addStretch(1)
    return frame, layout, workspace_entry, mode_combo, view_combo


def _build_main(parent: QWidget) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame(parent)
    frame.setProperty("card", "true")
    apply_shadow(frame, blur=24.0, y_offset=8.0, alpha=20, color=QColor(7, 18, 28, 60))
    enable_card_hover(frame)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    title = QLabel("Preview", frame)
    title.setProperty("role", "section")
    layout.addWidget(title)

    top_row = QHBoxLayout()
    top_row.setSpacing(8)
    top_row.addWidget(create_chip("Output", tone="good", icon="output", parent=frame), 0)
    top_row.addWidget(create_chip("Ready", tone="neutral", icon="check", parent=frame), 0)
    top_row.addStretch(1)
    layout.addLayout(top_row)

    return frame, layout


def _build_aux(parent: QWidget) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame(parent)
    frame.setProperty("card", "muted")
    apply_shadow(frame, blur=20.0, y_offset=7.0, alpha=16, color=QColor(7, 18, 28, 46))
    enable_card_hover(frame)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    title = QLabel("Activity", frame)
    title.setProperty("role", "section")
    layout.addWidget(title)
    return frame, layout


def build_workspace_panel(
    parent: QWidget,
    *,
    order: tuple[str, ...] = ("sidebar", "main", "aux"),
    show_sidebar: bool = True,
    show_aux: bool = True,
) -> WorkspaceRefs:
    root_layout = QHBoxLayout()
    root_layout.setSpacing(16)

    panels: dict[str, QFrame] = {}
    slot_layouts: dict[str, QVBoxLayout] = {}

    sidebar_frame, sidebar_layout, workspace_entry, mode_combo, view_combo = _build_sidebar(parent)
    main_frame, main_layout = _build_main(parent)
    aux_frame, aux_layout = _build_aux(parent)

    panels["sidebar"] = sidebar_frame
    panels["main"] = main_frame
    panels["aux"] = aux_frame

    # Slot blocks are mounted inside the main and aux panels for easy replacement.
    main_slot = QVBoxLayout()
    main_slot.setSpacing(10)
    main_layout.addLayout(main_slot, 1)
    main_slot.addWidget(
        make_placeholder(
            "Primary Slot",
            "Drop in console output, charts, table views, custom dashboards, or any widget tree.",
            icon="console",
            parent=main_frame,
        )
    )

    aux_slot = QVBoxLayout()
    aux_slot.setSpacing(10)
    aux_layout.addLayout(aux_slot, 1)
    aux_slot.addWidget(
        make_placeholder(
            "Secondary Slot",
            "Use this area for logs, details, metrics, timelines, or inspectors.",
            icon="details",
            parent=aux_frame,
        )
    )

    sidebar_slot = QVBoxLayout()
    sidebar_slot.setSpacing(8)
    sidebar_layout.addLayout(sidebar_slot)
    sidebar_slot.addWidget(
        make_placeholder(
            "Sidebar Slot",
            "Inject extra controls here without changing core shell logic.",
            icon="panel",
            parent=sidebar_frame,
        )
    )

    slot_layouts["main"] = main_slot
    slot_layouts["aux"] = aux_slot
    slot_layouts["sidebar"] = sidebar_slot

    for name in order:
        if name == "sidebar" and show_sidebar:
            root_layout.addWidget(sidebar_frame, 4)
        elif name == "main":
            root_layout.addWidget(main_frame, 6)
        elif name == "aux" and show_aux:
            root_layout.addWidget(aux_frame, 4)
    root_layout.addStretch(0)

    return WorkspaceRefs(
        root_layout=root_layout,
        panels=panels,
        slot_layouts=slot_layouts,
        workspace_entry=workspace_entry if show_sidebar else None,
        mode_combo=mode_combo if show_sidebar else None,
        view_combo=view_combo if show_sidebar else None,
    )


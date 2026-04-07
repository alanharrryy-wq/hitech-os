from __future__ import annotations

import time
from collections import deque
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QFrame, QVBoxLayout, QWidget

from ..chrome.frameless import FramelessResizeController
from ..chrome.titlebar import WindowChromeBar
from ..common.constants import WINDOW_HEIGHT, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_WIDTH
from ..common.types import TemplateConsoleConfig
from ..effects.polish import repolish
from ..effects.shadow import apply_shadow
from ..layout.scene import build_glass_dialog_scene
from ..panels.footer import FooterRefs, build_footer
from ..panels.hero import HeroRefs, build_hero_panel
from ..panels.toolbar import ToolbarRefs, build_toolbar_panel
from ..panels.workspace import WorkspaceRefs, build_workspace_panel
from ..style.scale import apply_layout_scale, normalize_scale
from ..style.stylesheet import build_stylesheet
from ..themes.catalog import THEME_LABELS, normalize_theme, resolve_theme


class TemplateConsoleWindow(QDialog):
    def __init__(self, config: TemplateConsoleConfig | None = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config or TemplateConsoleConfig()
        self._active_theme = normalize_theme(self.config.theme_id)
        self._active_scale = normalize_scale(self.config.ui_scale)
        self._floating_progress = None
        self._perf_timer: QTimer | None = None
        self._perf_fps_samples: deque[float] = deque(maxlen=8)
        self._perf_paint_ms_samples: deque[float] = deque(maxlen=8)
        self._perf_last_state = "ok"
        self._perf_last_issue = ""

        self.setWindowTitle(self.config.window_title)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setModal(False)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self._resize_controller = FramelessResizeController(self, margin=14, edge_hit=12, corner_hit=24)

        self.hero_refs: HeroRefs | None = None
        self.toolbar_refs: ToolbarRefs | None = None
        self.workspace_refs: WorkspaceRefs | None = None
        self.footer_refs: FooterRefs | None = None

        self._build_ui()
        self.apply_theme(self._active_theme, force=True)
        self.apply_ui_scale(self._active_scale, force=True)
        self._init_performance_visualizer()

    def _build_ui(self) -> None:
        outer, content_layer, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._active_theme,
            variant="selector",
            margins=(0, 0, 0, 0),
            motion_enabled=True,
            apply_stylesheet=False,
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content_layer)
        scene_layout.setContentsMargins(10, 10, 10, 10)
        scene_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("Shell")
        shell.setProperty("variant", "selector")
        apply_shadow(shell, blur=42.0, y_offset=13.0, alpha=72, color=QColor(6, 18, 30, 96))
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 22, 22, 22)
        shell_layout.setSpacing(16)

        self.window_chrome = WindowChromeBar(
            self,
            title=self.windowTitle(),
            on_close=self.close,
            allow_minimize=True,
            allow_maximize=True,
            title_icon=self.config.hero_icon,
        )
        shell_layout.addWidget(self.window_chrome)

        self.hero_refs = build_hero_panel(
            shell,
            eyebrow=self.config.hero_eyebrow,
            title=self.config.hero_title,
            subtitle=self.config.hero_subtitle,
            title_icon=self.config.hero_icon,
            chips=self.config.hero_chips,
        )
        shell_layout.addWidget(self.hero_refs.frame)

        self.toolbar_refs = build_toolbar_panel(
            shell,
            actions=self.config.toolbar_actions,
            on_action=self._on_toolbar_action,
            scale_id=self._active_scale,
            on_scale_changed=self.apply_ui_scale,
            theme_labels=THEME_LABELS,
            selected_theme_label=resolve_theme(self._active_theme).label,
            on_theme_changed=self._on_theme_combo_changed,
        )
        shell_layout.addWidget(self.toolbar_refs.frame)

        self.workspace_refs = build_workspace_panel(
            shell,
            order=self.config.panel_order,
            show_sidebar=self.config.show_sidebar,
            show_aux=self.config.show_aux,
        )
        shell_layout.addLayout(self.workspace_refs.root_layout, 1)

        self.footer_refs = build_footer(shell, hint=self.config.footer_hint)
        shell_layout.addWidget(self.footer_refs.frame)

    def _init_performance_visualizer(self) -> None:
        if self.toolbar_refs is None or self.toolbar_refs.perf_label is None:
            return
        if self._perf_timer is None:
            self._perf_timer = QTimer(self)
            self._perf_timer.setInterval(500)
            self._perf_timer.timeout.connect(self._refresh_performance_visualizer)
        if not self._perf_timer.isActive():
            self._perf_timer.start()
        self._refresh_performance_visualizer()

    def _refresh_performance_visualizer(self) -> None:
        if self.toolbar_refs is None or self.toolbar_refs.perf_label is None:
            return

        snapshot: dict[str, float | bool] = {}
        getter = getattr(self._glass_backdrop, "performance_snapshot", None)
        if callable(getter):
            try:
                snapshot = getter()
            except Exception:
                snapshot = {}

        raw_fps = float(snapshot.get("fps", 0.0) or 0.0)
        paint_ms = float(snapshot.get("paint_ms", 0.0) or 0.0)
        motion_interval_ms = float(snapshot.get("motion_interval_ms", 0.0) or 0.0)
        is_active = bool(snapshot.get("active", True))

        cadence_fps = 0.0
        if motion_interval_ms > 0.0:
            cadence_fps = 1000.0 / max(1.0, motion_interval_ms)

        effective_fps = raw_fps
        if effective_fps <= 0.0 and cadence_fps > 0.0 and is_active:
            effective_fps = cadence_fps

        if effective_fps > 0.0:
            self._perf_fps_samples.append(effective_fps)
        if paint_ms > 0.0:
            self._perf_paint_ms_samples.append(paint_ms)

        smoothed_fps = (
            sum(self._perf_fps_samples) / float(len(self._perf_fps_samples))
            if self._perf_fps_samples
            else effective_fps
        )
        smoothed_paint_ms = (
            sum(self._perf_paint_ms_samples) / float(len(self._perf_paint_ms_samples))
            if self._perf_paint_ms_samples
            else paint_ms
        )

        state = "ok"
        issue = ""

        cadence_gap = cadence_fps > 0.0 and smoothed_fps > 0.0 and smoothed_fps < (cadence_fps * 0.62)
        cadence_issue = cadence_gap and motion_interval_ms <= 30.0 and is_active

        if not is_active:
            text = "perf · idle"
        else:
            if smoothed_fps > 0.0 and smoothed_paint_ms > 0.0:
                text = f"{int(round(smoothed_fps)):02d} fps · {smoothed_paint_ms:.1f} ms"
            elif cadence_fps > 0.0:
                text = f"{int(round(cadence_fps)):02d} fps · live"
            else:
                text = "perf · live"

            if smoothed_paint_ms >= 24.0 or (cadence_issue and smoothed_fps < 28.0):
                state = "error"
                issue = "render heavy" if smoothed_paint_ms >= 24.0 else "cadence low"
            elif smoothed_paint_ms >= 18.5 or (cadence_issue and smoothed_fps < 40.0):
                state = "warn"
                issue = "warm frame" if smoothed_paint_ms >= 18.5 else "cadence dip"

            if issue:
                text += f" · {issue}"

        label = self.toolbar_refs.perf_label

        if label.text() != text:
            label.setText(text)

        has_issue = bool(issue)
        if str(label.property("state") or "ok") != state:
            label.setProperty("state", state)
            label.style().unpolish(label)
            label.style().polish(label)
        if bool(label.property("has_issue")) != has_issue:
            label.setProperty("has_issue", has_issue)
            label.style().unpolish(label)
            label.style().polish(label)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._perf_timer is not None and self._perf_timer.isActive():
            self._perf_timer.stop()
        super().closeEvent(event)

    def _set_footer_state(self, text: str, tone: str) -> None:
        if self.footer_refs is None:
            return
        if self.footer_refs.state_chip.text() != text:
            self.footer_refs.state_chip.setText(text)
        current_tone = str(self.footer_refs.state_chip.property("tone") or "")
        if current_tone != tone:
            self.footer_refs.state_chip.setProperty("tone", tone)
            repolish(self.footer_refs.state_chip)

    def apply_theme(self, theme_id: str, *, force: bool = False) -> None:
        resolved_theme = normalize_theme(theme_id)
        if (not force) and resolved_theme == self._active_theme and self.styleSheet():
            return
        theme = resolve_theme(resolved_theme)
        self._active_theme = theme.theme_id
        self.setStyleSheet(build_stylesheet(theme.theme_id, self._active_scale))
        self._glass_backdrop.apply_theme(resolved_theme)
        self._perf_fps_samples.clear()
        self._perf_paint_ms_samples.clear()
        if self.toolbar_refs is not None and self.toolbar_refs.theme_combo is not None:
            idx = self.toolbar_refs.theme_combo.findText(theme.label)
            if idx >= 0 and self.toolbar_refs.theme_combo.currentIndex() != idx:
                self.toolbar_refs.theme_combo.blockSignals(True)
                self.toolbar_refs.theme_combo.setCurrentIndex(idx)
                self.toolbar_refs.theme_combo.blockSignals(False)
        self._refresh_performance_visualizer()

    def _on_theme_combo_changed(self, label: str) -> None:
        self.apply_theme(label)
        self._set_footer_state(f"Theme: {resolve_theme(label).label}", "accent")

    def apply_ui_scale(self, scale_id: str, *, force: bool = False) -> None:
        resolved = normalize_scale(scale_id)
        if (not force) and resolved == self._active_scale:
            return
        self._active_scale = resolved
        self._resize_controller.apply_scale(resolved)
        self.window_chrome.apply_scale(resolved)
        if self.toolbar_refs is not None and self.toolbar_refs.scale_selector is not None:
            self.toolbar_refs.scale_selector.set_scale(resolved)
        apply_layout_scale(self, resolved)
        self.setStyleSheet(build_stylesheet(self._active_theme, resolved))
        self._perf_fps_samples.clear()
        self._perf_paint_ms_samples.clear()
        self._glass_backdrop.update()
        self._refresh_performance_visualizer()

    def set_slot_widget(self, slot_name: str, widget: QWidget) -> bool:
        if self.workspace_refs is None:
            return False
        layout = self.workspace_refs.slot_layouts.get(slot_name)
        if layout is None:
            return False
        while layout.count():
            item = layout.takeAt(0)
            child = item.widget()
            if child is not None:
                child.setParent(None)
                child.deleteLater()
        layout.addWidget(widget)
        return True

    def _on_toolbar_action(self, action_id: str) -> None:
        if action_id == "refresh":
            self._set_footer_state(f"Refreshed {time.strftime('%H:%M:%S')}", "good")
            return

        if action_id == "toggle_sidebar":
            if self.workspace_refs is None:
                return
            sidebar = self.workspace_refs.panels.get("sidebar")
            if sidebar is None:
                return
            sidebar.setVisible(not sidebar.isVisible())
            self._set_footer_state("Sidebar hidden" if not sidebar.isVisible() else "Sidebar visible", "accent")
            return

        if action_id == "open_selector":
            from .selector_screen import SelectorLikeScreen

            dialog = SelectorLikeScreen(self, theme_id=self._active_theme, scale_id=self._active_scale)
            if dialog.exec():
                result = dialog.result_selection()
                self.apply_theme(result.theme_id)
                self.apply_ui_scale(result.scale_id)
                if self.workspace_refs and self.workspace_refs.workspace_entry is not None:
                    self.workspace_refs.workspace_entry.setText(result.workspace)
                self._set_footer_state(f"{result.mode} · {result.profile}", "good")
            else:
                self._set_footer_state("Selector closed", "neutral")
            return

        if action_id == "open_progress":
            from .progress_screen import ProgressScreen

            self._floating_progress = ProgressScreen(
                self,
                window_title="Template Console Progress",
                theme_id=self._active_theme,
                scale_id=self._active_scale,
                initial_status="Starting template job...",
            )
            self._floating_progress.start_demo_sequence()
            self._set_footer_state("Progress screen launched", "accent")
            return

        self._set_footer_state(f"Action: {action_id}", "neutral")

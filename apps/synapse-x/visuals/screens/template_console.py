from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QPushButton, QVBoxLayout, QWidget

from ..chrome.frameless import FramelessResizeController
from ..chrome.titlebar import WindowChromeBar
from ..common.constants import WINDOW_HEIGHT, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_WIDTH
from ..common.types import ActionSpec, TemplateConsoleConfig
from ..effects.polish import repolish
from ..effects.shadow import apply_shadow
from ..layout.scene import build_glass_dialog_scene
from ..panels.chart_slot import ChartSlotPanel
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
        self._chart_visible = self._resolve_initial_chart_visibility(self.config.toolbar_actions)

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
        self.chart_slot: ChartSlotPanel | None = None

        self._build_ui()
        self.apply_theme(self._active_theme, force=True)
        self.apply_ui_scale(self._active_scale, force=True)

    @staticmethod
    def _resolve_initial_chart_visibility(actions: list[ActionSpec]) -> bool:
        for spec in actions:
            if spec.action_id == "toggle_charts":
                return bool(spec.checked if spec.checkable else True)
        return True

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
        apply_shadow(shell, blur=30.0, y_offset=10.0, alpha=58)
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
            toolbar_title=self.config.toolbar_title,
        )
        shell_layout.addWidget(self.toolbar_refs.frame)

        self.workspace_refs = build_workspace_panel(
            shell,
            order=self.config.panel_order,
            show_sidebar=self.config.show_sidebar,
            show_aux=self.config.show_aux,
            sidebar_title=self.config.sidebar_title,
            main_title=self.config.main_title,
            aux_title=self.config.aux_title,
            show_sidebar_builtin_controls=self.config.show_sidebar_builtin_controls,
            sidebar_hint=self.config.sidebar_hint,
            main_hint=self.config.main_hint,
            aux_hint=self.config.aux_hint,
        )
        shell_layout.addLayout(self.workspace_refs.root_layout, 1)

        if self.config.show_aux:
            self.chart_slot = ChartSlotPanel(
                shell,
                empty_title=f"{self.config.aux_title} surface ready",
                empty_subtitle=self.config.aux_hint,
            )
            self._replace_slot_widget("aux", self.chart_slot)
            self.set_chart_visible(self._chart_visible, update_toolbar=False)

        self.footer_refs = build_footer(shell, hint=self.config.footer_hint)
        shell_layout.addWidget(self.footer_refs.frame)

    def _replace_slot_widget(self, slot_name: str, widget: QWidget) -> bool:
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

    def _toolbar_button(self, action_id: str) -> QPushButton | None:
        if self.toolbar_refs is None:
            return None
        widget = self.toolbar_refs.buttons.get(action_id)
        return widget if isinstance(widget, QPushButton) else None

    def _sync_action_button_state(self, action_id: str, checked: bool) -> None:
        button = self._toolbar_button(action_id)
        if button is None or not button.isCheckable():
            return
        if button.isChecked() == checked:
            return
        button.blockSignals(True)
        button.setChecked(checked)
        button.blockSignals(False)
        repolish(button)

    def _set_footer_state(self, text: str, tone: str) -> None:
        if self.footer_refs is None:
            return
        self.footer_refs.state_chip.setText(text)
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
        if self.toolbar_refs is not None and self.toolbar_refs.theme_combo is not None:
            idx = self.toolbar_refs.theme_combo.findText(theme.label)
            if idx >= 0 and self.toolbar_refs.theme_combo.currentIndex() != idx:
                self.toolbar_refs.theme_combo.blockSignals(True)
                self.toolbar_refs.theme_combo.setCurrentIndex(idx)
                self.toolbar_refs.theme_combo.blockSignals(False)

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
        self._glass_backdrop.update()

    def set_slot_widget(self, slot_name: str, widget: QWidget) -> bool:
        normalized_slot = str(slot_name or "").strip().lower()
        if normalized_slot in {"chart", "charts", "metrics"}:
            return self.set_chart_widget(widget)
        if not normalized_slot:
            return False
        return self._replace_slot_widget(normalized_slot, widget)

    def set_chart_widget(self, widget: QWidget) -> bool:
        if self.chart_slot is None:
            return False
        self.chart_slot.set_chart_widget(widget)
        if not self._chart_visible:
            self.chart_slot.set_chart_visible(False)
        self._set_footer_state("Chart widget attached", "good")
        return True

    def clear_chart_widget(self) -> bool:
        if self.chart_slot is None:
            return False
        self.chart_slot.clear_chart_widget(delete=False)
        self._set_footer_state("Chart widget cleared", "neutral")
        return True

    def show_chart_placeholder(
        self,
        message: str,
        *,
        title: str | None = None,
        details: tuple[str, ...] = (),
        footer: str = "Attach a chart widget when telemetry is ready.",
    ) -> bool:
        if self.chart_slot is None:
            return False
        self.chart_slot.show_placeholder(
            message,
            title=title or f"{self.config.aux_title} surface ready",
            details=details,
            footer=footer,
        )
        self._set_footer_state("Chart slot in standby", "neutral")
        return True

    def show_missing_chart_dependencies(self, missing: tuple[str, ...] | list[str]) -> bool:
        if self.chart_slot is None:
            return False
        self.chart_slot.show_missing_dependencies(missing)
        missing_text = ", ".join(sorted({str(item).strip() for item in missing if str(item).strip()}))
        footer_text = "Chart dependencies missing"
        if missing_text:
            footer_text = f"Chart dependencies missing: {missing_text}"
        self._set_footer_state(footer_text, "warn")
        return True

    def set_chart_visible(self, visible: bool, *, update_toolbar: bool = True) -> bool:
        if self.chart_slot is None:
            return False
        self._chart_visible = bool(visible)
        self.chart_slot.set_chart_visible(self._chart_visible)
        if update_toolbar:
            self._sync_action_button_state("toggle_charts", self._chart_visible)
        self._set_footer_state("Charts visible" if self._chart_visible else "Charts hidden", "accent")
        return True

    def toggle_chart_visibility(self) -> bool:
        return self.set_chart_visible(not self._chart_visible)

    def _on_toolbar_action(self, action_id: str) -> None:
        if action_id == "refresh":
            self._set_footer_state(f"Refreshed {time.strftime('%H:%M:%S')}", "good")
            return

        if action_id == "toggle_charts":
            button = self._toolbar_button("toggle_charts")
            target_state = (button.isChecked() if button is not None and button.isCheckable() else not self._chart_visible)
            self.set_chart_visible(target_state, update_toolbar=False)
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

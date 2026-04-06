from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from ..chrome.frameless import FramelessResizeController
from ..chrome.titlebar import WindowChromeBar
from ..controls.chips import create_chip
from ..effects.polish import enable_card_hover, repolish
from ..effects.shadow import apply_shadow
from ..layout.scene import build_glass_dialog_scene
from ..style.scale import apply_layout_scale, normalize_scale
from ..style.stylesheet import build_stylesheet
from ..themes.catalog import normalize_theme
from ..widgets.primitives import make_separator


class ProgressScreen(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        window_title: str = "Progress",
        initial_status: str = "Preparing...",
        initial_detail: str = "",
        theme_id: str = "silver_frost_cyan",
        scale_id: str = "100",
    ) -> None:
        super().__init__(parent)
        self._last_pump = 0.0
        self._finalized = False
        self._spinner_frames = ("Working", "Working.", "Working..", "Working...")
        self._spinner_index = 0
        self._theme_id = normalize_theme(theme_id)
        self._scale_id = normalize_scale(scale_id)

        self.setWindowTitle(window_title)
        self.setModal(False)
        self.setMinimumSize(780, 320)
        self.resize(860, 340)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self._resize_controller = FramelessResizeController(self, margin=14, edge_hit=12, corner_hit=24)
        self.setStyleSheet(build_stylesheet(self._theme_id, self._scale_id))

        self._build_ui()
        self.apply_ui_scale(self._scale_id, force=True)
        self.set_status(initial_status, initial_detail)
        self.set_indeterminate(True)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(240)
        self._pulse_timer.timeout.connect(self._advance_spinner)
        self._pulse_timer.start()

        self.show()
        self.raise_()
        self.activateWindow()
        self._pump_events(force=True)

    def _build_ui(self) -> None:
        outer, content_layer, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_id,
            variant="progress",
            margins=(0, 0, 0, 0),
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content_layer)
        scene_layout.setContentsMargins(10, 10, 10, 10)
        scene_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("Shell")
        shell.setProperty("variant", "progress")
        apply_shadow(shell, blur=28.0, y_offset=10.0, alpha=54)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(20, 20, 20, 20)
        shell_layout.setSpacing(16)

        self.window_chrome = WindowChromeBar(
            self,
            title=self.windowTitle(),
            on_close=self.close,
            allow_minimize=True,
            allow_maximize=False,
            title_icon="activity",
        )
        shell_layout.addWidget(self.window_chrome)

        hero = QFrame()
        hero.setProperty("card", "hero")
        apply_shadow(hero, blur=20.0, y_offset=6.0, alpha=16)
        enable_card_hover(hero)
        shell_layout.addWidget(hero)

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(10)

        hero_top = QHBoxLayout()
        hero_top.setSpacing(12)
        hero_layout.addLayout(hero_top)

        hero_stack = QVBoxLayout()
        hero_stack.setSpacing(6)
        hero_top.addLayout(hero_stack, 1)

        eyebrow = QLabel("Execution")
        eyebrow.setProperty("role", "eyebrow")
        hero_stack.addWidget(eyebrow, 0, Qt.AlignLeft)

        title = QLabel("Running template workflow")
        title.setProperty("role", "title")
        hero_stack.addWidget(title)

        subtitle = QLabel("Live progress output for long-running tasks. Safe to close at any time.")
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        hero_stack.addWidget(subtitle)

        chip_stack = QVBoxLayout()
        chip_stack.setSpacing(8)
        hero_top.addLayout(chip_stack, 0)

        self.state_chip = create_chip("Running", tone="accent", icon="activity", parent=hero)
        chip_stack.addWidget(self.state_chip, 0, Qt.AlignRight)
        chip_stack.addWidget(create_chip("Glass Console", tone="neutral", icon="spark", parent=hero), 0, Qt.AlignRight)
        chip_stack.addStretch(1)

        hero_line = make_separator()
        hero_line.setProperty("tone", "glow")
        repolish(hero_line)
        hero_layout.addWidget(hero_line)

        body = QFrame()
        body.setProperty("card", "true")
        apply_shadow(body, blur=16.0, y_offset=6.0, alpha=12)
        enable_card_hover(body)
        shell_layout.addWidget(body)

        layout = QVBoxLayout(body)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.status_label = QLabel("")
        self.status_label.setProperty("role", "section")
        layout.addWidget(self.status_label)

        self.detail_label = QLabel("")
        self.detail_label.setProperty("role", "mono")
        self.detail_label.setWordWrap(True)
        self.detail_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.detail_label)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

    def apply_ui_scale(self, scale_id: str, *, force: bool = False) -> None:
        resolved = normalize_scale(scale_id)
        if (not force) and resolved == self._scale_id:
            return
        self._scale_id = resolved
        self._resize_controller.apply_scale(resolved)
        self.window_chrome.apply_scale(resolved)
        apply_layout_scale(self, resolved)
        self.setStyleSheet(build_stylesheet(self._theme_id, resolved))
        self._glass_backdrop.update()

    def _pump_events(self, *, force: bool = False) -> None:
        app = self.window().windowHandle()
        now = time.monotonic()
        if force or (now - self._last_pump) >= 0.08:
            self._last_pump = now
            if app is not None:
                # Keep UI responsive without forcing global event pumping.
                self.repaint()

    def _set_state_chip(self, text: str, tone: str) -> None:
        self.state_chip.setText(text)
        self.state_chip.setProperty("tone", tone)
        repolish(self.state_chip)

    def _advance_spinner(self) -> None:
        if self._finalized:
            return
        if self.progress.minimum() == 0 and self.progress.maximum() == 0:
            self._spinner_index = (self._spinner_index + 1) % len(self._spinner_frames)
            self._set_state_chip(self._spinner_frames[self._spinner_index], "accent")

    def set_indeterminate(self, enabled: bool = True) -> None:
        if enabled:
            self.progress.setRange(0, 0)
            self.progress.setFormat("")
            self._set_state_chip(self._spinner_frames[self._spinner_index], "accent")
        else:
            maximum = max(1, self.progress.maximum())
            self.progress.setRange(0, maximum)
            if self.progress.value() <= 0:
                self.progress.setValue(0)
            self.progress.setFormat("%p%")
            self._set_state_chip("Running", "accent")

    def set_status(self, text: str, detail: str = "") -> None:
        self.status_label.setText(text or "")
        self.detail_label.setText(detail or "")
        self._pump_events()

    def set_progress(
        self,
        value: int,
        maximum: Optional[int] = None,
        *,
        status: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        if maximum is not None:
            self.progress.setRange(0, max(1, int(maximum)))
        elif self.progress.minimum() == 0 and self.progress.maximum() == 0:
            self.progress.setRange(0, 100)

        max_value = max(1, self.progress.maximum())
        self.progress.setValue(max(0, min(int(value), max_value)))
        self.progress.setFormat("%p%")
        self._set_state_chip("Running", "accent")

        if status is not None:
            self.status_label.setText(status)
        if detail is not None:
            self.detail_label.setText(detail)
        self._pump_events()

    def finalize(self, text: str, detail: str = "", success: bool = True) -> None:
        self._finalized = True
        if self._pulse_timer.isActive():
            self._pulse_timer.stop()
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.status_label.setText(text or "")
        self.detail_label.setText(detail or "")
        self._set_state_chip("Done" if success else "Finished", "good" if success else "warn")
        self._pump_events(force=True)

    def start_demo_sequence(self) -> None:
        self.set_indeterminate(False)
        steps = [
            (15, "Loading workspace context...", "Collecting controls and layout state."),
            (35, "Preparing shell composition...", "Resolving panel order and slot bindings."),
            (58, "Applying theme contract...", "Materializing surfaces, chips, and controls."),
            (79, "Binding interactions...", "Wiring toolbar actions and panel slots."),
            (100, "Template ready", "Progress screen demo completed."),
        ]
        self._demo_index = 0

        def tick() -> None:
            if self._demo_index >= len(steps):
                self.finalize("Template ready", "You can close this window or keep it open.", success=True)
                return
            value, status, detail = steps[self._demo_index]
            self.set_progress(value, 100, status=status, detail=detail)
            self._demo_index += 1

        self._demo_timer = QTimer(self)
        self._demo_timer.setInterval(480)
        self._demo_timer.timeout.connect(tick)
        self._demo_timer.start()
        tick()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if hasattr(self, "_pulse_timer") and self._pulse_timer.isActive():
            self._pulse_timer.stop()
        if hasattr(self, "_demo_timer") and self._demo_timer.isActive():
            self._demo_timer.stop()
        super().closeEvent(event)

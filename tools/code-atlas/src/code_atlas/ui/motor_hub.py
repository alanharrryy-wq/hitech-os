# CODE_ATLAS_MOTOR_HUB_PREMIUM_V06
"""Premium Frost Motor Hub dialog for Code Atlas.

Skin-only upgrade over the modular Motor Hub:
- Keeps the existing dialog size and layout anatomy.
- Adds a non-layout animated frosted ambience layer, so motion does not affect sizeHint.
- Uses local pyside6_glass stylesheet tokens when available, plus organic non-repeating Qt-painted ambience.
- Delegates execution to MotorProcessRunner, which uses QProcess.
"""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PySide6.QtCore import QPointF, Qt, QElapsedTimer, QTimer, QUrl
from PySide6.QtGui import QBrush, QColor, QDesktopServices, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from forgeos.shared.pyside6_glass.theme import build_stylesheet as _build_glass_stylesheet
except Exception:  # optional local visual package; never block the hub
    _build_glass_stylesheet = None

from code_atlas.motors.registry import build_motor_registry, grouped_motor_registry
from code_atlas.motors.results import DEFAULT_OUTPUT_ROOT, find_latest_fail_zip, find_latest_result_zip
from code_atlas.motors.runner import MotorProcessRunner
from code_atlas.motors.specs import MotorSpec


class _AmbientBackdrop(QWidget):
    """Living premium Frost ambience that does not participate in layout.

    This layer is intentionally outside layout anatomy. It paints animated
    fog drift, moving light currents and non-repeating spark motes behind the
    existing widgets, so the Motor Hub keeps its size while the background
    finally feels alive instead of wallpaper-static.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._phase = 0.0
        self._time = 0.0
        self._clock = QElapsedTimer()
        self._clock.start()
        rng = random.Random(906_051)

        self._fog_orbs = [
            (
                rng.uniform(-0.12, 1.08),
                rng.uniform(-0.10, 1.10),
                rng.uniform(0.22, 0.62),
                rng.uniform(0.045, 0.155),
                rng.uniform(0.22, 0.90),
                rng.uniform(0.0, math.pi * 2.0),
            )
            for _ in range(11)
        ]
        self._dust = [
            (
                rng.random(),
                rng.random(),
                rng.uniform(0.35, 1.55),
                rng.uniform(3.0, 18.0),
                rng.uniform(-5.0, 8.0),
                rng.uniform(0.14, 1.05),
                rng.uniform(0.0, math.pi * 2.0),
            )
            for _ in range(138)
        ]
        self._glints = [
            (
                rng.random(),
                rng.random(),
                rng.uniform(5.0, 13.0),
                rng.uniform(0.055, 0.22),
                rng.uniform(0.22, 1.0),
                rng.uniform(0.0, math.pi * 2.0),
            )
            for _ in range(22)
        ]
        self._soft_blooms = [
            (
                rng.random(),
                rng.random(),
                rng.uniform(22.0, 76.0),
                rng.uniform(0.028, 0.095),
                rng.uniform(0.18, 0.70),
                rng.uniform(0.0, math.pi * 2.0),
            )
            for _ in range(24)
        ]
        self._currents = [
            (
                rng.uniform(-0.30, 0.92),
                rng.uniform(-0.18, 0.62),
                rng.uniform(0.050, 0.135),
                rng.uniform(0.25, 0.82),
                rng.uniform(0.38, 1.18),
            )
            for _ in range(7)
        ]

        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        self._time = self._clock.elapsed() / 1000.0
        self._phase = (self._time * 0.82) % (math.pi * 2.0)
        if self.isVisible():
            self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        w = max(1, rect.width())
        h = max(1, rect.height())
        t = self._time

        base = QLinearGradient(
            QPointF(w * (0.08 + math.sin(t * 0.09) * 0.030), 0),
            QPointF(w * (0.96 + math.cos(t * 0.07) * 0.040), h),
        )
        base.setColorAt(0.0, QColor(58, 68, 79, 196))
        base.setColorAt(0.28, QColor(72, 89, 99, 176))
        base.setColorAt(0.58, QColor(35, 61, 84, 188))
        base.setColorAt(0.82, QColor(18, 34, 62, 202))
        base.setColorAt(1.0, QColor(5, 10, 22, 218))
        painter.fillRect(rect, base)

        painter.setCompositionMode(QPainter.CompositionMode_Screen)
        self._draw_fog_orbs(painter, w, h, t)
        self._draw_living_currents(painter, w, h, t)
        self._draw_glass_sheen(painter, w, h, t)
        self._draw_soft_blooms(painter, w, h, t)
        self._draw_dust(painter, w, h, t)
        self._draw_glints(painter, w, h, t)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        vignette = QRadialGradient(
            QPointF(w * (0.48 + math.sin(t * 0.045) * 0.05), h * (0.42 + math.cos(t * 0.038) * 0.04)),
            max(w, h) * 0.83,
        )
        vignette.setColorAt(0.0, QColor(255, 255, 255, 0))
        vignette.setColorAt(0.70, QColor(5, 12, 24, 0))
        vignette.setColorAt(1.0, QColor(0, 3, 10, 92))
        painter.setPen(Qt.NoPen)
        painter.setBrush(vignette)
        painter.drawRect(rect)

    def _draw_fog_orbs(self, painter: QPainter, w: int, h: int, t: float) -> None:
        for idx, (nx, ny, scale, speed, alpha_mul, seed) in enumerate(self._fog_orbs):
            drift_x = math.sin(t * speed + seed) * w * (0.055 + 0.011 * (idx % 3))
            drift_y = math.cos(t * (speed * 0.77) + seed * 0.71) * h * (0.046 + 0.010 * (idx % 4))
            radius = max(w, h) * scale
            alpha = int(30 + 42 * alpha_mul)
            hue = QColor(222, 248, 255, alpha)
            if idx % 3 == 1:
                hue = QColor(164, 225, 255, max(18, alpha - 10))
            elif idx % 3 == 2:
                hue = QColor(255, 255, 255, max(18, alpha - 14))
            self._draw_orb(painter, QPointF(nx * w + drift_x, ny * h + drift_y), radius, hue)

    def _draw_orb(self, painter: QPainter, center: QPointF, radius: float, color: QColor) -> None:
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0.0, color)
        middle = QColor(color)
        middle.setAlpha(max(0, int(color.alpha() * 0.26)))
        glow.setColorAt(0.36, middle)
        haze = QColor(color)
        haze.setAlpha(max(0, int(color.alpha() * 0.075)))
        glow.setColorAt(0.68, haze)
        edge = QColor(color)
        edge.setAlpha(0)
        glow.setColorAt(1.0, edge)
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(center, radius, radius)

    def _draw_living_currents(self, painter: QPainter, w: int, h: int, t: float) -> None:
        span = w + h + 520.0
        for idx, (origin_x, origin_y, speed, alpha_mul, width_mul) in enumerate(self._currents):
            travel = ((t * speed * span) + idx * 173.0) % span - 260.0
            start = QPointF(origin_x * w + travel, origin_y * h - 80.0)
            end = QPointF(start.x() + w * (0.62 + idx * 0.035), h + 90.0)
            beam = QLinearGradient(start, end)
            beam.setColorAt(0.0, QColor(255, 255, 255, 0))
            beam.setColorAt(0.43, QColor(220, 248, 255, int(10 + 24 * alpha_mul)))
            beam.setColorAt(0.50, QColor(134, 225, 255, int(20 + 36 * alpha_mul)))
            beam.setColorAt(0.57, QColor(255, 255, 255, int(8 + 18 * alpha_mul)))
            beam.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(beam), 0.75 + width_mul))
            painter.drawLine(start, end)

    def _draw_glass_sheen(self, painter: QPainter, w: int, h: int, t: float) -> None:
        for idx, width in enumerate((1.00, 1.55, 0.82, 0.64)):
            drift = math.sin(t * (0.22 + idx * 0.07) + idx) * 58.0 + t * (8.0 + idx * 3.5)
            sheen = QLinearGradient(QPointF(w * (0.03 + idx * 0.07), 0), QPointF(w * (0.70 + idx * 0.10), h))
            sheen.setColorAt(0.0, QColor(255, 255, 255, 0))
            sheen.setColorAt(0.47, QColor(246, 253, 255, 12 + idx * 4))
            sheen.setColorAt(0.54, QColor(142, 224, 255, 20 + idx * 5))
            sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(sheen), width))
            painter.drawLine(QPointF(w * -0.08 + drift, -34), QPointF(w * (0.72 + idx * 0.14) + drift, h + 36))

    def _draw_soft_blooms(self, painter: QPainter, w: int, h: int, t: float) -> None:
        for idx, (nx, ny, radius, speed, alpha_mul, seed) in enumerate(self._soft_blooms):
            x = (nx * w + math.sin(t * speed + seed) * 26.0 + t * (3.5 + idx % 5)) % (w + radius * 2.0) - radius
            y = ny * h + math.cos(t * (speed * 0.82) + seed * 0.77) * 22.0
            pulse = 0.62 + 0.38 * math.sin(t * (0.44 + speed) + seed)
            color = QColor(236, 252, 255, int((10 + alpha_mul * 23) * pulse))
            glow = QRadialGradient(QPointF(x, y), radius)
            glow.setColorAt(0.0, color)
            mid = QColor(color)
            mid.setAlpha(max(0, int(color.alpha() * 0.24)))
            glow.setColorAt(0.42, mid)
            edge = QColor(color)
            edge.setAlpha(0)
            glow.setColorAt(1.0, edge)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(x, y), radius, radius)

    def _draw_dust(self, painter: QPainter, w: int, h: int, t: float) -> None:
        painter.setPen(Qt.NoPen)
        for idx, (nx, ny, radius, vx, vy, alpha_mul, seed) in enumerate(self._dust):
            x = (nx * w + t * vx + math.sin(t * 0.36 + seed) * 10.0) % (w + 40.0) - 20.0
            y = (ny * h + t * vy + math.cos(t * 0.31 + seed * 0.73) * 8.0) % (h + 40.0) - 20.0
            pulse = 0.42 + 0.58 * math.sin(t * (0.82 + alpha_mul * 0.40) + seed)
            alpha = int((7 + 38 * alpha_mul) * max(0.08, pulse))
            painter.setBrush(QColor(233, 250, 255, max(3, alpha)))
            painter.drawEllipse(QPointF(x, y), radius, radius)

    def _draw_glints(self, painter: QPainter, w: int, h: int, t: float) -> None:
        for idx, (nx, ny, length, speed, alpha_mul, seed) in enumerate(self._glints):
            pulse = 0.5 + 0.5 * math.sin(t * (1.20 + speed * 4.0) + seed)
            if pulse < 0.24:
                continue
            x = (nx * w + t * (18.0 * speed + 1.8) + math.sin(t * 0.31 + seed) * 12.0) % (w + 70.0) - 35.0
            y = ny * h + math.cos(t * 0.25 + seed * 0.69) * 14.0
            alpha = int((20 + 52 * alpha_mul) * pulse)
            painter.setPen(QPen(QColor(242, 253, 255, alpha), 0.76))
            painter.drawLine(QPointF(x - length, y), QPointF(x + length, y))
            painter.drawLine(QPointF(x, y - length), QPointF(x, y + length))
            if idx % 3 == 0:
                painter.setPen(QPen(QColor(142, 225, 255, max(0, alpha - 18)), 0.58))
                painter.drawLine(QPointF(x - length * 0.50, y - length * 0.50), QPointF(x + length * 0.50, y + length * 0.50))
                painter.drawLine(QPointF(x - length * 0.50, y + length * 0.50), QPointF(x + length * 0.50, y - length * 0.50))


class MotorHubDialog(QDialog):
    """Modular hub for Atlas, Playwright Mamastrophic and PRISMA_CTX."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Motores PRISMA")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setMinimumSize(1080, 720)
        self.resize(1180, 760)

        self._registry = build_motor_registry()
        self._grouped = grouped_motor_registry()
        self._last_result_zip: Path | None = None
        self._last_fail_zip: Path | None = None
        self._ambient = _AmbientBackdrop(self)
        self._ambient.lower()
        self._runner = MotorProcessRunner(self)
        self._runner.started.connect(self._on_started)
        self._runner.output_ready.connect(self._append_process_output)
        self._runner.finished.connect(self._on_finished)
        self._runner.failed_to_start.connect(self._on_failed_to_start)

        self._build_ui()
        self._sync_ambient_geometry()
        self._refresh_results()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._sync_ambient_geometry()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().showEvent(event)
        self._sync_ambient_geometry()

    def _sync_ambient_geometry(self) -> None:
        if hasattr(self, "_ambient"):
            self._ambient.setGeometry(self.rect())
            self._ambient.lower()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(18, 18, 18, 18)
        main.setSpacing(12)

        header = QFrame()
        header.setObjectName("MotorHubHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(6)

        title = QLabel("Motores PRISMA")
        title.setObjectName("MotorHubTitle")
        subtitle = QLabel(
            "Atlas, Playwright Mamastrophic y PRISMA_CTX desde un hub modular. "
            "Ejecución con QProcess, consola viva y sin congelar la interfaz."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("MotorHubSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main.addWidget(header)

        self.status_label = QLabel("Estado: listo")
        self.status_label.setObjectName("MotorHubStatus")
        self.status_label.setProperty("statusKind", "idle")
        main.addWidget(self.status_label)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("MotorHubTabs")
        self.tabs.addTab(self._build_motor_tab("Atlas"), "Atlas")
        self.tabs.addTab(self._build_motor_tab("Playwright"), "Playwright")
        self.tabs.addTab(self._build_motor_tab("PRISMA_CTX"), "PRISMA_CTX")
        self.tabs.addTab(self._build_results_tab(), "Resultados")
        main.addWidget(self.tabs, 1)

        console_label = QLabel("Consola viva")
        console_label.setObjectName("MotorHubSection")
        main.addWidget(console_label)

        self.console = QPlainTextEdit()
        self.console.setObjectName("MotorHubConsole")
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(5000)
        self.console.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.console.setPlaceholderText("Aquí aparecerá stdout/stderr del motor seleccionado.")
        main.addWidget(self.console, 2)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        main.addLayout(bottom)

        bottom.addWidget(self._button("Abrir F:\\descargasf", self._open_downloads, kind="secondary"))
        bottom.addWidget(self._button("Abrir último result ZIP", self._open_last_result, kind="secondary"))
        bottom.addWidget(self._button("Abrir último fail ZIP", self._open_last_fail, kind="secondary"))
        bottom.addWidget(self._button("Abrir raíz Playwright", self._open_playwright_root, kind="ghost"))
        bottom.addWidget(self._button("Abrir raíz PRISMA_CTX", self._open_prisma_ctx_root, kind="ghost"))
        bottom.addStretch(1)
        bottom.addWidget(self._button("Refrescar resultados", self._refresh_results, kind="secondary"))
        bottom.addWidget(self._button("Cerrar", self.close, kind="quiet"))

        self.setStyleSheet(_premium_stylesheet())
        self._apply_frost_depth_effects()

    def _build_motor_tab(self, group: str) -> QWidget:
        tab = QWidget()
        tab.setObjectName("MotorHubTabPage")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        specs = self._grouped.get(group, [])
        if not specs:
            empty = QLabel("No hay motores registrados para este grupo.")
            empty.setObjectName("MotorHubHint")
            empty.setWordWrap(True)
            layout.addWidget(empty)
            layout.addStretch(1)
            return tab

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        layout.addLayout(grid)

        for row, spec in enumerate(specs):
            label = QLabel("<b>{0}</b><br>{1}".format(_html_escape(spec.label), _html_escape(spec.description)))
            label.setObjectName("MotorHubMotorLabel")
            label.setProperty("motorGroup", spec.group)
            label.setWordWrap(True)
            label.setTextFormat(Qt.RichText)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            run_button = self._button("Ejecutar " + spec.label, lambda checked=False, item=spec: self._run_motor(item), kind="primary")
            grid.addWidget(label, row, 0)
            grid.addWidget(run_button, row, 1)

        layout.addStretch(1)
        return tab

    def _build_results_tab(self) -> QWidget:
        tab = QWidget()
        tab.setObjectName("MotorHubTabPage")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.result_label = QLabel("Último result ZIP: pendiente")
        self.result_label.setObjectName("MotorHubResultLabel")
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.fail_label = QLabel("Último fail ZIP: pendiente")
        self.fail_label.setObjectName("MotorHubResultLabel")
        self.fail_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.result_label)
        layout.addWidget(self.fail_label)

        actions = QHBoxLayout()
        actions.addWidget(self._button("Abrir result", self._open_last_result, kind="secondary"))
        actions.addWidget(self._button("Abrir fail", self._open_last_fail, kind="secondary"))
        actions.addWidget(self._button("Abrir carpeta de salida", self._open_downloads, kind="ghost"))
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addStretch(1)
        return tab

    def _button(self, text: str, callback, *, kind: str = "secondary") -> QPushButton:
        button = QPushButton(text)
        button.setProperty("buttonKind", kind)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def _apply_frost_depth_effects(self) -> None:
        """Apply lightweight native PySide6 glass depth without touching layout size."""
        targets: list[tuple[QWidget | None, int, int, QColor]] = [
            (self.findChild(QFrame, "MotorHubHeader"), 34, 10, QColor(7, 14, 25, 112)),
            (self.status_label, 24, 6, QColor(7, 14, 25, 72)),
            (self.tabs, 30, 9, QColor(7, 14, 25, 96)),
            (self.console, 24, 7, QColor(7, 14, 25, 88)),
        ]
        for widget, blur, offset_y, color in targets:
            if widget is None:
                continue
            widget.setAttribute(Qt.WA_StyledBackground, True)
            effect = QGraphicsDropShadowEffect(widget)
            effect.setBlurRadius(blur)
            effect.setOffset(0, offset_y)
            effect.setColor(color)
            widget.setGraphicsEffect(effect)

    def _run_motor(self, spec: MotorSpec) -> None:
        if self._runner.is_running():
            QMessageBox.warning(self, "Motor Hub", "Ya hay un motor corriendo. Espera a que termine.")
            return

        self.console.clear()
        self._append_console("== Motor: {0} ==".format(spec.label))
        self._append_console("Root: {0}".format(spec.root))
        self._append_console("Command: {0}".format(spec.command_preview()))
        self._append_console("")
        try:
            self._runner.start(spec)
        except Exception as exc:
            self._set_status("Estado: FAIL al iniciar {0}".format(spec.label), "fail")
            QMessageBox.critical(self, "Motor Hub", str(exc))

    def _on_started(self, spec: MotorSpec) -> None:
        self._set_status("Estado: corriendo {0}".format(spec.label), "running")

    def _append_process_output(self, channel: str, text: str) -> None:
        prefix = "[stderr] " if channel == "stderr" else ""
        for line in text.splitlines():
            self._append_console(prefix + line)

    def _on_finished(self, spec: MotorSpec, exit_code: int, exit_status: str) -> None:
        status = "PASS" if exit_code == 0 else "FAIL"
        self._set_status("Estado: {0} {1} exit={2}".format(status, spec.label, exit_code), "pass" if exit_code == 0 else "fail")
        self._append_console("")
        self._append_console("== {0}: {1} exit={2} status={3} ==".format(status, spec.label, exit_code, exit_status))
        self._refresh_results()

    def _on_failed_to_start(self, spec: MotorSpec, message: str) -> None:
        self._set_status("Estado: FAIL al iniciar {0}".format(spec.label), "fail")
        self._append_console("[QProcess] " + message)
        self._refresh_results()

    def _set_status(self, text: str, kind: str) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("statusKind", kind)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _append_console(self, text: str) -> None:
        self.console.appendPlainText(text)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _refresh_results(self) -> None:
        self._last_result_zip = find_latest_result_zip(DEFAULT_OUTPUT_ROOT)
        self._last_fail_zip = find_latest_fail_zip(DEFAULT_OUTPUT_ROOT)

        if hasattr(self, "result_label"):
            self.result_label.setText("Último result ZIP: {0}".format(self._last_result_zip or "(ninguno)"))
        if hasattr(self, "fail_label"):
            self.fail_label.setText("Último fail ZIP: {0}".format(self._last_fail_zip or "(ninguno)"))

    def _open_downloads(self) -> None:
        self._open_path(DEFAULT_OUTPUT_ROOT)

    def _open_last_result(self) -> None:
        self._refresh_results()
        if self._last_result_zip is None:
            QMessageBox.information(self, "Motor Hub", "No encontré result ZIP en F:\\descargasf.")
            return
        self._open_path(self._last_result_zip)

    def _open_last_fail(self) -> None:
        self._refresh_results()
        if self._last_fail_zip is None:
            QMessageBox.information(self, "Motor Hub", "No encontré fail ZIP en F:\\descargasf.")
            return
        self._open_path(self._last_fail_zip)

    def _open_playwright_root(self) -> None:
        self._open_path(Path(r"F:\repos\hitech-os\tools\Plawright Mamastrophic"))

    def _open_prisma_ctx_root(self) -> None:
        self._open_path(Path(r"F:\PRISMA_CTX"))

    def _open_path(self, path: str | Path) -> None:
        target = Path(path)
        if not target.exists():
            QMessageBox.warning(self, "Motor Hub", "No existe: {0}".format(target))
            return

        try:
            os.startfile(str(target))
            return
        except Exception:
            pass

        ok = QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))
        if not ok:
            QMessageBox.warning(self, "Motor Hub", "No pude abrir: {0}".format(target))


def _glass_base_stylesheet() -> str:
    """Return local pyside6_glass stylesheet if available, without making it mandatory."""
    if _build_glass_stylesheet is None:
        return ""
    calls = (
        lambda: _build_glass_stylesheet("silver_frost_cyan"),
        lambda: _build_glass_stylesheet(theme_id="silver_frost_cyan"),
        lambda: _build_glass_stylesheet(),
    )
    for call in calls:
        try:
            value = call()
        except Exception:
            continue
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _premium_stylesheet() -> str:
    glass_base = _glass_base_stylesheet()
    return glass_base + """
    QDialog {
        background: transparent;
        color: #f6fbff;
        font-family: Segoe UI, Inter, Arial, sans-serif;
    }
    QWidget#MotorHubTabPage {
        background: transparent;
    }
    QFrame#MotorHubHeader {
        border: 1px solid rgba(221, 248, 255, 0.52);
        border-radius: 18px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255,255,255,0.118),
            stop:0.34 rgba(232,246,255,0.072),
            stop:0.66 rgba(142,198,226,0.044),
            stop:1 rgba(9,18,30,0.118));
    }
    QLabel#MotorHubTitle {
        font-size: 24px;
        font-weight: 860;
        letter-spacing: 0.45px;
        color: #ffffff;
    }
    QLabel#MotorHubSubtitle {
        color: rgba(232, 244, 255, 0.88);
        font-size: 13px;
    }
    QLabel#MotorHubStatus {
        padding: 8px 10px;
        border-radius: 10px;
        border: 1px solid rgba(210, 240, 255, 0.38);
        background: rgba(245, 252, 255, 0.052);
        color: #eef8ff;
    }
    QLabel#MotorHubStatus[statusKind="running"] {
        border: 1px solid rgba(125, 218, 255, 0.62);
        background: rgba(64, 166, 255, 0.130);
        color: #f5fcff;
    }
    QLabel#MotorHubStatus[statusKind="pass"] {
        border: 1px solid rgba(103, 255, 198, 0.50);
        background: rgba(48, 184, 136, 0.115);
        color: #edfff8;
    }
    QLabel#MotorHubStatus[statusKind="fail"] {
        border: 1px solid rgba(255, 124, 144, 0.58);
        background: rgba(214, 58, 84, 0.135);
        color: #fff2f4;
    }
    QLabel#MotorHubSection {
        font-weight: 760;
        color: #ffffff;
        letter-spacing: 0.2px;
    }
    QLabel#MotorHubHint {
        color: rgba(226, 240, 255, 0.76);
    }
    QLabel#MotorHubMotorLabel,
    QLabel#MotorHubResultLabel {
        border: 1px solid rgba(214, 242, 255, 0.26);
        border-radius: 13px;
        padding: 10px 12px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255,255,255,0.088),
            stop:0.48 rgba(220,238,255,0.034),
            stop:1 rgba(22,38,56,0.052));
        color: rgba(247, 251, 255, 0.97);
    }
    QPushButton {
        border: 1px solid rgba(217, 244, 255, 0.40);
        border-radius: 11px;
        padding: 8px 12px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255,255,255,0.104),
            stop:0.55 rgba(190,223,247,0.046),
            stop:1 rgba(16,31,48,0.082));
        color: #f8fcff;
        font-weight: 710;
    }
    QPushButton[buttonKind="primary"] {
        border: 1px solid rgba(190, 238, 255, 0.66);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(120, 204, 255, 0.240),
            stop:0.46 rgba(255,255,255,0.116),
            stop:1 rgba(78, 122, 196, 0.162));
    }
    QPushButton[buttonKind="ghost"] {
        border: 1px solid rgba(210, 238, 255, 0.26);
        background: rgba(255, 255, 255, 0.034);
        color: rgba(239, 247, 255, 0.93);
    }
    QPushButton[buttonKind="quiet"] {
        border: 1px solid rgba(210, 238, 255, 0.22);
        background: rgba(255, 255, 255, 0.028);
        color: rgba(236, 245, 255, 0.88);
    }
    QPushButton:hover {
        border: 1px solid rgba(240, 252, 255, 0.78);
        background: rgba(184, 232, 255, 0.170);
    }
    QPushButton:pressed {
        background: rgba(97, 171, 255, 0.235);
    }
    QPlainTextEdit#MotorHubConsole {
        border: 1px solid rgba(194, 232, 255, 0.32);
        border-radius: 12px;
        background: rgba(3, 8, 15, 0.38);
        color: #dceeff;
        padding: 8px;
        selection-background-color: rgba(104, 188, 255, 0.45);
        font-family: Consolas, Cascadia Mono, monospace;
        font-size: 12px;
    }
    QPlainTextEdit#MotorHubConsole:focus {
        border: 1px solid rgba(219, 246, 255, 0.48);
        background: rgba(2, 7, 14, 0.48);
    }
    QTabWidget#MotorHubTabs::pane {
        border: 1px solid rgba(194, 232, 255, 0.31);
        border-radius: 13px;
        padding: 8px;
        background: rgba(255, 255, 255, 0.020);
    }
    QTabBar::tab {
        padding: 8px 14px;
        margin-right: 4px;
        border-radius: 9px;
        border: 1px solid rgba(211, 239, 255, 0.24);
        background: rgba(255, 255, 255, 0.045);
        color: rgba(237, 246, 255, 0.88);
    }
    QTabBar::tab:hover {
        background: rgba(147, 207, 255, 0.120);
        color: #ffffff;
    }
    QTabBar::tab:selected {
        border: 1px solid rgba(224, 250, 255, 0.62);
        background: rgba(174, 226, 255, 0.155);
        color: #ffffff;
    }
    QScrollBar:vertical {
        background: rgba(255,255,255,0.04);
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: rgba(178, 225, 255, 0.34);
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
    """


def _html_escape(text: object) -> str:
    value = str(text)
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

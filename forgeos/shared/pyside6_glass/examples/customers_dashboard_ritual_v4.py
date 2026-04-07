from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_repo_root() -> None:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "forgeos" / "shared" / "pyside6_glass").exists():
            value = str(candidate)
            if value not in sys.path:
                sys.path.insert(0, value)
            return


_bootstrap_repo_root()

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from forgeos.shared.pyside6_glass.orchestrators.ritual_dashboard_orchestrator import RitualDashboardOrchestrator
from forgeos.shared.pyside6_glass.orchestrators.ritual_dashboard_state import RitualDashboardState
from forgeos.shared.pyside6_glass.ui_baseline.screen_template import VisualScreenTemplate


class CustomersDashboardRitualScreen(VisualScreenTemplate):
    visual_role = "dashboard"
    visual_variant = "data-heavy"
    visual_emphasis = "high"
    visual_fx_level = "rich"
    visual_level = "premium"
    data_state = "ready"
    base_preset = "glass-default"

    enable_hero = True
    enable_main = True
    enable_side = True
    enable_footer = True
    enable_status = True

    def __init__(self, parent: QWidget | None = None) -> None:
        self.orchestrator = RitualDashboardOrchestrator()
        self._button_by_source: dict[str, QPushButton] = {}
        self._basin_progress: QProgressBar | None = None
        self._basin_label: QLabel | None = None
        self._status_label: QLabel | None = None
        self._ritual_list: QListWidget | None = None
        self._dashboard_stack: QStackedWidget | None = None
        self._locked_label: QLabel | None = None
        self._hero_hint_label: QLabel | None = None
        super().__init__(parent)
        self.orchestrator.state_changed.connect(self._apply_state)
        self.orchestrator.dashboard_unlocked.connect(self._celebrate_unlock)
        self._apply_state(self.orchestrator.snapshot())

    def build_hero(self) -> QWidget | None:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("Ritual de activación del dashboard", host)
        title.setWordWrap(True)
        layout.addWidget(title)

        self._hero_hint_label = QLabel(
            "Activa las fuentes correctas para llenar el cuenco central y soltar la superficie útil.",
            host,
        )
        self._hero_hint_label.setWordWrap(True)
        layout.addWidget(self._hero_hint_label)

        buttons_row = QWidget(host)
        buttons_layout = QHBoxLayout(buttons_row)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        for spec in self.orchestrator.source_specs():
            button = QPushButton(spec.label, buttons_row)
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.clicked.connect(lambda checked=False, source_id=spec.id: self._on_source_clicked(source_id))
            buttons_layout.addWidget(button)
            self._button_by_source[spec.id] = button

        layout.addWidget(buttons_row)
        return host

    def build_main(self) -> QWidget | None:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        basin_group = QGroupBox("Cuenco compartido", host)
        basin_layout = QVBoxLayout(basin_group)
        basin_layout.setSpacing(8)

        self._basin_label = QLabel("Cuenco vacío. Activa las fuentes de arriba.", basin_group)
        self._basin_label.setWordWrap(True)
        basin_layout.addWidget(self._basin_label)

        self._basin_progress = QProgressBar(basin_group)
        self._basin_progress.setRange(0, 100)
        self._basin_progress.setValue(0)
        self._basin_progress.setFormat("Agua limpia %p%")
        basin_layout.addWidget(self._basin_progress)

        stream_hint = QLabel(
            "Cada botón inyecta una corriente semántica. Cuando el cuenco llega al umbral correcto, el tablero despierta.",
            basin_group,
        )
        stream_hint.setWordWrap(True)
        basin_layout.addWidget(stream_hint)
        layout.addWidget(basin_group)

        self._dashboard_stack = QStackedWidget(host)
        self._dashboard_stack.addWidget(self._build_locked_surface())
        self._dashboard_stack.addWidget(self._build_unlocked_surface())
        layout.addWidget(self._dashboard_stack, 1)

        chart_group = QGroupBox("Gráfica ritual", host)
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.addWidget(
            QLabel(
                "La gráfica vive; abajo ya no hay ruido, solo la curva lista para conectarse a serie real.",
                chart_group,
            )
        )

        chart_curve = QLabel(
            "╭╮      ╭─╮      ╭╮\n"
            "│╰╮  ╭──╯ │  ╭──╯│\n"
            "│ ╰──╯    ╰──╯   │",
            chart_group,
        )
        chart_layout.addWidget(chart_curve)

        layout.addWidget(chart_group)
        return host

    def build_side(self) -> QWidget | None:
        panel = QGroupBox("Fuentes y trazos", self)
        layout = QVBoxLayout(panel)

        detail = QLabel(
            "Aquí ves qué fuente está empujada y cuál sigue dormida. El orchestrator manda el estado; la screen solo lo cuenta bonito.",
            panel,
        )
        detail.setWordWrap(True)
        layout.addWidget(detail)

        self._ritual_list = QListWidget(panel)
        layout.addWidget(self._ritual_list)
        return panel

    def build_footer(self) -> QWidget | None:
        panel = QGroupBox("Siguiente jugada", self)
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("• Clientes + Cobranza + Analítica liberan la superficie útil.", panel))
        layout.addWidget(QLabel("• Pedidos y Reportes enriquecen contexto, pero no son llave maestra.", panel))
        layout.addWidget(QLabel("• Luego esto se conecta al orchestrator del core de verdad.", panel))
        return panel

    def build_status(self) -> QWidget | None:
        panel = QGroupBox("Estado ritual", self)
        layout = QVBoxLayout(panel)
        self._status_label = QLabel("Esperando activación...", panel)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)
        return panel

    def _build_locked_surface(self) -> QWidget:
        panel = QFrame(self)
        layout = QVBoxLayout(panel)
        self._locked_label = QLabel(
            "La interfaz final sigue sellada. Activa la combinación correcta y el tablero se abre solo.",
            panel,
        )
        self._locked_label.setWordWrap(True)
        layout.addWidget(self._locked_label)
        return panel

    def _build_unlocked_surface(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        kpi_row = QWidget(panel)
        kpi_layout = QGridLayout(kpi_row)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setHorizontalSpacing(10)
        kpi_layout.setVerticalSpacing(10)

        for index, (title, value, detail) in enumerate(
            (
                ("Clientes vivos", "12,480", "Cartera con actividad reciente"),
                ("Cobranza sana", "93.2%", "Pago útil sin fricción rara"),
                ("Alertas", "17", "Cuentas con seguimiento caliente"),
                ("NPS", "61", "Pulso decente, no de funeral"),
            )
        ):
            card = QGroupBox(title, kpi_row)
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(value, card))
            note = QLabel(detail, card)
            note.setWordWrap(True)
            card_layout.addWidget(note)
            kpi_layout.addWidget(card, index // 2, index % 2)

        layout.addWidget(kpi_row)

        table = QTableWidget(5, 4, panel)
        table.setHorizontalHeaderLabels(["Segmento", "Clientes", "Ingreso", "Tendencia"])
        for row_index, row in enumerate(
            (
                ("Enterprise", "320", "$ 4.2M", "Up"),
                ("Mid-market", "1,240", "$ 2.1M", "Stable"),
                ("SMB", "10,920", "$ 1.3M", "Up"),
                ("Latam", "4,180", "$ 0.8M", "Watch"),
                ("NA", "5,090", "$ 3.5M", "Strong"),
            )
        ):
            for column_index, value in enumerate(row):
                table.setItem(row_index, column_index, QTableWidgetItem(value))
        layout.addWidget(table)
        return panel

    def _on_source_clicked(self, source_id: str) -> None:
        self.orchestrator.toggle_source(source_id)

    def _apply_state(self, state: RitualDashboardState) -> None:
        for source in state.sources:
            button = self._button_by_source.get(source.id)
            if button is not None:
                button.blockSignals(True)
                button.setChecked(source.active)
                button.setText(("● " if source.active else "○ ") + source.label)
                button.blockSignals(False)

        if self._hero_hint_label is not None:
            needed = ", ".join(
                spec.label
                for spec in self.orchestrator.source_specs()
                if spec.id in state.required_source_ids
            )
            self._hero_hint_label.setText(
                f"Llave actual: {needed}. Fuentes activas: {state.activation_count}."
            )

        if self._basin_label is not None:
            self._basin_label.setText(state.basin_label)

        if self._basin_progress is not None:
            self._basin_progress.setValue(int(state.basin_fill_ratio * 100))

        if self._status_label is not None:
            self._status_label.setText(state.status_label)

        if self._ritual_list is not None:
            self._ritual_list.clear()
            for source in state.sources:
                prefix = "ACTIVA" if source.active else "DORMIDA"
                marker = "requerida" if source.id in state.required_source_ids else "opcional"
                item = QListWidgetItem(f"{prefix} · {source.label} · {marker} · {source.hint}")
                self._ritual_list.addItem(item)

        if self._dashboard_stack is not None:
            self._dashboard_stack.setCurrentIndex(1 if state.unlocked else 0)

        if self._locked_label is not None and not state.unlocked:
            self._locked_label.setText(
                f"Todavía no. Progreso ritual: {int(state.basin_fill_ratio * 100)}%.\n{state.status_label}"
            )

    def _celebrate_unlock(self, state: RitualDashboardState) -> None:
        if self._status_label is not None:
            self._status_label.setText(
                f"🔥 Ritual completo. Superficie liberada: {state.unlocked_surface}."
            )


def main() -> int:
    app = QApplication.instance() or QApplication([])
    widget = CustomersDashboardRitualScreen()
    widget.setWindowTitle("Customers Dashboard Ritual")
    widget.resize(1320, 860)
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

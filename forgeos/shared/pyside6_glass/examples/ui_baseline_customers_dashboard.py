from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from forgeos.shared.pyside6_glass.ui_baseline.screen_template import VisualScreenTemplate


class CustomersDashboardScreen(VisualScreenTemplate):
    visual_role = "dashboard"
    visual_variant = "data-heavy"
    visual_emphasis = "high"
    visual_fx_level = "subtle"
    visual_level = "premium"
    data_state = "ready"
    base_preset = "glass-default"

    def build_hero(self) -> QWidget | None:
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        for title, value in (
            ("Clientes activos", "12,480"),
            ("NPS", "61"),
            ("Churn 30d", "1.9%"),
        ):
            card = QGroupBox(title, container)
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(value, card))
            card_layout.addWidget(QLabel("Placeholder conectado al runtime oficial.", card))
            layout.addWidget(card)

        return container

    def build_main(self) -> QWidget | None:
        table = QTableWidget(6, 4, self)
        table.setHorizontalHeaderLabels(["Segmento", "Clientes", "Ingreso", "Tendencia"])
        rows = [
            ("Enterprise", "320", "$ 4.2M", "Up"),
            ("Mid-market", "1,240", "$ 2.1M", "Stable"),
            ("SMB", "10,920", "$ 1.3M", "Up"),
            ("Latam", "4,180", "$ 0.8M", "Watch"),
            ("EU", "2,210", "$ 1.0M", "Up"),
            ("NA", "5,090", "$ 3.5M", "Strong"),
        ]
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                table.setItem(row_index, col_index, QTableWidgetItem(value))
        return table

    def build_side(self) -> QWidget | None:
        panel = QGroupBox("Inspector / filtros", self)
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Cohortes prioritarias", panel))
        listing = QListWidget(panel)
        listing.addItems(
            [
                "Enterprise > Renovación < 45 días",
                "SMB > Ticket creciente",
                "Latam > Riesgo churn medio",
                "NA > Oportunidad cross-sell",
            ]
        )
        layout.addWidget(listing)
        return panel

    def build_footer(self) -> QWidget | None:
        footer = QGroupBox("Acciones", self)
        layout = QVBoxLayout(footer)
        layout.addWidget(QLabel("• Exportar snapshot"))
        layout.addWidget(QLabel("• Abrir pipeline de seguimiento"))
        layout.addWidget(QLabel("• Escalar cuentas con churn alto"))
        return footer

    def build_status(self) -> QWidget | None:
        panel = QGroupBox("Estado del dashboard", self)
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Sincronización: hace 4 min"))
        layout.addWidget(QLabel("Origen: customers_daily_rollup"))
        layout.addWidget(QLabel("Runtime: delegado al core"))
        return panel


def main() -> int:
    app = QApplication.instance() or QApplication([])
    widget = CustomersDashboardScreen()
    widget.setWindowTitle("Customers Dashboard")
    widget.resize(1280, 800)
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QComboBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QWidget,
    )
except Exception as exc:  # noqa: BLE001
    Signal = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


if Signal is not None:

    class ControlsPanel(QWidget):
        ingest_clicked = Signal()
        full_ingest_clicked = Signal()
        repair_clicked = Signal()
        metrics_clicked = Signal()
        status_clicked = Signal()
        watch_toggled = Signal(bool)
        quick_action_requested = Signal(str)

        def __init__(self) -> None:
            super().__init__()
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            self.ingest_button = QPushButton("Ingest")
            self.full_ingest_button = QPushButton("Full Ingest")
            self.repair_button = QPushButton("Repair")
            self.metrics_button = QPushButton("Metrics")
            self.status_button = QPushButton("Status")
            self.watch_button = QPushButton("Watch OFF")
            self.watch_button.setCheckable(True)
            self.quick_action_label = QLabel("Funciones:")
            self.quick_action_combo = QComboBox()
            self.quick_action_button = QPushButton("Ejecutar Funcion")

            self.quick_action_combo.addItem("Ver estado del sistema", "status")
            self.quick_action_combo.addItem("Ingerir fuentes configuradas", "ingest_default")
            self.quick_action_combo.addItem("Ingerir carpeta seleccionada...", "ingest_folder")
            self.quick_action_combo.addItem("Reprocesar todo (Full Ingest)", "full_ingest_default")
            self.quick_action_combo.addItem("Reprocesar carpeta seleccionada...", "full_ingest_folder")
            self.quick_action_combo.addItem("Actualizar metricas", "metrics")
            self.quick_action_combo.addItem("Reparar base e indices", "repair")
            self.quick_action_combo.addItem("Activar monitoreo continuo (Watch ON)", "watch_on")
            self.quick_action_combo.addItem("Desactivar monitoreo continuo (Watch OFF)", "watch_off")
            self.quick_action_combo.addItem("Exportar sesion seleccionada", "export_selected_session")

            layout.addWidget(self.ingest_button)
            layout.addWidget(self.full_ingest_button)
            layout.addWidget(self.repair_button)
            layout.addWidget(self.metrics_button)
            layout.addWidget(self.status_button)
            layout.addWidget(self.watch_button)
            layout.addSpacing(16)
            layout.addWidget(self.quick_action_label)
            layout.addWidget(self.quick_action_combo, 1)
            layout.addWidget(self.quick_action_button)
            layout.addStretch(1)

            self.ingest_button.clicked.connect(self.ingest_clicked.emit)
            self.full_ingest_button.clicked.connect(self.full_ingest_clicked.emit)
            self.repair_button.clicked.connect(self.repair_clicked.emit)
            self.metrics_button.clicked.connect(self.metrics_clicked.emit)
            self.status_button.clicked.connect(self.status_clicked.emit)
            self.watch_button.toggled.connect(self._emit_watch_state)
            self.quick_action_button.clicked.connect(self._emit_quick_action)

        def _emit_watch_state(self, enabled: bool) -> None:
            self.watch_button.setText("Watch ON" if enabled else "Watch OFF")
            self.watch_toggled.emit(enabled)

        def _emit_quick_action(self) -> None:
            code = self.quick_action_combo.currentData()
            if code:
                self.quick_action_requested.emit(str(code))

        def set_busy(self, busy: bool) -> None:
            for button in (
                self.ingest_button,
                self.full_ingest_button,
                self.repair_button,
                self.metrics_button,
                self.status_button,
                self.quick_action_button,
            ):
                button.setEnabled(not busy)
            self.quick_action_combo.setEnabled(not busy)
else:

    class ControlsPanel:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for ControlsPanel") from _IMPORT_ERROR

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QProcess, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


OUTPUT_ROOT = Path(r"F:\descargasf")
CODE_ATLAS_ROOT = Path(__file__).resolve().parents[3]
BACKEND_SCRIPT = CODE_ATLAS_ROOT / "scripts" / "RUN_LEGAL_READINESS_BACKEND.ps1"

PROFILE_ITEMS = (
    ("plan", "Plan y autoridad"),
    ("static", "Static legal baseline"),
    ("full", "Full: static + runtime"),
    ("runtime-only", "Runtime únicamente"),
)

SURFACE_ITEMS = (
    ("all", "Todas las superficies"),
    ("chart-lab", "Chart Lab"),
    ("web", "Web / EIT"),
    ("tablet", "Tablet / POS"),
    ("pc", "PC Backoffice"),
    ("mobile", "Mobile"),
    ("control-center", "Control Center"),
)


class LegalReadinessDialog(QDialog):
    """Code Atlas Legal / Investor Readiness control panel.

    The dialog launches the installed backend through one QProcess. The backend
    itself executes one external stage at a time. A cooperative cancellation
    marker prevents the next stage from starting and never kills ports, servers,
    databases or unrelated processes.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PRISMA Legal / Investor Readiness")
        self.setMinimumSize(1040, 700)
        self.resize(1160, 780)

        self._process: QProcess | None = None
        self._run_started_at: datetime | None = None
        self._cancel_file: Path | None = None
        self._last_final_zip: Path | None = None
        self._mode = "idle"
        self._build_ui()
        self._connect_signals()
        self._sync_profile_controls()
        self._refresh_latest_zip()
        QTimer.singleShot(80, self._run_authority_check)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("LegalHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        title = QLabel("⚖ Legal / Investor Readiness")
        title.setObjectName("LegalTitle")
        subtitle = QLabel(
            "Code Atlas dirige NDC, motores CTX y Mamastrophic con una sola etapa externa a la vez. "
            "Workers y shards operan únicamente dentro del motor activo."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("LegalSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        self.status_label = QLabel("Estado: validando autoridad…")
        self.status_label.setObjectName("LegalStatus")
        self.status_label.setProperty("statusKind", "running")
        root.addWidget(self.status_label)

        controls = QFrame()
        controls.setObjectName("LegalControls")
        form = QFormLayout(controls)
        form.setContentsMargins(14, 12, 14, 12)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(10)

        self.profile_combo = QComboBox()
        for value, label in PROFILE_ITEMS:
            self.profile_combo.addItem(label, value)
        self.profile_combo.setCurrentIndex(0)

        self.surface_combo = QComboBox()
        for value, label in SURFACE_ITEMS:
            self.surface_combo.addItem(label, value)

        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 18)
        self.workers_spin.setValue(6)
        self.workers_spin.setSuffix(" workers")

        self.shards_spin = QSpinBox()
        self.shards_spin.setRange(1, 18)
        self.shards_spin.setValue(1)
        self.shards_spin.setSuffix(" shards")

        self.strict_check = QCheckBox("Bloquear si la evidencia runtime queda parcial")
        self.strict_check.setChecked(False)

        form.addRow("Perfil", self.profile_combo)
        form.addRow("Superficie runtime", self.surface_combo)
        form.addRow("Workers internos", self.workers_spin)
        form.addRow("Shards internos", self.shards_spin)
        form.addRow("Política", self.strict_check)
        root.addWidget(controls)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.authority_button = self._button("Validar autoridad", "secondary")
        self.plan_button = self._button("Ver plan", "secondary")
        self.run_button = self._button("Ejecutar Legal", "primary")
        self.stop_button = self._button("Detener después de etapa", "warning")
        self.stop_button.setEnabled(False)
        self.open_zip_button = self._button("Abrir ZIP legal", "secondary")
        self.open_output_button = self._button("Abrir F:\\descargasf", "ghost")
        actions.addWidget(self.authority_button)
        actions.addWidget(self.plan_button)
        actions.addWidget(self.run_button)
        actions.addWidget(self.stop_button)
        actions.addStretch(1)
        actions.addWidget(self.open_zip_button)
        actions.addWidget(self.open_output_button)
        root.addLayout(actions)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setObjectName("LegalProgress")
        root.addWidget(self.progress_bar)

        self.stage_label = QLabel("Etapa: pendiente")
        self.stage_label.setObjectName("LegalStage")
        root.addWidget(self.stage_label)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(8000)
        self.console.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.console.setPlaceholderText("Aquí aparecerán autoridad, plan, progreso y salida del pipeline.")
        self.console.setObjectName("LegalConsole")
        root.addWidget(self.console, 1)

        footer = QHBoxLayout()
        self.latest_label = QLabel("Último ZIP legal: buscando…")
        self.latest_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.latest_label.setObjectName("LegalLatest")
        close_button = self._button("Cerrar", "quiet")
        close_button.clicked.connect(self.close)
        footer.addWidget(self.latest_label, 1)
        footer.addWidget(close_button)
        root.addLayout(footer)

        self.setStyleSheet(_stylesheet())

    def _connect_signals(self) -> None:
        self.profile_combo.currentIndexChanged.connect(self._sync_profile_controls)
        self.authority_button.clicked.connect(self._run_authority_check)
        self.plan_button.clicked.connect(self._run_plan)
        self.run_button.clicked.connect(self._run_pipeline)
        self.stop_button.clicked.connect(self._request_stop_after_stage)
        self.open_zip_button.clicked.connect(self._open_last_zip)
        self.open_output_button.clicked.connect(lambda: self._open_path(OUTPUT_ROOT))

    def _button(self, text: str, kind: str) -> QPushButton:
        button = QPushButton(text)
        button.setProperty("buttonKind", kind)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _selected_profile(self) -> str:
        return str(self.profile_combo.currentData() or "plan")

    def _selected_surface(self) -> str:
        return str(self.surface_combo.currentData() or "all")

    def _sync_profile_controls(self) -> None:
        profile = self._selected_profile()
        runtime = profile in {"full", "runtime-only"}
        self.surface_combo.setEnabled(runtime)
        self.shards_spin.setEnabled(runtime)
        self.strict_check.setEnabled(runtime)
        self.run_button.setText("Ejecutar plan" if profile == "plan" else "Ejecutar Legal")

    def _resolve_powershell(self) -> str:
        candidates = ("powershell.exe", "pwsh.exe", "powershell", "pwsh")
        for candidate in candidates:
            path = _which(candidate)
            if path:
                return path
        raise RuntimeError("POWERSHELL_RUNTIME_NOT_FOUND")

    def _backend_args(self, *, authority_only: bool = False, print_plan: bool = False) -> list[str]:
        profile = self._selected_profile()
        args = [
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(BACKEND_SCRIPT),
            "-Profile",
            profile,
            "-Surface",
            self._selected_surface(),
            "-Workers",
            str(self.workers_spin.value()),
            "-Shards",
            str(self.shards_spin.value()),
        ]
        if profile in {"full", "runtime-only"}:
            args.append("-IncludeRuntime")
        if self.strict_check.isChecked():
            args.append("-Strict")
        if authority_only:
            args.append("-AuthorityOnly")
        if print_plan:
            args.append("-PrintPlan")
        if self._cancel_file is not None:
            args.extend(["-CancelFile", str(self._cancel_file)])
        return args

    def _run_authority_check(self) -> None:
        self._start_backend(mode="authority", authority_only=True)

    def _run_plan(self) -> None:
        self._start_backend(mode="plan", print_plan=True)

    def _run_pipeline(self) -> None:
        if self._selected_profile() == "plan":
            self._run_plan()
            return
        self._start_backend(mode="pipeline")

    def _start_backend(
        self,
        *,
        mode: str,
        authority_only: bool = False,
        print_plan: bool = False,
    ) -> None:
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            QMessageBox.warning(self, "Legal / Investor Readiness", "Ya hay una corrida activa.")
            return
        if not BACKEND_SCRIPT.exists():
            QMessageBox.critical(self, "Legal / Investor Readiness", f"No existe el backend:\n{BACKEND_SCRIPT}")
            return

        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        self._cleanup_cancel_file()
        self._cancel_file = Path(tempfile.gettempdir()) / f"code-atlas-legal-{uuid.uuid4().hex}.cancel.json"
        self._run_started_at = datetime.now()
        self._last_final_zip = None
        self._mode = mode
        self.console.clear()
        self.progress_bar.setValue(0)
        self.stage_label.setText("Etapa: preparando")
        self._append(f"Backend: {BACKEND_SCRIPT}")
        self._append(f"Modo: {mode}")
        self._append(f"Perfil: {self._selected_profile()}")
        self._append(f"Superficie: {self._selected_surface()}")
        self._append(f"Workers: {self.workers_spin.value()} | Shards: {self.shards_spin.value()}")
        self._append("Concurrencia externa: 1")
        self._append("")

        try:
            program = self._resolve_powershell()
            process = QProcess(self)
            self._process = process
            process.setWorkingDirectory(str(CODE_ATLAS_ROOT))
            process.setProgram(program)
            process.setArguments(self._backend_args(authority_only=authority_only, print_plan=print_plan))
            process.setProcessChannelMode(QProcess.SeparateChannels)
            process.readyReadStandardOutput.connect(self._read_stdout)
            process.readyReadStandardError.connect(self._read_stderr)
            process.finished.connect(self._on_finished)
            process.errorOccurred.connect(self._on_error)
            self._set_running(True)
            self._set_status("Estado: ejecutando " + mode, "running")
            process.start()
        except Exception as exc:
            self._set_running(False)
            self._set_status("Estado: FAIL al iniciar", "fail")
            QMessageBox.critical(self, "Legal / Investor Readiness", str(exc))

    def _read_stdout(self) -> None:
        process = self._process
        if process is None:
            return
        text = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if text:
            self._consume_output("stdout", text)

    def _read_stderr(self) -> None:
        process = self._process
        if process is None:
            return
        text = bytes(process.readAllStandardError()).decode("utf-8", errors="replace")
        if text:
            self._consume_output("stderr", text)

    def _consume_output(self, channel: str, text: str) -> None:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("CODE_ATLAS_LEGAL_PROGRESS "):
                raw = stripped.split(" ", 1)[1]
                try:
                    payload = json.loads(raw)
                    percent = int(payload.get("percent", 0))
                    label = str(payload.get("label", ""))
                    self.progress_bar.setValue(max(0, min(100, percent)))
                    self.stage_label.setText("Etapa: " + label)
                except Exception:
                    pass
            elif stripped.startswith("FINAL_ZIP="):
                candidate = Path(stripped.split("=", 1)[1].strip())
                self._last_final_zip = candidate
                self.latest_label.setText("ZIP legal: " + str(candidate))
            prefix = "[stderr] " if channel == "stderr" else ""
            self._append(prefix + line)

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self._read_stdout()
        self._read_stderr()
        process = self._process
        if process is not None:
            process.deleteLater()
        self._process = None
        self._set_running(False)
        self._cleanup_cancel_file()

        if self._last_final_zip is None:
            self._last_final_zip = self._find_newest_legal_zip()
        self._refresh_latest_zip()

        passed = int(exit_code) == 0
        if passed:
            self.progress_bar.setValue(100)
            self._set_status(f"Estado: PASS {self._mode}", "pass")
        else:
            self._set_status(f"Estado: FAIL {self._mode} exit={exit_code}", "fail")
        self._append("")
        self._append(f"Proceso terminado: exit={exit_code} status={exit_status}")
        if self._last_final_zip is not None:
            self._append(f"ZIP final: {self._last_final_zip}")

    def _on_error(self, error: QProcess.ProcessError) -> None:
        self._append(f"[QProcess] error={error}")
        self._set_status("Estado: FAIL de QProcess", "fail")

    def _request_stop_after_stage(self) -> None:
        if self._process is None or self._process.state() == QProcess.NotRunning:
            return
        if self._cancel_file is None:
            return
        payload = {
            "schema": "CODE_ATLAS_LEGAL_CANCEL_REQUEST_V1",
            "requested_at": datetime.now().isoformat(timespec="seconds"),
            "policy": "finish current stage; do not start the next stage",
        }
        self._cancel_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.stop_button.setEnabled(False)
        self._set_status("Estado: cancelación solicitada después de la etapa actual", "warning")
        self._append("Cancelación cooperativa solicitada. No se matará el proceso activo.")

    def _set_running(self, running: bool) -> None:
        self.profile_combo.setEnabled(not running)
        self.workers_spin.setEnabled(not running)
        self.authority_button.setEnabled(not running)
        self.plan_button.setEnabled(not running)
        self.run_button.setEnabled(not running)
        self.open_zip_button.setEnabled(not running)
        self.stop_button.setEnabled(running and self._mode == "pipeline")
        self._sync_profile_controls()
        if running:
            self.profile_combo.setEnabled(False)
            self.surface_combo.setEnabled(False)
            self.workers_spin.setEnabled(False)
            self.shards_spin.setEnabled(False)
            self.strict_check.setEnabled(False)

    def _set_status(self, text: str, kind: str) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("statusKind", kind)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _append(self, text: str) -> None:
        self.console.appendPlainText(text)
        bar = self.console.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _find_newest_legal_zip(self) -> Path | None:
        if not OUTPUT_ROOT.exists():
            return None
        candidates = [
            path
            for pattern in ("catlegal * result.zip", "catlegal * fail.zip")
            for path in OUTPUT_ROOT.glob(pattern)
            if path.is_file()
        ]
        if self._run_started_at is not None:
            threshold = self._run_started_at.timestamp() - 2
            candidates = [path for path in candidates if path.stat().st_mtime >= threshold]
        return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None

    def _refresh_latest_zip(self) -> None:
        if self._last_final_zip is None or not self._last_final_zip.exists():
            self._last_final_zip = self._find_newest_legal_zip()
        self.latest_label.setText(
            "Último ZIP legal: " + (str(self._last_final_zip) if self._last_final_zip else "(ninguno)")
        )

    def _open_last_zip(self) -> None:
        self._refresh_latest_zip()
        if self._last_final_zip is None:
            QMessageBox.information(self, "Legal / Investor Readiness", "No encontré un ZIP catlegal.")
            return
        self._open_path(self._last_final_zip)

    def _open_path(self, path: Path) -> None:
        target = Path(path)
        if not target.exists():
            QMessageBox.warning(self, "Legal / Investor Readiness", f"No existe:\n{target}")
            return
        try:
            os.startfile(str(target))
            return
        except Exception:
            pass
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(target))):
            QMessageBox.warning(self, "Legal / Investor Readiness", f"No pude abrir:\n{target}")

    def _cleanup_cancel_file(self) -> None:
        path = self._cancel_file
        self._cancel_file = None
        if path is None:
            return
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            QMessageBox.information(
                self,
                "Legal / Investor Readiness",
                "La corrida sigue activa. Solicita detener después de la etapa actual y espera a que termine.",
            )
            event.ignore()
            return
        self._cleanup_cancel_file()
        super().closeEvent(event)


def _which(name: str) -> str | None:
    try:
        import shutil

        return shutil.which(name)
    except Exception:
        return None


def _stylesheet() -> str:
    return """
    QDialog {
        background: #07101c;
        color: #f4f8ff;
        font-family: Segoe UI, Inter, Arial, sans-serif;
    }
    QFrame#LegalHeader,
    QFrame#LegalControls {
        border: 1px solid rgba(189, 226, 255, 0.30);
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.055);
    }
    QLabel#LegalTitle {
        font-size: 23px;
        font-weight: 850;
        color: #ffffff;
    }
    QLabel#LegalSubtitle,
    QLabel#LegalLatest {
        color: rgba(228, 241, 255, 0.82);
    }
    QLabel#LegalStatus,
    QLabel#LegalStage {
        padding: 8px 10px;
        border-radius: 10px;
        border: 1px solid rgba(190, 228, 255, 0.30);
        background: rgba(255, 255, 255, 0.045);
    }
    QLabel#LegalStatus[statusKind="running"] {
        border-color: rgba(96, 196, 255, 0.70);
        background: rgba(43, 134, 205, 0.22);
    }
    QLabel#LegalStatus[statusKind="pass"] {
        border-color: rgba(95, 240, 172, 0.64);
        background: rgba(32, 153, 108, 0.22);
    }
    QLabel#LegalStatus[statusKind="warning"] {
        border-color: rgba(255, 210, 104, 0.70);
        background: rgba(185, 128, 32, 0.22);
    }
    QLabel#LegalStatus[statusKind="fail"] {
        border-color: rgba(255, 112, 138, 0.72);
        background: rgba(181, 42, 74, 0.24);
    }
    QComboBox,
    QSpinBox,
    QPlainTextEdit {
        border: 1px solid rgba(190, 228, 255, 0.30);
        border-radius: 9px;
        background: rgba(5, 14, 26, 0.72);
        color: #f3f8ff;
        padding: 7px;
    }
    QPlainTextEdit#LegalConsole {
        font-family: Consolas, Cascadia Mono, monospace;
        font-size: 12px;
    }
    QProgressBar#LegalProgress {
        min-height: 20px;
        border: 1px solid rgba(190, 228, 255, 0.30);
        border-radius: 9px;
        text-align: center;
        background: rgba(255, 255, 255, 0.04);
    }
    QProgressBar#LegalProgress::chunk {
        border-radius: 8px;
        background: rgba(81, 188, 255, 0.70);
    }
    QPushButton {
        border: 1px solid rgba(201, 235, 255, 0.38);
        border-radius: 10px;
        padding: 8px 12px;
        color: #f6fbff;
        background: rgba(255, 255, 255, 0.065);
        font-weight: 700;
    }
    QPushButton[buttonKind="primary"] {
        border-color: rgba(161, 224, 255, 0.74);
        background: rgba(58, 153, 225, 0.30);
    }
    QPushButton[buttonKind="warning"] {
        border-color: rgba(255, 204, 104, 0.58);
        background: rgba(178, 119, 24, 0.22);
    }
    QPushButton[buttonKind="ghost"],
    QPushButton[buttonKind="quiet"] {
        background: rgba(255, 255, 255, 0.035);
    }
    QPushButton:hover {
        background: rgba(128, 205, 255, 0.18);
    }
    QPushButton:disabled {
        color: rgba(225, 235, 245, 0.38);
        border-color: rgba(190, 210, 225, 0.15);
        background: rgba(255, 255, 255, 0.02);
    }
    """

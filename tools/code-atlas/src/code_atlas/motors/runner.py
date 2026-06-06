# CODE_ATLAS_MOTOR_HUB_MODULE_V01
"""QProcess based execution layer for the Motor Hub UI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

from .specs import MotorSpec


class MotorProcessRunner(QObject):
    """Runs one MotorSpec at a time without freezing the PySide6 event loop."""

    started = Signal(object)
    output_ready = Signal(str, str)
    finished = Signal(object, int, str)
    failed_to_start = Signal(object, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: QProcess | None = None
        self._current_spec: MotorSpec | None = None

    def is_running(self) -> bool:
        process = self._process
        if process is None:
            return False
        return process.state() != QProcess.NotRunning

    def start(self, spec: MotorSpec) -> None:
        if self.is_running():
            raise RuntimeError("Ya hay un motor corriendo. Espera a que termine.")

        root = Path(spec.root)
        if not root.exists():
            raise FileNotFoundError("No existe la raíz del motor: {0}".format(root))

        process = QProcess(self)
        self._process = process
        self._current_spec = spec

        process.setWorkingDirectory(str(root))
        process.setProgram(spec.program)
        process.setArguments([str(arg) for arg in spec.args])
        process.setProcessChannelMode(QProcess.SeparateChannels)

        process.readyReadStandardOutput.connect(self._read_stdout)
        process.readyReadStandardError.connect(self._read_stderr)
        process.finished.connect(self._on_finished)
        process.errorOccurred.connect(self._on_error)

        self.started.emit(spec)
        process.start()

    def stop_request_only(self) -> None:
        """Ask the child process to close gracefully.

        This intentionally does not kill, terminate ports, or clean external services.
        """

        process = self._process
        if process is not None and process.state() != QProcess.NotRunning:
            process.closeWriteChannel()

    def _read_stdout(self) -> None:
        process = self._process
        if process is None:
            return
        text = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if text:
            self.output_ready.emit("stdout", text)

    def _read_stderr(self) -> None:
        process = self._process
        if process is None:
            return
        text = bytes(process.readAllStandardError()).decode("utf-8", errors="replace")
        if text:
            self.output_ready.emit("stderr", text)

    def _on_error(self, error: QProcess.ProcessError) -> None:
        spec = self._current_spec
        if spec is None:
            return
        self.failed_to_start.emit(spec, "QProcess error: {0}".format(error))

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        process = self._process
        spec = self._current_spec
        status_text = str(exit_status)
        if process is not None:
            remaining_stdout = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
            remaining_stderr = bytes(process.readAllStandardError()).decode("utf-8", errors="replace")
            if remaining_stdout:
                self.output_ready.emit("stdout", remaining_stdout)
            if remaining_stderr:
                self.output_ready.emit("stderr", remaining_stderr)
            process.deleteLater()
        self._process = None
        self._current_spec = None
        if spec is not None:
            self.finished.emit(spec, int(exit_code), status_text)

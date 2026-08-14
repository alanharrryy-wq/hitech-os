from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QProcess, Signal

from .artifacts import discover_stage_artifact, snapshot_zip_files
from .authority import validate_authority_chain
from .contracts import LegalPipelineConfig, LegalStageResult
from .io_utils import now_iso
from .registry import build_legal_stage_registry


class LegalPipelineController(QObject):
    """Sequential, adapter-neutral QProcess controller for diligence evidence stages."""

    pipeline_started = Signal(object)
    stage_started = Signal(object, int, int)
    stage_output = Signal(str, str, str)
    progress = Signal(int, str, object)
    stage_finished = Signal(object)
    pipeline_finished = Signal(object)
    failed_to_start = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config: LegalPipelineConfig | None = None
        self._stages = []
        self._index = -1
        self._process: QProcess | None = None
        self._results: list[dict[str, Any]] = []
        self._before: dict[str, dict[str, Any]] = {}
        self._stdout: list[str] = []
        self._stderr: list[str] = []
        self._cancel_requested = False

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() != QProcess.NotRunning

    def start(self, config: LegalPipelineConfig) -> None:
        if self.is_running():
            raise RuntimeError("LEGAL_PIPELINE_ALREADY_RUNNING")
        cfg = config.normalized()
        authority = validate_authority_chain(cfg.output_root)
        if authority["status"] != "PASS":
            raise RuntimeError("AUTHORITY_CHAIN_FAILED:" + ";".join(authority["errors"]))
        self._config = cfg
        self._stages = build_legal_stage_registry(cfg)
        self._index = -1
        self._results = []
        self._cancel_requested = False
        self.pipeline_started.emit({"config": cfg.to_dict(), "authority": authority})
        self._start_next()

    def request_stop_after_current_stage(self) -> None:
        self._cancel_requested = True
        process = self._process
        if process is not None and process.state() != QProcess.NotRunning:
            process.closeWriteChannel()

    def _start_next(self) -> None:
        if self._cancel_requested:
            self.pipeline_finished.emit({"status": "CANCELLED_AFTER_CURRENT_STAGE", "stage_results": self._results})
            return
        self._index += 1
        if self._index >= len(self._stages):
            self.pipeline_finished.emit({"status": "STAGES_COMPLETE_NEEDS_PACKAGING", "stage_results": self._results})
            return

        spec = self._stages[self._index]
        if not spec.enabled:
            result = LegalStageResult(
                stage_id=spec.stage_id,
                label=spec.label,
                status="SKIPPED_UNCONFIGURED",
                finished_at=now_iso(),
                error="UNCONFIGURED_STAGE" if spec.required else "",
            )
            self._results.append(result.to_dict())
            self.stage_finished.emit(result)
            if spec.required:
                self.pipeline_finished.emit({"status": "FAIL", "stage_results": self._results})
                return
            self._start_next()
            return

        root = Path(spec.root or ".")
        if not root.exists():
            self.failed_to_start.emit(f"MISSING_STAGE_ROOT:{root}")
            return

        assert self._config is not None
        self._before = snapshot_zip_files(Path(self._config.output_root))
        self._stdout = []
        self._stderr = []
        process = QProcess(self)
        self._process = process
        process.setWorkingDirectory(str(root))
        process.setProgram(spec.program)
        process.setArguments([str(value) for value in spec.args])
        process.setProcessChannelMode(QProcess.SeparateChannels)
        process.readyReadStandardOutput.connect(self._read_stdout)
        process.readyReadStandardError.connect(self._read_stderr)
        process.finished.connect(self._finished)
        process.errorOccurred.connect(self._error)
        self.stage_started.emit(spec, self._index + 1, len(self._stages))
        process.start()

    def _read_stdout(self) -> None:
        if self._process is None:
            return
        text = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if not text:
            return
        self._stdout.append(text)
        spec = self._stages[self._index]
        self.stage_output.emit(spec.stage_id, "stdout", text)
        for line in text.splitlines():
            if line.startswith("CODE_ATLAS_LEGAL_PROGRESS "):
                try:
                    payload = json.loads(line.split(" ", 1)[1])
                    self.progress.emit(int(payload.get("percent", 0)), str(payload.get("label", "")), payload)
                except Exception:
                    pass

    def _read_stderr(self) -> None:
        if self._process is None:
            return
        text = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
        if text:
            self._stderr.append(text)
            spec = self._stages[self._index]
            self.stage_output.emit(spec.stage_id, "stderr", text)

    def _finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self._read_stdout()
        self._read_stderr()
        spec = self._stages[self._index]
        assert self._config is not None
        artifact = discover_stage_artifact(
            output_root=Path(self._config.output_root),
            before=self._before,
            expected_prefixes=spec.expected_prefixes,
        )
        result = LegalStageResult(
            stage_id=spec.stage_id,
            label=spec.label,
            status="PASS" if exit_code == 0 and artifact else "FAIL",
            exit_code=int(exit_code),
            started_at="",
            finished_at=now_iso(),
            artifact=artifact,
            error="" if exit_code == 0 and artifact else f"exit={exit_code} artifact_missing={artifact is None}",
        )
        self._results.append(result.to_dict())
        self.stage_finished.emit(result)
        if self._process is not None:
            self._process.deleteLater()
        self._process = None
        if result.status == "FAIL" and spec.required:
            self.pipeline_finished.emit({"status": "FAIL", "stage_results": self._results})
            return
        self._start_next()

    def _error(self, error: QProcess.ProcessError) -> None:
        spec = self._stages[self._index]
        self.failed_to_start.emit(f"{spec.stage_id}:QProcessError:{error}")

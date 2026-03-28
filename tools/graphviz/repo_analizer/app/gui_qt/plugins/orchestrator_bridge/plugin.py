"""Wave 6 premium bridge implementation for orchestrator_bridge.

This plugin remains a UI and process bridge only:
- loads conservative runtime configuration from local JSON,
- launches the approved one_button.ps1 asynchronously,
- streams stdout and stderr live without freezing the host UI,
- parses structured output plus robust fallbacks,
- persists the latest N runs to tools/_local/orchestrator_bridge,
- exposes rerun and output convenience actions.

It does not implement business logic from the external orchestrator engine.
"""

from __future__ import annotations

import json
import ntpath
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

_THIS_FILE = Path(__file__).resolve()
_APP_ROOT = _THIS_FILE.parents[4]
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from app.gui_qt.plugins.plugin_base import Plugin, PluginContext


QT_API = ""
try:  # pragma: no cover
    from PySide6.QtCore import QProcess, QTimer, Qt
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QProgressBar,
        QPushButton,
        QSizePolicy,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_API = "PySide6"
except Exception:  # pragma: no cover
    try:
        from PyQt6.QtCore import QProcess, QTimer, Qt
        from PyQt6.QtWidgets import (
            QApplication,
            QCheckBox,
            QComboBox,
            QFormLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPlainTextEdit,
            QProgressBar,
            QPushButton,
            QSizePolicy,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        QT_API = "PyQt6"
    except Exception:  # pragma: no cover
        try:
            from PySide2.QtCore import QProcess, QTimer, Qt
            from PySide2.QtWidgets import (
                QApplication,
                QCheckBox,
                QComboBox,
                QFormLayout,
                QGroupBox,
                QHBoxLayout,
                QLabel,
                QLineEdit,
                QPlainTextEdit,
                QProgressBar,
                QPushButton,
                QSizePolicy,
                QTextEdit,
                QVBoxLayout,
                QWidget,
            )

            QT_API = "PySide2"
        except Exception:  # pragma: no cover
            try:
                from PyQt5.QtCore import QProcess, QTimer, Qt  # type: ignore
                from PyQt5.QtWidgets import (  # type: ignore
                    QApplication,
                    QCheckBox,
                    QComboBox,
                    QFormLayout,
                    QGroupBox,
                    QHBoxLayout,
                    QLabel,
                    QLineEdit,
                    QPlainTextEdit,
                    QProgressBar,
                    QPushButton,
                    QSizePolicy,
                    QTextEdit,
                    QVBoxLayout,
                    QWidget,
                )

                QT_API = "PyQt5"
            except Exception:  # pragma: no cover
                QT_API = "stub"

                class _SignalStub:
                    def connect(self, *_args: Any, **_kwargs: Any) -> None:
                        return None

                class Qt:  # type: ignore
                    TextSelectableByMouse = 1

                    class TextInteractionFlag:
                        TextSelectableByMouse = 1

                class QWidget:  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        self._visible = False
                    def setObjectName(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setWindowTitle(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def show(self) -> None:
                        self._visible = True
                    def raise_(self) -> None:
                        return None
                    def activateWindow(self) -> None:
                        return None
                    def setLayout(self, *args: Any, **kwargs: Any) -> None:
                        return None

                class QApplication:  # type: ignore
                    @staticmethod
                    def instance() -> Any:
                        return QApplication()
                    @staticmethod
                    def clipboard() -> Any:
                        class _Clipboard:
                            def setText(self, *_args: Any, **_kwargs: Any) -> None:
                                return None
                        return _Clipboard()

                class _LayoutStub:
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def addWidget(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def addStretch(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def addRow(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setContentsMargins(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setSpacing(self, *args: Any, **kwargs: Any) -> None:
                        return None

                class QVBoxLayout(_LayoutStub):  # type: ignore
                    pass

                class QHBoxLayout(_LayoutStub):  # type: ignore
                    pass

                class QFormLayout(_LayoutStub):  # type: ignore
                    pass

                class QGroupBox(QWidget):  # type: ignore
                    pass

                class QLabel(QWidget):  # type: ignore
                    def __init__(self, text: str = "", *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                        self._text = text
                    def setText(self, value: str) -> None:
                        self._text = value
                    def text(self) -> str:
                        return self._text
                    def setWordWrap(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setTextInteractionFlags(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setStyleSheet(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setSizePolicy(self, *args: Any, **kwargs: Any) -> None:
                        return None

                class QLineEdit(QWidget):  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                        self._text = ""
                    def setPlaceholderText(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setText(self, value: str) -> None:
                        self._text = value
                    def text(self) -> str:
                        return self._text

                class QTextEdit(QWidget):  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                        self._text = ""
                    def setPlaceholderText(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setFixedHeight(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setAcceptRichText(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setPlainText(self, value: str) -> None:
                        self._text = value
                    def toPlainText(self) -> str:
                        return self._text

                class QPlainTextEdit(QTextEdit):  # type: ignore
                    NoWrap = 0
                    class LineWrapMode:
                        NoWrap = 0
                    def setReadOnly(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setLineWrapMode(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def appendPlainText(self, value: str) -> None:
                        self._text = (self._text + ("\n" if self._text else "") + value)
                    def clear(self) -> None:
                        self._text = ""
                    def verticalScrollBar(self) -> Any:
                        class _Bar:
                            def maximum(self) -> int:
                                return 0
                            def setValue(self, *_args: Any, **_kwargs: Any) -> None:
                                return None
                        return _Bar()

                class QPushButton(QWidget):  # type: ignore
                    def __init__(self, text: str = "", *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                        self._text = text
                        self.clicked = _SignalStub()
                    def setEnabled(self, *args: Any, **kwargs: Any) -> None:
                        return None

                class QCheckBox(QPushButton):  # type: ignore
                    def __init__(self, text: str = "", *args: Any, **kwargs: Any) -> None:
                        super().__init__(text, *args, **kwargs)
                        self._checked = False
                    def setChecked(self, value: bool) -> None:
                        self._checked = bool(value)
                    def isChecked(self) -> bool:
                        return self._checked

                class QComboBox(QWidget):  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                        self._items: List[str] = []
                        self._index = 0
                    def addItems(self, items: Iterable[str]) -> None:
                        self._items.extend(list(items))
                    def currentText(self) -> str:
                        return self._items[self._index] if self._items else ""
                    def findText(self, text_value: str) -> int:
                        try:
                            return self._items.index(text_value)
                        except ValueError:
                            return -1
                    def setCurrentIndex(self, index: int) -> None:
                        self._index = index if 0 <= index < len(self._items) else 0
                    def setEnabled(self, *args: Any, **kwargs: Any) -> None:
                        return None

                class QProgressBar(QWidget):  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                    def setTextVisible(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setFixedHeight(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setRange(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setVisible(self, *args: Any, **kwargs: Any) -> None:
                        return None

                class QSizePolicy:  # type: ignore
                    Expanding = 0
                    Preferred = 0

                class QTimer:  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        self.timeout = _SignalStub()
                    def setSingleShot(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def start(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def stop(self) -> None:
                        return None

                class QProcess:  # type: ignore
                    class ProcessState:
                        NotRunning = 0
                    class ExitStatus:
                        NormalExit = 0
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        self.readyReadStandardOutput = _SignalStub()
                        self.readyReadStandardError = _SignalStub()
                        self.started = _SignalStub()
                        self.finished = _SignalStub()
                        self.errorOccurred = _SignalStub()
                    def setProgram(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setArguments(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setWorkingDirectory(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def start(self) -> None:
                        return None
                    def kill(self) -> None:
                        return None
                    def terminate(self) -> None:
                        return None
                    def state(self) -> int:
                        return self.ProcessState.NotRunning
                    def readAllStandardOutput(self) -> bytes:
                        return b""
                    def readAllStandardError(self) -> bytes:
                        return b""


PLUGIN_ID = "orchestrator_bridge"
PLUGIN_NAME = "Orchestrator Bridge"
PLUGIN_VERSION = "0.6.0"
DOCK_TITLE = "Orchestrator Bridge"
MENU_TEXT = "Orchestrator Bridge"
TOOLBAR_TEXT = "Orchestrator Bridge"

REPO_ROOT = r"F:\repos\hitech-os"
PLUGIN_HOST_ROOT = r"F:\repos\hitech-os\tools\graphviz\repo_analizer"
ORCHESTRATOR_ROOT = r"F:\repos\hitech-os\tools\orchestrator_factory"
DEFAULT_ONE_BUTTON_PATH = r"F:\repos\hitech-os\tools\orchestrator_factory\tools\one_button.ps1"
DEFAULT_HANDOFF_DIR = r"F:\OneDrive\Descargas"
DEFAULT_RUNTIME_ROOT = r"F:\repos\hitech-os\tools\_local\orchestrator_bridge"
PLUGIN_CONFIG_FILENAME = "bridge_config.json"
HISTORY_FILENAME = "last_runs.json"

DEFAULT_BADGE = "Idle"
DEFAULT_DETAIL = "Waiting for configuration and environment validation."
DEFAULT_RESULT = "not_run"
DEFAULT_CONTRACT_DETAIL = "NOT_RUN"
DEFAULT_EXIT_CODE = "<none>"
DEFAULT_ZIP_PATH = "<none>"

ZIP_FALLBACK_RE = re.compile(r"([A-Za-z]:\\[^\r\n|]*?\.zip)", re.IGNORECASE)
REUSE_RE = re.compile(r"\b(reused?|re-using|using existing|already exists?|existing artifact)\b", re.IGNORECASE)
WARNING_RE = re.compile(r"\b(warn(?:ing)?|caution)\b", re.IGNORECASE)
ERROR_RE = re.compile(r"\b(error|failed?|exception|fatal|traceback)\b", re.IGNORECASE)
BLOCKED_RE = re.compile(r"\b(blocked|denied|forbidden|policy violation|not allowed)\b", re.IGNORECASE)
SUCCESS_RE = re.compile(r"\b(success(?:ful|fully)?|completed?|done|finished)\b", re.IGNORECASE)
WINDOWS_ABS_RE = re.compile(r"^[A-Za-z]:\\")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

EXIT_CODE_MAP: Dict[int, str] = {
    0: "Succeeded",
    10: "FailedRetryable",
    20: "Failed",
    30: "Blocked",
    40: "Failed",
    50: "Blocked",
    60: "FailedRetryable",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "one_button_path": DEFAULT_ONE_BUTTON_PATH,
    "default_handoff_dir": DEFAULT_HANDOFF_DIR,
    "runtime_root": DEFAULT_RUNTIME_ROOT,
    "timeouts": {
        "startup_ms": 15000,
        "run_ms": 1800000,
        "kill_after_timeout_ms": 3000,
    },
    "history": {
        "max_runs": 25,
    },
}

THEME_TOKENS: Dict[str, str] = {
    "font_family": "Segoe UI, Arial, sans-serif",
    "bg": "#0f141c",
    "surface": "#151c27",
    "surface_alt": "#101823",
    "surface_soft": "#1a2230",
    "surface_raised": "#202a3a",
    "border": "rgba(255,255,255,0.10)",
    "border_strong": "rgba(255,255,255,0.18)",
    "text": "#eef4ff",
    "text_dim": "#b2bfd4",
    "text_muted": "#8c9bb3",
    "accent": "#67b7ff",
    "accent_soft": "rgba(103,183,255,0.16)",
    "success": "#42d392",
    "success_soft": "rgba(66,211,146,0.16)",
    "warning": "#f6c458",
    "warning_soft": "rgba(246,196,88,0.16)",
    "danger": "#ff6b7a",
    "danger_soft": "rgba(255,107,122,0.16)",
    "blocked": "#ff9e58",
    "blocked_soft": "rgba(255,158,88,0.16)",
    "radius_l": "18px",
    "radius_m": "12px",
    "radius_s": "10px",
    "space_xs": "6px",
    "space_s": "10px",
    "space_m": "14px",
    "space_l": "18px",
}

STATE_VISUALS: Dict[str, Dict[str, str]] = {
    "idle": {"chip": "#8c9bb3", "soft": "rgba(140,155,179,0.16)", "title": "Idle"},
    "ready": {"chip": "#67b7ff", "soft": "rgba(103,183,255,0.16)", "title": "Ready"},
    "running": {"chip": "#67b7ff", "soft": "rgba(103,183,255,0.22)", "title": "Running"},
    "success": {"chip": "#42d392", "soft": "rgba(66,211,146,0.18)", "title": "Success"},
    "reused": {"chip": "#7dd3fc", "soft": "rgba(125,211,252,0.18)", "title": "Reused"},
    "blocked": {"chip": "#ff9e58", "soft": "rgba(255,158,88,0.20)", "title": "Blocked"},
    "failed": {"chip": "#ff6b7a", "soft": "rgba(255,107,122,0.20)", "title": "Failed"},
}


def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def _text_selectable_flag() -> Any:
    flag = getattr(Qt, "TextSelectableByMouse", None)
    if flag is not None:
        return flag
    interaction = getattr(Qt, "TextInteractionFlag", None)
    if interaction is not None:
        return interaction.TextSelectableByMouse
    return 0


def _line_wrap_no_wrap() -> Any:
    enum = getattr(QPlainTextEdit, "NoWrap", None)
    if enum is not None:
        return enum
    line_wrap_mode = getattr(QPlainTextEdit, "LineWrapMode", None)
    if line_wrap_mode is not None:
        return line_wrap_mode.NoWrap
    return 0


def _normalize_windows_path(path_value: str) -> str:
    return ntpath.normcase(ntpath.normpath((path_value or "").strip().strip('"')))


def _is_windows_abs(path_value: str) -> bool:
    return bool(path_value and WINDOWS_ABS_RE.match(path_value.strip().strip('"')))


def _is_under_any_root(path_value: str, roots: Iterable[str]) -> bool:
    normalized_path = _normalize_windows_path(path_value)
    for root in roots:
        normalized_root = _normalize_windows_path(root)
        if not normalized_root:
            continue
        if normalized_path == normalized_root:
            return True
        if normalized_path.startswith(normalized_root + "\\"):
            return True
    return False


def _safe_json_load(path_value: str) -> Dict[str, Any]:
    try:
        if not path_value or not os.path.isfile(path_value):
            return {}
        with open(path_value, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _safe_json_dump(path_value: str, payload: Any) -> Tuple[bool, str]:
    directory = os.path.dirname(path_value)
    try:
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path_value, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def _coerce_int(value: Any, default_value: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default_value
    return max(minimum, min(maximum, parsed))


def _quote_ps_arg(arg: str) -> str:
    return arg.replace("\x00", " ").strip()


def map_exit_code_to_contract_detail(
    exit_code: int,
    warnings_present: bool = False,
    timed_out: bool = False,
    contract_violations_present: bool = False,
    status_hint: str = "",
) -> str:
    if timed_out:
        return "LaunchTimeout"
    if contract_violations_present:
        return "Blocked"
    detail = EXIT_CODE_MAP.get(exit_code, "Failed")
    if exit_code not in EXIT_CODE_MAP and (status_hint or "").strip().lower() in ("success", "reused", "blocked", "failed"):
        detail = {
            "success": "Succeeded",
            "reused": "Succeeded",
            "blocked": "Blocked",
            "failed": "Failed",
        }[(status_hint or "").strip().lower()]
    if detail == "Succeeded" and warnings_present:
        return "SucceededWithWarnings"
    return detail


def normalize_contract_detail_to_ui_status(
    contract_detail: str,
    reused_detected: bool = False,
    status_hint: str = "",
) -> str:
    if contract_detail in ("Succeeded", "SucceededWithWarnings"):
        if reused_detected or (status_hint or "").strip().lower() == "reused":
            return "reused"
        return "success"
    if contract_detail == "Blocked":
        return "blocked"
    return "failed"


def validate_request_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    mode = str(payload.get("mode") or "").strip().lower()
    project_id = str(payload.get("project_id") or "").strip()
    policy = str(payload.get("policy") or "").strip()
    intent = str(payload.get("intent") or "").strip()
    non_interactive = bool(payload.get("non_interactive"))

    if mode not in ("existing", "new", "existing_project", "new_project"):
        errors.append("Mode must be either 'existing'/'new' or 'existing_project'/'new_project'.")
    if non_interactive and not project_id:
        errors.append("Project ID is required when Non-interactive is enabled.")
    if project_id and not PROJECT_ID_RE.match(project_id):
        errors.append(
            "Project ID contains invalid characters. Use letters, numbers, dot, dash, or underscore only."
        )
    if policy and CONTROL_CHAR_RE.search(policy):
        errors.append("Policy contains control characters. Clean the value and try again.")
    if intent and CONTROL_CHAR_RE.search(intent):
        errors.append("Intent contains control characters. Clean the text and try again.")
    return errors


def load_plugin_manifest(plugin_dir: str) -> Dict[str, Any]:
    manifest_path = os.path.join(plugin_dir, 'plugin.json')
    data = _safe_json_load(manifest_path)
    return data if isinstance(data, dict) else {}


@dataclass
class BridgeConfig:
    one_button_path: str
    default_handoff_dir: str
    runtime_root: str
    startup_timeout_ms: int
    run_timeout_ms: int
    kill_after_timeout_ms: int
    max_runs: int
    config_path: str = ""

    @property
    def history_path(self) -> str:
        return ntpath.join(self.runtime_root, HISTORY_FILENAME)

    @property
    def allowed_output_roots(self) -> List[str]:
        roots = [REPO_ROOT, PLUGIN_HOST_ROOT, ORCHESTRATOR_ROOT, self.default_handoff_dir, self.runtime_root]
        return [root for root in roots if root]

    def validate(self) -> List[str]:
        problems: List[str] = []
        if not self.one_button_path:
            problems.append("Configuration missing one_button_path.")
        elif not _is_windows_abs(self.one_button_path):
            problems.append(f"Configured one_button_path must be an absolute Windows path: {self.one_button_path}")
        elif not self.one_button_path.lower().endswith(".ps1"):
            problems.append(f"Configured one_button_path must point to a .ps1 file: {self.one_button_path}")
        elif not _is_under_any_root(self.one_button_path, [ORCHESTRATOR_ROOT]):
            problems.append(
                f"Configured one_button_path is outside the approved orchestrator root: {self.one_button_path}"
            )

        if not self.default_handoff_dir:
            problems.append("Configuration missing default_handoff_dir.")
        elif not _is_windows_abs(self.default_handoff_dir):
            problems.append(
                f"Configured default_handoff_dir must be an absolute Windows path: {self.default_handoff_dir}"
            )

        if not self.runtime_root:
            problems.append("Configuration missing runtime_root.")
        elif not _is_windows_abs(self.runtime_root):
            problems.append(f"Configured runtime_root must be an absolute Windows path: {self.runtime_root}")
        elif not _is_under_any_root(self.runtime_root, [ntpath.join(REPO_ROOT, "tools", "_local")]):
            problems.append(f"Configured runtime_root must stay under tools\\_local: {self.runtime_root}")

        if self.startup_timeout_ms <= 0:
            problems.append("Configured startup timeout must be greater than zero.")
        if self.run_timeout_ms <= 0:
            problems.append("Configured run timeout must be greater than zero.")
        if self.kill_after_timeout_ms <= 0:
            problems.append("Configured kill_after_timeout_ms must be greater than zero.")
        if self.max_runs <= 0:
            problems.append("Configured history.max_runs must be greater than zero.")
        return problems


@dataclass
class ParseState:
    phases: List[Tuple[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    contract_violations: List[str] = field(default_factory=list)
    raw_zip_path: str = ""
    accepted_zip_path: str = ""
    reused_detected: bool = False
    status_hint: str = ""
    last_status_message: str = ""
    total_lines: int = 0

    def note_warning(self, message: str) -> None:
        if message and message not in self.warnings:
            self.warnings.append(message)

    def note_error(self, message: str) -> None:
        if message and message not in self.errors:
            self.errors.append(message)

    def note_contract_violation(self, message: str) -> None:
        if message and message not in self.contract_violations:
            self.contract_violations.append(message)

    def note_status_hint(self, candidate: str) -> None:
        normalized = (candidate or "").strip().lower()
        if normalized in ("success", "reused", "blocked", "failed"):
            self.status_hint = normalized


class _OutputParser:
    def __init__(self, config: BridgeConfig) -> None:
        self._config = config
        self.state = ParseState()

    def ingest_line(self, line: str, source: str) -> None:
        text = (line or "").rstrip("\r\n")
        if not text:
            return

        self.state.total_lines += 1
        if self._try_structured(text):
            return

        self._try_zip_fallback(text)
        self._try_warning_fallback(text, source)
        self._try_error_fallback(text, source)
        self._try_reuse_fallback(text)
        self._try_status_fallback(text)

    def finalize(self, exit_code: int, timed_out: bool = False) -> Dict[str, Any]:
        contract_detail = map_exit_code_to_contract_detail(
            exit_code=exit_code,
            warnings_present=bool(self.state.warnings),
            timed_out=timed_out,
            contract_violations_present=bool(self.state.contract_violations),
            status_hint=self.state.status_hint,
        )
        normalized_status = normalize_contract_detail_to_ui_status(
            contract_detail=contract_detail,
            reused_detected=bool(self.state.reused_detected),
            status_hint=self.state.status_hint,
        )

        final_message = self.state.last_status_message or contract_detail
        if timed_out:
            final_message = "Execution timed out before the bridge received a final completion signal."
        elif self.state.contract_violations:
            final_message = self.state.contract_violations[-1]
        elif contract_detail == "SucceededWithWarnings" and self.state.warnings:
            final_message = self.state.warnings[-1]
        elif normalized_status in ("failed", "blocked") and self.state.errors:
            final_message = self.state.errors[-1]

        return {
            "normalized_status": normalized_status,
            "contract_detail": contract_detail,
            "zip_path": self.state.accepted_zip_path or self.state.raw_zip_path,
            "zip_path_publicable": bool(self.state.accepted_zip_path),
            "warnings": list(self.state.warnings),
            "errors": list(self.state.errors),
            "contract_violations": list(self.state.contract_violations),
            "reused_detected": bool(self.state.reused_detected),
            "last_status_message": final_message,
            "structured_status_count": len(self.state.phases),
            "total_lines": self.state.total_lines,
        }

    def _try_structured(self, text: str) -> bool:
        if text.startswith("OB_STATUS|"):
            parts = text.split("|", 2)
            if len(parts) != 3 or not parts[1].strip() or not parts[2].strip():
                self.state.note_contract_violation(f"Malformed OB_STATUS line: {text}")
                return True
            phase = parts[1].strip()
            message = parts[2].strip()
            self.state.phases.append((phase, message))
            self.state.last_status_message = f"{phase}: {message}"
            self._try_reuse_fallback(message)
            self._try_status_fallback(phase)
            self._try_status_fallback(message)
            return True

        if text.startswith("OB_ZIP|"):
            parts = text.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                self.state.note_contract_violation(f"Malformed OB_ZIP line: {text}")
                return True
            self._register_zip_candidate(parts[1].strip(), exact_contract=True)
            return True

        if text.startswith("OB_WARNING|"):
            parts = text.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                self.state.note_contract_violation(f"Malformed OB_WARNING line: {text}")
                return True
            self.state.note_warning(parts[1].strip())
            return True

        if text.startswith("OB_ERROR|"):
            parts = text.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                self.state.note_contract_violation(f"Malformed OB_ERROR line: {text}")
                return True
            self.state.note_error(parts[1].strip())
            return True

        return False

    def _register_zip_candidate(self, candidate: str, exact_contract: bool) -> None:
        candidate = candidate.strip().strip('"')
        if not candidate:
            return

        if not _is_windows_abs(candidate):
            if exact_contract:
                self.state.note_contract_violation(f"OB_ZIP is not an absolute Windows path: {candidate}")
            return

        if not candidate.lower().endswith(".zip"):
            if exact_contract:
                self.state.note_contract_violation(f"OB_ZIP is not a .zip path: {candidate}")
            return

        if not self.state.raw_zip_path:
            self.state.raw_zip_path = candidate

        if self._is_publicable_zip_path(candidate):
            if not self.state.accepted_zip_path:
                self.state.accepted_zip_path = candidate
            elif _normalize_windows_path(self.state.accepted_zip_path) != _normalize_windows_path(candidate):
                self.state.note_contract_violation(
                    f"Conflicting ZIP paths received: {self.state.accepted_zip_path} vs {candidate}"
                )
        elif exact_contract:
            self.state.note_warning(f"ZIP path outside allowed roots or not found yet: {candidate}")

    def _is_publicable_zip_path(self, path_value: str) -> bool:
        if not path_value or not _is_windows_abs(path_value):
            return False
        if not path_value.lower().endswith(".zip"):
            return False
        if not _is_under_any_root(path_value, self._config.allowed_output_roots):
            return False
        return os.path.exists(path_value)

    def _try_zip_fallback(self, text: str) -> None:
        match = ZIP_FALLBACK_RE.search(text)
        if match:
            self._register_zip_candidate(match.group(1), exact_contract=False)

    def _try_warning_fallback(self, text: str, source: str) -> None:
        if WARNING_RE.search(text):
            self.state.note_warning(f"{source}: {text}")

    def _try_error_fallback(self, text: str, source: str) -> None:
        if ERROR_RE.search(text) or BLOCKED_RE.search(text):
            self.state.note_error(f"{source}: {text}")

    def _try_reuse_fallback(self, text: str) -> None:
        if REUSE_RE.search(text):
            self.state.reused_detected = True
            self.state.note_status_hint("reused")

    def _try_status_fallback(self, text: str) -> None:
        if REUSE_RE.search(text):
            self.state.note_status_hint("reused")
            return
        if BLOCKED_RE.search(text):
            self.state.note_status_hint("blocked")
            return
        if ERROR_RE.search(text):
            self.state.note_status_hint("failed")
            return
        if SUCCESS_RE.search(text):
            self.state.note_status_hint("success")

    def _contract_detail_from_exit(self, exit_code: int) -> str:
        detail = EXIT_CODE_MAP.get(exit_code, "Failed")
        if exit_code == 0 and self.state.warnings:
            return "SucceededWithWarnings"
        if exit_code not in EXIT_CODE_MAP:
            self.state.note_error(f"UnknownExitCode: {exit_code}")
        return detail


def _load_bridge_config(plugin_dir: str) -> Tuple[BridgeConfig, List[str]]:
    config_path = os.path.join(plugin_dir, PLUGIN_CONFIG_FILENAME)
    raw = _safe_json_load(config_path)

    one_button_path = str(raw.get("one_button_path") or DEFAULT_CONFIG["one_button_path"]).strip()
    default_handoff_dir = str(raw.get("default_handoff_dir") or DEFAULT_CONFIG["default_handoff_dir"]).strip()
    runtime_root = str(raw.get("runtime_root") or DEFAULT_CONFIG["runtime_root"]).strip()

    timeouts_raw = raw.get("timeouts") if isinstance(raw.get("timeouts"), dict) else {}
    history_raw = raw.get("history") if isinstance(raw.get("history"), dict) else {}

    config = BridgeConfig(
        one_button_path=one_button_path,
        default_handoff_dir=default_handoff_dir,
        runtime_root=runtime_root,
        startup_timeout_ms=_coerce_int(
            timeouts_raw.get("startup_ms"),
            int(DEFAULT_CONFIG["timeouts"]["startup_ms"]),
            1000,
            600000,
        ),
        run_timeout_ms=_coerce_int(
            timeouts_raw.get("run_ms"),
            int(DEFAULT_CONFIG["timeouts"]["run_ms"]),
            5000,
            28800000,
        ),
        kill_after_timeout_ms=_coerce_int(
            timeouts_raw.get("kill_after_timeout_ms"),
            int(DEFAULT_CONFIG["timeouts"]["kill_after_timeout_ms"]),
            1000,
            30000,
        ),
        max_runs=_coerce_int(
            history_raw.get("max_runs"),
            int(DEFAULT_CONFIG["history"]["max_runs"]),
            1,
            500,
        ),
        config_path=config_path,
    )
    return config, config.validate()


class _BridgePanel(QWidget):
    """Premium dock content for the bridge runner."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("orchestrator_bridge_panel")
        self.setWindowTitle(DOCK_TITLE)

        self._plugin_dir = os.path.abspath(os.path.dirname(__file__))
        self._config, self._config_problems = _load_bridge_config(self._plugin_dir)
        self._process: Optional[QProcess] = None
        self._parser: Optional[_OutputParser] = None
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._run_in_progress = False
        self._current_payload: Dict[str, Any] = {}
        self._last_launched_payload: Dict[str, Any] = {}
        self._last_result: Dict[str, Any] = {}
        self._terminal_error_handled = False
        self._timeout_triggered = False
        self._history_records: List[Dict[str, Any]] = []
        self._timeline_records: List[str] = []
        self._pulse_phase = 0

        self._startup_timer = QTimer(self)
        self._startup_timer.setSingleShot(True)
        self._startup_timer.timeout.connect(self._on_startup_timeout)

        self._run_timer = QTimer(self)
        self._run_timer.setSingleShot(True)
        self._run_timer.timeout.connect(self._on_run_timeout)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._on_pulse_tick)

        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._clear_feedback)

        self._build_ui()
        self._wire_events()
        self._ensure_runtime_ready(log_if_ok=True)
        self._history_records = self._load_history_records()
        self._hydrate_last_payload_from_history()
        self._render_history_records()
        self._refresh_ready_state()
        self._append_log(f"[{_utc_now()}] UI ready on {QT_API}. Wave 6 premium UI active.")
        self._append_log(f"[{_utc_now()}] Config file: {self._config.config_path}")
        self._append_log(f"[{_utc_now()}] Runtime root: {self._config.runtime_root}")
        self._push_timeline_event("Bridge ready", "Premium dock initialized without changing runner boundaries.", "info")

    def _build_stylesheet(self) -> str:
        t = THEME_TOKENS
        return f"""
        QWidget#orchestrator_bridge_panel {{
            background: {t['bg']};
            color: {t['text']};
            font-family: {t['font_family']};
        }}
        QGroupBox {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {t['surface_raised']}, stop:1 {t['surface']});
            border: 1px solid {t['border']};
            border-radius: {t['radius_l']};
            margin-top: 16px;
            padding: 12px;
            font-weight: 600;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 14px;
            top: -10px;
            padding: 0 8px;
            color: {t['text_dim']};
            background: {t['bg']};
            border-radius: 8px;
        }}
        QLabel#bridgeHeadline {{
            font-size: 17px;
            font-weight: 700;
            color: {t['text']};
        }}
        QLabel#bridgeSubtle, QLabel#bridgeMeta, QLabel#bridgeResultLabel {{
            color: {t['text_dim']};
        }}
        QLabel#bridgeFeedbackLabel {{
            padding: 6px 10px;
            border-radius: 10px;
            background: {t['accent_soft']};
            border: 1px solid {t['border']};
            color: {t['text']};
            font-weight: 600;
        }}
        QLabel#bridgeFeedbackLabel[kind='success'] {{
            background: {t['success_soft']};
            border: 1px solid rgba(66,211,146,0.30);
        }}
        QLabel#bridgeFeedbackLabel[kind='warning'] {{
            background: {t['warning_soft']};
            border: 1px solid rgba(246,196,88,0.30);
        }}
        QLabel#bridgeFeedbackLabel[kind='danger'] {{
            background: {t['danger_soft']};
            border: 1px solid rgba(255,107,122,0.30);
        }}
        QLabel#bridgeStatusChip, QLabel#bridgeResultStatusChip {{
            padding: 6px 12px;
            border-radius: 999px;
            font-weight: 700;
            letter-spacing: 0.4px;
        }}
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
            background: {t['surface_alt']};
            border: 1px solid {t['border']};
            border-radius: {t['radius_m']};
            padding: 10px 12px;
            color: {t['text']};
            selection-background-color: rgba(103,183,255,0.34);
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
            border: 1px solid rgba(103,183,255,0.90);
            background: #0f1927;
        }}
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QComboBox:disabled {{
            color: {t['text_muted']};
            background: rgba(255,255,255,0.03);
        }}
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #283548, stop:1 #1d2735);
            border: 1px solid {t['border_strong']};
            border-radius: {t['radius_m']};
            padding: 10px 14px;
            color: {t['text']};
            font-weight: 700;
        }}
        QPushButton:hover {{
            border: 1px solid rgba(103,183,255,0.55);
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #314157, stop:1 #223044);
        }}
        QPushButton:pressed {{
            background: #192231;
            padding-top: 11px;
            padding-bottom: 9px;
        }}
        QPushButton:disabled {{
            color: {t['text_muted']};
            border: 1px solid rgba(255,255,255,0.05);
            background: rgba(255,255,255,0.04);
        }}
        QPushButton#bridgeRunButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2f6fff, stop:1 #2457ce);
            border: 1px solid rgba(103,183,255,0.75);
        }}
        QPushButton#bridgeRunButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d7bff, stop:1 #2b62e0);
        }}
        QPushButton#bridgeDangerGhost {{
            background: rgba(255,255,255,0.04);
        }}
        QCheckBox {{
            color: {t['text_dim']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 5px;
            border: 1px solid {t['border_strong']};
            background: {t['surface_alt']};
        }}
        QCheckBox::indicator:checked {{
            background: {t['accent']};
            border: 1px solid rgba(103,183,255,0.90);
        }}
        QProgressBar {{
            background: rgba(255,255,255,0.05);
            border: 1px solid {t['border']};
            border-radius: 7px;
        }}
        QProgressBar::chunk {{
            border-radius: 6px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #67b7ff, stop:1 #8fe0ff);
        }}
        """

    def _status_style(self, state_name: str) -> str:
        visual = STATE_VISUALS.get(state_name, STATE_VISUALS["idle"])
        return (
            "padding: 6px 12px; border-radius: 999px; font-weight: 700;"
            f" color: {visual['chip']}; background: {visual['soft']}; border: 1px solid {visual['chip']};"
        )

    def _build_ui(self) -> None:
        self.setStyleSheet(self._build_stylesheet())
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        self.header_group = QGroupBox("Bridge Status")
        header_layout = QVBoxLayout(self.header_group)
        header_layout.setContentsMargins(14, 14, 14, 14)
        header_layout.setSpacing(10)

        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(10)

        self.status_chip = QLabel(DEFAULT_BADGE)
        self.status_chip.setObjectName("bridgeStatusChip")
        self.status_chip.setStyleSheet(self._status_style("idle"))

        title_wrap = QWidget()
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        self.header_title = QLabel("Orchestrator Bridge")
        self.header_title.setObjectName("bridgeHeadline")
        self.status_detail = QLabel(DEFAULT_DETAIL)
        self.status_detail.setObjectName("bridgeSubtle")
        self.status_detail.setWordWrap(True)

        self.meta_label = QLabel("Bridge-only runner • Async process • Premium dock")
        self.meta_label.setObjectName("bridgeMeta")

        title_layout.addWidget(self.header_title)
        title_layout.addWidget(self.status_detail)
        title_layout.addWidget(self.meta_label)

        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("bridgeFeedbackLabel")
        self.feedback_label.hide()

        top_row_layout.addWidget(self.status_chip, 0)
        top_row_layout.addWidget(title_wrap, 1)
        top_row_layout.addWidget(self.feedback_label, 0)

        self.running_bar = QProgressBar()
        self.running_bar.setTextVisible(False)
        self.running_bar.setFixedHeight(10)
        self.running_bar.setRange(0, 1)
        self.running_bar.setVisible(False)

        header_layout.addWidget(top_row)
        header_layout.addWidget(self.running_bar)

        root.addWidget(self.header_group)
        root.addWidget(self._build_form_group())
        root.addWidget(self._build_actions_group())

        mid_row = QWidget()
        mid_layout = QHBoxLayout(mid_row)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(12)
        mid_layout.addWidget(self._build_result_group(), 1)
        mid_layout.addWidget(self._build_history_group(), 1)
        root.addWidget(mid_row)

        bottom_row = QWidget()
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(12)
        bottom_layout.addWidget(self._build_timeline_group(), 1)
        bottom_layout.addWidget(self._build_log_group(), 1)
        root.addWidget(bottom_row, 1)

    def _build_form_group(self) -> QGroupBox:
        group = QGroupBox("Run Request")
        form = QFormLayout(group)
        form.setContentsMargins(14, 18, 14, 14)
        form.setSpacing(10)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["existing", "new"])

        self.policy_edit = QLineEdit()
        self.policy_edit.setPlaceholderText("safe-default or approved policy name")

        self.project_id_edit = QLineEdit()
        self.project_id_edit.setPlaceholderText("HITECH-OS")

        self.intent_edit = QTextEdit()
        self.intent_edit.setPlaceholderText("Describe the orchestration intent that the external one_button runner should execute...")
        self.intent_edit.setFixedHeight(88)
        if hasattr(self.intent_edit, "setAcceptRichText"):
            self.intent_edit.setAcceptRichText(False)

        self.dry_run_checkbox = QCheckBox("Dry run")
        self.dry_run_checkbox.setChecked(True)

        self.non_interactive_checkbox = QCheckBox("Non-interactive")
        self.non_interactive_checkbox.setChecked(True)

        checks = QWidget()
        checks_layout = QHBoxLayout(checks)
        checks_layout.setContentsMargins(0, 0, 0, 0)
        checks_layout.setSpacing(14)
        checks_layout.addWidget(self.dry_run_checkbox)
        checks_layout.addWidget(self.non_interactive_checkbox)
        checks_layout.addStretch(1)

        helper = QLabel("Guardrails remain in the bridge. Business logic stays in one_button.ps1.")
        helper.setObjectName("bridgeSubtle")
        helper.setWordWrap(True)

        form.addRow("Mode", self.mode_combo)
        form.addRow("Policy", self.policy_edit)
        form.addRow("Project ID", self.project_id_edit)
        form.addRow("Intent", self.intent_edit)
        form.addRow("Flags", checks)
        form.addRow("Notes", helper)
        return group

    def _build_actions_group(self) -> QGroupBox:
        group = QGroupBox("Execution")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        self.run_button = QPushButton("Run Bridge")
        self.run_button.setObjectName("bridgeRunButton")
        self.rerun_button = QPushButton("Rerun Last")
        self.clear_button = QPushButton("Clear Panels")
        self.clear_button.setObjectName("bridgeDangerGhost")

        self.rerun_button.setEnabled(False)

        layout.addWidget(self.run_button)
        layout.addWidget(self.rerun_button)
        layout.addWidget(self.clear_button)
        layout.addStretch(1)
        return group

    def _build_result_group(self) -> QGroupBox:
        group = QGroupBox("Result")
        outer = QVBoxLayout(group)
        outer.setContentsMargins(14, 18, 14, 14)
        outer.setSpacing(10)

        selectable = _text_selectable_flag()

        header_row = QWidget()
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.result_status_value = QLabel(DEFAULT_RESULT)
        self.result_status_value.setObjectName("bridgeResultStatusChip")
        self.result_status_value.setTextInteractionFlags(selectable)
        self.result_status_value.setStyleSheet(self._status_style("idle"))

        self.result_hint_label = QLabel("No result published yet.")
        self.result_hint_label.setObjectName("bridgeSubtle")
        self.result_hint_label.setWordWrap(True)

        header_layout.addWidget(self.result_status_value, 0)
        header_layout.addWidget(self.result_hint_label, 1)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)

        self.result_contract_detail_value = QLabel(DEFAULT_CONTRACT_DETAIL)
        self.result_contract_detail_value.setTextInteractionFlags(selectable)
        self.result_contract_detail_value.setWordWrap(True)

        self.result_exit_code_value = QLabel(DEFAULT_EXIT_CODE)
        self.result_exit_code_value.setTextInteractionFlags(selectable)

        self.result_zip_path_value = QLabel(DEFAULT_ZIP_PATH)
        self.result_zip_path_value.setWordWrap(True)
        self.result_zip_path_value.setTextInteractionFlags(selectable)
        self.result_zip_path_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        form.addRow("Contract Detail", self.result_contract_detail_value)
        form.addRow("Exit Code", self.result_exit_code_value)
        form.addRow("ZIP Path", self.result_zip_path_value)

        action_row = QWidget()
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)

        self.copy_zip_path_button = QPushButton("Copy ZIP Path")
        self.open_zip_button = QPushButton("Open ZIP")
        self.open_folder_button = QPushButton("Open Folder")

        self.open_zip_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.copy_zip_path_button.setEnabled(False)

        action_layout.addWidget(self.copy_zip_path_button)
        action_layout.addWidget(self.open_zip_button)
        action_layout.addWidget(self.open_folder_button)
        action_layout.addStretch(1)

        outer.addWidget(header_row)
        outer.addLayout(form)
        outer.addWidget(action_row)
        return group

    def _build_history_group(self) -> QGroupBox:
        group = QGroupBox("Run History")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        helper = QLabel("Last persisted launches from this bridge session footprint.")
        helper.setObjectName("bridgeSubtle")
        helper.setWordWrap(True)

        self.session_history_output = QPlainTextEdit()
        self.session_history_output.setReadOnly(True)
        self.session_history_output.setLineWrapMode(_line_wrap_no_wrap())

        layout.addWidget(helper)
        layout.addWidget(self.session_history_output)
        return group

    def _build_timeline_group(self) -> QGroupBox:
        group = QGroupBox("Execution Timeline")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        helper = QLabel("High-signal events and microfeedback for the current dock session.")
        helper.setObjectName("bridgeSubtle")
        helper.setWordWrap(True)

        self.timeline_output = QPlainTextEdit()
        self.timeline_output.setReadOnly(True)
        self.timeline_output.setLineWrapMode(_line_wrap_no_wrap())

        layout.addWidget(helper)
        layout.addWidget(self.timeline_output)
        return group

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Raw Logs")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)

        helper = QLabel("Streaming stdout/stderr from the approved one_button runner.")
        helper.setObjectName("bridgeSubtle")
        helper.setWordWrap(True)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setLineWrapMode(_line_wrap_no_wrap())

        layout.addWidget(helper)
        layout.addWidget(self.log_output)
        return group

    def _wire_events(self) -> None:
        self.run_button.clicked.connect(self._on_run_clicked)
        self.rerun_button.clicked.connect(self._on_rerun_clicked)
        self.copy_zip_path_button.clicked.connect(self._on_copy_zip_path_clicked)
        self.open_zip_button.clicked.connect(self._on_open_zip_clicked)
        self.open_folder_button.clicked.connect(self._on_open_folder_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)

    def collect_payload(self) -> Dict[str, Any]:
        return {
            "mode": self.mode_combo.currentText().strip(),
            "policy": self.policy_edit.text().strip(),
            "project_id": self.project_id_edit.text().strip(),
            "intent": self.intent_edit.toPlainText().strip(),
            "dry_run": bool(self.dry_run_checkbox.isChecked()),
            "non_interactive": bool(self.non_interactive_checkbox.isChecked()),
        }

    def show_panel(self) -> None:
        self.show()
        for method_name in ("raise_", "activateWindow"):
            method = getattr(self, method_name, None)
            if callable(method):
                method()

    def _set_label_visible(self, widget: Any, visible: bool) -> None:
        for method_name in ("setVisible", "show", "hide"):
            method = getattr(widget, method_name, None)
            if not callable(method):
                continue
            if method_name == "setVisible":
                method(bool(visible))
                return
            if visible and method_name == "show":
                method()
                return
            if (not visible) and method_name == "hide":
                method()
                return

    def _flash_feedback(self, message: str, kind: str = "info", timeout_ms: int = 1800) -> None:
        self.feedback_label.setProperty("kind", kind)
        self.feedback_label.setText(message)
        self.feedback_label.style().unpolish(self.feedback_label) if hasattr(self.feedback_label, "style") else None
        self.feedback_label.style().polish(self.feedback_label) if hasattr(self.feedback_label, "style") else None
        self._set_label_visible(self.feedback_label, True)
        self._feedback_timer.start(timeout_ms)

    def _clear_feedback(self) -> None:
        self._set_label_visible(self.feedback_label, False)

    def append_error(self, message: str) -> None:
        self._append_log(f"[{_utc_now()}] ERROR: {message}")

    def _push_timeline_event(self, title: str, detail: str, kind: str = "info") -> None:
        icon_map = {"info": "•", "run": "▶", "success": "✓", "warning": "△", "blocked": "⛔", "danger": "✕"}
        line = f"{icon_map.get(kind, '•')} [{_utc_now()}] {title} :: {detail}"
        self._timeline_records.append(line)
        self._timeline_records = self._timeline_records[-140:]
        self.timeline_output.setPlainText("\n".join(self._timeline_records))
        scrollbar = getattr(self.timeline_output, "verticalScrollBar", None)
        if callable(scrollbar):
            bar = scrollbar()
            if bar is not None and hasattr(bar, "maximum") and hasattr(bar, "setValue"):
                bar.setValue(bar.maximum())

    def _append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)
        scrollbar = getattr(self.log_output, "verticalScrollBar", None)
        if callable(scrollbar):
            bar = scrollbar()
            if bar is not None and hasattr(bar, "maximum") and hasattr(bar, "setValue"):
                bar.setValue(bar.maximum())

        lowered = message.lower()
        kind = "info"
        if " blocked" in lowered or "contract_violation" in lowered:
            kind = "blocked"
        elif "error" in lowered or "failed" in lowered or "timeout" in lowered:
            kind = "danger"
        elif "warning" in lowered or "warn" in lowered:
            kind = "warning"
        elif "process started" in lowered or "launching approved runner" in lowered or "rerunning approved runner" in lowered:
            kind = "run"
        elif "opened zip" in lowered or "opened folder" in lowered or "copied to clipboard" in lowered:
            kind = "success"
        self._push_timeline_event("Log", message, kind)

    def _set_status_badge(self, title: str, detail: str) -> None:
        normalized = str(title or "Idle").strip().lower()
        if normalized not in STATE_VISUALS:
            normalized = "idle"
        visual = STATE_VISUALS[normalized]
        display_title = visual.get("title", title or DEFAULT_BADGE)
        self.status_chip.setText(display_title)
        self.status_chip.setStyleSheet(self._status_style(normalized))
        self.status_detail.setText(detail)
        self.header_title.setText(f"Orchestrator Bridge · {display_title}")
        self.meta_label.setText(
            {
                "idle": "Bridge-only runner • Waiting for request",
                "ready": "Bridge-only runner • Validated and ready",
                "running": "Bridge-only runner • Streaming live process output",
                "success": "Bridge-only runner • Approved handoff published",
                "reused": "Bridge-only runner • Existing artifact reused",
                "blocked": "Bridge-only runner • Guardrail prevented launch",
                "failed": "Bridge-only runner • Execution ended with errors",
            }.get(normalized, "Bridge-only runner")
        )

    def _set_result(self, normalized_status: str, contract_detail: str, exit_code: Any, zip_path: str) -> None:
        normalized = (normalized_status or DEFAULT_RESULT).strip().lower()
        state_for_chip = normalized if normalized in STATE_VISUALS else "idle"
        self.result_status_value.setText(normalized or DEFAULT_RESULT)
        self.result_status_value.setStyleSheet(self._status_style(state_for_chip))
        self.result_contract_detail_value.setText(contract_detail or DEFAULT_CONTRACT_DETAIL)
        self.result_exit_code_value.setText(str(exit_code) if exit_code is not None else DEFAULT_EXIT_CODE)
        self.result_zip_path_value.setText(zip_path or DEFAULT_ZIP_PATH)
        self.result_hint_label.setText(
            {
                "success": "Artifact available. Quick actions are enabled when the ZIP remains publicable.",
                "reused": "Artifact reused from a prior successful path. Review the ZIP before handing off.",
                "blocked": "Bridge guardrails stopped the run before it could invoke business logic.",
                "failed": "Execution finished without a consumable success artifact.",
                "idle": "No result published yet.",
                "not_run": "No result published yet.",
            }.get(normalized, "Result ready for review.")
        )
        self._refresh_zip_actions()

    def _refresh_zip_actions(self) -> None:
        zip_path = str(self._last_result.get("zip_path") or "")
        publicable = bool(self._last_result.get("zip_path_publicable"))
        exists_now = bool(zip_path and os.path.exists(zip_path))
        self.copy_zip_path_button.setEnabled(bool(zip_path))
        self.open_zip_button.setEnabled(bool(zip_path and publicable and exists_now))
        folder_exists = bool(zip_path and publicable and exists_now and os.path.isdir(ntpath.dirname(zip_path)))
        self.open_folder_button.setEnabled(folder_exists)

    def _refresh_rerun_state(self) -> None:
        self.rerun_button.setEnabled(bool(self._last_launched_payload) and not self._run_in_progress)

    def _refresh_ready_state(self) -> None:
        ok, detail = self._validate_environment()
        if self._run_in_progress:
            self._set_status_badge("running", "Approved one_button.ps1 is executing asynchronously.")
            self.run_button.setEnabled(False)
            self._refresh_rerun_state()
            return
        if ok:
            self._set_status_badge("ready", detail)
            self.run_button.setEnabled(True)
        else:
            self._set_status_badge("blocked", detail)
            self.run_button.setEnabled(False)
        self._refresh_rerun_state()
        self._refresh_zip_actions()

    def _ensure_runtime_ready(self, log_if_ok: bool = False) -> Tuple[bool, str]:
        try:
            os.makedirs(self._config.runtime_root, exist_ok=True)
            if log_if_ok:
                self._append_log(f"[{_utc_now()}] Runtime directory ready: {self._config.runtime_root}")
            return True, "ok"
        except Exception as exc:
            return False, f"Could not create runtime directory {self._config.runtime_root}: {exc}"

    def _load_history_records(self) -> List[Dict[str, Any]]:
        ok, detail = self._ensure_runtime_ready(log_if_ok=False)
        if not ok:
            self._append_log(f"[{_utc_now()}] ERROR: {detail}")
            return []
        try:
            if not os.path.isfile(self._config.history_path):
                return []
            with open(self._config.history_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, list):
                raise ValueError("History file is not a JSON list.")
            records = [item for item in data if isinstance(item, dict)]
            trimmed = records[-self._config.max_runs :]
            self._append_log(f"[{_utc_now()}] Loaded {len(trimmed)} persisted run records.")
            return trimmed
        except Exception as exc:
            self._append_log(f"[{_utc_now()}] ERROR: Could not load persisted history: {exc}")
            return []

    def _persist_history_records(self) -> None:
        payload = self._history_records[-self._config.max_runs :]
        ok, detail = _safe_json_dump(self._config.history_path, payload)
        if ok:
            self._append_log(
                f"[{_utc_now()}] Persisted {len(payload)} run records to {self._config.history_path}"
            )
        else:
            self._append_log(f"[{_utc_now()}] ERROR: Could not persist history: {detail}")

    def _hydrate_last_payload_from_history(self) -> None:
        for item in reversed(self._history_records):
            request = item.get("request")
            if isinstance(request, dict):
                self._last_launched_payload = dict(request)
                break
        self._refresh_rerun_state()

    def _render_history_records(self) -> None:
        self.session_history_output.clear()
        if not self._history_records:
            self.session_history_output.setPlainText("<no persisted runs yet>")
            return
        lines: List[str] = []
        for item in reversed(self._history_records[-self._config.max_runs :]):
            lines.append(
                "[{timestamp}] {parsed_status} • exit={exit_code} • mode={mode} • policy={policy} • project_id={project_id} • zip={zip_path}".format(
                    timestamp=item.get("timestamp", "<unknown>"),
                    parsed_status=item.get("parsed_status", "<unknown>"),
                    exit_code=item.get("exit_code", "<unknown>"),
                    mode=item.get("mode", "<none>"),
                    policy=item.get("policy", "<none>"),
                    project_id=item.get("project_id", "<none>"),
                    zip_path=item.get("zip_path", "<none>") or "<none>",
                )
            )
        self.session_history_output.setPlainText("\n".join(lines))

    def _validate_environment(self) -> Tuple[bool, str]:
        if self._config_problems:
            return False, self._config_problems[0]
        if not os.path.isdir(REPO_ROOT):
            return False, f"Repo root not found: {REPO_ROOT}"
        if not os.path.isfile(self._config.one_button_path):
            return False, (
                "Configured one_button_path does not exist. Update bridge_config.json or restore the script: "
                f"{self._config.one_button_path}"
            )
        runtime_ok, runtime_detail = self._ensure_runtime_ready(log_if_ok=False)
        if not runtime_ok:
            return False, runtime_detail
        return True, "Environment and configuration validated. Ready to launch approved one_button.ps1."

    def _validate_payload(self, payload: Dict[str, Any]) -> List[str]:
        return validate_request_payload(payload)

    def _apply_payload_to_form(self, payload: Dict[str, Any]) -> None:
        mode = str(payload.get("mode") or "existing").strip().lower()
        if mode in ("existing_project",):
            mode = "existing"
        elif mode in ("new_project",):
            mode = "new"
        if mode not in ("existing", "new"):
            mode = "existing"
        index = self.mode_combo.findText(mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)
        self.policy_edit.setText(str(payload.get("policy") or ""))
        self.project_id_edit.setText(str(payload.get("project_id") or ""))
        self.intent_edit.setPlainText(str(payload.get("intent") or ""))
        self.dry_run_checkbox.setChecked(bool(payload.get("dry_run", True)))
        self.non_interactive_checkbox.setChecked(bool(payload.get("non_interactive", True)))

    def _build_process_arguments(self, payload: Dict[str, Any]) -> List[str]:
        args = ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", self._config.one_button_path]
        mode_raw = _quote_ps_arg(str(payload.get("mode") or "existing")).lower()
        session_mode = "new_project" if mode_raw in ("new", "new_project") else "existing_project"
        args.extend(["--session-mode", session_mode])

        policy_raw = _quote_ps_arg(str(payload.get("policy") or "open_new_round"))
        policy = policy_raw if policy_raw in ("resume_latest_round", "open_new_round", "upgrade") else "open_new_round"
        if session_mode == "new_project":
            policy = "open_new_round"
        args.extend(["--policy", policy])

        project_id = _quote_ps_arg(str(payload.get("project_id") or ""))
        if project_id:
            args.extend(["--project-id", project_id])

        if session_mode == "new_project":
            project_name = _quote_ps_arg(str(payload.get("project_name") or project_id or "new_project"))
            initiative_type = _quote_ps_arg(str(payload.get("initiative_type") or "general"))
            args.extend(["--project-name", project_name])
            args.extend(["--initiative-type", initiative_type])

        if payload.get("intent"):
            args.extend(["--intent", _quote_ps_arg(str(payload["intent"]))])
        if payload.get("dry_run"):
            args.append("--dry-run")
        if payload.get("non_interactive"):
            args.append("--non-interactive")
        return args

    def _resolve_powershell_program(self) -> str:
        for candidate in ("powershell.exe", "pwsh.exe"):
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
        return ""

    def _set_running_ui(self, running: bool) -> None:
        self._run_in_progress = running
        self.run_button.setEnabled(not running)
        self.clear_button.setEnabled(not running)
        self.run_button.setText("Running…" if running else "Run Bridge")
        for widget in (
            self.mode_combo,
            self.policy_edit,
            self.project_id_edit,
            self.intent_edit,
            self.dry_run_checkbox,
            self.non_interactive_checkbox,
        ):
            widget.setEnabled(not running)
        self.running_bar.setVisible(bool(running))
        if running:
            self.running_bar.setRange(0, 0)
            self._pulse_phase = 0
            self._pulse_timer.start(220)
            self.open_zip_button.setEnabled(False)
            self.open_folder_button.setEnabled(False)
            self.copy_zip_path_button.setEnabled(False)
            self._set_status_badge("running", "Approved one_button.ps1 is executing asynchronously.")
        else:
            self._pulse_timer.stop()
            self.running_bar.setRange(0, 1)
            self._refresh_ready_state()
        self._refresh_rerun_state()

    def _start_process(self, payload: Dict[str, Any], from_rerun: bool = False) -> None:
        if self._run_in_progress:
            self._append_log(f"[{_utc_now()}] Run ignored: a process is already active in this dock.")
            self._flash_feedback("Run already in progress", "warning")
            return

        ok, detail = self._validate_environment()
        if not ok:
            self._last_result = {"zip_path": "", "zip_path_publicable": False}
            self._set_status_badge("blocked", detail)
            self._set_result("blocked", "Blocked", None, "")
            self._append_log(f"[{_utc_now()}] BLOCKED: {detail}")
            self._flash_feedback("Environment blocked", "danger")
            return

        validation_errors = self._validate_payload(payload)
        if validation_errors:
            detail = validation_errors[0]
            self._last_result = {"zip_path": "", "zip_path_publicable": False}
            self._set_status_badge("blocked", detail)
            self._set_result("blocked", "InvalidInput", None, "")
            for item in validation_errors:
                self._append_log(f"[{_utc_now()}] INPUT_ERROR: {item}")
            self._flash_feedback("Fix input guardrails", "danger")
            return

        program = self._resolve_powershell_program()
        if not program:
            self._last_result = {"zip_path": "", "zip_path_publicable": False}
            self._set_status_badge("failed", "PowerShell executable not found in PATH.")
            self._set_result("failed", "LaunchFailure", None, "")
            self._append_log(f"[{_utc_now()}] ERROR: PowerShell executable not found in PATH.")
            self._flash_feedback("PowerShell missing", "danger")
            return

        self._current_payload = dict(payload)
        self._last_launched_payload = dict(payload)
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._parser = _OutputParser(self._config)
        self._last_result = {}
        self._terminal_error_handled = False
        self._timeout_triggered = False
        self._set_result(DEFAULT_RESULT, "RUNNING", None, "")
        self._set_running_ui(True)

        args = self._build_process_arguments(payload)
        launch_label = "Rerunning approved runner" if from_rerun else "Launching approved runner"
        self._append_log(f"[{_utc_now()}] {launch_label}.")
        self._append_log(f"[{_utc_now()}] PROGRAM {program}")
        self._append_log(f"[{_utc_now()}] WORKDIR {REPO_ROOT}")
        self._append_log(f"[{_utc_now()}] SCRIPT {self._config.one_button_path}")
        self._append_log(f"[{_utc_now()}] ARGS {args}")
        self._push_timeline_event("Launch request", f"mode={payload.get('mode')} policy={payload.get('policy') or '<none>'}", "run")

        process = QProcess(self)
        self._process = process
        process.setProgram(program)
        process.setArguments(args)
        process.setWorkingDirectory(REPO_ROOT)

        started = getattr(process, "started", None)
        if started is not None:
            started.connect(self._on_process_started)
        process.readyReadStandardOutput.connect(self._on_stdout_ready)
        process.readyReadStandardError.connect(self._on_stderr_ready)
        process.finished.connect(self._on_process_finished)
        error_signal = getattr(process, "errorOccurred", None)
        if error_signal is not None:
            error_signal.connect(self._on_process_error)

        process.start()
        self._startup_timer.start(self._config.startup_timeout_ms)

    def _consume_output_chunk(self, chunk: str, source: str) -> None:
        if not chunk:
            return
        if source == "stdout":
            self._stdout_buffer += chunk
            self._stdout_buffer = self._drain_buffer(self._stdout_buffer, source)
        else:
            self._stderr_buffer += chunk
            self._stderr_buffer = self._drain_buffer(self._stderr_buffer, source)

    def _drain_buffer(self, buffer_text: str, source: str) -> str:
        while True:
            newline_index = buffer_text.find("\n")
            if newline_index < 0:
                break
            line = buffer_text[: newline_index + 1]
            buffer_text = buffer_text[newline_index + 1 :]
            self._handle_output_line(line, source)
        return buffer_text

    def _flush_remaining_buffers(self) -> None:
        if self._stdout_buffer:
            self._handle_output_line(self._stdout_buffer, "stdout")
            self._stdout_buffer = ""
        if self._stderr_buffer:
            self._handle_output_line(self._stderr_buffer, "stderr")
            self._stderr_buffer = ""

    def _handle_output_line(self, line: str, source: str) -> None:
        text = (line or "").rstrip("\r\n")
        if not text:
            return
        self._append_log(f"[{_utc_now()}] {source.upper()} {text}")
        if self._parser is not None:
            self._parser.ingest_line(text, source)
            if self._parser.state.last_status_message and self._run_in_progress:
                self.status_detail.setText(self._parser.state.last_status_message)
            if text.startswith("OB_STATUS|"):
                parts = text.split("|", 2)
                if len(parts) == 3:
                    self._push_timeline_event(parts[1].strip(), parts[2].strip(), "run")
            elif text.startswith("OB_WARNING|"):
                self._push_timeline_event("Warning", text.split("|", 1)[1].strip(), "warning")
            elif text.startswith("OB_ERROR|"):
                self._push_timeline_event("Error", text.split("|", 1)[1].strip(), "danger")
            elif text.startswith("OB_ZIP|"):
                self._push_timeline_event("ZIP candidate", text.split("|", 1)[1].strip(), "success")
            elif WARNING_RE.search(text):
                self._push_timeline_event("Warning", text, "warning")
            elif ERROR_RE.search(text):
                self._push_timeline_event("Error", text, "danger")
            elif BLOCKED_RE.search(text):
                self._push_timeline_event("Blocked", text, "blocked")

    def _stop_timers(self) -> None:
        self._startup_timer.stop()
        self._run_timer.stop()

    def _arm_forced_kill(self) -> None:
        try:
            QTimer.singleShot(self._config.kill_after_timeout_ms, self._kill_process_if_needed)
        except Exception:
            self._kill_process_if_needed()

    def _kill_process_if_needed(self) -> None:
        if self._process is None:
            return
        state_func = getattr(self._process, "state", None)
        if callable(state_func):
            try:
                state_value = state_func()
            except Exception:
                state_value = None
        else:
            state_value = None

        not_running_markers = {0}
        qprocess_not_running = getattr(QProcess, "NotRunning", None)
        if qprocess_not_running is not None:
            not_running_markers.add(qprocess_not_running)
        process_state_enum = getattr(QProcess, "ProcessState", None)
        if process_state_enum is not None and hasattr(process_state_enum, "NotRunning"):
            not_running_markers.add(process_state_enum.NotRunning)

        if state_value in not_running_markers:
            return
        try:
            self._process.kill()
            self._append_log(f"[{_utc_now()}] Forced process kill issued after timeout grace period.")
            self._push_timeline_event("Forced kill", "Process exceeded timeout grace period and was killed.", "danger")
        except Exception as exc:
            self._append_log(f"[{_utc_now()}] ERROR: Could not force kill timed out process: {exc}")

    def _record_run(self, exit_code: Optional[int], result: Dict[str, Any]) -> None:
        record = {
            "timestamp": _utc_now(),
            "mode": self._current_payload.get("mode", ""),
            "policy": self._current_payload.get("policy", ""),
            "project_id": self._current_payload.get("project_id", ""),
            "intent": self._current_payload.get("intent", ""),
            "dry_run": bool(self._current_payload.get("dry_run", False)),
            "non_interactive": bool(self._current_payload.get("non_interactive", False)),
            "exit_code": exit_code if exit_code is not None else "<none>",
            "parsed_status": result.get("normalized_status", "failed"),
            "contract_detail": result.get("contract_detail", "Failed"),
            "zip_path": result.get("zip_path", ""),
            "request": dict(self._current_payload),
        }
        self._history_records.append(record)
        self._history_records = self._history_records[-self._config.max_runs :]
        self._render_history_records()
        self._persist_history_records()
        self._hydrate_last_payload_from_history()

    def _on_run_clicked(self) -> None:
        self._start_process(self.collect_payload(), from_rerun=False)

    def _on_rerun_clicked(self) -> None:
        if not self._last_launched_payload:
            self._append_log(f"[{_utc_now()}] Rerun ignored: no previous payload is available.")
            self._flash_feedback("No previous run", "warning")
            return
        self._apply_payload_to_form(self._last_launched_payload)
        self._flash_feedback("Replaying last parameters", "info")
        self._start_process(dict(self._last_launched_payload), from_rerun=True)

    def _on_process_started(self) -> None:
        self._startup_timer.stop()
        self._run_timer.start(self._config.run_timeout_ms)
        self._append_log(f"[{_utc_now()}] Process started successfully.")
        self._flash_feedback("Runner started", "info")

    def _on_stdout_ready(self) -> None:
        if self._process is None:
            return
        chunk = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._consume_output_chunk(chunk, source="stdout")

    def _on_stderr_ready(self) -> None:
        if self._process is None:
            return
        chunk = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
        self._consume_output_chunk(chunk, source="stderr")

    def _on_startup_timeout(self) -> None:
        if self._process is None or not self._run_in_progress:
            return
        self._timeout_triggered = True
        self._append_log(
            f"[{_utc_now()}] ERROR: Process did not report startup within {self._config.startup_timeout_ms} ms."
        )
        self._flash_feedback("Startup timeout", "danger")
        try:
            self._process.terminate()
        except Exception:
            pass
        self._arm_forced_kill()

    def _on_run_timeout(self) -> None:
        if self._process is None or not self._run_in_progress:
            return
        self._timeout_triggered = True
        self._append_log(f"[{_utc_now()}] ERROR: Run timeout exceeded {self._config.run_timeout_ms} ms.")
        self._flash_feedback("Run timeout", "danger")
        try:
            self._process.terminate()
        except Exception:
            pass
        self._arm_forced_kill()

    def _on_process_error(self, error_code: Any) -> None:
        self._append_log(f"[{_utc_now()}] PROCESS ERROR: {error_code}")
        if not self._run_in_progress or self._process is None or self._terminal_error_handled:
            return

        state_value = None
        state_func = getattr(self._process, "state", None)
        if callable(state_func):
            try:
                state_value = state_func()
            except Exception:
                state_value = None

        not_running_markers = {0}
        qprocess_not_running = getattr(QProcess, "NotRunning", None)
        if qprocess_not_running is not None:
            not_running_markers.add(qprocess_not_running)
        process_state_enum = getattr(QProcess, "ProcessState", None)
        if process_state_enum is not None and hasattr(process_state_enum, "NotRunning"):
            not_running_markers.add(process_state_enum.NotRunning)

        if state_value in not_running_markers or state_value is None:
            self._terminal_error_handled = True
            self._stop_timers()
            self._flush_remaining_buffers()
            self._set_running_ui(False)
            self._last_result = {"zip_path_publicable": False, "zip_path": ""}
            result = {
                "normalized_status": "failed",
                "contract_detail": "LaunchFailure",
                "zip_path": "",
                "zip_path_publicable": False,
            }
            self._set_result(result["normalized_status"], result["contract_detail"], None, "")
            self._set_status_badge("failed", f"Process launch failed: {error_code}")
            self._record_run(None, result)
            self._flash_feedback("Launch failed", "danger")
            if self._process is not None:
                self._process.deleteLater()
                self._process = None

    def _on_process_finished(self, exit_code: int, _exit_status: Any = None) -> None:
        if self._terminal_error_handled:
            return
        self._stop_timers()
        self._flush_remaining_buffers()
        self._set_running_ui(False)

        parser = self._parser or _OutputParser(self._config)
        result = parser.finalize(int(exit_code), timed_out=self._timeout_triggered)
        self._last_result = result
        self._set_result(
            result.get("normalized_status", "failed"),
            result.get("contract_detail", "Failed"),
            exit_code,
            result.get("zip_path", ""),
        )

        detail_message = result.get("last_status_message") or result.get("contract_detail", "Finished")
        badge_title = str(result.get("normalized_status", "failed")).lower()
        self._set_status_badge(badge_title, detail_message)

        if result.get("warnings"):
            self._append_log(f"[{_utc_now()}] WARNINGS: {len(result['warnings'])}")
            for item in result["warnings"]:
                self._append_log(f"[{_utc_now()}] WARNING {item}")
        if result.get("errors"):
            self._append_log(f"[{_utc_now()}] ERRORS: {len(result['errors'])}")
            for item in result["errors"]:
                self._append_log(f"[{_utc_now()}] ERROR {item}")
        if result.get("contract_violations"):
            for item in result["contract_violations"]:
                self._append_log(f"[{_utc_now()}] CONTRACT_VIOLATION {item}")

        self._record_run(int(exit_code), result)
        self._append_log(f"[{_utc_now()}] Process finished with exit code {exit_code}.")
        self._push_timeline_event("Run finished", detail_message, "success" if result.get("normalized_status") in ("success", "reused") else "danger")
        if result.get("normalized_status") in ("success", "reused"):
            self._flash_feedback("Run completed", "success")
        elif result.get("normalized_status") == "blocked":
            self._flash_feedback("Run blocked", "warning")
        else:
            self._flash_feedback("Run failed", "danger")

        if self._process is not None:
            self._process.deleteLater()
            self._process = None
        self._timeout_triggered = False

    def _on_copy_zip_path_clicked(self) -> None:
        zip_path = str(self._last_result.get("zip_path") or "")
        if not zip_path:
            self._append_log(f"[{_utc_now()}] Copy ZIP Path ignored: no ZIP path is available.")
            self._flash_feedback("No ZIP path yet", "warning")
            return
        try:
            app = QApplication.instance()
            if app is None:
                raise RuntimeError("QApplication instance not available.")
            clipboard = app.clipboard()
            if clipboard is None:
                raise RuntimeError("Clipboard is not available.")
            clipboard.setText(zip_path)
            self._append_log(f"[{_utc_now()}] ZIP path copied to clipboard: {zip_path}")
            self._flash_feedback("ZIP path copied", "success")
        except Exception as exc:
            self._append_log(f"[{_utc_now()}] ERROR: Could not copy ZIP path: {exc}")
            self._flash_feedback("Copy failed", "danger")

    def _on_open_zip_clicked(self) -> None:
        zip_path = str(self._last_result.get("zip_path") or "")
        if not zip_path or not bool(self._last_result.get("zip_path_publicable")) or not os.path.exists(zip_path):
            self._append_log(f"[{_utc_now()}] Open ZIP blocked: no accepted ZIP path is available.")
            self._flash_feedback("ZIP not available", "warning")
            return
        try:
            os.startfile(zip_path)  # type: ignore[attr-defined]
            self._append_log(f"[{_utc_now()}] Opened ZIP: {zip_path}")
            self._flash_feedback("ZIP opened", "success")
        except Exception as exc:
            self._append_log(f"[{_utc_now()}] ERROR: Could not open ZIP {zip_path}: {exc}")
            self._flash_feedback("Open ZIP failed", "danger")

    def _on_open_folder_clicked(self) -> None:
        zip_path = str(self._last_result.get("zip_path") or "")
        if not zip_path or not bool(self._last_result.get("zip_path_publicable")):
            self._append_log(f"[{_utc_now()}] Open Folder blocked: no accepted ZIP path is available.")
            self._flash_feedback("Folder not available", "warning")
            return
        folder = ntpath.dirname(zip_path)
        if not folder or not os.path.isdir(folder):
            self._append_log(f"[{_utc_now()}] Open Folder blocked: folder does not exist for {zip_path}")
            self._flash_feedback("Folder missing", "warning")
            return
        try:
            os.startfile(folder)  # type: ignore[attr-defined]
            self._append_log(f"[{_utc_now()}] Opened folder: {folder}")
            self._flash_feedback("Folder opened", "success")
        except Exception as exc:
            self._append_log(f"[{_utc_now()}] ERROR: Could not open folder {folder}: {exc}")
            self._flash_feedback("Open folder failed", "danger")

    def _on_clear_clicked(self) -> None:
        self.log_output.clear()
        self.timeline_output.clear()
        self._timeline_records = []
        self._last_result = {}
        self._set_result(DEFAULT_RESULT, DEFAULT_CONTRACT_DETAIL, None, "")
        self._refresh_ready_state()
        self._push_timeline_event("Panels cleared", "Visual panels were reset. Persisted run history remains available.", "info")
        self._append_log(f"[{_utc_now()}] Logs cleared by user. Persisted run history remains available.")
        self._flash_feedback("Panels cleared", "info")

    def _on_pulse_tick(self) -> None:
        if not self._run_in_progress:
            self._pulse_timer.stop()
            return
        variants = ("Running", "Running.", "Running..", "Running...")
        self._pulse_phase = (self._pulse_phase + 1) % len(variants)
        self.status_chip.setText(variants[self._pulse_phase])
        if self._parser is not None and self._parser.state.last_status_message:
            self.status_detail.setText(self._parser.state.last_status_message)


class PluginImplementation(Plugin):
    """Host-facing plugin implementation for the orchestrator bridge."""

    plugin_id = PLUGIN_ID
    plugin_name = PLUGIN_NAME
    version = PLUGIN_VERSION

    def __init__(self, context: Optional[PluginContext] = None) -> None:
        try:
            super().__init__()
        except Exception:
            pass
        self.context: Optional[PluginContext] = context
        self._panel: Optional[_BridgePanel] = None
        self._dock_handle: Any = None
        self._toolbar_action_handle: Any = None
        self._menu_action_handle: Any = None
        self._registered = False

    def activate(self, context: Optional[PluginContext] = None) -> None:
        self._bind_context(context)
        self._register_once()

    def initialize(self, context: Optional[PluginContext] = None) -> None:
        self._bind_context(context)
        self._register_once()

    def on_load(self, context: Optional[PluginContext] = None) -> None:
        self._bind_context(context)
        self._register_once()

    def deactivate(self) -> None:
        self._registered = False

    def _bind_context(self, context: Optional[PluginContext]) -> None:
        if context is not None:
            self.context = context

    def _register_once(self) -> None:
        if self._registered or self.context is None:
            return
        self._dock_handle = self._register_safe_dock(self.context)
        self._toolbar_action_handle = self._register_safe_toolbar_action(self.context)
        self._menu_action_handle = self._register_safe_menu_action(self.context)
        self._registered = True
        panel = self._get_or_create_panel()
        panel._append_log(f"[{_utc_now()}] Plugin registered with host safe actions.")

    def _get_or_create_panel(self) -> _BridgePanel:
        if self._panel is None:
            self._panel = _BridgePanel()
        return self._panel

    def open_dock(self) -> None:
        panel = self._get_or_create_panel()
        if self._dock_handle is not None:
            for method_name in ("show", "raise_", "activateWindow"):
                method = getattr(self._dock_handle, method_name, None)
                if callable(method):
                    method()
        panel.show_panel()
        panel._append_log(f"[{_utc_now()}] Dock opened from toolbar or menu action.")

    def _register_safe_dock(self, context: PluginContext) -> Any:
        register = getattr(context, "register_safe_dock", None)
        if not callable(register):
            self._get_or_create_panel().append_error("Host context does not expose register_safe_dock.")
            return None
        register(
            contribution_id=f"{PLUGIN_ID}.dock",
            title=DOCK_TITLE,
            widget_factory=self._get_or_create_panel,
            area="right",
            visible=True,
            object_name="orchestratorBridgeDockSurface",
        )
        return None

    def _register_safe_toolbar_action(self, context: PluginContext) -> Any:
        register = getattr(context, "register_safe_toolbar_action", None)
        if not callable(register):
            self._get_or_create_panel().append_error("Host context does not expose register_safe_toolbar_action.")
            return None
        register(
            contribution_id=f"{PLUGIN_ID}.toolbar_action",
            text=TOOLBAR_TEXT,
            callback=self.open_dock,
            tooltip="Open Orchestrator Bridge dock.",
        )
        return None

    def _register_safe_menu_action(self, context: PluginContext) -> Any:
        register = getattr(context, "register_safe_menu_action", None)
        if not callable(register):
            self._get_or_create_panel().append_error("Host context does not expose register_safe_menu_action.")
            return None
        register(
            contribution_id=f"{PLUGIN_ID}.menu_action",
            menu_path="Tools",
            text=MENU_TEXT,
            callback=self.open_dock,
            tooltip="Open Orchestrator Bridge dock.",
        )
        return None

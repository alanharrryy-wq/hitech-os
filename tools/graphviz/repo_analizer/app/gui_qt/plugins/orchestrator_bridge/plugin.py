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
try:
    from app.gui_qt.event_bus import Events
except Exception:  # pragma: no cover - plugin test harness fallback
    class Events:  # type: ignore
        PROCESS_SESSION_STATE_CHANGED = "process_session_state_changed"


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
        QScrollArea,
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
            QScrollArea,
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
                QScrollArea,
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
                    QScrollArea,
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

                class QScrollArea(QWidget):  # type: ignore
                    def __init__(self, *args: Any, **kwargs: Any) -> None:
                        super().__init__(*args, **kwargs)
                    def setWidget(self, *args: Any, **kwargs: Any) -> None:
                        return None
                    def setWidgetResizable(self, *args: Any, **kwargs: Any) -> None:
                        return None

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


from .bridge_config import (
    BridgeConfig,
    DEFAULT_CONFIG,
    DEFAULT_HANDOFF_DIR,
    DEFAULT_ONE_BUTTON_PATH,
    DEFAULT_RUNTIME_ROOT,
    ORCHESTRATOR_ROOT,
    PLUGIN_HOST_ROOT,
    REPO_ROOT,
    load_bridge_config,
    load_plugin_manifest,
)
from .bridge_contract import (
    BLOCKED_RE,
    ERROR_RE,
    MODE_EXISTING,
    MODE_NEW,
    POLICY_OPEN_NEW,
    POLICY_RESUME_LATEST,
    POLICY_UPGRADE,
    WARNING_RE,
    VALID_POLICIES,
    derive_project_id_from_name,
    map_exit_code_to_contract_detail,
    normalize_mode,
    normalize_policy,
    normalize_contract_detail_to_ui_status,
    validate_request_payload,
)
from .bridge_history import BridgeHistoryStore
from .bridge_output import OutputParser
from .process_session_controller import ProcessSessionController

PLUGIN_ID = "orchestrator_bridge"
PLUGIN_NAME = "Orchestrator Bridge"
PLUGIN_VERSION = "0.6.0"
DOCK_TITLE = "Orchestrator Bridge"
MENU_TEXT = "Orchestrator Bridge"
TOOLBAR_TEXT = "Orchestrator Bridge"

PLUGIN_CONFIG_FILENAME = "bridge_config.json"

DEFAULT_BADGE = "Idle"
DEFAULT_DETAIL = "Waiting for configuration and environment validation."
DEFAULT_RESULT = "not_run"
DEFAULT_CONTRACT_DETAIL = "NOT_RUN"
DEFAULT_EXIT_CODE = "<none>"
DEFAULT_ZIP_PATH = "<none>"

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
    "validating": {"chip": "#9ec1ff", "soft": "rgba(158,193,255,0.20)", "title": "Validating"},
    "running": {"chip": "#67b7ff", "soft": "rgba(103,183,255,0.22)", "title": "Running"},
    "success": {"chip": "#42d392", "soft": "rgba(66,211,146,0.18)", "title": "Success"},
    "succeeded": {"chip": "#42d392", "soft": "rgba(66,211,146,0.18)", "title": "Succeeded"},
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


def _quote_ps_arg(arg: str) -> str:
    return arg.replace("\x00", " ").strip()


def _format_process_error_code(error_code: Any) -> str:
    if error_code is None:
        return "process_error"
    if isinstance(error_code, bool):
        return "1" if error_code else "0"
    if isinstance(error_code, int):
        return str(error_code)
    value = getattr(error_code, "value", None)
    if isinstance(value, int):
        return str(value)
    text = str(error_code).strip()
    if not text:
        return "process_error"
    return text


_OutputParser = OutputParser
_load_bridge_config = load_bridge_config

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
        self._session_controller = ProcessSessionController(
            logger=lambda message: self._append_log(f"[{_utc_now()}] SESSION {message}"),
            transition_notifier=self._on_session_transition,
        )
        self._run_in_progress = False
        self._current_payload: Dict[str, Any] = {}
        self._last_launched_payload: Dict[str, Any] = {}
        self._last_result: Dict[str, Any] = {}
        self._active_zip_path: str = ""
        self._terminal_error_handled = False
        self._timeout_triggered = False
        self._launch_error_recorded = False
        self._history_records: List[Dict[str, Any]] = []
        self._timeline_records: List[str] = []
        self._pulse_phase = 0
        self._project_id_manual_override = False

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
        self._refresh_mode_ui()
        self._history_store = BridgeHistoryStore(
            self._config,
            logger=lambda msg: self._append_log(f"[{_utc_now()}] {msg}"),
        )
        self._ensure_runtime_ready(log_if_ok=True)
        self._history_records = self._load_history_records()
        self._hydrate_last_payload_from_history()
        self._sync_session_flags_from_controller()
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
        host_layout = QVBoxLayout(self)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(14, 14, 14, 18)
        root.setSpacing(14)

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
        root.addStretch(1)

        scroll_area.setWidget(content)
        host_layout.addWidget(scroll_area)

    def _build_form_group(self) -> QGroupBox:
        group = QGroupBox("Run Request")
        form = QFormLayout(group)
        form.setContentsMargins(14, 18, 14, 14)
        form.setSpacing(10)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([MODE_EXISTING, MODE_NEW])

        self.policy_combo = QComboBox()
        self.policy_combo.addItems([POLICY_RESUME_LATEST, POLICY_OPEN_NEW, POLICY_UPGRADE])

        self.project_id_edit = QLineEdit()
        self.project_id_edit.setPlaceholderText("project-id (auto-generated for new_project)")
        self.project_id_hint = QLabel("Auto from Project Name unless overridden.")
        self.project_id_hint.setObjectName("bridgeSubtle")
        self.project_id_hint.setWordWrap(True)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("Smoke Local")

        self.initiative_type_edit = QLineEdit()
        self.initiative_type_edit.setPlaceholderText("operations")

        self.intent_edit = QTextEdit()
        self.intent_edit.setPlaceholderText("Describe the orchestration intent that the external one_button runner should execute...")
        self.intent_edit.setFixedHeight(80)
        if hasattr(self.intent_edit, "setAcceptRichText"):
            self.intent_edit.setAcceptRichText(False)

        self.dry_run_checkbox = QCheckBox("Dry run")
        self.dry_run_checkbox.setChecked(True)

        self.non_interactive_checkbox = QCheckBox("Non-interactive (required)")
        self.non_interactive_checkbox.setChecked(True)
        self.non_interactive_checkbox.setEnabled(False)

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
        form.addRow("Policy", self.policy_combo)
        form.addRow("Project Name", self.project_name_edit)
        form.addRow("Initiative Type", self.initiative_type_edit)
        form.addRow("Project ID", self.project_id_edit)
        form.addRow("", self.project_id_hint)
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
        self.rerun_button = QPushButton("Load Last")
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

        details_form = QFormLayout()
        details_form.setContentsMargins(0, 0, 0, 0)
        details_form.setSpacing(10)

        self.result_contract_detail_value = QLabel(DEFAULT_CONTRACT_DETAIL)
        self.result_contract_detail_value.setTextInteractionFlags(selectable)
        self.result_contract_detail_value.setWordWrap(True)

        self.result_exit_code_value = QLabel(DEFAULT_EXIT_CODE)
        self.result_exit_code_value.setTextInteractionFlags(selectable)

        self.result_session_id_value = QLabel("<none>")
        self.result_session_id_value.setWordWrap(True)
        self.result_session_id_value.setTextInteractionFlags(selectable)

        self.result_mode_value = QLabel("<none>")
        self.result_mode_value.setTextInteractionFlags(selectable)
        self.result_policy_value = QLabel("<none>")
        self.result_policy_value.setTextInteractionFlags(selectable)
        self.result_dry_run_value = QLabel("<none>")
        self.result_dry_run_value.setTextInteractionFlags(selectable)
        self.result_project_id_value = QLabel("<none>")
        self.result_project_id_value.setTextInteractionFlags(selectable)
        self.result_project_name_value = QLabel("<none>")
        self.result_project_name_value.setWordWrap(True)
        self.result_project_name_value.setTextInteractionFlags(selectable)
        self.result_initiative_value = QLabel("<none>")
        self.result_initiative_value.setTextInteractionFlags(selectable)
        self.result_run_id_value = QLabel("<none>")
        self.result_run_id_value.setTextInteractionFlags(selectable)
        self.result_round_id_value = QLabel("<none>")
        self.result_round_id_value.setTextInteractionFlags(selectable)
        self.result_canonical_zip_value = QLabel(DEFAULT_ZIP_PATH)
        self.result_canonical_zip_value.setWordWrap(True)
        self.result_canonical_zip_value.setTextInteractionFlags(selectable)
        self.result_handoff_zip_value = QLabel("<none>")
        self.result_handoff_zip_value.setWordWrap(True)
        self.result_handoff_zip_value.setTextInteractionFlags(selectable)
        self.result_project_manifest_value = QLabel("<none>")
        self.result_project_manifest_value.setWordWrap(True)
        self.result_project_manifest_value.setTextInteractionFlags(selectable)
        self.result_run_manifest_value = QLabel("<none>")
        self.result_run_manifest_value.setWordWrap(True)
        self.result_run_manifest_value.setTextInteractionFlags(selectable)
        self.result_round_manifest_value = QLabel("<none>")
        self.result_round_manifest_value.setWordWrap(True)
        self.result_round_manifest_value.setTextInteractionFlags(selectable)
        self.result_lock_path_value = QLabel("<none>")
        self.result_lock_path_value.setWordWrap(True)
        self.result_lock_path_value.setTextInteractionFlags(selectable)
        self.result_ledger_path_value = QLabel("<none>")
        self.result_ledger_path_value.setWordWrap(True)
        self.result_ledger_path_value.setTextInteractionFlags(selectable)
        self.result_message_value = QLabel("<none>")
        self.result_message_value.setWordWrap(True)
        self.result_message_value.setTextInteractionFlags(selectable)

        details_form.addRow("Contract Detail", self.result_contract_detail_value)
        details_form.addRow("Exit Code", self.result_exit_code_value)
        details_form.addRow("Session ID", self.result_session_id_value)
        details_form.addRow("Mode", self.result_mode_value)
        details_form.addRow("Policy", self.result_policy_value)
        details_form.addRow("Dry Run", self.result_dry_run_value)
        details_form.addRow("Project ID", self.result_project_id_value)
        details_form.addRow("Project Name", self.result_project_name_value)
        details_form.addRow("Initiative", self.result_initiative_value)
        details_form.addRow("Run ID", self.result_run_id_value)
        details_form.addRow("Round ID", self.result_round_id_value)
        details_form.addRow("Canonical ZIP", self.result_canonical_zip_value)
        details_form.addRow("Handoff ZIP", self.result_handoff_zip_value)
        details_form.addRow("Project Manifest", self.result_project_manifest_value)
        details_form.addRow("Run Manifest", self.result_run_manifest_value)
        details_form.addRow("Round Manifest", self.result_round_manifest_value)
        details_form.addRow("Lock Path", self.result_lock_path_value)
        details_form.addRow("Ledger Path", self.result_ledger_path_value)
        details_form.addRow("Message", self.result_message_value)

        details_widget = QWidget()
        details_widget.setLayout(details_form)
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setWidget(details_widget)
        if hasattr(details_scroll, "setMinimumHeight"):
            details_scroll.setMinimumHeight(180)
        if hasattr(details_scroll, "setMaximumHeight"):
            details_scroll.setMaximumHeight(320)

        action_row = QWidget()
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)

        self.copy_zip_path_button = QPushButton("Copy ZIP Path")
        self.copy_session_id_button = QPushButton("Copy Session ID")
        self.open_zip_button = QPushButton("Open ZIP")
        self.open_folder_button = QPushButton("Open Folder")

        self.open_zip_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.copy_zip_path_button.setEnabled(False)
        self.copy_session_id_button.setEnabled(False)

        action_layout.addWidget(self.copy_zip_path_button)
        action_layout.addWidget(self.copy_session_id_button)
        action_layout.addWidget(self.open_zip_button)
        action_layout.addWidget(self.open_folder_button)
        action_layout.addStretch(1)

        outer.addWidget(header_row)
        outer.addWidget(details_scroll)
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
        if hasattr(self.session_history_output, "setMinimumHeight"):
            self.session_history_output.setMinimumHeight(180)

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
        if hasattr(self.timeline_output, "setMinimumHeight"):
            self.timeline_output.setMinimumHeight(180)

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
        if hasattr(self.log_output, "setMinimumHeight"):
            self.log_output.setMinimumHeight(180)

        layout.addWidget(helper)
        layout.addWidget(self.log_output)
        return group

    def _wire_events(self) -> None:
        self.run_button.clicked.connect(self._on_run_clicked)
        self.rerun_button.clicked.connect(self._on_rerun_clicked)
        self.copy_zip_path_button.clicked.connect(self._on_copy_zip_path_clicked)
        self.open_zip_button.clicked.connect(self._on_open_zip_clicked)
        self.open_folder_button.clicked.connect(self._on_open_folder_clicked)
        self.copy_session_id_button.clicked.connect(self._on_copy_session_id_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        self.policy_combo.currentTextChanged.connect(self._on_policy_changed)
        self.project_name_edit.textChanged.connect(self._on_project_name_changed)
        self.project_id_edit.textEdited.connect(self._on_project_id_edited)

    def collect_payload(self) -> Dict[str, Any]:
        mode = normalize_mode(self.mode_combo.currentText().strip())
        policy = normalize_policy(self.policy_combo.currentText().strip(), mode)
        return {
            "mode": mode,
            "policy": policy,
            "project_name": self.project_name_edit.text().strip(),
            "initiative_type": self.initiative_type_edit.text().strip(),
            "project_id": self.project_id_edit.text().strip(),
            "intent": self.intent_edit.toPlainText().strip(),
            "dry_run": bool(self.dry_run_checkbox.isChecked()),
            "non_interactive": True,
        }

    def _on_mode_changed(self, _value: str) -> None:
        if normalize_mode(self.mode_combo.currentText()) == MODE_NEW:
            self._project_id_manual_override = False
        self._refresh_mode_ui()

    def _on_policy_changed(self, _value: str) -> None:
        mode = normalize_mode(self.mode_combo.currentText())
        policy = normalize_policy(self.policy_combo.currentText(), mode)
        if self.policy_combo.currentText() != policy:
            self.policy_combo.blockSignals(True)
            self.policy_combo.setCurrentText(policy)
            self.policy_combo.blockSignals(False)
        intent_required = policy in {POLICY_OPEN_NEW, POLICY_UPGRADE}
        self.intent_edit.setPlaceholderText(
            "Describe the orchestration intent that the external one_button runner should execute..."
            if intent_required
            else "Optional intent for resume_latest_round."
        )

    def _on_project_name_changed(self, _value: str) -> None:
        self._sync_project_id_from_name()

    def _on_project_id_edited(self, _value: str) -> None:
        self._project_id_manual_override = True

    def _sync_project_id_from_name(self) -> None:
        mode = normalize_mode(self.mode_combo.currentText())
        if mode != MODE_NEW:
            return
        if self._project_id_manual_override:
            return
        project_name = self.project_name_edit.text().strip()
        if not project_name:
            self.project_id_edit.setText("")
            return
        generated = derive_project_id_from_name(project_name)
        self.project_id_edit.setText(generated)

    def _refresh_mode_ui(self) -> None:
        mode = normalize_mode(self.mode_combo.currentText())
        self.mode_combo.blockSignals(True)
        self.mode_combo.setCurrentText(mode)
        self.mode_combo.blockSignals(False)

        self.project_name_edit.setEnabled(mode == MODE_NEW and not self._run_in_progress)
        self.initiative_type_edit.setEnabled(mode == MODE_NEW and not self._run_in_progress)
        self.project_id_hint.setText(
            "Auto from Project Name unless overridden."
            if mode == MODE_NEW
            else "Required for existing_project mode."
        )

        selected_policy = normalize_policy(self.policy_combo.currentText(), mode)
        self.policy_combo.blockSignals(True)
        self.policy_combo.clear()
        if mode == MODE_NEW:
            self.policy_combo.addItems([POLICY_OPEN_NEW])
            self.policy_combo.setCurrentText(POLICY_OPEN_NEW)
            if not self.project_id_edit.text().strip():
                self._project_id_manual_override = False
            if not self._project_id_manual_override:
                self._sync_project_id_from_name()
        else:
            self.policy_combo.addItems([POLICY_RESUME_LATEST, POLICY_OPEN_NEW, POLICY_UPGRADE])
            selected_policy = selected_policy if selected_policy in VALID_POLICIES else POLICY_RESUME_LATEST
            self.policy_combo.setCurrentText(selected_policy)
        self.policy_combo.blockSignals(False)

        intent_required = self.policy_combo.currentText() in {POLICY_OPEN_NEW, POLICY_UPGRADE}
        intent_hint = (
            "Describe the orchestration intent that the external one_button runner should execute..."
            if intent_required
            else "Optional intent for resume_latest_round."
        )
        self.intent_edit.setPlaceholderText(intent_hint)

    def set_tool_context(self, payload: Dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            return
        local = payload.get("local")
        if not isinstance(local, dict):
            return
        policy = str(local.get("policy") or "").strip()
        project_id = str(local.get("project_id") or "").strip()
        project_name = str(local.get("project_name") or "").strip()
        initiative_type = str(local.get("initiative_type") or "").strip()
        intent = str(local.get("intent") or "").strip()
        mode = str(local.get("mode") or "").strip()
        if not any((policy, project_id, project_name, initiative_type, intent, mode)):
            return
        patch: Dict[str, Any] = {}
        if mode:
            patch["mode"] = mode
        if policy:
            patch["policy"] = policy
        if project_name:
            patch["project_name"] = project_name
        if initiative_type:
            patch["initiative_type"] = initiative_type
        if project_id:
            patch["project_id"] = project_id
        if intent:
            patch["intent"] = intent
        if patch:
            self._apply_payload_to_form(patch)

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
                "validating": "Bridge-only runner • Validating payload and runtime",
                "running": "Bridge-only runner • Streaming live process output",
                "success": "Bridge-only runner • Approved handoff published",
                "succeeded": "Bridge-only runner • Approved handoff published",
                "reused": "Bridge-only runner • Existing artifact reused",
                "blocked": "Bridge-only runner • Guardrail prevented launch",
                "failed": "Bridge-only runner • Execution ended with errors",
            }.get(normalized, "Bridge-only runner")
        )

    def _set_result(
        self,
        normalized_status: str,
        contract_detail: str,
        exit_code: Any,
        zip_path: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = dict(result or {})
        request_payload: Dict[str, Any] = dict(self._session_controller.snapshot.current_payload or {})
        if not request_payload:
            request_payload = dict(self._last_launched_payload or {})
        if not request_payload:
            try:
                request_payload = dict(self.collect_payload())
            except Exception:
                request_payload = {}

        def _pick(*keys: str, default: str = "<none>") -> str:
            for key in keys:
                candidate = payload.get(key)
                if candidate not in (None, ""):
                    return str(candidate)
            for key in keys:
                candidate = request_payload.get(key)
                if candidate not in (None, ""):
                    return str(candidate)
            return default

        normalized = (normalized_status or DEFAULT_RESULT).strip().lower()
        if normalized == "success":
            normalized = "succeeded"
        state_for_chip = normalized if normalized in STATE_VISUALS else "idle"
        self.result_status_value.setText(normalized or DEFAULT_RESULT)
        self.result_status_value.setStyleSheet(self._status_style(state_for_chip))
        self.result_contract_detail_value.setText(contract_detail or DEFAULT_CONTRACT_DETAIL)
        self.result_exit_code_value.setText(str(exit_code) if exit_code is not None else DEFAULT_EXIT_CODE)
        self.result_session_id_value.setText(_pick("session_id"))
        self.result_mode_value.setText(_pick("session_mode", "mode"))
        self.result_policy_value.setText(_pick("policy"))
        if "dry_run" in payload:
            self.result_dry_run_value.setText(str(bool(payload.get("dry_run"))))
        elif "dry_run" in request_payload:
            self.result_dry_run_value.setText(str(bool(request_payload.get("dry_run"))))
        else:
            self.result_dry_run_value.setText("<none>")
        self.result_project_id_value.setText(_pick("project_id"))
        self.result_project_name_value.setText(_pick("project_name"))
        self.result_initiative_value.setText(_pick("initiative_type"))
        self.result_run_id_value.setText(_pick("run_id"))
        self.result_round_id_value.setText(_pick("round_id"))
        self.result_canonical_zip_value.setText(
            str(payload.get("canonical_zip_path") or zip_path or DEFAULT_ZIP_PATH)
        )
        self.result_handoff_zip_value.setText(_pick("handoff_copy_path"))
        self.result_project_manifest_value.setText(_pick("project_manifest_path"))
        self.result_run_manifest_value.setText(_pick("run_manifest_path"))
        self.result_round_manifest_value.setText(_pick("round_manifest_path"))
        self.result_lock_path_value.setText(_pick("lock_path"))
        self.result_ledger_path_value.setText(_pick("ledger_path"))
        self.result_message_value.setText(_pick("message", "last_status_message"))
        self.result_hint_label.setText(
            {
                "succeeded": "Artifact available. Quick actions are enabled when the ZIP remains available.",
                "reused": "Artifact reused from a prior successful path. Review the ZIP before handing off.",
                "blocked": "Bridge guardrails stopped the run before it could invoke business logic.",
                "failed": "Execution finished without a consumable success artifact.",
                "idle": "No result published yet.",
                "not_run": "No result published yet.",
            }.get(normalized, "Result ready for review.")
        )
        self._refresh_zip_actions()

    def _refresh_zip_actions(self) -> None:
        canonical_zip = str(self._last_result.get("canonical_zip_path") or "")
        handoff_zip = str(self._last_result.get("handoff_copy_path") or "")
        fallback_zip = str(self._last_result.get("zip_path") or "")

        if canonical_zip and os.path.exists(canonical_zip):
            preferred = canonical_zip
        elif handoff_zip and os.path.exists(handoff_zip):
            preferred = handoff_zip
        else:
            preferred = fallback_zip

        self._active_zip_path = preferred
        exists_now = bool(preferred and os.path.exists(preferred))

        self.copy_zip_path_button.setEnabled(exists_now)
        self.open_zip_button.setEnabled(exists_now)
        folder_exists = bool(exists_now and os.path.isdir(ntpath.dirname(preferred)))
        self.open_folder_button.setEnabled(folder_exists)
        self.copy_session_id_button.setEnabled(bool(str(self._last_result.get("session_id") or "").strip()))

    def _sync_session_flags_from_controller(self) -> None:
        snapshot = self._session_controller.snapshot
        self._run_in_progress = bool(snapshot.run_in_progress)
        self._timeout_triggered = bool(snapshot.timeout_triggered)
        self._terminal_error_handled = bool(snapshot.terminal_error_handled)
        self._current_payload = dict(snapshot.current_payload)
        self._last_launched_payload = dict(snapshot.last_launched_payload)

    def _on_session_transition(self, payload: Dict[str, Any]) -> None:
        event_payload = dict(payload)
        event_payload["timestamp_utc"] = _utc_now()
        self._publish_process_session_event(event_payload)
        state = str(event_payload.get("state") or "").strip()
        reason = str(event_payload.get("reason") or "").strip()
        if state:
            self._push_timeline_event(
                "Session state",
                f"{state} ({reason or 'no-reason'})",
                "run" if state in {"validating", "running"} else "info",
            )

    def _publish_process_session_event(self, payload: Dict[str, Any]) -> None:
        host = self.window()
        bus = getattr(host, "event_bus", None)
        if bus is None or not hasattr(bus, "publish"):
            return
        try:
            bus.publish(Events.PROCESS_SESSION_STATE_CHANGED, dict(payload))
        except Exception:
            return

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
            self._session_controller.mark_ready(reason="environment-ok")
            self._sync_session_flags_from_controller()
            self._set_status_badge("ready", detail)
            self.run_button.setEnabled(True)
        else:
            self._set_status_badge("blocked", detail)
            self.run_button.setEnabled(False)
        self._refresh_rerun_state()
        self._refresh_zip_actions()

    def _ensure_runtime_ready(self, log_if_ok: bool = False) -> Tuple[bool, str]:
        ok, detail = self._history_store.ensure_runtime_ready()
        if ok and log_if_ok:
            self._append_log(f"[{_utc_now()}] Runtime directory ready: {self._config.runtime_root}")
        return ok, detail

    def _load_history_records(self) -> List[Dict[str, Any]]:
        records = self._history_store.load_records()
        if records:
            self._append_log(f"[{_utc_now()}] Loaded {len(records)} persisted run records.")
        return [dict(item) for item in records]

    def _persist_history_records(self) -> None:
        payload = [dict(item) for item in self._history_records[-self._config.max_runs :]]
        ok, detail = self._history_store.save_records(payload)
        if ok:
            self._append_log(
                f"[{_utc_now()}] Persisted {len(payload)} run records to {self._config.history_path}"
            )
        else:
            self._append_log(f"[{_utc_now()}] ERROR: Could not persist history: {detail}")

    def _hydrate_last_payload_from_history(self) -> None:
        candidate_payload = {
            str(k): v
            for k, v in self._history_store.extract_last_payload(
                [dict(item) for item in self._history_records]
            ).items()
        }
        ok, detail = self._session_controller.restore_last_payload(
            candidate_payload,
            validator=self._validate_payload,
        )
        if not ok:
            if candidate_payload:
                self._append_log(
                    f"[{_utc_now()}] WARN: Skipping partial/invalid session restore payload ({detail})."
                )
            self._last_launched_payload = {}
        else:
            self._sync_session_flags_from_controller()
        self._refresh_rerun_state()

    def _render_history_records(self) -> None:
        self.session_history_output.clear()
        if not self._history_records:
            self.session_history_output.setPlainText("<no persisted runs yet>")
            return
        lines: List[str] = []
        for item in reversed(self._history_records[-self._config.max_runs :]):
            zip_path = item.get("canonical_zip_path") or item.get("handoff_copy_path") or item.get("zip_path", "")
            lines.append(
                "[{timestamp}] {status} • exit={exit_code} • mode={mode} • policy={policy} • project_id={project_id} • session_id={session_id} • zip={zip_path}".format(
                    timestamp=item.get("timestamp", "<unknown>"),
                    status=item.get("status") or item.get("parsed_status", "<unknown>"),
                    exit_code=item.get("exit_code", "<unknown>"),
                    mode=item.get("mode", "<none>"),
                    policy=item.get("policy", "<none>"),
                    project_id=item.get("project_id", "<none>"),
                    session_id=item.get("session_id", "<none>") or "<none>",
                    zip_path=zip_path or "<none>",
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
        payload["mode"] = normalize_mode(payload.get("mode"))
        payload["policy"] = normalize_policy(payload.get("policy"), payload["mode"])
        payload["non_interactive"] = True
        if payload["mode"] == MODE_NEW:
            project_name = str(payload.get("project_name") or "").strip()
            generated = derive_project_id_from_name(project_name) if project_name else ""
            if generated and not str(payload.get("project_id") or "").strip():
                payload["project_id"] = generated
        return validate_request_payload(payload)

    def _apply_payload_to_form(self, payload: Dict[str, Any]) -> None:
        mode = normalize_mode(payload.get("mode"))
        index = self.mode_combo.findText(mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)
        self._project_id_manual_override = bool(str(payload.get("project_id") or "").strip())
        self.project_name_edit.setText(str(payload.get("project_name") or ""))
        self.initiative_type_edit.setText(str(payload.get("initiative_type") or ""))
        self.project_id_edit.setText(str(payload.get("project_id") or ""))
        self.intent_edit.setPlainText(str(payload.get("intent") or ""))
        self._refresh_mode_ui()
        policy = normalize_policy(payload.get("policy"), mode)
        self.policy_combo.setCurrentText(policy)
        self.dry_run_checkbox.setChecked(bool(payload.get("dry_run", True)))
        self.non_interactive_checkbox.setChecked(True)

    def _build_process_arguments(self, payload: Dict[str, Any]) -> List[str]:
        args = ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", self._config.one_button_path]
        session_mode = normalize_mode(payload.get("mode"))
        args.extend(["--session-mode", session_mode])

        policy = normalize_policy(payload.get("policy"), session_mode)
        args.extend(["--policy", policy])

        project_id = _quote_ps_arg(str(payload.get("project_id") or ""))
        if project_id:
            args.extend(["--project-id", project_id])

        if session_mode == MODE_NEW:
            project_name = _quote_ps_arg(str(payload.get("project_name") or project_id or "new_project"))
            initiative_type = _quote_ps_arg(str(payload.get("initiative_type") or "general"))
            args.extend(["--project-name", project_name])
            args.extend(["--initiative-type", initiative_type])

        if payload.get("intent"):
            args.extend(["--intent", _quote_ps_arg(str(payload["intent"]))])
        if payload.get("dry_run"):
            args.append("--dry-run")
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
            self.policy_combo,
            self.project_name_edit,
            self.initiative_type_edit,
            self.project_id_edit,
            self.intent_edit,
            self.dry_run_checkbox,
        ):
            widget.setEnabled(not running)
        self.non_interactive_checkbox.setEnabled(False)
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
        self._refresh_mode_ui()
        self._refresh_rerun_state()

    def _start_process(self, payload: Dict[str, Any], from_rerun: bool = False) -> None:
        payload = dict(payload or {})
        self._sync_session_flags_from_controller()
        if self._run_in_progress:
            self._append_log(f"[{_utc_now()}] Run ignored: a process is already active in this dock.")
            self._flash_feedback("Run already in progress", "warning")
            return
        self._set_status_badge("validating", "Validating request and runtime before launch.")
        self._push_timeline_event("Validation", "Checking environment and payload guardrails.", "info")

        ok, detail = self._validate_environment()
        if not ok:
            self._session_controller.mark_blocked(f"environment:{detail}")
            self._sync_session_flags_from_controller()
            self._last_result = {"zip_path": "", "zip_path_publicable": False}
            self._set_status_badge("blocked", detail)
            self._set_result("blocked", "Blocked", None, "")
            self._append_log(f"[{_utc_now()}] BLOCKED: {detail}")
            self._flash_feedback("Environment blocked", "danger")
            return

        validation_errors = self._validate_payload(payload)
        if validation_errors:
            detail = validation_errors[0]
            self._session_controller.mark_blocked(f"payload:{detail}")
            self._sync_session_flags_from_controller()
            self._last_result = {"zip_path": "", "zip_path_publicable": False}
            self._set_status_badge("blocked", detail)
            self._set_result("blocked", "InvalidInput", None, "")
            for item in validation_errors:
                self._append_log(f"[{_utc_now()}] INPUT_ERROR: {item}")
            self._flash_feedback("Fix input guardrails", "danger")
            return

        program = self._resolve_powershell_program()
        if not program:
            self._session_controller.mark_blocked("missing-powershell")
            self._sync_session_flags_from_controller()
            self._last_result = {"zip_path": "", "zip_path_publicable": False}
            self._set_status_badge("failed", "PowerShell executable not found in PATH.")
            self._set_result("failed", "LaunchFailure", None, "")
            self._append_log(f"[{_utc_now()}] ERROR: PowerShell executable not found in PATH.")
            self._flash_feedback("PowerShell missing", "danger")
            return

        session_ok, session_detail = self._session_controller.begin_launch(dict(payload))
        if not session_ok:
            self._append_log(f"[{_utc_now()}] SESSION_BLOCKED: {session_detail}")
            self._flash_feedback("Session blocked", "warning")
            return
        self._sync_session_flags_from_controller()

        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._parser = _OutputParser(self._config)
        self._last_result = {}
        self._launch_error_recorded = False
        self._set_result(DEFAULT_RESULT, "RUNNING", None, "", {})
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

        self._startup_timer.stop()
        self._startup_timer.start(self._config.startup_timeout_ms)
        process.start()

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

    def _record_run(self, exit_code: Any, result: Dict[str, Any]) -> None:
        current_payload = dict(self._session_controller.snapshot.current_payload)
        exit_code_display = "<none>"
        if exit_code is not None:
            text_value = str(exit_code).strip()
            if text_value:
                exit_code_display = text_value
        if exit_code_display == "<none>" and str(result.get("contract_detail") or "").strip() == "LaunchFailure":
            exit_code_display = "process_error"
        record = {
            "timestamp": _utc_now(),
            "mode": current_payload.get("mode", ""),
            "policy": current_payload.get("policy", ""),
            "project_name": current_payload.get("project_name", ""),
            "initiative_type": current_payload.get("initiative_type", ""),
            "project_id": current_payload.get("project_id", ""),
            "intent": current_payload.get("intent", ""),
            "dry_run": bool(current_payload.get("dry_run", False)),
            "non_interactive": bool(current_payload.get("non_interactive", False)),
            "exit_code": exit_code_display,
            "status": result.get("status") or result.get("normalized_status", "failed"),
            "parsed_status": result.get("normalized_status", "failed"),
            "contract_detail": result.get("contract_detail", "Failed"),
            "zip_path": result.get("zip_path", ""),
            "canonical_zip_path": result.get("canonical_zip_path", ""),
            "handoff_copy_path": result.get("handoff_copy_path", ""),
            "session_id": result.get("session_id", ""),
            "run_id": result.get("run_id", ""),
            "round_id": result.get("round_id", ""),
            "request": current_payload,
        }
        self._history_records = self._history_store.append_record(
            [dict(item) for item in self._history_records],
            record,
        )
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
        if self._run_in_progress:
            self._append_log(f"[{_utc_now()}] Rerun ignored: process still running.")
            self._flash_feedback("Run still in progress", "warning")
            return
        self._apply_payload_to_form(self._last_launched_payload)
        self._set_status_badge("ready", "Last payload loaded. Review and click Run Bridge.")
        self._push_timeline_event("Last payload loaded", "Parameters restored from the latest persisted run.", "info")
        self._flash_feedback("Last payload loaded. Click Run Bridge.", "info")

    def _on_process_started(self) -> None:
        self._startup_timer.stop()
        self._run_timer.start(self._config.run_timeout_ms)
        self._session_controller.mark_started()
        self._sync_session_flags_from_controller()
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
        self._session_controller.mark_startup_timeout()
        self._sync_session_flags_from_controller()
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
        self._session_controller.mark_run_timeout()
        self._sync_session_flags_from_controller()
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

        process_not_running = bool(state_value in not_running_markers or state_value is None)
        if self._session_controller.mark_process_error(
            error_code,
            process_not_running=process_not_running,
        ):
            self._sync_session_flags_from_controller()
            self._launch_error_recorded = True
            self._stop_timers()
            self._flush_remaining_buffers()
            self._set_running_ui(False)
            resolved_error_code = _format_process_error_code(error_code)
            self._last_result = {"zip_path_publicable": False, "zip_path": ""}
            result = {
                "normalized_status": "failed",
                "contract_detail": "LaunchFailure",
                "zip_path": "",
                "zip_path_publicable": False,
                "message": f"Process launch failed: {resolved_error_code}",
            }
            self._set_result(
                result["normalized_status"],
                result["contract_detail"],
                resolved_error_code,
                "",
                result,
            )
            self._set_status_badge("failed", f"Process launch failed: {resolved_error_code}")
            self._record_run(resolved_error_code, result)
            self._flash_feedback("Launch failed", "danger")
            if self._process is not None:
                self._process.deleteLater()
                self._process = None

    def _on_process_finished(self, exit_code: int, _exit_status: Any = None) -> None:
        self._sync_session_flags_from_controller()
        if self._launch_error_recorded:
            self._launch_error_recorded = False
            self._stop_timers()
            if self._process is not None:
                self._process.deleteLater()
                self._process = None
            return
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
            result,
        )

        detail_message = result.get("last_status_message") or result.get("contract_detail", "Finished")
        badge_title = str(result.get("normalized_status", "failed")).lower()
        if badge_title == "success":
            badge_title = "succeeded"
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
        if result.get("notes"):
            self._append_log(f"[{_utc_now()}] NOTES: {len(result['notes'])}")
            for item in result["notes"]:
                self._append_log(f"[{_utc_now()}] NOTE {item}")
        if bool(result.get("contract_mismatch")):
            self._append_log(f"[{_utc_now()}] CONTRACT_MISMATCH runner output violated bridge contract.")
            self._push_timeline_event(
                "Contract mismatch",
                "Runner output did not satisfy expected bridge contract.",
                "blocked",
            )

        self._record_run(int(exit_code), result)
        self._append_log(f"[{_utc_now()}] Process finished with exit code {exit_code}.")
        self._push_timeline_event("Run finished", detail_message, "success" if result.get("normalized_status") in ("success", "reused", "succeeded") else "danger")
        if result.get("normalized_status") in ("success", "reused"):
            self._flash_feedback("Run completed", "success")
        elif result.get("normalized_status") == "blocked":
            self._flash_feedback("Run blocked", "warning")
        else:
            self._flash_feedback("Run failed", "danger")

        self._session_controller.mark_finished(str(result.get("normalized_status", "failed")))
        self._sync_session_flags_from_controller()
        self._refresh_rerun_state()

        if self._process is not None:
            self._process.deleteLater()
            self._process = None

    def _on_copy_zip_path_clicked(self) -> None:
        zip_path = str(self._active_zip_path or self._last_result.get("zip_path") or "")
        if not zip_path or not os.path.exists(zip_path):
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

    def _on_copy_session_id_clicked(self) -> None:
        session_id = str(self._last_result.get("session_id") or "")
        if not session_id:
            self._append_log(f"[{_utc_now()}] Copy Session ID ignored: no session id is available.")
            self._flash_feedback("No session id yet", "warning")
            return
        try:
            app = QApplication.instance()
            if app is None:
                raise RuntimeError("QApplication instance not available.")
            clipboard = app.clipboard()
            if clipboard is None:
                raise RuntimeError("Clipboard is not available.")
            clipboard.setText(session_id)
            self._append_log(f"[{_utc_now()}] Session ID copied to clipboard: {session_id}")
            self._flash_feedback("Session ID copied", "success")
        except Exception as exc:
            self._append_log(f"[{_utc_now()}] ERROR: Could not copy Session ID: {exc}")
            self._flash_feedback("Copy failed", "danger")

    def _on_open_zip_clicked(self) -> None:
        zip_path = str(self._active_zip_path or self._last_result.get("zip_path") or "")
        if not zip_path or not os.path.exists(zip_path):
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
        zip_path = str(self._active_zip_path or self._last_result.get("zip_path") or "")
        if not zip_path:
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
        self._session_controller.cancel(reason="manual-clear")
        self._sync_session_flags_from_controller()
        self.log_output.clear()
        self.timeline_output.clear()
        self._timeline_records = []
        self._last_result = {}
        self._active_zip_path = ""
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
    description = "Orchestrator Bridge tool for controlled asynchronous orchestration runs."

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

    def get_panel(self) -> _BridgePanel:
        return self._get_or_create_panel()

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


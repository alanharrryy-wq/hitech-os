
from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget, QFrame

from visuals.effects.shadow import apply_shadow

from ..widgets.json_viewer import JsonViewer
from ..widgets.log_console import LogConsole


class DetailPanel(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        apply_shadow(self, blur=16.0, y_offset=6.0, alpha=12)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.title_label = QLabel("Detail Inspector", self)
        self.title_label.setProperty("role", "section")
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Select a recent row or search result to inspect the underlying session and raw payload.", self)
        self.subtitle_label.setProperty("role", "hint")
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs, 1)

        self.overview_console = LogConsole(self, title="Session overview")
        self.payload_viewer = JsonViewer(self, title="Session payload")
        self.raw_preview = LogConsole(self, title="Raw snippets")

        self.tabs.addTab(self.overview_console, "Overview")
        self.tabs.addTab(self.payload_viewer, "Payload")
        self.tabs.addTab(self.raw_preview, "Raw")

    def set_payload_title(self, title: str, subtitle: str) -> None:
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)

    def clear_detail(self, *, reason: str = "Select a row to inspect session detail.") -> None:
        self.title_label.setText("Detail Inspector")
        self.subtitle_label.setText(reason)
        self.overview_console.set_lines([reason])
        self.payload_viewer.set_payload({})
        self.raw_preview.set_lines(["No timeline entries available."])

    def set_loading(self, session_id: str) -> None:
        self.title_label.setText(f"Detail Inspector · {session_id}")
        self.subtitle_label.setText("Hydrating session detail in the background.")
        self.overview_console.set_lines([f"Loading session detail for {session_id}..."])
        self.payload_viewer.set_payload({"status": "loading", "session_id": session_id})
        self.raw_preview.set_lines(["Waiting for timeline hydration..."])

    def set_error(self, title: str, body: str) -> None:
        self.title_label.setText("Detail Inspector · error")
        self.subtitle_label.setText(title)
        self.overview_console.set_lines([title])
        self.payload_viewer.set_payload({"error": title, "detail": body})
        self.raw_preview.set_lines([body or "No traceback available."])

    def set_result_row(self, row: dict[str, Any]) -> None:
        session_id = str(row.get("session_id") or "unknown-session")
        record_type = str(row.get("record_type") or row.get("kind") or "record")
        self.title_label.setText(f"Detail Inspector · {session_id}")
        self.subtitle_label.setText(f"Selected {record_type} row from the results deck.")
        self.payload_viewer.set_payload(row)
        self.overview_console.set_lines(
            [
                f"Session: {session_id}",
                f"Type: {record_type}",
                f"Timestamp: {row.get('timestamp_utc') or row.get('day') or 'n/a'}",
                f"Source: {row.get('source_path') or row.get('source_ref') or 'n/a'}",
            ]
        )
        self.raw_preview.set_lines([str(row.get("text") or row.get("summary") or row.get("headline") or "No raw preview available.")])

    def set_session_detail(self, payload: dict[str, Any]) -> None:
        session = payload.get("session") or {}
        insights = payload.get("session_insights") or {}
        related = payload.get("related_sessions") or []
        session_id = str(session.get("session_id") or "unknown-session")
        confidence = str(session.get("confidence") or insights.get("confidence") or "n/a")
        self.title_label.setText(f"Detail Inspector · {session_id}")
        self.subtitle_label.setText(f"Hydrated session detail with confidence {confidence}.")
        lines = [
            f"Session: {session_id}",
            f"Confidence: {confidence}",
            f"Records: {len(payload.get('records') or [])}",
            f"Errors: {len(payload.get('errors') or [])}",
            f"Tools: {len(payload.get('tools') or [])}",
        ]
        root_causes = insights.get("probable_root_causes") or []
        if root_causes:
            lines.append("")
            lines.append("Probable root causes:")
            for item in root_causes[:4]:
                lines.append(f"- {item.get('category')} ({item.get('confidence')}, score {item.get('score')})")
        if related:
            lines.append("")
            lines.append("Related sessions:")
            for item in related[:4]:
                lines.append(f"- {item.get('session_id') or item.get('label') or item}")
        self.overview_console.set_lines(lines)
        self.payload_viewer.set_payload(payload)
        timeline = payload.get("timeline") or []
        raw_lines = []
        for item in timeline[:12]:
            raw_lines.append(f"[{item.get('timestamp_utc')}] {item.get('headline') or item.get('message') or item.get('kind')}")
        self.raw_preview.set_lines(raw_lines or ["No timeline entries available."])

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.gui_qt.event_bus import Events

from .guardian_contract import (
    CloudflareGuardianContext,
    build_guardian_cards,
    normalize_guardian_context,
)


class CloudflareGuardianDeck(QWidget):
    """Graph-side diagnostics deck for Cloudflare Guardian."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plugin_context = None
        self._guardian_context = CloudflareGuardianContext()
        self._cards: dict[str, tuple[QLabel, QLabel]] = {}
        self._build_ui()
        self._refresh_cards()

    def bind_plugin_context(self, context: Any) -> None:
        self._plugin_context = context

    def refresh_from_state(self) -> dict[str, str]:
        self._refresh_cards()
        return self._guardian_context.to_payload()

    def shutdown(self) -> None:
        self._plugin_context = None

    def set_tool_context(self, payload: dict[str, Any]) -> None:
        local = dict(payload.get("local", {})) if isinstance(payload, dict) else {}
        shared = local.get("guardian_diagnostics", local)
        self._guardian_context = normalize_guardian_context(shared)
        self._refresh_cards()

    def on_tool_activate(self) -> None:
        self._refresh_cards()

    def on_tool_restore(self) -> None:
        self._refresh_cards()

    def _build_ui(self) -> None:
        self.setObjectName("cloudflare_guardianDeck")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        title = QLabel("Cloudflare Guardian Diagnostics", self)
        title.setObjectName("guardianTitle")
        root.addWidget(title)

        subtitle = QLabel(
            "Graph stays diagnostics-only: health, path, evidence, and drift.",
            self,
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("guardianSubtitle")
        root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        order = ["Health", "Path", "Evidence", "Config Drift"]
        for index, name in enumerate(order):
            frame = QFrame(self)
            frame.setObjectName("guardianCard")
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(12, 10, 12, 10)
            frame_layout.setSpacing(6)
            header = QLabel(name, frame)
            header.setObjectName("guardianCardHeader")
            headline = QLabel("", frame)
            headline.setWordWrap(True)
            headline.setObjectName("guardianCardHeadline")
            detail = QLabel("", frame)
            detail.setWordWrap(True)
            detail.setObjectName("guardianCardDetail")
            frame_layout.addWidget(header)
            frame_layout.addWidget(headline)
            frame_layout.addWidget(detail)
            grid.addWidget(frame, index // 2, index % 2)
            self._cards[name] = (headline, detail)
        root.addLayout(grid)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self.run_check_button = QPushButton("Run check", self)
        self.rerun_button = QPushButton("Rerun", self)
        self.remediation_button = QPushButton("Apply remediation", self)
        for button in (self.run_check_button, self.rerun_button, self.remediation_button):
            action_row.addWidget(button)
        action_row.addStretch(1)
        root.addLayout(action_row)
        root.addStretch(1)

        self.run_check_button.clicked.connect(lambda: self._route_to_run("check"))
        self.rerun_button.clicked.connect(lambda: self._route_to_run("rerun"))
        self.remediation_button.clicked.connect(lambda: self._route_to_run("remediation"))

    def _refresh_cards(self) -> None:
        cards = build_guardian_cards(self._guardian_context)
        for name, card in cards.items():
            headline, detail = self._cards[name]
            headline.setText(card.headline)
            detail.setText(card.detail)

    def _route_to_run(self, action: str) -> None:
        bus = getattr(self._plugin_context, "event_bus", None)
        container = getattr(self._plugin_context, "container", None)
        group_runtime = (
            getattr(container, "get", lambda _name: None)("shell_group_runtime")
            if container is not None
            else None
        )
        if group_runtime is not None and hasattr(group_runtime, "apply_group"):
            try:
                group_runtime.apply_group("run", reason=f"guardian-{action}", force=True)
            except Exception:
                pass
        if bus is not None and hasattr(bus, "publish"):
            bus.publish(
                Events.STATUS_CHANGED,
                {
                    "status": "run-group-opened",
                    "message": f"Run group opened from Graph ({action}).",
                },
            )


__all__ = ["CloudflareGuardianDeck"]


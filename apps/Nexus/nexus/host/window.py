from __future__ import annotations

import json
from typing import Any

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from forgeos.shared.pyside6_glass import (
    GlassPanelTemplate,
    GlassWorkspaceRuntime,
    get_template_preset,
)

from ..integration.module import NexusHostedModule, create_nexus_hosted_module
from ..runtime.engine import NEXUS_STAGE_SEQUENCE
from .surfaces import (
    NexusApprovalsSurface,
    NexusHealthSurface,
    NexusRecordsSurface,
    NexusSummarySurface,
    NexusTimelineSurface,
)


class NexusGlassDesktopWindow(QWidget):
    """Desktop-hosted Nexus module mounted inside the reusable glass host."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        namespace: str = "nexus",
        enable_http_bridge: bool = False,
        http_port: int = 0,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("NexusGlassDesktopWindow")
        self._namespace = namespace
        self._event_cursor = 0
        self._record_seed = 0
        self._records_cache: list[dict[str, Any]] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.template = GlassPanelTemplate(
            self,
            config=get_template_preset("tabbed_workspace"),
            title="Hitech Nexus",
            subtitle="Hosted runtime module using neutral command/query/snapshot/event contracts.",
            eyebrow="HOSTED MODULE",
            include_default_actions=False,
            show_status=True,
            show_footer=True,
            theme_id="silver_frost_cyan",
            density="comfortable",
        )
        root.addWidget(self.template, 1)

        self.runtime = GlassWorkspaceRuntime(self.template, preset="tabbed_workspace")
        self.runtime.register_layout("nexus_focus", {"main_side": [980, 220]})
        self.runtime.register_layout("nexus_balanced", {"main_side": [700, 500]})
        self.runtime.apply_resolved_config()
        self.runtime.bind_default_shortcuts(self.template)

        self.module: NexusHostedModule = create_nexus_hosted_module(
            self.runtime,
            namespace=namespace,
            debug=False,
        )
        self._http_url: str | None = None
        if enable_http_bridge:
            self._http_url = self.module.start_local_http(port=http_port)

        self._build_surfaces()
        self._build_controls()
        self._bind_actions()
        self.refresh_all()

        if self._http_url:
            self._status(f"Nexus loaded. Local HTTP bridge: {self._http_url}")
        else:
            self._status("Nexus loaded. In-process bridge active.")

    def _build_surfaces(self) -> None:
        self.summary_surface = NexusSummarySurface(self.template)
        self.records_surface = NexusRecordsSurface(self.template)
        self.approvals_surface = NexusApprovalsSurface(self.template)
        self.timeline_surface = NexusTimelineSurface(self.template)
        self.health_surface = NexusHealthSurface(self.template)

        self.template.slots.main_slot.addWidget(self.summary_surface, 1)

        self.detail_label = QLabel("Nexus Command Detail", self.template)
        self.detail_label.setProperty("role", "panel_title")
        self.detail_preview = self._make_text_preview("Command/query/snapshot output will appear here.")

        self.template.slots.side_slot.addWidget(self.detail_label)
        self.template.slots.side_slot.addWidget(self.detail_preview, 1)

        if self.template.workspace_tabs is not None:
            self.template.add_workspace_tab(
                tab_id="records",
                title="Records",
                widget=self.records_surface,
                icon_name="layers",
                state="visible",
            )
            self.template.add_workspace_tab(
                tab_id="approvals",
                title="Approvals",
                widget=self.approvals_surface,
                icon_name="check",
                state="visible",
            )
            self.template.add_workspace_tab(
                tab_id="timeline",
                title="Timeline",
                widget=self.timeline_surface,
                icon_name="activity",
                state="visible",
            )
            self.template.add_workspace_tab(
                tab_id="health",
                title="Health",
                widget=self.health_surface,
                icon_name="shield",
                state="visible",
            )

    def _build_controls(self) -> None:
        controls_host = QWidget(self.template)
        controls_layout = QVBoxLayout(controls_host)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        self.input_record_id = QLineEdit(controls_host)
        self.input_record_id.setPlaceholderText("record id (optional)")
        self.input_title = QLineEdit(controls_host)
        self.input_title.setPlaceholderText("record title")
        self.input_owner = QLineEdit(controls_host)
        self.input_owner.setPlaceholderText("owner (example: agent.intake)")
        self.input_note = QLineEdit(controls_host)
        self.input_note.setPlaceholderText("note for stage/approval updates")
        self.combo_stage = QComboBox(controls_host)
        self.combo_stage.addItems(list(NEXUS_STAGE_SEQUENCE))

        controls_layout.addWidget(QLabel("Record ID", controls_host))
        controls_layout.addWidget(self.input_record_id)
        controls_layout.addWidget(QLabel("Title", controls_host))
        controls_layout.addWidget(self.input_title)
        controls_layout.addWidget(QLabel("Owner", controls_host))
        controls_layout.addWidget(self.input_owner)
        controls_layout.addWidget(QLabel("Stage", controls_host))
        controls_layout.addWidget(self.combo_stage)
        controls_layout.addWidget(QLabel("Note", controls_host))
        controls_layout.addWidget(self.input_note)

        self.btn_upsert = QPushButton("Upsert Record", controls_host)
        self.btn_advance_stage = QPushButton("Advance Stage", controls_host)
        self.btn_approval_approve = QPushButton("Approve", controls_host)
        self.btn_approval_reject = QPushButton("Reject", controls_host)
        self.btn_approval_hold = QPushButton("Hold", controls_host)
        self.btn_append_note = QPushButton("Append Note", controls_host)
        self.btn_refresh = QPushButton("Refresh All", controls_host)
        self.btn_snapshot = QPushButton("Snapshot Workspace", controls_host)
        self.btn_poll_events = QPushButton("Poll Events", controls_host)
        self.btn_save_state = QPushButton("Save Workspace", controls_host)
        self.btn_load_state = QPushButton("Load Workspace", controls_host)
        self.btn_layout_focus = QPushButton("Focus Layout", controls_host)
        self.btn_layout_balanced = QPushButton("Balanced Layout", controls_host)

        for button in (
            self.btn_upsert,
            self.btn_advance_stage,
            self.btn_approval_approve,
            self.btn_approval_reject,
            self.btn_approval_hold,
            self.btn_append_note,
            self.btn_refresh,
            self.btn_snapshot,
            self.btn_poll_events,
            self.btn_save_state,
            self.btn_load_state,
            self.btn_layout_focus,
            self.btn_layout_balanced,
        ):
            controls_layout.addWidget(button)

        self.template.create_panel(
            panel_id="nexus_controls",
            title="Nexus Controls",
            target_slot="status",
            role="tools",
            subtitle="First vertical-slice command/query/snapshot/event controls.",
            card_kind="muted",
            state="visible",
        ).content_layout.addWidget(controls_host, 1)

    def _bind_actions(self) -> None:
        self.btn_upsert.clicked.connect(self._on_upsert_record)
        self.btn_advance_stage.clicked.connect(self._on_advance_stage)
        self.btn_approval_approve.clicked.connect(lambda: self._on_approval_state("approved"))
        self.btn_approval_reject.clicked.connect(lambda: self._on_approval_state("rejected"))
        self.btn_approval_hold.clicked.connect(lambda: self._on_approval_state("hold"))
        self.btn_append_note.clicked.connect(self._on_append_note)
        self.btn_refresh.clicked.connect(self.refresh_all)
        self.btn_snapshot.clicked.connect(self._on_snapshot_workspace)
        self.btn_poll_events.clicked.connect(self._on_poll_events)
        self.btn_save_state.clicked.connect(self._on_save_workspace_state)
        self.btn_load_state.clicked.connect(self._on_load_workspace_state)
        self.btn_layout_focus.clicked.connect(lambda: self._on_apply_layout("nexus_focus"))
        self.btn_layout_balanced.clicked.connect(lambda: self._on_apply_layout("nexus_balanced"))
        self.records_surface.table.itemSelectionChanged.connect(self._on_record_selected)

        self.template.add_footer_action("Overview", on_click=lambda: self.template.set_active_workspace_tab("workspace"))
        self.template.add_footer_action("Records", on_click=lambda: self.template.set_active_workspace_tab("records"))
        self.template.add_footer_action("Timeline", on_click=lambda: self.template.set_active_workspace_tab("timeline"))
        self.template.add_footer_action("Poll", on_click=self._on_poll_events)

    def _on_upsert_record(self) -> None:
        try:
            record_id = self.input_record_id.text().strip()
            if not record_id:
                self._record_seed += 1
                record_id = f"nx-desktop-{self._record_seed:04d}"
            title = self.input_title.text().strip() or f"Nexus Record {record_id}"
            owner = self.input_owner.text().strip() or "agent.desktop"
            stage = self.combo_stage.currentText().strip().lower() or "intake"

            response = self.module.command(
                f"{self._namespace}.record.upsert",
                {
                    "record_id": record_id,
                    "record": {
                        "title": title,
                        "owner": owner,
                        "stage": stage,
                        "status": "active",
                        "tags": ["desktop", "hosted"],
                    },
                },
                capabilities=("nexus.write",),
                idempotency_key=f"record-upsert-{record_id}",
            )
            self._require_ok(response, "record upsert")
            self._write_detail(response)
            self.refresh_all()
            self._status(f"Record '{record_id}' upserted.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Upsert failed: {exc}")

    def _on_advance_stage(self) -> None:
        try:
            record_id = self._selected_record_id()
            if not record_id:
                raise ValueError("select a record first")
            current = self.module.query(
                f"{self._namespace}.record.get",
                {"record_id": record_id},
            )
            payload = self._require_ok(current, "record get")
            record = dict(payload.get("record") or {})
            current_stage = str(record.get("stage") or "intake")
            target_stage = self._next_stage(current_stage)
            note = self.input_note.text().strip()
            response = self.module.command(
                f"{self._namespace}.record.stage.set",
                {"record_id": record_id, "stage": target_stage, "note": note},
                capabilities=("nexus.write",),
            )
            self._require_ok(response, "set stage")
            self._write_detail(response)
            self.refresh_all()
            self._status(f"Record '{record_id}' moved to stage '{target_stage}'.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Stage advance failed: {exc}")

    def _on_approval_state(self, state: str) -> None:
        try:
            record_id = self.approvals_surface.selected_record_id() or self._selected_record_id()
            if not record_id:
                raise ValueError("select a record/approval first")
            note = self.input_note.text().strip()
            response = self.module.command(
                f"{self._namespace}.approval.state.set",
                {"record_id": record_id, "state": state, "note": note},
                capabilities=("nexus.write",),
            )
            self._require_ok(response, "set approval")
            self._write_detail(response)
            self.refresh_all()
            self._status(f"Approval for '{record_id}' set to '{state}'.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Approval update failed: {exc}")

    def _on_append_note(self) -> None:
        try:
            record_id = self._selected_record_id()
            if not record_id:
                raise ValueError("select a record first")
            note = self.input_note.text().strip()
            if not note:
                raise ValueError("note is required")
            response = self.module.command(
                f"{self._namespace}.note.append",
                {"record_id": record_id, "note": note},
                capabilities=("nexus.write",),
            )
            self._require_ok(response, "append note")
            self._write_detail(response)
            self.refresh_all()
            self._status(f"Note appended to '{record_id}'.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Append note failed: {exc}")

    def _on_snapshot_workspace(self) -> None:
        try:
            response = self.module.snapshot(f"{self._namespace}.workspace")
            payload = self._require_ok(response, "workspace snapshot")
            self._write_detail(payload)
            self._status("Workspace snapshot loaded.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Snapshot failed: {exc}")

    def _on_poll_events(self) -> None:
        try:
            events_payload = self.module.poll_events(since_sequence=self._event_cursor, limit=100)
            events = list(events_payload.get("events") or [])
            self._event_cursor = int(events_payload.get("cursor") or self._event_cursor)
            self.timeline_surface.append_integration_events(events)
            self._status(f"Polled {len(events)} integration events.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Event poll failed: {exc}")

    def _on_save_workspace_state(self) -> None:
        try:
            path = self.module.save_workspace_state()
            self._status(f"Workspace state saved: {path}")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Save workspace failed: {exc}")

    def _on_load_workspace_state(self) -> None:
        try:
            loaded = self.module.load_workspace_state()
            if loaded:
                self._status("Workspace state loaded from persisted storage.")
            else:
                self._status("No persisted workspace state found.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Load workspace failed: {exc}")

    def _on_apply_layout(self, layout_name: str) -> None:
        try:
            response = self.module.command(
                "workspace.layout.apply",
                {"layout_name": layout_name},
                capabilities=("workspace.write",),
            )
            self._require_ok(response, f"apply layout {layout_name}")
            self._status(f"Applied layout: {layout_name}")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Layout command failed: {exc}")

    def _on_record_selected(self) -> None:
        record_id = self._selected_record_id()
        if not record_id:
            return
        response = self.module.query(f"{self._namespace}.record.get", {"record_id": record_id})
        if not response.get("ok"):
            return
        data = dict(response.get("data") or {})
        record = dict(data.get("record") or {})
        self.records_surface.show_record_detail(record)
        self._write_detail({"selected_record": record})

    def refresh_all(self) -> None:
        try:
            summary_payload = self._require_ok(
                self.module.query(f"{self._namespace}.summary.get"),
                "summary query",
            )
            records_payload = self._require_ok(
                self.module.query(f"{self._namespace}.records.list"),
                "records query",
            )
            approvals_payload = self._require_ok(
                self.module.query(f"{self._namespace}.approvals.list"),
                "approvals query",
            )
            health_payload = self._require_ok(
                self.module.query(f"{self._namespace}.health.get"),
                "health query",
            )
            timeline_payload = self._require_ok(
                self.module.snapshot(f"{self._namespace}.timeline", {"limit": 80}),
                "timeline snapshot",
            )

            self.summary_surface.update_summary(summary_payload)
            self._records_cache = list(records_payload.get("records") or [])
            self.records_surface.update_records(self._records_cache)
            self.approvals_surface.update_approvals(list(approvals_payload.get("approvals") or []))
            self.health_surface.update_health(health_payload)
            timeline = dict(timeline_payload.get("timeline") or {})
            self.timeline_surface.set_timeline_entries(list(timeline.get("entries") or []))
            self._status("Nexus refresh completed.")
        except Exception as exc:  # noqa: BLE001
            self._status(f"Refresh failed: {exc}")

    def run_smoke_cycle(self) -> dict[str, Any]:
        upsert = self.module.command(
            f"{self._namespace}.record.upsert",
            {
                "record_id": "nx-smoke-0001",
                "record": {
                    "title": "Smoke record",
                    "owner": "smoke.agent",
                    "stage": "intake",
                    "status": "active",
                },
            },
            capabilities=("nexus.write",),
            idempotency_key="nx-smoke-0001-upsert",
        )
        summary = self.module.query(f"{self._namespace}.summary.get")
        snapshot = self.module.snapshot(f"{self._namespace}.workspace")
        events = self.module.poll_events(since_sequence=0, limit=25)
        contracts = self.module.contracts()
        return {
            "upsert_ok": bool(upsert.get("ok")),
            "summary_ok": bool(summary.get("ok")),
            "snapshot_ok": bool(snapshot.get("ok")),
            "events_count": len(events.get("events") or []),
            "contract_commands": len((contracts.get("endpoints") or {}).get("commands") or []),
        }

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.module.stop_local_http()
        return super().closeEvent(event)

    def _selected_record_id(self) -> str | None:
        selected = self.records_surface.selected_record_id()
        if selected:
            return selected
        if self._records_cache:
            return str(self._records_cache[0].get("record_id") or "")
        return None

    def _next_stage(self, stage: str) -> str:
        normalized = str(stage or "").strip().lower()
        if normalized not in NEXUS_STAGE_SEQUENCE:
            return NEXUS_STAGE_SEQUENCE[0]
        index = NEXUS_STAGE_SEQUENCE.index(normalized)
        if index >= len(NEXUS_STAGE_SEQUENCE) - 1:
            return NEXUS_STAGE_SEQUENCE[-1]
        return NEXUS_STAGE_SEQUENCE[index + 1]

    def _require_ok(self, payload: dict[str, Any], operation: str) -> dict[str, Any]:
        if not bool(payload.get("ok")):
            error = payload.get("error") or {}
            message = str(error.get("message") or f"{operation} failed")
            raise RuntimeError(message)
        return dict(payload.get("data") or {})

    def _status(self, message: str) -> None:
        self.template.set_status_text(str(message))

    def _write_detail(self, payload: dict[str, Any]) -> None:
        self.detail_preview.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))

    def _make_text_preview(self, placeholder: str) -> QWidget:
        preview = self._text_preview = self._text_widget(placeholder)
        return preview

    def _text_widget(self, placeholder: str) -> Any:
        from PySide6.QtWidgets import QTextEdit

        widget = QTextEdit(self.template)
        widget.setReadOnly(True)
        widget.setPlaceholderText(placeholder)
        return widget


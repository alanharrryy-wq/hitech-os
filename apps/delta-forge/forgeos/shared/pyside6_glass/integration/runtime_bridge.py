from __future__ import annotations

from typing import Any

from ..runtime import GlassWorkspaceRuntime
from .contracts import (
    IntegrationCommandEnvelope,
    IntegrationQueryEnvelope,
    IntegrationSnapshotRequest,
    IntegrationValidationError,
)
from .service import IntegrationService


class GlassRuntimeIntegrationBridge:
    """
    Bridge between current desktop runtime and neutral integration contracts.

    This bridge exposes structured commands/queries/snapshots backed by the
    runtime/template APIs while keeping transport concerns outside.
    """

    def __init__(
        self,
        runtime: GlassWorkspaceRuntime,
        service: IntegrationService | None = None,
        *,
        namespace: str = "workspace",
        required_write_capabilities: tuple[str, ...] = (),
        register_defaults: bool = True,
    ) -> None:
        self.runtime = runtime
        self.template = runtime.template
        self.service = service or IntegrationService()
        self.namespace = str(namespace or "workspace").strip().lower() or "workspace"
        self.required_write_capabilities = tuple(required_write_capabilities)
        if register_defaults:
            self.register_default_contracts()

    def register_default_contracts(self) -> None:
        ns = self.namespace
        write_caps = self.required_write_capabilities

        self.service.register_snapshot_provider(
            f"{ns}",
            self._snapshot_workspace,
            description="Workspace snapshot including layout/tabs/panels/theme selection.",
        )
        self.service.register_snapshot_provider(
            f"{ns}.layout",
            self._snapshot_layout,
            description="Layout-only snapshot.",
        )
        self.service.register_snapshot_provider(
            f"{ns}.view",
            self._snapshot_view,
            description="Active view/tabs/panels summary snapshot.",
        )

        self.service.register_query(
            f"{ns}.diagnostics.get",
            self._query_diagnostics,
            description="Runtime diagnostics payload.",
        )
        self.service.register_query(
            f"{ns}.panels.list",
            self._query_panels,
            description="Panel inventory and states.",
        )
        self.service.register_query(
            f"{ns}.tabs.list",
            self._query_tabs,
            description="Tab inventory and states.",
        )

        self.service.register_command(
            f"{ns}.panel.state.set",
            self._command_set_panel_state,
            required_capabilities=write_caps,
            description="Set panel state (visible/hidden/collapsed/deferred/disabled/background/hold).",
        )
        self.service.register_command(
            f"{ns}.panel.visibility.set",
            self._command_set_panel_visibility,
            required_capabilities=write_caps,
            description="Set panel visibility boolean.",
        )
        self.service.register_command(
            f"{ns}.tab.activate",
            self._command_activate_tab,
            required_capabilities=write_caps,
            description="Set active workspace tab.",
        )
        self.service.register_command(
            f"{ns}.tab.state.set",
            self._command_set_tab_state,
            required_capabilities=write_caps,
            description="Set workspace tab state.",
        )
        self.service.register_command(
            f"{ns}.layout.apply",
            self._command_apply_layout,
            required_capabilities=write_caps,
            description="Apply named layout preset.",
        )
        self.service.register_command(
            f"{ns}.preset.activate",
            self._command_activate_preset,
            required_capabilities=write_caps,
            description="Activate runtime preset.",
        )
        self.service.register_command(
            f"{ns}.theme.set",
            self._command_set_theme,
            required_capabilities=write_caps,
            description="Set active theme.",
        )
        self.service.register_command(
            f"{ns}.density.set",
            self._command_set_density,
            required_capabilities=write_caps,
            description="Set active density.",
        )
        self.service.register_command(
            f"{ns}.typography.scale.set",
            self._command_set_typography_scale,
            required_capabilities=write_caps,
            description="Set active typography scale.",
        )
        self.service.register_command(
            f"{ns}.state.save",
            self._command_save_state,
            required_capabilities=write_caps,
            description="Persist current workspace state.",
        )
        self.service.register_command(
            f"{ns}.state.load",
            self._command_load_state,
            required_capabilities=write_caps,
            description="Load persisted workspace state.",
        )

    def _query_diagnostics(self, envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        return {
            "runtime": self.runtime.diagnostics(),
            "service": self.service.diagnostics_payload(),
            "namespace": self.namespace,
            "workspace_id": envelope.context.workspace_id,
        }

    def _query_panels(self, _envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        panels: list[dict[str, Any]] = []
        for panel_id in self.template.panel_ids():
            panel = self.template.panel(panel_id)
            if panel is None:
                continue
            panels.append(
                {
                    "panel_id": panel_id,
                    "state": str(panel.property("panelState") or "visible"),
                    "role": str(panel.property("panelRole") or "workspace"),
                    "visible": bool(panel.isVisible()),
                    "enabled": bool(panel.isEnabled()),
                }
            )
        return {"panels": panels}

    def _query_tabs(self, _envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        tabs = self.template.workspace_tabs
        if tabs is None:
            return {"enabled": False, "tabs": [], "active_tab_id": None}
        return {
            "enabled": True,
            "tabs": [
                {
                    "tab_id": tab_id,
                    "state": tabs.tab_state(tab_id),
                }
                for tab_id in tabs.tab_ids()
            ],
            "active_tab_id": tabs.active_tab_id(),
        }

    def _snapshot_workspace(self, _request: IntegrationSnapshotRequest) -> dict[str, Any]:
        return {
            "workspace_state": self.runtime.export_workspace_state().to_payload(),
            "runtime": self.runtime.diagnostics(),
        }

    def _snapshot_layout(self, _request: IntegrationSnapshotRequest) -> dict[str, Any]:
        return {"layout": self.template.snapshot_layout_state()}

    def _snapshot_view(self, _request: IntegrationSnapshotRequest) -> dict[str, Any]:
        tabs = self.template.workspace_tabs
        return {
            "active_tab_id": tabs.active_tab_id() if tabs is not None else None,
            "tab_states": tabs.snapshot_states() if tabs is not None else {},
            "panel_visibility": {
                panel_id: bool(self.template.panel(panel_id).isVisible())
                for panel_id in self.template.panel_ids()
                if self.template.panel(panel_id) is not None
            },
            "theme_id": self.runtime.current_config().theme.theme_id,
            "density": self.runtime.current_config().theme.density,
            "typography_scale": self.runtime.current_config().theme.typography.scale,
        }

    def _command_set_panel_state(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        panel_id = self._required_text(envelope.payload, "panel_id")
        state = self._required_text(envelope.payload, "state")
        self.template.set_panel_state(panel_id, state)
        self._emit_runtime_event("panel.state.changed", {"panel_id": panel_id, "state": state}, envelope)
        return {"panel_id": panel_id, "state": state}

    def _command_set_panel_visibility(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        panel_id = self._required_text(envelope.payload, "panel_id")
        visible = bool(envelope.payload.get("visible"))
        self.template.set_panel_visible(panel_id, visible)
        self._emit_runtime_event(
            "panel.visibility.changed",
            {"panel_id": panel_id, "visible": visible},
            envelope,
        )
        return {"panel_id": panel_id, "visible": visible}

    def _command_activate_tab(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        tab_id = self._required_text(envelope.payload, "tab_id")
        activated = self.template.set_active_workspace_tab(tab_id)
        self._emit_runtime_event("tab.activated", {"tab_id": tab_id, "activated": activated}, envelope)
        return {"tab_id": tab_id, "activated": activated}

    def _command_set_tab_state(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        tab_id = self._required_text(envelope.payload, "tab_id")
        state = self._required_text(envelope.payload, "state")
        self.template.set_workspace_tab_state(tab_id, state)
        self._emit_runtime_event("tab.state.changed", {"tab_id": tab_id, "state": state}, envelope)
        return {"tab_id": tab_id, "state": state}

    def _command_apply_layout(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        name = self._required_text(envelope.payload, "layout_name")
        applied = self.runtime.apply_layout(name, tolerate_missing=False)
        self._emit_runtime_event("layout.applied", {"layout_name": name}, envelope)
        return {"layout_name": name, "applied": bool(applied is None or applied)}

    def _command_activate_preset(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        preset = self._required_text(envelope.payload, "preset")
        self.runtime.activate_preset(preset)
        self._emit_runtime_event("preset.activated", {"preset": preset}, envelope)
        return {"preset": preset}

    def _command_set_theme(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        theme_id = self._required_text(envelope.payload, "theme_id")
        self.template.set_theme(theme_id)
        self._emit_runtime_event("theme.changed", {"theme_id": theme_id}, envelope)
        return {"theme_id": theme_id}

    def _command_set_density(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        density = self._required_text(envelope.payload, "density")
        self.template.set_density(density)
        self._emit_runtime_event("density.changed", {"density": density}, envelope)
        return {"density": density}

    def _command_set_typography_scale(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        scale = self._required_text(envelope.payload, "scale")
        self.template.set_typography_scale(scale)
        self._emit_runtime_event("typography.scale.changed", {"scale": scale}, envelope)
        return {"scale": scale}

    def _command_save_state(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        path = envelope.payload.get("path")
        saved = self.runtime.save_workspace_state(path=path)
        self._emit_runtime_event("state.saved", {"path": str(saved) if saved else None}, envelope)
        return {"path": str(saved) if saved else None}

    def _command_load_state(self, envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        path = envelope.payload.get("path")
        state = self.runtime.load_workspace_state(path=path)
        loaded = state is not None
        self._emit_runtime_event("state.loaded", {"loaded": loaded}, envelope)
        return {"loaded": loaded}

    def _required_text(self, payload: dict[str, Any], key: str) -> str:
        value = str(payload.get(key) or "").strip()
        if not value:
            raise IntegrationValidationError(f"{key} is required")
        return value

    def _emit_runtime_event(
        self,
        event_suffix: str,
        payload: dict[str, Any],
        envelope: IntegrationCommandEnvelope,
    ) -> None:
        self.service.emit_event(
            f"{self.namespace}.{event_suffix}",
            payload,
            topic=self.namespace,
            context=envelope.context,
            correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
            source="integration.runtime_bridge",
        )


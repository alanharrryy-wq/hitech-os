from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from .contracts import (
    IntegrationCommandEnvelope,
    IntegrationQueryEnvelope,
    IntegrationSnapshotRequest,
    IntegrationValidationError,
)
from .service import IntegrationService


@dataclass(slots=True)
class ReferenceWorkspaceState:
    workspace_id: str = "workspace-reference"
    active_view: str = "overview"
    item_revision: int = 0
    panel_states: dict[str, str] = field(
        default_factory=lambda: {
            "main": "visible",
            "side": "visible",
        }
    )
    items: dict[str, dict[str, Any]] = field(default_factory=dict)
    lock: RLock = field(default_factory=RLock)

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            return {
                "workspace_id": self.workspace_id,
                "active_view": self.active_view,
                "item_revision": self.item_revision,
                "item_count": len(self.items),
                "items": {key: dict(value) for key, value in self.items.items()},
                "panel_states": dict(self.panel_states),
            }


def register_reference_workspace_endpoints(
    service: IntegrationService,
    *,
    namespace: str = "workspace",
    required_write_capability: str = "workspace.write",
    state: ReferenceWorkspaceState | None = None,
) -> ReferenceWorkspaceState:
    """
    Register neutral reference endpoints for demos/web-shell validation.

    This is intentionally domain-agnostic and acts as a reusable baseline
    for lightweight client integration tests and shell references.
    """

    workspace_state = state or ReferenceWorkspaceState()
    ns = str(namespace or "workspace").strip().lower() or "workspace"
    write_caps = (str(required_write_capability).strip(),) if required_write_capability else ()

    def _command_upsert_item(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        item_id = str(envelope.payload.get("item_id") or "").strip()
        if not item_id:
            raise IntegrationValidationError("item_id is required")
        item_payload = envelope.payload.get("item") or {}
        if not isinstance(item_payload, dict):
            raise IntegrationValidationError("item must be a mapping payload")
        with workspace_state.lock:
            workspace_state.items[item_id] = dict(item_payload)
            workspace_state.item_revision += 1
            revision = workspace_state.item_revision
            count = len(workspace_state.items)
        return {
            "item_id": item_id,
            "item_count": count,
            "item_revision": revision,
        }

    def _command_panel_state(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        panel_id = str(envelope.payload.get("panel_id") or "").strip()
        state_value = str(envelope.payload.get("state") or "").strip().lower()
        if not panel_id:
            raise IntegrationValidationError("panel_id is required")
        if not state_value:
            raise IntegrationValidationError("state is required")
        with workspace_state.lock:
            workspace_state.panel_states[panel_id] = state_value
            workspace_state.item_revision += 1
            revision = workspace_state.item_revision
        return {"panel_id": panel_id, "state": state_value, "item_revision": revision}

    def _command_set_view(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        view_id = str(envelope.payload.get("view_id") or "").strip().lower()
        if not view_id:
            raise IntegrationValidationError("view_id is required")
        with workspace_state.lock:
            workspace_state.active_view = view_id
            workspace_state.item_revision += 1
            revision = workspace_state.item_revision
        return {"view_id": view_id, "item_revision": revision}

    def _query_summary(_envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        snapshot = workspace_state.snapshot()
        return {
            "workspace_id": snapshot["workspace_id"],
            "active_view": snapshot["active_view"],
            "item_count": snapshot["item_count"],
            "item_revision": snapshot["item_revision"],
            "panel_states": snapshot["panel_states"],
        }

    def _query_item_get(envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        item_id = str(envelope.params.get("item_id") or "").strip()
        if not item_id:
            raise IntegrationValidationError("params.item_id is required")
        with workspace_state.lock:
            item = workspace_state.items.get(item_id)
            revision = workspace_state.item_revision
        return {
            "item_id": item_id,
            "exists": item is not None,
            "item": dict(item or {}),
            "item_revision": revision,
        }

    def _snapshot_workspace(_request: IntegrationSnapshotRequest) -> dict[str, Any]:
        return {"workspace": workspace_state.snapshot()}

    def _snapshot_layout(_request: IntegrationSnapshotRequest) -> dict[str, Any]:
        snapshot = workspace_state.snapshot()
        return {
            "layout": {
                "active_view": snapshot["active_view"],
                "panel_states": snapshot["panel_states"],
            }
        }

    service.register_command(
        f"{ns}.item.upsert",
        _command_upsert_item,
        required_capabilities=write_caps,
        description="Upsert a generic workspace item by id.",
    )
    service.register_command(
        f"{ns}.panel.state.set",
        _command_panel_state,
        required_capabilities=write_caps,
        description="Set panel state in the reference workspace.",
    )
    service.register_command(
        f"{ns}.view.set",
        _command_set_view,
        required_capabilities=write_caps,
        description="Set active view id for reference workspace.",
    )
    service.register_query(
        f"{ns}.summary.get",
        _query_summary,
        description="Get workspace summary payload.",
    )
    service.register_query(
        f"{ns}.item.get",
        _query_item_get,
        description="Get one workspace item payload by id.",
    )
    service.register_snapshot_provider(
        f"{ns}",
        _snapshot_workspace,
        description="Get full reference workspace snapshot.",
    )
    service.register_snapshot_provider(
        f"{ns}.layout",
        _snapshot_layout,
        description="Get layout-focused snapshot payload.",
    )
    return workspace_state


def create_reference_workspace_service(
    *,
    debug: bool = False,
    namespace: str = "workspace",
) -> tuple[IntegrationService, ReferenceWorkspaceState]:
    service = IntegrationService(debug=debug)
    state = register_reference_workspace_endpoints(service, namespace=namespace)
    return service, state


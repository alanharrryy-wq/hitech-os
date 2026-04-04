from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

CURRENT_WORKSPACE_SCHEMA_VERSION = 2


@dataclass(slots=True)
class GlassWorkspaceState:
    """Serializable workspace state for tabs, panels, layouts and visual preferences."""

    schema_version: int = CURRENT_WORKSPACE_SCHEMA_VERSION
    layout: dict[str, list[int]] = field(default_factory=dict)
    selected_layout_preset: str | None = None
    tab_states: dict[str, str] = field(default_factory=dict)
    tab_order: list[str] = field(default_factory=list)
    active_tab_id: str | None = None
    panel_states: dict[str, str] = field(default_factory=dict)
    panel_visibility: dict[str, bool] = field(default_factory=dict)
    theme_id: str | None = None
    density: str | None = None
    typography_scale: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "layout": {key: [int(size) for size in value] for key, value in self.layout.items()},
            "selected_layout_preset": self.selected_layout_preset,
            "tab_states": {str(key): str(value) for key, value in self.tab_states.items()},
            "tab_order": [str(item) for item in self.tab_order],
            "active_tab_id": self.active_tab_id,
            "panel_states": {str(key): str(value) for key, value in self.panel_states.items()},
            "panel_visibility": {str(key): bool(value) for key, value in self.panel_visibility.items()},
            "theme_id": self.theme_id,
            "density": self.density,
            "typography_scale": self.typography_scale,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> GlassWorkspaceState:
        payload = payload or {}
        schema = int(payload.get("schema_version") or 1)
        migrated = _migrate_payload(dict(payload), schema)

        layout_payload = migrated.get("layout") or {}
        layout: dict[str, list[int]] = {}
        if isinstance(layout_payload, Mapping):
            for key, value in layout_payload.items():
                if isinstance(value, (list, tuple)):
                    layout[str(key)] = [int(size) for size in value]

        tab_order_payload = migrated.get("tab_order") or []
        tab_states_payload = migrated.get("tab_states") or {}
        panel_states_payload = migrated.get("panel_states") or {}
        panel_visibility_payload = migrated.get("panel_visibility") or {}
        metadata_payload = migrated.get("metadata") or {}

        return cls(
            schema_version=CURRENT_WORKSPACE_SCHEMA_VERSION,
            layout=layout,
            selected_layout_preset=str(migrated.get("selected_layout_preset"))
            if migrated.get("selected_layout_preset")
            else None,
            tab_states={
                str(key): str(value)
                for key, value in tab_states_payload.items()
            }
            if isinstance(tab_states_payload, Mapping)
            else {},
            tab_order=[str(item) for item in tab_order_payload] if isinstance(tab_order_payload, list) else [],
            active_tab_id=str(migrated.get("active_tab_id")) if migrated.get("active_tab_id") else None,
            panel_states={
                str(key): str(value)
                for key, value in panel_states_payload.items()
            }
            if isinstance(panel_states_payload, Mapping)
            else {},
            panel_visibility={
                str(key): bool(value)
                for key, value in panel_visibility_payload.items()
            }
            if isinstance(panel_visibility_payload, Mapping)
            else {},
            theme_id=str(migrated.get("theme_id")) if migrated.get("theme_id") else None,
            density=str(migrated.get("density")) if migrated.get("density") else None,
            typography_scale=str(migrated.get("typography_scale")) if migrated.get("typography_scale") else None,
            metadata=dict(metadata_payload) if isinstance(metadata_payload, Mapping) else {},
        )


def _migrate_payload(payload: dict[str, Any], source_schema: int) -> dict[str, Any]:
    """
    Migration strategy:
    - v1 -> v2 adds tab_order, layout preset and visual preference fields.
    - unknown future schemas: keep payload but guard with safe fallbacks.
    """
    working = dict(payload)
    schema = int(source_schema)

    if schema <= 1:
        tab_states = working.get("tab_states") or {}
        if isinstance(tab_states, Mapping):
            working.setdefault("tab_order", list(tab_states.keys()))
        working.setdefault("selected_layout_preset", "main_side")
        metadata = dict(working.get("metadata") or {})
        metadata.setdefault("migrated_from_schema", schema)
        working["metadata"] = metadata
        working.setdefault("theme_id", metadata.get("active_theme_id"))
        working.setdefault("density", metadata.get("active_density"))
        working.setdefault("typography_scale", metadata.get("active_typography_scale"))

    working["schema_version"] = CURRENT_WORKSPACE_SCHEMA_VERSION
    return working


def save_workspace_state(path: str | Path, state: GlassWorkspaceState) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state.to_payload(), indent=2, ensure_ascii=True), encoding="utf-8")
    return target


def load_workspace_state(path: str | Path) -> GlassWorkspaceState | None:
    source = Path(path)
    if not source.exists() or not source.is_file():
        return None
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, Mapping):
        return None
    return GlassWorkspaceState.from_payload(payload)

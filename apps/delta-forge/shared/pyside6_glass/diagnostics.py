from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .config import GlassResolvedConfig, GlassTemplateConfig
from .template import GlassPanelTemplate


def config_snapshot(config: GlassTemplateConfig) -> dict[str, Any]:
    return asdict(config.normalized())


def resolved_snapshot(resolved: GlassResolvedConfig) -> dict[str, Any]:
    return {
        "config": config_snapshot(resolved.config),
        "layers_applied": list(resolved.layers_applied),
        "field_sources": dict(resolved.field_sources),
    }


def template_runtime_snapshot(template: GlassPanelTemplate) -> dict[str, Any]:
    tabs = template.workspace_tabs
    return {
        "title": template.windowTitle(),
        "panel_ids": list(template.panel_ids()),
        "layout_state": template.snapshot_layout_state(),
        "tabs": {
            "enabled": tabs is not None,
            "tab_ids": list(tabs.tab_ids()) if tabs else [],
            "active": tabs.active_tab_id() if tabs else None,
            "tab_states": tabs.snapshot_states() if tabs else {},
        },
    }


def validate_template_config(config: GlassTemplateConfig) -> list[str]:
    issues: list[str] = []
    normalized = config.normalized()
    if normalized.tabs.enabled and not normalized.tabs.default_tab_id.strip():
        issues.append("tabs.default_tab_id cannot be empty when tabs are enabled")
    if normalized.regions.min_main_width < 120:
        issues.append("regions.min_main_width is unexpectedly small")
    if normalized.persistence.enabled and not normalized.persistence.storage_path.strip():
        issues.append("persistence.storage_path is required when persistence is enabled")
    if normalized.theme.visual_scale.icon_scale <= 0:
        issues.append("theme.visual_scale.icon_scale must be > 0")
    return issues

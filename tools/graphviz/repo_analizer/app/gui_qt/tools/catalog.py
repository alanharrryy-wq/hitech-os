from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable, Mapping

from PySide6.QtCore import QSettings

from .models import ToolCategory, ToolDescriptor, ToolLaunchEntry, ToolSource, ToolState


class ToolCatalogService:
    """
    Canonical catalog of tools for launcher/switcher/runtime policies.

    Bridges manifest/plugin descriptors into product-level tool metadata.
    """

    KEY_ENABLED_OVERRIDES = "tools/enabled_overrides"
    KEY_RECENTS = "tools/recent_ids"

    def __init__(self, settings: QSettings) -> None:
        self.settings = settings
        self._tools: dict[str, ToolDescriptor] = {}
        self._enabled_overrides = self._load_enabled_overrides()
        self._recent_tool_ids = self._load_recent_ids()

    def register_tool(
        self,
        tool_id: str,
        *,
        display_name: str,
        description: str = "",
        category: ToolCategory = "other",
        source: ToolSource = "plugin",
        icon_name: str = "",
        enabled: bool = True,
        user_facing: bool = True,
        feature_flag: str = "",
        tags: Iterable[str] | None = None,
        state: ToolState = "registered",
    ) -> ToolDescriptor:
        normalized_tool_id = self._normalize_tool_id(tool_id)
        resolved_enabled = self._enabled_overrides.get(normalized_tool_id, enabled)
        descriptor = ToolDescriptor(
            tool_id=normalized_tool_id,
            display_name=(display_name or normalized_tool_id).strip(),
            description=(description or "").strip(),
            category=category,
            source=source,
            icon_name=(icon_name or "").strip(),
            enabled=bool(resolved_enabled),
            user_facing=bool(user_facing),
            feature_flag=(feature_flag or "").strip(),
            tags=[str(tag).strip() for tag in (tags or []) if str(tag).strip()],
            state=state,
        )
        self._tools[normalized_tool_id] = descriptor
        return descriptor

    def register_from_manifest(
        self,
        *,
        tool_id: str,
        manifest_like: Mapping[str, Any] | None = None,
        default_source: ToolSource = "plugin",
    ) -> ToolDescriptor:
        manifest = manifest_like or {}
        name = str(manifest.get("name") or tool_id).strip()
        description = str(manifest.get("description") or "").strip()
        enabled = bool(manifest.get("enabled", True))
        source: ToolSource = default_source
        tags = []
        category = self._infer_category(tool_id=tool_id, name=name, description=description)
        icon_name = self._infer_icon_name(tool_id=tool_id, category=category)
        return self.register_tool(
            tool_id,
            display_name=name,
            description=description,
            category=category,
            source=source,
            icon_name=icon_name,
            enabled=enabled,
            user_facing=True,
            tags=tags,
            state="registered",
        )

    def has_tool(self, tool_id: str) -> bool:
        return self._normalize_tool_id(tool_id) in self._tools

    def get_tool(self, tool_id: str) -> ToolDescriptor | None:
        return self._tools.get(self._normalize_tool_id(tool_id))

    def set_state(self, tool_id: str, state: ToolState) -> None:
        descriptor = self.get_tool(tool_id)
        if descriptor is None:
            return
        descriptor.state = state

    def set_enabled(self, tool_id: str, enabled: bool) -> None:
        normalized = self._normalize_tool_id(tool_id)
        descriptor = self._tools.get(normalized)
        if descriptor is None:
            return
        descriptor.enabled = bool(enabled)
        self._enabled_overrides[normalized] = bool(enabled)
        self._save_enabled_overrides()

    def mark_recent(self, tool_id: str) -> None:
        normalized = self._normalize_tool_id(tool_id)
        if normalized in self._recent_tool_ids:
            self._recent_tool_ids.remove(normalized)
        self._recent_tool_ids.insert(0, normalized)
        self._recent_tool_ids = self._recent_tool_ids[:20]
        self._save_recent_ids()

    def list_launch_entries(
        self,
        *,
        active_tool_id: str | None,
        visible_tool_ids: set[str] | None = None,
    ) -> tuple[ToolLaunchEntry, ...]:
        visible_ids = visible_tool_ids or set()
        entries: list[ToolLaunchEntry] = []
        recency_index = {tool_id: idx for idx, tool_id in enumerate(self._recent_tool_ids)}
        for descriptor in self._sorted_tools():
            if descriptor.source == "core" or not descriptor.user_facing:
                continue
            entries.append(
                ToolLaunchEntry(
                    tool_id=descriptor.tool_id,
                    display_name=descriptor.display_name,
                    description=descriptor.description,
                    category=descriptor.category,
                    icon_name=descriptor.icon_name,
                    enabled=descriptor.enabled,
                    active=descriptor.tool_id == active_tool_id,
                    visible=descriptor.tool_id in visible_ids,
                    state=descriptor.state,
                    recent_rank=recency_index.get(descriptor.tool_id, 10_000),
                )
            )
        return tuple(
            sorted(
                entries,
                key=lambda item: (
                    item.recent_rank,
                    item.category,
                    item.display_name.lower(),
                ),
            )
        )

    def to_debug_payload(self) -> dict[str, Any]:
        return {
            "tools": [asdict(item) for item in self._sorted_tools()],
            "enabled_overrides": dict(self._enabled_overrides),
            "recent_tool_ids": list(self._recent_tool_ids),
        }

    def list_categories(self) -> tuple[ToolCategory, ...]:
        categories = {descriptor.category for descriptor in self._tools.values()}
        return tuple(sorted(categories))

    def list_recent_tool_ids(self) -> tuple[str, ...]:
        return tuple(self._recent_tool_ids)

    def list_enabled_tool_ids(self) -> tuple[str, ...]:
        return tuple(
            descriptor.tool_id
            for descriptor in self._sorted_tools()
            if descriptor.enabled and descriptor.user_facing and descriptor.source != "core"
        )

    def _sorted_tools(self) -> list[ToolDescriptor]:
        return sorted(self._tools.values(), key=lambda item: (item.category, item.display_name.lower()))

    def _load_enabled_overrides(self) -> dict[str, bool]:
        raw = self.settings.value(self.KEY_ENABLED_OVERRIDES, {})
        if isinstance(raw, dict):
            return {self._normalize_tool_id(str(k)): bool(v) for k, v in raw.items()}
        return {}

    def _save_enabled_overrides(self) -> None:
        self.settings.setValue(self.KEY_ENABLED_OVERRIDES, dict(self._enabled_overrides))

    def _load_recent_ids(self) -> list[str]:
        raw = self.settings.value(self.KEY_RECENTS, [])
        if isinstance(raw, list):
            values = [self._normalize_tool_id(str(item)) for item in raw if str(item).strip()]
            return [item for item in values if item]
        return []

    def _save_recent_ids(self) -> None:
        self.settings.setValue(self.KEY_RECENTS, list(self._recent_tool_ids))

    def _normalize_tool_id(self, value: str) -> str:
        normalized = "".join(ch if ch.isalnum() else "_" for ch in str(value).strip().lower())
        return normalized.strip("_") or "tool"

    def _infer_category(self, *, tool_id: str, name: str, description: str) -> ToolCategory:
        haystack = " ".join((tool_id, name, description)).lower()
        if "orchestrator" in haystack or "bridge" in haystack:
            return "orchestration"
        if "cloudflare_guardian" in haystack or "cloudflare" in haystack or "analysis" in haystack or "repo" in haystack:
            return "analysis"
        if "ops" in haystack or "operation" in haystack:
            return "operations"
        if "quality" in haystack or "validation" in haystack:
            return "quality"
        if "system" in haystack or "shell" in haystack:
            return "system"
        return "other"

    def _infer_icon_name(self, *, tool_id: str, category: ToolCategory) -> str:
        if "cloudflare_guardian" in tool_id or "cloudflare" in tool_id:
            return "shield"
        if "orchestrator" in tool_id:
            return "flow"
        category_icons = {
            "analysis": "graph",
            "orchestration": "flow",
            "operations": "gear",
            "quality": "check",
            "system": "layout",
            "other": "tool",
        }
        return category_icons.get(category, "tool")


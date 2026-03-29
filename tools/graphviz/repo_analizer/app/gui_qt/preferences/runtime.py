from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from .models import WorkstationPreferences
from .policy import RuntimePolicy


class PreferencesRuntime:
    """Runtime service for loading, storing and applying user preferences."""

    PREFIX = "preferences/"
    SCHEMA_VERSION_KEY = "schema_version"
    SCHEMA_VERSION = 1
    LEGACY_SKIN_KEY = "skin_name"
    TOOL_PREFIX = "tool_preferences/"

    def __init__(self, settings: QSettings, *, default_skin_name: str) -> None:
        self.settings = settings
        self._default_skin_name = default_skin_name
        self._preferences = self._load(default_skin_name=default_skin_name).normalized()
        self.settings.setValue(self._key(self.SCHEMA_VERSION_KEY), self.SCHEMA_VERSION)
        self._save(self._preferences)

    @property
    def current(self) -> WorkstationPreferences:
        return self._preferences

    def update(self, **changes: Any) -> WorkstationPreferences:
        allowed_fields = set(asdict(self._preferences).keys())
        payload = {k: v for k, v in changes.items() if k in allowed_fields}
        if not payload:
            return self._preferences

        self._preferences = replace(self._preferences, **payload).normalized()
        self._save(self._preferences)
        return self._preferences

    def reset_defaults(self) -> WorkstationPreferences:
        defaults = WorkstationPreferences.defaults(
            skin_name=self._default_skin_name,
        ).normalized()
        self._preferences = defaults
        self._save(self._preferences)
        return self._preferences

    def apply_app_font(self, app: QApplication | None = None) -> None:
        app = app or QApplication.instance()
        if app is None:
            return

        prefs = self._preferences
        current_font = QFont(app.font())
        if prefs.font_family and prefs.font_family.lower() not in {"system", "default"}:
            available = set(QFontDatabase.families())
            if prefs.font_family in available:
                current_font.setFamily(prefs.font_family)
        current_font.setPointSize(max(10, int(prefs.font_size)))
        app.setFont(current_font)

    def prefers_single_active_tool(self) -> bool:
        return self._preferences.layout_behavior == "single_active_tool"

    def plugin_load_flags(self) -> tuple[bool, bool]:
        """Return (include_dev_tools, enable_legacy_plugins)."""
        return (
            bool(self._preferences.include_dev_tools),
            bool(self._preferences.enable_legacy_plugins),
        )

    def runtime_policy(self) -> RuntimePolicy:
        return RuntimePolicy.from_preferences(self._preferences)

    def validate_persistence_contract(self) -> list[str]:
        issues: list[str] = []
        current_payload = asdict(self._preferences)
        persisted = self._load(default_skin_name=self._default_skin_name).normalized()
        persisted_payload = asdict(persisted)
        if current_payload != persisted_payload:
            issues.append("persisted preferences diverge from runtime snapshot")

        schema = self._coerce_int(
            self.settings.value(self._key(self.SCHEMA_VERSION_KEY), self.SCHEMA_VERSION),
            fallback=self.SCHEMA_VERSION,
        )
        if schema != self.SCHEMA_VERSION:
            issues.append(
                f"unsupported preferences schema version: {schema} (expected {self.SCHEMA_VERSION})"
            )
        return issues

    def settings_center_hook_payload(self) -> dict[str, Any]:
        prefs = self._preferences
        return {
            "schema_version": self.SCHEMA_VERSION,
            "preferences": asdict(prefs),
            "policy": asdict(self.runtime_policy()),
            "fields": (
                "skin_name",
                "font_family",
                "font_size",
                "density",
                "contrast",
                "motion",
                "performance",
                "layout_behavior",
                "include_dev_tools",
                "enable_legacy_plugins",
            ),
        }

    def get_tool_preferences(self, tool_id: str) -> dict[str, Any]:
        key = self._tool_key(tool_id)
        raw = self.settings.value(key, {})
        if isinstance(raw, dict):
            return dict(raw)
        return {}

    def update_tool_preferences(self, tool_id: str, **changes: Any) -> dict[str, Any]:
        current = self.get_tool_preferences(tool_id)
        for key, value in changes.items():
            if not str(key).strip():
                continue
            current[str(key)] = value
        self.settings.setValue(self._tool_key(tool_id), current)
        return current

    def reset_tool_preferences(self, tool_id: str) -> None:
        self.settings.remove(self._tool_key(tool_id))

    def _key(self, name: str) -> str:
        return f"{self.PREFIX}{name}"

    def _tool_key(self, tool_id: str) -> str:
        normalized = "".join(ch if ch.isalnum() else "_" for ch in str(tool_id).strip().lower())
        normalized = normalized.strip("_") or "tool"
        return f"{self.TOOL_PREFIX}{normalized}"

    def _load(self, *, default_skin_name: str) -> WorkstationPreferences:
        skin_name = str(
            self.settings.value(
                self._key("skin_name"),
                self.settings.value(self.LEGACY_SKIN_KEY, default_skin_name),
            )
            or default_skin_name
        )
        return WorkstationPreferences(
            skin_name=skin_name,
            font_family=str(self.settings.value(self._key("font_family"), "System") or "System"),
            font_size=self._coerce_int(self.settings.value(self._key("font_size"), 11), fallback=11),
            density=self._coerce_str(self.settings.value(self._key("density"), "comfortable"), fallback="comfortable"),
            contrast=self._coerce_str(self.settings.value(self._key("contrast"), "normal"), fallback="normal"),
            motion=self._coerce_str(self.settings.value(self._key("motion"), "full"), fallback="full"),
            performance=self._coerce_str(self.settings.value(self._key("performance"), "balanced"), fallback="balanced"),
            layout_behavior=self._coerce_str(
                self.settings.value(self._key("layout_behavior"), "single_active_tool"),
                fallback="single_active_tool",
            ),
            include_dev_tools=self._coerce_bool(self.settings.value(self._key("include_dev_tools"), False)),
            enable_legacy_plugins=self._coerce_bool(
                self.settings.value(self._key("enable_legacy_plugins"), False)
            ),
        )

    def _save(self, prefs: WorkstationPreferences) -> None:
        payload = asdict(prefs)
        for key, value in payload.items():
            self.settings.setValue(self._key(key), value)

        # Keep legacy key in sync for compatibility with previous skin runtime.
        self.settings.setValue(self.LEGACY_SKIN_KEY, prefs.skin_name)

    @staticmethod
    def _coerce_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        text = str(value or "").strip().lower()
        return text in {"1", "true", "yes", "on"}

    @staticmethod
    def _coerce_int(value: object, *, fallback: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _coerce_str(value: object, *, fallback: str) -> str:
        text = str(value or "").strip()
        return text or fallback

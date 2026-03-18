from __future__ import annotations

"""Manifest models and loading helpers for package-based plugins."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_PLUGIN_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
_SEMVER_PATTERN = re.compile(
    r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9][A-Za-z0-9.\-]*)?$"
)
_PY_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_ALLOWED_UI_KEYS = {"dock", "toolbar", "menu", "status", "reports"}


@dataclass(slots=True)
class PluginManifest:
    """Normalized plugin manifest loaded from plugin.json."""

    id: str
    name: str
    version: str
    module: str
    class_name: str = "PluginImplementation"
    description: str = ""
    author: str = ""
    enabled: bool = True
    dependencies: list[str] = field(default_factory=list)
    ui: dict[str, Any] = field(default_factory=dict)
    manifest_path: Path | None = None
    plugin_dir: Path | None = None

    @classmethod
    def from_file(cls, manifest_path: str | Path) -> "PluginManifest":
        manifest_file = Path(manifest_path).resolve()
        if not manifest_file.exists():
            raise FileNotFoundError(f"Plugin manifest not found: {manifest_file}")

        raw = json.loads(manifest_file.read_text(encoding="utf-8"))
        return cls.from_dict(raw, manifest_file)

    @classmethod
    def from_dict(
        cls,
        raw: dict[str, Any],
        manifest_path: str | Path | None = None,
    ) -> "PluginManifest":
        if not isinstance(raw, dict):
            raise ValueError("Plugin manifest payload must be an object")

        required = ["id", "name", "version", "module"]
        missing = [key for key in required if not raw.get(key)]
        if missing:
            raise ValueError(
                f"Plugin manifest is missing required fields: {', '.join(sorted(missing))}"
            )

        plugin_id = str(raw["id"]).strip()
        if not _PLUGIN_ID_PATTERN.fullmatch(plugin_id):
            raise ValueError(
                "Plugin manifest field 'id' must match "
                "'^[a-z][a-z0-9_]{1,63}$'"
            )

        plugin_name = str(raw["name"]).strip()
        if len(plugin_name) < 2:
            raise ValueError(
                "Plugin manifest field 'name' must contain at least 2 characters"
            )

        plugin_version = str(raw["version"]).strip()
        if not _SEMVER_PATTERN.fullmatch(plugin_version):
            raise ValueError(
                "Plugin manifest field 'version' must use semver "
                "(example: 1.2.3 or 1.2.3-beta)"
            )

        module_ref = str(raw["module"]).strip().replace("\\", "/")
        if module_ref.startswith("/") or module_ref.startswith("."):
            raise ValueError(
                "Plugin manifest field 'module' must be a relative module path"
            )
        module_parts = [part for part in module_ref.split("/") if part]
        if not module_parts:
            raise ValueError("Plugin manifest field 'module' cannot be empty")
        if any(part == ".." for part in module_parts):
            raise ValueError(
                "Plugin manifest field 'module' cannot traverse parent directories"
            )
        if not all(_PY_IDENTIFIER_PATTERN.fullmatch(part) for part in module_parts):
            raise ValueError(
                "Plugin manifest field 'module' must contain only Python identifier segments"
            )

        class_name = str(raw.get("class_name", "PluginImplementation")).strip()
        if not class_name:
            class_name = "PluginImplementation"
        if not _PY_IDENTIFIER_PATTERN.fullmatch(class_name):
            raise ValueError(
                "Plugin manifest field 'class_name' must be a valid Python identifier"
            )

        enabled_raw = raw.get("enabled", True)
        if not isinstance(enabled_raw, bool):
            raise ValueError("Plugin manifest field 'enabled' must be boolean")

        dependencies = raw.get("dependencies", [])
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) and item.strip() for item in dependencies
        ):
            raise ValueError("Plugin manifest field 'dependencies' must be a list of strings")
        normalized_dependencies = [item.strip() for item in dependencies]
        if len(set(normalized_dependencies)) != len(normalized_dependencies):
            raise ValueError(
                "Plugin manifest field 'dependencies' cannot contain duplicates"
            )
        invalid_dependencies = [
            dep for dep in normalized_dependencies if not _PLUGIN_ID_PATTERN.fullmatch(dep)
        ]
        if invalid_dependencies:
            raise ValueError(
                "Plugin manifest field 'dependencies' contains invalid plugin ids: "
                + ", ".join(sorted(invalid_dependencies))
            )
        if plugin_id in normalized_dependencies:
            raise ValueError(
                "Plugin manifest field 'dependencies' cannot include the plugin itself"
            )

        ui = raw.get("ui", {})
        if ui is None:
            ui = {}
        if not isinstance(ui, dict):
            raise ValueError("Plugin manifest field 'ui' must be an object")
        invalid_ui_keys = sorted(
            key for key in ui.keys() if str(key) not in _ALLOWED_UI_KEYS
        )
        if invalid_ui_keys:
            raise ValueError(
                "Plugin manifest field 'ui' contains unsupported keys: "
                + ", ".join(invalid_ui_keys)
            )
        invalid_ui_types = sorted(
            str(key) for key, value in ui.items() if not isinstance(value, bool)
        )
        if invalid_ui_types:
            raise ValueError(
                "Plugin manifest field 'ui' values must be booleans for keys: "
                + ", ".join(invalid_ui_types)
            )

        manifest_file = Path(manifest_path).resolve() if manifest_path else None

        return cls(
            id=plugin_id,
            name=plugin_name,
            version=plugin_version,
            module=module_ref,
            class_name=class_name,
            description=str(raw.get("description", "")).strip(),
            author=str(raw.get("author", "")).strip(),
            enabled=enabled_raw,
            dependencies=normalized_dependencies,
            ui=ui,
            manifest_path=manifest_file,
            plugin_dir=manifest_file.parent if manifest_file else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "module": self.module,
            "class_name": self.class_name,
            "description": self.description,
            "author": self.author,
            "enabled": self.enabled,
            "dependencies": list(self.dependencies),
            "ui": dict(self.ui),
        }

    def module_path_parts(self) -> list[str]:
        return [part for part in self.module.replace("\\", "/").split("/") if part]

from __future__ import annotations

"""Manifest models and loading helpers for package-based plugins."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
        required = ["id", "name", "version", "module"]
        missing = [key for key in required if not raw.get(key)]
        if missing:
            raise ValueError(
                f"Plugin manifest is missing required fields: {', '.join(sorted(missing))}"
            )

        dependencies = raw.get("dependencies", [])
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) and item.strip() for item in dependencies
        ):
            raise ValueError("Plugin manifest field 'dependencies' must be a list of strings")

        ui = raw.get("ui", {})
        if ui is None:
            ui = {}
        if not isinstance(ui, dict):
            raise ValueError("Plugin manifest field 'ui' must be an object")

        manifest_file = Path(manifest_path).resolve() if manifest_path else None

        return cls(
            id=str(raw["id"]).strip(),
            name=str(raw["name"]).strip(),
            version=str(raw["version"]).strip(),
            module=str(raw["module"]).strip(),
            class_name=str(raw.get("class_name", "PluginImplementation")).strip() or "PluginImplementation",
            description=str(raw.get("description", "")).strip(),
            author=str(raw.get("author", "")).strip(),
            enabled=bool(raw.get("enabled", True)),
            dependencies=[item.strip() for item in dependencies],
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

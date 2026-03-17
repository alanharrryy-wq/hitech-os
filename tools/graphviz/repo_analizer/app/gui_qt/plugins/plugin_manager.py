"""
Plugin manager for dynamically loading and managing plugins.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from .plugin_base import Plugin, PluginContext
from .plugin_manifest import PluginManifest

if TYPE_CHECKING:
    from ..command_dispatcher import CommandDispatcher
    from ..event_bus import EventBus
    from ..services import ServiceContainer


class PluginManager:
    """
    Plugin manager for loading, initializing, and managing plugins.

    Supports:
    - legacy single-file plugins ending in *_plugin.py
    - package plugins defined by plugin.json
    - dependency-aware initialization for manifest plugins
    """

    PLUGIN_FILE_SUFFIX = "_plugin.py"
    PLUGIN_MANIFEST_NAME = "plugin.json"

    def __init__(
        self,
        event_bus: EventBus,
        dispatcher: CommandDispatcher,
        container: ServiceContainer,
    ) -> None:
        self.event_bus = event_bus
        self.dispatcher = dispatcher
        self.container = container
        self._plugins: Dict[str, Plugin] = {}
        self._contexts: Dict[str, PluginContext] = {}
        self._loaded_modules = []
        self._manifests: Dict[str, PluginManifest] = {}
        self._plugin_dependencies: Dict[str, list[str]] = {}
        self._plugins_dir = Path(__file__).resolve().parent
        self._app_root = Path(__file__).resolve().parents[3]

    def _plugins_package_name(self) -> str:
        package_name = __package__
        if not package_name:
            raise RuntimeError("PluginManager package name is not available")
        return package_name

    def _host_package_name(self) -> str:
        plugins_package = self._plugins_package_name()
        if "." not in plugins_package:
            raise RuntimeError(
                f"Cannot determine host package name from '{plugins_package}'"
            )
        return plugins_package.rsplit(".", 1)[0]

    def _ensure_internal_import_environment(self) -> None:
        if str(self._app_root) not in sys.path:
            sys.path.insert(0, str(self._app_root))

        plugins_package = self._plugins_package_name()
        host_package = self._host_package_name()

        plugin_base_module = importlib.import_module(f"{plugins_package}.plugin_base")
        sys.modules.setdefault(f"{host_package}.plugin_base", plugin_base_module)

    def _is_internal_plugin_file(self, filepath: Path) -> bool:
        return filepath.resolve().parent == self._plugins_dir

    def _is_discoverable_plugin_file(self, filepath: Path) -> bool:
        return (
            filepath.is_file()
            and filepath.suffix == ".py"
            and not filepath.name.startswith("_")
            and filepath.name.endswith(self.PLUGIN_FILE_SUFFIX)
        )

    def _discover_manifest_plugin_dirs(self, directory: Path) -> list[Path]:
        discovered: list[Path] = []
        for child in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            if (child / self.PLUGIN_MANIFEST_NAME).exists():
                discovered.append(child)
        return discovered

    def _load_internal_plugin_module(self, filepath: Path):
        self._ensure_internal_import_environment()
        importlib.invalidate_caches()

        module_name = f"{self._plugins_package_name()}.{filepath.stem}"

        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)

        return module

    def _load_external_plugin_module(self, filepath: Path):
        module_name = f"_dynamic_plugin_{filepath.stem}_{abs(hash(str(filepath.resolve())))}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if not spec or not spec.loader:
            raise RuntimeError(f"Cannot load plugin from {filepath}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _load_manifest_plugin_module(self, manifest: PluginManifest):
        if manifest.plugin_dir is None:
            raise RuntimeError("Manifest plugin directory is not defined")

        self._ensure_internal_import_environment()
        importlib.invalidate_caches()

        module_ref = manifest.module.replace("\\", "/").strip("/")
        if not module_ref:
            raise RuntimeError(
                f"Plugin manifest '{manifest.id}' has an empty module reference"
            )

        if module_ref.startswith("app."):
            module_name = module_ref.replace("/", ".")
        else:
            module_name = (
                f"{self._plugins_package_name()}.{manifest.plugin_dir.name}."
                f"{module_ref.replace('/', '.')}"
            )

        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)

        return module

    def _find_plugin_class(self, module, class_name: str | None = None):
        if class_name:
            attr = getattr(module, class_name, None)
            if (
                isinstance(attr, type)
                and issubclass(attr, Plugin)
                and attr is not Plugin
            ):
                return attr
            raise ValueError(
                f"Plugin class '{class_name}' was not found in {module.__file__}"
            )

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Plugin)
                and attr is not Plugin
                and getattr(attr, "__module__", None) == module.__name__
            ):
                return attr

        raise ValueError(f"No Plugin class found in {module.__file__}")

    def _register_plugin(
        self,
        plugin: Plugin,
        *,
        manifest: PluginManifest | None = None,
        fallback_name: str,
    ) -> str:
        plugin_name = getattr(plugin, "name", "") or fallback_name
        if manifest is not None:
            plugin_name = manifest.id
            try:
                plugin.name = plugin_name
            except Exception:
                pass

        if plugin_name in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' is already loaded")

        self._plugins[plugin_name] = plugin
        self._plugin_dependencies[plugin_name] = (
            list(manifest.dependencies) if manifest is not None else []
        )
        if manifest is not None:
            self._manifests[plugin_name] = manifest

        return plugin_name

    def load_plugin_from_file(self, filepath: str) -> Optional[str]:
        filepath_obj = Path(filepath).resolve()
        if not filepath_obj.exists():
            raise FileNotFoundError(f"Plugin file not found: {filepath_obj}")

        if self._is_internal_plugin_file(filepath_obj):
            module = self._load_internal_plugin_module(filepath_obj)
        else:
            module = self._load_external_plugin_module(filepath_obj)

        if module not in self._loaded_modules:
            self._loaded_modules.append(module)

        plugin_class = self._find_plugin_class(module)
        plugin = plugin_class()
        return self._register_plugin(plugin, fallback_name=filepath_obj.stem)

    def load_plugin_from_manifest(self, manifest_path: str) -> Optional[str]:
        manifest = PluginManifest.from_file(manifest_path)
        module = self._load_manifest_plugin_module(manifest)

        if module not in self._loaded_modules:
            self._loaded_modules.append(module)

        plugin_class = self._find_plugin_class(module, manifest.class_name)
        plugin = plugin_class()
        return self._register_plugin(
            plugin,
            manifest=manifest,
            fallback_name=manifest.id,
        )

    def load_plugins_from_directory(self, directory: str) -> list[str]:
        directory_path = Path(directory).resolve()
        if not directory_path.exists():
            return []

        loaded: list[str] = []

        for plugin_dir in self._discover_manifest_plugin_dirs(directory_path):
            manifest_path = plugin_dir / self.PLUGIN_MANIFEST_NAME
            try:
                plugin_name = self.load_plugin_from_manifest(str(manifest_path))
                if plugin_name:
                    loaded.append(plugin_name)
            except Exception as exc:
                print(f"Failed to load plugin manifest from {manifest_path}: {exc}")

        for file_path in sorted(directory_path.iterdir(), key=lambda p: p.name.lower()):
            if not self._is_discoverable_plugin_file(file_path):
                continue

            try:
                plugin_name = self.load_plugin_from_file(str(file_path))
                if plugin_name:
                    loaded.append(plugin_name)
            except Exception as exc:
                print(f"Failed to load plugin from {file_path}: {exc}")

        return loaded

    def initialize_plugin(self, name: str) -> bool:
        if name not in self._plugins:
            return False

        if name in self._contexts:
            return True

        plugin = self._plugins[name]
        manifest = self._manifests.get(name)
        if manifest is not None and not manifest.enabled:
            print(f"Skipping disabled plugin '{name}' from manifest")
            return False

        context = PluginContext(self.event_bus, self.dispatcher, self.container)
        self._contexts[name] = context

        try:
            plugin.initialize(context)
            return True
        except Exception as exc:
            print(f"Failed to initialize plugin '{name}': {exc}")
            self._contexts.pop(name, None)
            return False

    def initialize_all(self) -> list[str]:
        initialized: list[str] = []
        visiting: set[str] = set()
        resolved: set[str] = set()
        failed: set[str] = set()

        def initialize_with_dependencies(name: str) -> bool:
            if name in resolved:
                return True
            if name in failed:
                return False
            if name in visiting:
                print(f"Dependency cycle detected while initializing plugin '{name}'")
                failed.add(name)
                return False
            if name not in self._plugins:
                failed.add(name)
                return False

            visiting.add(name)
            for dependency in self._plugin_dependencies.get(name, []):
                if dependency not in self._plugins:
                    print(
                        f"Cannot initialize plugin '{name}': missing dependency '{dependency}'"
                    )
                    visiting.remove(name)
                    failed.add(name)
                    return False
                if not initialize_with_dependencies(dependency):
                    visiting.remove(name)
                    failed.add(name)
                    return False

            visiting.remove(name)
            if self.initialize_plugin(name):
                resolved.add(name)
                initialized.append(name)
                return True

            failed.add(name)
            return False

        for name in list(self._plugins.keys()):
            initialize_with_dependencies(name)

        return initialized

    def get_plugin(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def get_plugin_manifest(self, name: str) -> Optional[PluginManifest]:
        return self._manifests.get(name)

    def has_plugin(self, name: str) -> bool:
        return name in self._plugins

    def shutdown_plugin(self, name: str) -> bool:
        if name not in self._plugins:
            return False

        plugin = self._plugins[name]
        plugin.shutdown()
        self._contexts.pop(name, None)
        return True

    def shutdown_all(self) -> None:
        for name in list(self._plugins.keys()):
            self.shutdown_plugin(name)

    def get_all_plugins(self) -> Dict[str, Plugin]:
        return self._plugins.copy()

    def get_enabled_plugins(self) -> Dict[str, Plugin]:
        return {name: p for name, p in self._plugins.items() if p.enabled}

    def enable_plugin(self, name: str) -> bool:
        if name in self._plugins:
            self._plugins[name].enabled = True
            manifest = self._manifests.get(name)
            if manifest is not None:
                manifest.enabled = True
            return True
        return False

    def disable_plugin(self, name: str) -> bool:
        if name in self._plugins:
            self._plugins[name].enabled = False
            manifest = self._manifests.get(name)
            if manifest is not None:
                manifest.enabled = False
            return True
        return False

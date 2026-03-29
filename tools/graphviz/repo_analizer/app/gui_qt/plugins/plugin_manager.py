"""
Plugin manager for dynamically loading and managing plugins.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .plugin_base import Plugin, PluginContext
from .plugin_manifest import PluginManifest

if TYPE_CHECKING:
    from ..command_dispatcher import CommandDispatcher
    from ..event_bus import EventBus
    from ..services import ServiceContainer


_DEBUG_TRUE_VALUES = {'1', 'true', 'yes', 'on'}
_DEV_PLUGIN_IDS = {'failure_injection', 'mi_plugin', 'demo_ui_validation'}
_PRODUCT_PLUGIN_IDS = {'cloudflare_guardian', 'orchestrator_bridge'}
_DEV_PLUGIN_KEYWORDS = {'demo', 'diagnostic', 'diagnostics', 'failure', 'inject', 'prueba', 'test'}
_LEGACY_PLUGIN_ALLOW_ENV = 'HITECH_QT_ENABLE_LEGACY_PLUGINS'
_DEV_PLUGIN_ALLOW_ENV = 'HITECH_QT_INCLUDE_DEV_TOOLS'


@dataclass(slots=True)
class PluginDiagnosticEvent:
    phase: str
    status: str
    plugin: str = ''
    message: str = ''
    source: str = ''


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
        self._diagnostic_events: list[PluginDiagnosticEvent] = []
        self._load_failures: list[str] = []
        self._init_failures: list[str] = []
        self._skipped_plugins: list[str] = []
        self._contract_warnings: list[str] = []
        self._manifest_validation_failures: list[str] = []
        self._include_dev_tools, self._enable_legacy_plugins = self._resolve_plugin_load_flags()

    def _resolve_debug_mode(self) -> bool:
        env_value = os.environ.get('HITECH_QT_DEV_TRACE', '').strip().lower()
        if env_value in _DEBUG_TRUE_VALUES:
            return True

        settings = self.container.get('settings') if self.container is not None else None
        if settings is not None:
            try:
                raw = settings.value('developer_debug_mode', False)
                text = str(raw).strip().lower()
                if text in _DEBUG_TRUE_VALUES:
                    return True
            except Exception:
                pass
        return False

    def _resolve_plugin_load_flags(self) -> tuple[bool, bool]:
        include_dev_tools = self._coerce_flag(
            os.environ.get(_DEV_PLUGIN_ALLOW_ENV, ''),
            fallback=False,
        )
        enable_legacy_plugins = self._coerce_flag(
            os.environ.get(_LEGACY_PLUGIN_ALLOW_ENV, ''),
            fallback=False,
        )

        settings = self.container.get('settings') if self.container is not None else None
        if settings is not None:
            include_dev_tools = include_dev_tools or self._coerce_flag(
                settings.value('preferences/include_dev_tools', False),
                fallback=False,
            )
            enable_legacy_plugins = enable_legacy_plugins or self._coerce_flag(
                settings.value('preferences/enable_legacy_plugins', False),
                fallback=False,
            )

        if self._resolve_debug_mode():
            include_dev_tools = True

        return include_dev_tools, enable_legacy_plugins

    def _coerce_flag(self, value: object, *, fallback: bool) -> bool:
        if isinstance(value, bool):
            return value
        text = str(value or '').strip().lower()
        if not text:
            return fallback
        return text in _DEBUG_TRUE_VALUES

    def _is_manifest_dev_only(self, manifest: PluginManifest) -> bool:
        if manifest.id in _PRODUCT_PLUGIN_IDS:
            return False
        if manifest.id in _DEV_PLUGIN_IDS:
            return True
        haystack = " ".join(
            (
                manifest.id,
                manifest.name,
                manifest.description,
                manifest.author,
            )
        ).lower()
        return any(keyword in haystack for keyword in _DEV_PLUGIN_KEYWORDS)

    def _is_legacy_plugin_file_dev_only(self, filepath: Path) -> bool:
        stem = filepath.stem.lower()
        if stem in _DEV_PLUGIN_IDS:
            return True
        return any(keyword in stem for keyword in _DEV_PLUGIN_KEYWORDS)

    def _emit_log(self, message: str) -> None:
        main_window = self.container.get('main_window') if self.container is not None else None
        logger = getattr(main_window, 'log', None)
        if callable(logger):
            try:
                logger(message)
                return
            except Exception:
                pass
        print(message)

    def _record_event(
        self,
        *,
        phase: str,
        status: str,
        plugin: str = '',
        message: str = '',
        source: str = '',
    ) -> None:
        event = PluginDiagnosticEvent(
            phase=phase,
            status=status,
            plugin=plugin,
            message=message,
            source=source,
        )
        self._diagnostic_events.append(event)

        debug_mode = self._resolve_debug_mode()
        if status in {'failed', 'warning'} or debug_mode:
            plugin_part = f' plugin={plugin}' if plugin else ''
            source_part = f' source={source}' if source else ''
            message_part = f' msg={message}' if message else ''
            self._emit_log(
                f"[plugin-diag] {phase}:{status}{plugin_part}{source_part}{message_part}"
            )

    def _record_contract_warning(self, plugin_name: str, message: str) -> None:
        entry = f"{plugin_name}: {message}"
        self._contract_warnings.append(entry)
        self._record_event(
            phase='contract',
            status='warning',
            plugin=plugin_name,
            message=message,
        )

    def _resolve_manifest_module_file(self, manifest: PluginManifest) -> Path | None:
        if manifest.plugin_dir is None:
            return None

        parts = manifest.module_path_parts()
        if not parts:
            return None

        candidate_root = manifest.plugin_dir.joinpath(*parts)
        module_file = candidate_root.with_suffix('.py')
        package_init = candidate_root / '__init__.py'

        if module_file.exists():
            return module_file
        if package_init.exists():
            return package_init
        return None

    def _validate_manifest_contract(self, manifest: PluginManifest) -> None:
        if manifest.manifest_path is None:
            raise ValueError("Plugin manifest path is not defined")
        if manifest.plugin_dir is None:
            raise ValueError(f"Plugin manifest '{manifest.id}' has no plugin directory")
        if not manifest.plugin_dir.exists():
            raise ValueError(
                f"Plugin directory does not exist for '{manifest.id}': {manifest.plugin_dir}"
            )

        module_file = self._resolve_manifest_module_file(manifest)
        if module_file is None:
            module_ref = manifest.module.replace("\\", "/")
            raise ValueError(
                f"Plugin manifest '{manifest.id}' module '{module_ref}' does not resolve to "
                f"a module file under {manifest.plugin_dir}"
            )

        if manifest.class_name == "Plugin":
            raise ValueError(
                f"Plugin manifest '{manifest.id}' cannot use abstract base class 'Plugin' as class_name"
            )

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

        if not plugin_name:
            raise ValueError('Plugin name cannot be empty')

        if plugin_name in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' is already loaded")

        version = str(getattr(plugin, 'version', '') or '').strip()
        if not version:
            self._record_contract_warning(plugin_name, 'missing version')

        description = str(getattr(plugin, 'description', '') or '').strip()
        if not description:
            self._record_contract_warning(plugin_name, 'missing description')

        self._plugins[plugin_name] = plugin
        self._plugin_dependencies[plugin_name] = (
            list(manifest.dependencies) if manifest is not None else []
        )
        if manifest is not None:
            self._manifests[plugin_name] = manifest

        self._record_event(
            phase='register',
            status='ok',
            plugin=plugin_name,
            message='plugin registered',
            source=str(manifest.manifest_path) if manifest is not None and manifest.manifest_path else fallback_name,
        )
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
        plugin_name = self._register_plugin(plugin, fallback_name=filepath_obj.stem)
        self._record_event(
            phase='load',
            status='ok',
            plugin=plugin_name,
            message='loaded from file',
            source=str(filepath_obj),
        )
        return plugin_name

    def load_plugin_from_manifest(self, manifest_path: str) -> Optional[str]:
        manifest = PluginManifest.from_file(manifest_path)
        self._validate_manifest_contract(manifest)
        module = self._load_manifest_plugin_module(manifest)

        if module not in self._loaded_modules:
            self._loaded_modules.append(module)

        plugin_class = self._find_plugin_class(module, manifest.class_name)
        plugin = plugin_class()
        plugin_name = self._register_plugin(
            plugin,
            manifest=manifest,
            fallback_name=manifest.id,
        )
        self._record_event(
            phase='load',
            status='ok',
            plugin=plugin_name,
            message='loaded from manifest',
            source=str(manifest.manifest_path) if manifest.manifest_path else manifest_path,
        )
        return plugin_name

    def load_plugins_from_directory(self, directory: str) -> list[str]:
        directory_path = Path(directory).resolve()
        if not directory_path.exists():
            self._record_event(
                phase='discover',
                status='warning',
                message='plugin directory not found',
                source=str(directory_path),
            )
            return []

        loaded: list[str] = []
        self._record_event(
            phase='policy',
            status='ok',
            message=(
                f'include_dev_tools={self._include_dev_tools} '
                f'legacy_plugins={self._enable_legacy_plugins}'
            ),
            source=str(directory_path),
        )

        manifest_dirs = self._discover_manifest_plugin_dirs(directory_path)
        self._record_event(
            phase='discover',
            status='ok',
            message=f'manifest_dirs={len(manifest_dirs)}',
            source=str(directory_path),
        )

        for plugin_dir in manifest_dirs:
            manifest_path = plugin_dir / self.PLUGIN_MANIFEST_NAME
            try:
                manifest_preview = PluginManifest.from_file(str(manifest_path))
                if (not self._include_dev_tools) and self._is_manifest_dev_only(manifest_preview):
                    msg = f"Skipping development tool manifest '{manifest_preview.id}' by policy"
                    self._skipped_plugins.append(msg)
                    self._record_event(
                        phase='manifest',
                        status='skipped',
                        plugin=manifest_preview.id,
                        message='development tool hidden by policy',
                        source=str(manifest_path),
                    )
                    continue
                plugin_name = self.load_plugin_from_manifest(str(manifest_path))
                if plugin_name:
                    loaded.append(plugin_name)
            except Exception as exc:
                failure = f"Failed to load plugin manifest from {manifest_path}: {exc}"
                self._load_failures.append(failure)
                self._manifest_validation_failures.append(failure)
                self._record_event(
                    phase='manifest',
                    status='failed',
                    message=str(exc),
                    source=str(manifest_path),
                )
                print(failure)

        discoverable_files = [
            file_path
            for file_path in sorted(directory_path.iterdir(), key=lambda p: p.name.lower())
            if self._is_discoverable_plugin_file(file_path)
        ]
        self._record_event(
            phase='discover',
            status='ok',
            message=f'legacy_files={len(discoverable_files)}',
            source=str(directory_path),
        )

        for file_path in discoverable_files:
            if not self._enable_legacy_plugins:
                msg = (
                    f"Skipping legacy plugin file '{file_path.name}' "
                    "because legacy plugin loading is disabled"
                )
                self._skipped_plugins.append(msg)
                self._record_event(
                    phase='load',
                    status='skipped',
                    message='legacy plugin loading disabled by policy',
                    source=str(file_path),
                )
                continue
            if (not self._include_dev_tools) and self._is_legacy_plugin_file_dev_only(file_path):
                msg = f"Skipping development legacy plugin '{file_path.name}' by policy"
                self._skipped_plugins.append(msg)
                self._record_event(
                    phase='load',
                    status='skipped',
                    message='legacy development tool hidden by policy',
                    source=str(file_path),
                )
                continue
            try:
                plugin_name = self.load_plugin_from_file(str(file_path))
                if plugin_name:
                    loaded.append(plugin_name)
            except Exception as exc:
                failure = f"Failed to load plugin from {file_path}: {exc}"
                self._load_failures.append(failure)
                self._record_event(
                    phase='load',
                    status='failed',
                    message=str(exc),
                    source=str(file_path),
                )
                print(failure)

        return loaded

    def initialize_plugin(self, name: str) -> bool:
        if name not in self._plugins:
            self._record_event(
                phase='initialize',
                status='failed',
                plugin=name,
                message='plugin not loaded',
            )
            return False

        if name in self._contexts:
            self._record_event(
                phase='initialize',
                status='skipped',
                plugin=name,
                message='already initialized',
            )
            return True

        plugin = self._plugins[name]
        manifest = self._manifests.get(name)
        if manifest is not None and not manifest.enabled:
            msg = f"Skipping disabled plugin '{name}' from manifest"
            self._skipped_plugins.append(msg)
            self._record_event(
                phase='initialize',
                status='skipped',
                plugin=name,
                message='manifest disabled',
            )
            print(msg)
            return False

        context = PluginContext(self.event_bus, self.dispatcher, self.container)
        self._contexts[name] = context

        try:
            plugin.initialize(context)
            self._record_event(
                phase='initialize',
                status='ok',
                plugin=name,
                message='initialized',
            )
            return True
        except Exception as exc:
            failure = f"Failed to initialize plugin '{name}': {exc}"
            self._init_failures.append(failure)
            self._record_event(
                phase='initialize',
                status='failed',
                plugin=name,
                message=str(exc),
            )
            print(failure)
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
                self._record_event(
                    phase='dependency',
                    status='failed',
                    plugin=name,
                    message='dependency cycle detected',
                )
                failed.add(name)
                return False
            if name not in self._plugins:
                self._record_event(
                    phase='dependency',
                    status='failed',
                    plugin=name,
                    message='plugin not loaded',
                )
                failed.add(name)
                return False

            visiting.add(name)
            for dependency in self._plugin_dependencies.get(name, []):
                if dependency not in self._plugins:
                    print(
                        f"Cannot initialize plugin '{name}': missing dependency '{dependency}'"
                    )
                    self._record_event(
                        phase='dependency',
                        status='failed',
                        plugin=name,
                        message=f"missing dependency '{dependency}'",
                    )
                    visiting.remove(name)
                    failed.add(name)
                    return False
                if not initialize_with_dependencies(dependency):
                    self._record_event(
                        phase='dependency',
                        status='failed',
                        plugin=name,
                        message=f"dependency '{dependency}' failed",
                    )
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

    def get_diagnostics_report(self) -> dict[str, Any]:
        loaded_plugins = sorted(self._plugins.keys())
        initialized_plugins = sorted(self._contexts.keys())
        return {
            'loaded_plugins': loaded_plugins,
            'loaded_plugins_count': len(loaded_plugins),
            'initialized_plugins': initialized_plugins,
            'initialized_plugins_count': len(initialized_plugins),
            'include_dev_tools': self._include_dev_tools,
            'enable_legacy_plugins': self._enable_legacy_plugins,
            'load_failures': list(self._load_failures),
            'load_failures_count': len(self._load_failures),
            'init_failures': list(self._init_failures),
            'init_failures_count': len(self._init_failures),
            'skipped_plugins': list(self._skipped_plugins),
            'skipped_plugins_count': len(self._skipped_plugins),
            'contract_warnings': list(self._contract_warnings),
            'contract_warnings_count': len(self._contract_warnings),
            'manifest_validation_failures': list(self._manifest_validation_failures),
            'manifest_validation_failures_count': len(self._manifest_validation_failures),
            'events': [asdict(event) for event in self._diagnostic_events],
        }

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

    # Public compatibility aliases for product language.
    def get_all_tools(self) -> Dict[str, Plugin]:
        return self.get_all_plugins()

    def get_enabled_tools(self) -> Dict[str, Plugin]:
        return self.get_enabled_plugins()

    def enable_plugin(self, name: str) -> bool:
        if name in self._plugins:
            self._plugins[name].enabled = True
            manifest = self._manifests.get(name)
            if manifest is not None:
                manifest.enabled = True
            return True
        return False

    def enable_tool(self, name: str) -> bool:
        return self.enable_plugin(name)

    def disable_plugin(self, name: str) -> bool:
        if name in self._plugins:
            self._plugins[name].enabled = False
            manifest = self._manifests.get(name)
            if manifest is not None:
                manifest.enabled = False
            return True
        return False

    def disable_tool(self, name: str) -> bool:
        return self.disable_plugin(name)


from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import PluginContract

@dataclass
class PluginRegistry:
    _plugins: dict[str, PluginContract] = field(default_factory=dict)

    def register(self, plugin: PluginContract) -> PluginContract:
        self._plugins[plugin.name] = plugin
        return plugin

    def list_plugins(self, *, enabled_only: bool = False) -> list[dict]:
        plugins = sorted(self._plugins.values(), key=lambda item: item.name)
        if enabled_only:
            plugins = [plugin for plugin in plugins if plugin.enabled]
        return [plugin.describe() for plugin in plugins]

    def enabled_plugins(self) -> list[PluginContract]:
        return [plugin for plugin in self._plugins.values() if plugin.enabled]

    def run_health_checks(self) -> list[dict]:
        results: list[dict] = []
        for plugin in self.enabled_plugins():
            if plugin.health_check is None:
                results.append({"name": plugin.name, "kind": plugin.kind, "status": "not_configured"})
                continue
            outcome = plugin.health_check()
            if isinstance(outcome, dict):
                payload = dict(outcome)
            else:
                payload = {"status": "ok" if outcome else "failed"}
            payload.setdefault("status", "ok")
            payload["name"] = plugin.name
            payload["kind"] = plugin.kind
            results.append(payload)
        return results

_DEFAULT_REGISTRY = PluginRegistry()

def get_registry() -> PluginRegistry:
    return _DEFAULT_REGISTRY

def register_plugin(plugin: PluginContract) -> PluginContract:
    return _DEFAULT_REGISTRY.register(plugin)

def list_registered_plugins(*, enabled_only: bool = False) -> list[dict]:
    return _DEFAULT_REGISTRY.list_plugins(enabled_only=enabled_only)

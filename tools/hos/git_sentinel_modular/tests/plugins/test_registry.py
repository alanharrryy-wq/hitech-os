from __future__ import annotations

from tools.hos.git_sentinel_modular.plugins import PluginContract, PluginRegistry

def test_registry_lists_health_checks():
    registry = PluginRegistry()
    registry.register(PluginContract(name="demo", kind="external", health_check=lambda: {"status": "ok"}))
    payload = registry.run_health_checks()
    assert payload == [{"name": "demo", "kind": "external", "status": "ok"}]

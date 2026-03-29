import importlib
import json
import os
from pathlib import Path
from unittest import TestCase

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_ROOT = PACKAGE_ROOT.parent
if str(PLUGINS_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PLUGINS_ROOT))

plugin_module = importlib.import_module("orchestrator_bridge.plugin")
plugin_package = importlib.import_module("orchestrator_bridge")


class PluginPackageIntegrationTests(TestCase):
    def test_manifest_contains_required_host_fields(self):
        manifest = plugin_module.load_plugin_manifest(str(PACKAGE_ROOT))
        for key in ("id", "name", "version", "description", "author", "enabled", "module", "class_name", "dependencies", "ui"):
            self.assertIn(key, manifest)
        self.assertEqual(manifest["module"], "plugin")
        self.assertEqual(manifest["class_name"], "PluginImplementation")

    def test_plugin_class_is_loadable_and_matches_package_export(self):
        cls = getattr(plugin_module, "PluginImplementation")
        package_cls = getattr(plugin_package, "PluginImplementation")
        self.assertIs(cls, package_cls)
        instance = cls()
        self.assertEqual(instance.plugin_id, "orchestrator_bridge")
        self.assertEqual(instance.version, "0.6.0")

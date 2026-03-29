import sys
from pathlib import Path
from unittest import TestCase

APP_HOST_ROOT = Path(__file__).resolve().parents[3]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

from app.gui_qt.preferences import PreferencesRuntime, RuntimePolicyApplicator


class _FakeSettings:
    def __init__(self, initial: dict[str, object] | None = None) -> None:
        self._data = dict(initial or {})

    def value(self, key, default_value=""):
        return self._data.get(key, default_value)

    def setValue(self, key, value) -> None:
        self._data[key] = value

    def remove(self, key) -> None:
        self._data.pop(key, None)


class _FakeWidget:
    def __init__(self) -> None:
        self.properties = {}

    def setProperty(self, key: str, value) -> None:
        self.properties[key] = value


class _FakeDock:
    def __init__(self) -> None:
        self.properties = {}
        self._widget = _FakeWidget()

    def setProperty(self, key: str, value) -> None:
        self.properties[key] = value

    def widget(self):
        return self._widget


class _FakeMainWindow:
    def __init__(self) -> None:
        self.properties = {}
        self._central = _FakeWidget()
        self.tools_launcher_dock = _FakeDock()
        self.results_dock = _FakeDock()

    def setProperty(self, key: str, value) -> None:
        self.properties[key] = value

    def centralWidget(self):
        return self._central


class PreferencesRuntimePolicyTests(TestCase):
    def test_preferences_runtime_normalizes_and_validates_persistence(self):
        settings = _FakeSettings(
            {
                "preferences/font_size": "30",
                "preferences/density": "invalid",
                "preferences/motion": "off",
                "preferences/performance": "performance",
            }
        )
        runtime = PreferencesRuntime(settings, default_skin_name="orange_ember")
        prefs = runtime.current
        self.assertEqual(prefs.font_size, 28)
        self.assertEqual(prefs.density, "comfortable")
        self.assertEqual(prefs.motion, "off")
        self.assertEqual(prefs.performance, "performance")
        self.assertEqual(runtime.validate_persistence_contract(), [])

        settings.setValue("preferences/schema_version", 999)
        issues = runtime.validate_persistence_contract()
        self.assertTrue(any("unsupported preferences schema version" in issue for issue in issues))

    def test_runtime_policy_applicator_handles_missing_surfaces_safely(self):
        settings = _FakeSettings()
        runtime = PreferencesRuntime(settings, default_skin_name="orange_ember")
        policy = runtime.runtime_policy()
        applicator = RuntimePolicyApplicator()
        main_window = _FakeMainWindow()
        report = applicator.apply(main_window, policy)

        self.assertTrue(report.applied_targets)
        self.assertIn("workspace_summary_dock", report.skipped_targets)
        self.assertEqual(report.failures, [])
        self.assertIn("runtimeTypographyScale", main_window.properties)
        self.assertIn("runtimeSpacingScale", main_window.properties)
        self.assertIn("runtimeMinReadableFontPt", main_window.properties)

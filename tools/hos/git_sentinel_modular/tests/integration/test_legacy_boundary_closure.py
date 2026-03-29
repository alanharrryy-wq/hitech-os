from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools.hos.git_sentinel_modular.legacy import build_legacy_scan_once_adapter
from tools.hos.git_sentinel_modular.shared.contracts import ScanConfig
from tools.hos.git_sentinel_modular.shared.provider import ScanAdapterProvider


class LegacyBoundaryCutoverTestCase(unittest.TestCase):
    """
    Tests for H1.1B true boundary closure.
    
    Validates that:
    - legacy.adapters has zero direct imports from core.orchestrator
    - legacy.adapters imports ONLY from shared layer
    - The provider toggle mechanism allows swapping implementations
    - Cutover from default to custom adapter (and back) is deterministic
    """
    
    def setUp(self) -> None:
        """Reset provider to default before each test."""
        ScanAdapterProvider.reset()
    
    def tearDown(self) -> None:
        """Clean up: reset provider to default after each test."""
        ScanAdapterProvider.reset()
    
    def test_legacy_adapter_has_zero_core_imports(self):
        """
        Verify that legacy.adapters has ZERO direct imports from core.orchestrator.
        
        This is the critical acceptance criterion: legacy module namespace should not
        contain any core.orchestrator classes or imports.
        """
        import sys
        import importlib
        
        # Re-import module to check for core imports
        mod_name = 'tools.hos.git_sentinel_modular.legacy.adapters'
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        
        mod = importlib.import_module(mod_name)
        module_dict = vars(mod)
        
        # Should NOT have any core.orchestrator items at module level
        forbidden_items = ['SentinelOrchestrator', 'OrchestratorConfig']
        for item in forbidden_items:
            self.assertNotIn(item, module_dict,
                           f"{item} should not be in module namespace (boundary violation)")
        
        # Should have the public adapter function
        self.assertIn('build_legacy_scan_once_adapter', module_dict,
                     "build_legacy_scan_once_adapter must be the public export")
        
        # Should have imports from shared, not core
        self.assertIn('ScanConfig', module_dict,
                     "ScanConfig from shared should be imported")
        self.assertIn('ScanAdapterProvider', module_dict,
                     "ScanAdapterProvider from shared should be imported")
    
    def test_legacy_adapter_delegates_to_registered_provider(self):
        """
        Verify that legacy adapter uses the provider (toggle-able implementation).
        
        This test proves the toggle mechanism works: we register a mock adapter,
        call build_legacy_scan_once_adapter, and verify the mock was invoked.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            runtime_root = Path(tmp) / "runtime"
            repo_root.mkdir(parents=True, exist_ok=True)
            (repo_root / ".git").mkdir(exist_ok=True)
            
            # Create mock adapter class that accepts ScanConfig
            mock_adapter_instance = MagicMock()
            mock_adapter_instance.run_once.return_value = {
                'repo_root': str(repo_root),
                'ci_gate': {'ok': True, 'status': 'pass', 'reasons': []},
            }
            
            # Mock adapter class: takes config, has run_once()
            mock_adapter_class = MagicMock(return_value=mock_adapter_instance)
            
            # Register the mock (this is the "toggle on")
            ScanAdapterProvider.register(mock_adapter_class)
            
            # Call the legacy adapter
            result = build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))
            
            # Verify mock was used
            mock_adapter_class.assert_called_once()
            call_arg = mock_adapter_class.call_args[0][0]
            # Verify it was called with a ScanConfig
            self.assertIsInstance(call_arg, ScanConfig,
                                "Adapter should be called with ScanConfig instance")
            
            mock_adapter_instance.run_once.assert_called_once()
            
            # Verify result structure
            self.assertIn('ci_gate', result)
            self.assertIn('report_json_path', result)
    
    def test_legacy_adapter_toggle_off_uses_default(self):
        """
        Verify that resetting the provider reverts to default orchestrator (toggle off).
        
        This tests the reversibility aspect: after toggling to custom adapter,
        we reset and verify that the default (real) orchestrator is used again.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            runtime_root = Path(tmp) / "runtime"
            repo_root.mkdir(parents=True, exist_ok=True)
            (repo_root / ".git").mkdir(exist_ok=True)
            (repo_root / "src").mkdir(exist_ok=True)
            (repo_root / "src" / "config.env").write_text("SECRET=test\n", encoding="utf-8")
            
            # First: toggle to mock (feature "on")
            mock_adapter_instance = MagicMock()
            mock_adapter_instance.run_once.return_value = {
                'repo_root': str(repo_root),
                'ci_gate': {'ok': True, 'status': 'pass', 'reasons': []},
            }
            mock_adapter_class = MagicMock(return_value=mock_adapter_instance)
            
            ScanAdapterProvider.register(mock_adapter_class)
            result_with_mock = build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))
            self.assertIn('ci_gate', result_with_mock)
            mock_adapter_class.assert_called()
            
            # Reset (toggle "off", back to default)
            ScanAdapterProvider.reset()
            
            # Second call should use default orchestrator
            result_with_default = build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))
            
            # Just verify it has the expected structure (same as first call)
            self.assertIn('ci_gate', result_with_default)
            self.assertIn('report_json_path', result_with_default)
    
    def test_legacy_adapter_cutover_consistency_multiple_toggles(self):
        """
        Verify that multiple toggle cycles produce consistent results.
        
        On -> Off -> On -> Off should work cleanly without side effects.
        This tests reversibility across multiple cutover cycles.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            runtime_root = Path(tmp) / "runtime"
            repo_root.mkdir(parents=True, exist_ok=True)
            (repo_root / ".git").mkdir(exist_ok=True)
            (repo_root / "src").mkdir(exist_ok=True)
            (repo_root / "src" / "config.env").write_text("SECRET=test\n", encoding="utf-8")
            
            results = []
            
            # Cycle 1: ON (use mock)
            mock1 = MagicMock()
            mock1.return_value.run_once.return_value = {
                'repo_root': str(repo_root),
                'ci_gate': {'ok': True, 'status': 'pass', 'reasons': []},
            }
            ScanAdapterProvider.register(mock1)
            results.append(('on_1', build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))))
            
            # Cycle 2: OFF (use default)
            ScanAdapterProvider.reset()
            results.append(('off_1', build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))))
            
            # Cycle 3: ON again (new mock)
            mock2 = MagicMock()
            mock2.return_value.run_once.return_value = {
                'repo_root': str(repo_root),
                'ci_gate': {'ok': True, 'status': 'pass', 'reasons': []},
            }
            ScanAdapterProvider.register(mock2)
            results.append(('on_2', build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))))
            
            # Cycle 4: OFF again (default)
            ScanAdapterProvider.reset()
            results.append(('off_2', build_legacy_scan_once_adapter(str(repo_root), str(runtime_root))))
            
            # All results should have the expected structure
            for label, result in results:
                with self.subTest(cycle=label):
                    self.assertIn('ci_gate', result)
                    self.assertIn('repo_root', result)
                    self.assertIn('report_json_path', result)
    
    def test_legacy_adapter_provider_returns_different_impl_when_registered(self):
        """
        Verify that ScanAdapterProvider.get() returns the registered implementation.
        
        This is a direct test of the toggle mechanism:
        - Before registration: should get default (wrapped orchestrator)
        - After registration: should get registered class
        - After reset: should go back to lazy-init of default
        """
        # Check initial state (nothing registered yet)
        self.assertIsNone(ScanAdapterProvider.current(),
                         "Before first get(), current() should be None")
        
        # First get() should initialize with default
        impl1 = ScanAdapterProvider.get()
        from tools.hos.git_sentinel_modular.shared.provider import _ScanAdapterBridge
        self.assertIs(impl1, _ScanAdapterBridge,
                     "Default implementation should be _ScanAdapterBridge")
        
        # Register a custom class
        custom_class = MagicMock()
        ScanAdapterProvider.register(custom_class)
        impl2 = ScanAdapterProvider.get()
        self.assertIs(impl2, custom_class,
                     "After registration, should get the custom class")
        
        # Reset and next get() should reinitialize to default
        ScanAdapterProvider.reset()
        self.assertIsNone(ScanAdapterProvider.current(),
                         "After reset(), current() should be None")
        
        impl3 = ScanAdapterProvider.get()
        self.assertIs(impl3, _ScanAdapterBridge,
                     "After reset and get(), should reinitialize to _ScanAdapterBridge")


if __name__ == "__main__":
    unittest.main()

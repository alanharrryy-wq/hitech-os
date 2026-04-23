from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from tests.helpers import project_root


def _load_installer_module():
    installer_path = project_root() / "installer" / "install_ar_k_integration.py"
    spec = importlib.util.spec_from_file_location("install_ar_k_integration", installer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load installer module from {installer_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class InstallerPayloadFilterTests(unittest.TestCase):
    def test_reports_real_is_excluded_from_payload(self) -> None:
        installer = _load_installer_module()
        self.assertFalse(installer.should_include_in_payload(Path("reports_real/registries/module_registry.json")))
        self.assertFalse(installer.should_include_in_payload(Path("reports/reports/execution_summary.json")))
        self.assertFalse(installer.should_include_in_payload(Path(".ark_install/last_apply.json")))
        self.assertFalse(installer.should_include_in_payload(Path("pya/__pycache__/engine.cpython-312.pyc")))
        self.assertTrue(installer.should_include_in_payload(Path("pya/engines/scanner/engine.py")))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


def test_runtime_core_initializes_without_legacy_state_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    try:
        from capatch_plugins import runtime_core

        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            runtime_core.initialize_plugin_runtime(base_dir)
            state = runtime_core.get_plugin_state()
            assert state['initialized'] is True
            assert state['plugins_dir'] == (base_dir / 'capatch_plugins').resolve()
            assert state['runtime_version'] == runtime_core.CAPATCH_PLUGIN_RUNTIME_VERSION

            source = (root / 'capatch_plugins' / 'runtime_core.py').read_text(encoding='utf-8')
            assert 'from capatch_legacy import CapatchError' not in source
            assert 'from capatch_legacy import SupportResolution' not in source
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass


def test_cli_consumers_point_to_runtime_core() -> None:
    root = Path(__file__).resolve().parents[1]
    main_text = (root / 'capatch_cli' / 'main.py').read_text(encoding='utf-8')
    commands_plugin_text = (root / 'capatch_cli' / 'commands_plugin.py').read_text(encoding='utf-8')
    commands_diagnostic_text = (root / 'capatch_cli' / 'commands_diagnostic.py').read_text(encoding='utf-8')
    diagnostics_runtime_text = (root / 'capatch_diagnostics' / 'runtime.py').read_text(encoding='utf-8')

    assert 'from capatch_plugins.runtime_core import initialize_plugin_runtime' in main_text
    assert 'from capatch_plugins.runtime_core import handle_plugin_cli_actions' in commands_plugin_text
    assert 'from capatch_diagnostics.runtime import run_diagnostic_command' in commands_diagnostic_text
    assert 'from diagnostic_runtime import run_diagnostic_command' not in commands_diagnostic_text
    assert 'plugin_state=get_plugin_state()' in commands_diagnostic_text
    assert 'core_confidence_engine' not in diagnostics_runtime_text
    assert 'core_decision_ledger' not in diagnostics_runtime_text
    assert 'core_intervention_gates' not in diagnostics_runtime_text


def test_runtime_core_fail_raises_canonical_capatch_error() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    try:
        from capatch_ops.base import CapatchError
        from capatch_plugins import runtime_core

        try:
            runtime_core.fail('boom')
        except CapatchError as exc:
            assert str(exc) == 'boom'
        else:
            raise AssertionError('runtime_core.fail debe usar CapatchError canónico')
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass

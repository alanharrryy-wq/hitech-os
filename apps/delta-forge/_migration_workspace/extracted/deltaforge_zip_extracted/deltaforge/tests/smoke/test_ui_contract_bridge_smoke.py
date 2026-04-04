from __future__ import annotations

import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
INTEROP_PATH = REPO_ROOT / 'ui/window/interop.py'
BOOTSTRAP_PATH = REPO_ROOT / 'bootstrap/app_bootstrap.py'
RESOLVER_BRIDGE_PATH = REPO_ROOT / 'bootstrap/resolver_bridge.py'
EVENT_WIRING_PATH = REPO_ROOT / 'bootstrap/event_wiring.py'

EXPECTED_ACTIONS = (
    'create_session',
    'close_session',
    'select_session',
    'browse_root_dir',
    'validate_active',
    'plan_active',
    'apply_active',
    'rollback_active',
    'refresh_active',
    'select_op',
    'select_target',
)

EXPECTED_PROJECTIONS = (
    'get_session_tabs_projection',
    'get_active_session_id',
    'get_command_bar_projection',
    'get_workspace_projection',
    'get_status_projection',
)



def test_interop_declares_exact_ui_controller_actions() -> None:
    source = INTEROP_PATH.read_text(encoding='utf-8')
    for needle in EXPECTED_ACTIONS:
        assert needle in source, f'missing controller action in interop bridge: {needle}'
    assert 'dispatch_ui_action' in source



def test_interop_declares_exact_projection_slots() -> None:
    source = INTEROP_PATH.read_text(encoding='utf-8')
    for needle in EXPECTED_PROJECTIONS:
        assert needle in source, f'missing projection contract in interop bridge: {needle}'



def test_bootstrap_accepts_factory_or_materialized_dependencies() -> None:
    bootstrap_source = BOOTSTRAP_PATH.read_text(encoding='utf-8')
    resolver_source = RESOLVER_BRIDGE_PATH.read_text(encoding='utf-8')
    event_source = EVENT_WIRING_PATH.read_text(encoding='utf-8')
    assert 'resolve_workspace_facade' in bootstrap_source
    assert 'resolve_command_controller' in bootstrap_source
    assert 'wire_optional_filesystem_bridge' in bootstrap_source
    assert 'create_workspace_facade' in resolver_source
    assert 'workspace_facade' in resolver_source
    assert 'create_command_controller' in resolver_source
    assert 'command_controller' in resolver_source
    assert 'bind_filesystem_changed' in event_source

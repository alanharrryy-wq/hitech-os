from __future__ import annotations

import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CANONICAL_FILES = {
    'bootstrap/app_bootstrap.py',
    'bootstrap/event_wiring.py',
    'bootstrap/resolver_bridge.py',
    'ui/theme/theme_api.py',
    'ui/window/interop.py',
    'ui/window/main_window.py',
    'ui/widgets/command_bar.py',
    'ui/widgets/session_tabs.py',
}



def _compile(path: pathlib.Path) -> None:
    source = path.read_text(encoding='utf-8')
    compile(source, str(path), 'exec')



def test_canonical_files_exist_and_compile() -> None:
    for relative in CANONICAL_FILES:
        path = REPO_ROOT / relative
        assert path.exists(), f'missing canonical file: {relative}'
        _compile(path)



def test_bootstrap_targets_canonical_main_window() -> None:
    bootstrap_path = REPO_ROOT / 'bootstrap/app_bootstrap.py'
    source = bootstrap_path.read_text(encoding='utf-8')
    assert 'ui.window.main_window' in source
    assert 'main_window_alt' not in source



def test_main_window_targets_canonical_widgets_and_bridge() -> None:
    main_window_path = REPO_ROOT / 'ui/window/main_window.py'
    source = main_window_path.read_text(encoding='utf-8')
    assert 'ui.widgets.command_bar' in source
    assert 'ui.widgets.session_tabs' in source
    assert 'ui.window.interop' in source
    assert 'ui.panes.command_bar' not in source
    assert 'ui.panes.session_tabs' not in source

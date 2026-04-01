from __future__ import annotations

import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCOPED_TREES = (
    REPO_ROOT / 'deltaforge' / 'ui',
    REPO_ROOT / 'deltaforge' / 'bootstrap',
)
OPTIONAL_LEGACY_SHIMS = {
    REPO_ROOT / 'deltaforge' / 'ui' / 'window' / 'main_window_alt.py': 'deltaforge.ui.window.main_window',
    REPO_ROOT / 'deltaforge' / 'ui' / 'panes' / 'command_bar.py': 'deltaforge.ui.widgets.command_bar',
    REPO_ROOT / 'deltaforge' / 'ui' / 'panes' / 'session_tabs.py': 'deltaforge.ui.widgets.session_tabs',
}
FORBIDDEN_IMPORT_NEEDLES = (
    'main_window_alt',
    'ui.panes.command_bar',
    'ui.panes.session_tabs',
)
SHIM_FORBIDDEN_NEEDLES = (
    'QMainWindow(',
    'QWidget(',
    'QSplitter(',
    'clicked.connect(',
    'itemSelectionChanged.connect(',
    'set_projection(',
)


def _iter_python_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for tree in SCOPED_TREES:
        if tree.exists():
            files.extend(sorted(tree.rglob('*.py')))
    return files


def test_no_forbidden_legacy_import_routes() -> None:
    for path in _iter_python_files():
        source = path.read_text(encoding='utf-8')
        for needle in FORBIDDEN_IMPORT_NEEDLES:
            assert needle not in source, f'legacy import route still active in {path}: {needle}'


def test_optional_legacy_files_are_shim_only() -> None:
    for path, target in OPTIONAL_LEGACY_SHIMS.items():
        if not path.exists():
            continue
        source = path.read_text(encoding='utf-8')
        assert target in source, f'legacy shim must re-export canonical target: {path}'
        for needle in SHIM_FORBIDDEN_NEEDLES:
            assert needle not in source, f'legacy shim contains active logic in {path}: {needle}'

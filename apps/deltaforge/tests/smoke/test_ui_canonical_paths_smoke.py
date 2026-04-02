from __future__ import annotations

import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCOPED_TREES = (
    REPO_ROOT / 'ui',
    REPO_ROOT / 'bootstrap',
)
OPTIONAL_LEGACY_SHIMS = {
    REPO_ROOT / 'ui' / 'window' / 'main_window_alt.py': 'ui.window.main_window',
    REPO_ROOT / 'ui' / 'panes' / 'command_bar.py': 'ui.widgets.command_bar',
    REPO_ROOT / 'ui' / 'panes' / 'session_tabs.py': 'ui.widgets.session_tabs',
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
ALL_SOURCE_TREES = (
    REPO_ROOT / 'application',
    REPO_ROOT / 'bootstrap',
    REPO_ROOT / 'domain',
    REPO_ROOT / 'infrastructure',
    REPO_ROOT / 'ui',
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


def test_source_tree_has_no_old_deltaforge_prefixed_imports() -> None:
    for tree in ALL_SOURCE_TREES:
        for path in sorted(tree.rglob('*.py')):
            source = path.read_text(encoding='utf-8')
            assert 'from deltaforge.' not in source, f'old import prefix found in {path}'
            assert 'import deltaforge.' not in source, f'old import prefix found in {path}'

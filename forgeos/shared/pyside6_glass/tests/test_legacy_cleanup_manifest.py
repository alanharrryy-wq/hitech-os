from pyside6_glass.legacy_cleanup import (
    LEGACY_DELETE_PATHS,
    LEGACY_REPLACE_PATHS,
    legacy_delete_paths,
    legacy_replace_paths,
    should_delete_path,
)


def test_cleanup_manifest_contains_expected_entries():
    assert 'shared/pyside6_glass/.pytest_cache' in LEGACY_DELETE_PATHS
    assert 'shared/pyside6_glass/backdrop.py' in LEGACY_REPLACE_PATHS
    assert legacy_delete_paths() == LEGACY_DELETE_PATHS
    assert legacy_replace_paths() == LEGACY_REPLACE_PATHS


def test_should_delete_path_normalizes_slashes():
    assert should_delete_path(r'shared\pyside6_glass\theme.py.bak_silver_case')
    assert not should_delete_path('shared/pyside6_glass/theme.py')

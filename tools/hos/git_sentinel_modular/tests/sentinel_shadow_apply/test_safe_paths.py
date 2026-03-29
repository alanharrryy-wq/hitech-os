from __future__ import annotations

import pytest

from tools.hos.git_sentinel_modular.sentinel_shadow_apply.safe_paths import assert_safe_relative_path, normalize_relpath

def test_safe_paths_reject_parent_escape():
    with pytest.raises(ValueError):
        assert_safe_relative_path("../bad.txt")

def test_normalize_relpath_rewrites_backslashes():
    assert normalize_relpath(r"a\b.txt") == "a/b.txt"

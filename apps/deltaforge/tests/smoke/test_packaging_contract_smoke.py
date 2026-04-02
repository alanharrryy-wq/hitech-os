from __future__ import annotations

import pathlib
import tomllib


APP_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYPROJECT_PATH = APP_ROOT / "pyproject.toml"


def test_flattened_layout_has_no_nested_source_package() -> None:
    assert not (APP_ROOT / "deltaforge").exists()


def test_pyproject_declares_explicit_flat_package_discovery() -> None:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    find = data["tool"]["setuptools"]["packages"]["find"]
    assert find["where"] == ["."]
    assert find["include"] == ["application*", "bootstrap*", "domain*", "infrastructure*", "ui*"]
    assert find["namespaces"] is False


def test_console_script_targets_runtime_bootstrap() -> None:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    scripts = data["project"]["scripts"]
    assert scripts["deltaforge"] == "bootstrap:run"

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

PACKAGE_NAME = "tools.hos.git_sentinel_modular"

def _repo_root_from_here() -> Path:
    current = Path(__file__).resolve()
    return current.parents[4]

def _ensure_namespace() -> None:
    repo_root = _repo_root_from_here()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    tools_dir = repo_root / "tools"
    hos_dir = tools_dir / "hos"
    package_dir = hos_dir / "git_sentinel_modular"

    namespaces = {
        "tools": tools_dir,
        "tools.hos": hos_dir,
        PACKAGE_NAME: package_dir,
    }

    for name, path in namespaces.items():
        module = sys.modules.get(name)
        if module is None:
            module = types.ModuleType(name)
            module.__path__ = [str(path)]
            sys.modules[name] = module
        elif not getattr(module, "__path__", None):
            module.__path__ = [str(path)]

    init_file = package_dir / "__init__.py"
    if init_file.exists():
        spec = importlib.util.spec_from_file_location(PACKAGE_NAME, init_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            module.__path__ = [str(package_dir)]
            sys.modules[PACKAGE_NAME] = module
            spec.loader.exec_module(module)

_ensure_namespace()

@pytest.fixture()
def sandbox_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    downloads_root = tmp_path / "downloads"
    runtime_root = tmp_path / "runtime"
    repo_root.mkdir(parents=True, exist_ok=True)
    downloads_root.mkdir(parents=True, exist_ok=True)
    runtime_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("GSM_REPO_ROOT", str(repo_root))
    monkeypatch.setenv("GSM_DOWNLOADS_ROOT", str(downloads_root))
    monkeypatch.setenv("GSM_RUNTIME_ROOT", str(runtime_root))
    return tmp_path

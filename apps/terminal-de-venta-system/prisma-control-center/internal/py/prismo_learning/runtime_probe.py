# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Runtime probes that do not mutate project state."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .paths import find_repo_root, control_center_py_root


def probe_runtime() -> dict[str, Any]:
    repo = find_repo_root()
    pyroot = control_center_py_root(repo) if repo else None
    panel = pyroot / "panel_3150.py" if pyroot else None
    bridge = pyroot / "prismo_ai_bridge.py" if pyroot else None
    return {
        "repo_detected": bool(repo),
        "control_center_py_detected": bool(pyroot),
        "panel_3150_detected": bool(panel and panel.exists()),
        "prismo_ai_bridge_detected": bool(bridge and bridge.exists()),
        "read_only": True,
        "mutation_allowed": False,
    }

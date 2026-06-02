# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Tool status detector for local PRISMO runtime."""
from __future__ import annotations
import shutil, sys
from pathlib import Path
from typing import Any
from .paths import find_repo_root, store_root


def tool_status(public: bool = False) -> dict[str, Any]:
    repo = find_repo_root()
    store = store_root()
    payload = {
        "ok": True,
        "read_only": True,
        "mutation_allowed": False,
        "tools": {
            "python": {"available": True, "version": sys.version.split()[0]},
            "git": {"available": bool(shutil.which("git"))},
            "node": {"available": bool(shutil.which("node"))},
            "pnpm": {"available": bool(shutil.which("pnpm"))},
        },
        "paths": {"repo_detected": bool(repo), "store_exists": store.exists()},
    }
    if not public:
        payload["paths"].update({"repo_root": str(repo) if repo else None, "store_root": str(store)})
    return payload

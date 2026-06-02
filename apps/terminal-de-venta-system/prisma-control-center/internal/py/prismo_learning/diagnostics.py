# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Diagnostics and degraded-state payloads."""
from __future__ import annotations
from typing import Any
from .constants import constant_snapshot
from .paths import find_repo_root, store_root
from .tools_status import tool_status


def diagnostic_snapshot(public: bool = False) -> dict[str, Any]:
    repo = find_repo_root()
    payload = {
        "ok": True,
        "engine": constant_snapshot(),
        "tool_status": tool_status(public=public),
        "read_only": True,
        "mutation_allowed": False,
    }
    if not public:
        payload["paths"] = {"repo_root": str(repo) if repo else None, "store_root": str(store_root())}
    return payload


def safe_error(code: str, message: str, recoverable: bool = True) -> dict[str, Any]:
    return {"ok": False, "status": "error", "error": {"code": code, "message": message, "recoverable": recoverable}, "read_only": True, "mutation_allowed": False}

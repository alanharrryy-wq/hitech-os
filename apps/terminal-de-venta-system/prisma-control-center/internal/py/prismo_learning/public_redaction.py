# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Public redaction helpers for PRISMO endpoints.

Local endpoints can expose sanitized source labels. Public endpoints must hide local paths,
raw snippets and host-specific filesystem details.
"""
from __future__ import annotations
from typing import Any
from .sanitize import shallow_public_copy, safe_source_label

PUBLIC_DROP_KEYS = {
    "source_path", "absolute_path", "raw_preview", "raw_text", "secret_preview",
    "local_roots", "repo_root", "store_root", "backup_path",
}


def redact_for_public(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: redact_for_public(v) for k, v in obj.items() if k not in PUBLIC_DROP_KEYS}
    if isinstance(obj, list):
        return [redact_for_public(v) for v in obj]
    if isinstance(obj, str):
        return safe_source_label(obj)
    return shallow_public_copy(obj)


def endpoint_payload(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    if public:
        return redact_for_public(payload)
    return payload

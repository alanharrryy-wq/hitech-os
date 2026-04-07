#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.dependency.blocker.template"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Template para bloquear cambios riesgosos sobre archivos de dependencias."
PLUGIN_MIN_RUNTIME = "3.0.0"

CRITICAL_FILES = {
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "package.json",
    "package-lock.json",
}

BLOCKED_OPERATION_TYPES = {
    "ReplaceExactMany",
    "ReplaceRegexMany",
    "DeleteRegexMany",
}


def register(api):
    api.register_guard(block_on_risky_dependency_change)


def plugin_self_test(api):
    return {"ok": True}


def block_on_risky_dependency_change(ctx, operations, preview_content_by_target):
    risky = []
    for operation in operations:
        spec = getattr(operation, "spec", None)
        op_type = str(getattr(spec, "type", "") or "")
        file_value = str(getattr(spec, "file", "") or "").replace("\\", "/")
        file_name = file_value.split("/")[-1].lower()
        if file_name in CRITICAL_FILES and op_type in BLOCKED_OPERATION_TYPES:
            risky.append(f"{op_type}:{file_value}")

    if risky:
        return {
            "allow": False,
            "reason": (
                "Template bloqueo cambios potencialmente riesgosos sobre dependencias. "
                "Personalizalo para correr validaciones reales antes de permitir la inyeccion."
            ),
            "warning": "Coincidencias: " + ", ".join(risky[:8]),
        }

    return {"allow": True}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.diff.budget.template"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Template para bloquear previews demasiado grandes o dispersos."
PLUGIN_MIN_RUNTIME = "3.0.0"

MAX_FILES = 6
MAX_TOTAL_CHARS = 12000


def register(api):
    api.register_guard(enforce_diff_budget)


def plugin_self_test(api):
    return {"ok": True}


def enforce_diff_budget(ctx, operations, preview_content_by_target):
    touched_files = len(preview_content_by_target)
    total_chars = sum(len(value) for value in preview_content_by_target.values())

    if touched_files > MAX_FILES:
        return {
            "allow": False,
            "reason": f"El preview toca {touched_files} archivos y el limite del template es {MAX_FILES}.",
        }

    if total_chars > MAX_TOTAL_CHARS:
        return {
            "allow": False,
            "reason": (
                f"El preview suma {total_chars} caracteres y el limite del template es {MAX_TOTAL_CHARS}."
            ),
        }

    return {"allow": True}

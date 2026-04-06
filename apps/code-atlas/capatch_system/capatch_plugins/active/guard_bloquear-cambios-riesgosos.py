#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Objetivo del plugin:
bloquear cambios riesgosos

Notas:
- Este archivo es compatible con capatch runtime v3.
- El plugin debe fallar con gracia; si algo truena, capatch sigue vivo.
- Ajusta plugin_self_test() para validar tu regla real.
"""

PLUGIN_ID = "guard.bloquear-cambios-riesgosos"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Plugin base-guard generado para capatch."
PLUGIN_MIN_RUNTIME = "3.0.0"

def register(api):
    api.register_guard(guard)
    api.register_before_apply(before_apply)
    api.register_after_apply(after_apply)


def plugin_self_test(api):
    return {
        "ok": True,
        "notes": [
            "Plugin compilado correctamente.",
            "TODO principal: bloquear cambios riesgosos",
        ],
    }


def guard(ctx, operations, preview_content_by_target):
    # TODO: si detectas una condicion de riesgo real, regresa:
    # return {"allow": False, "reason": "explica por que se bloquea"}
    return {"allow": True}


def before_apply(ctx, operations, preview_content_by_target):
    return None


def after_apply(ctx, operations, results):
    return None

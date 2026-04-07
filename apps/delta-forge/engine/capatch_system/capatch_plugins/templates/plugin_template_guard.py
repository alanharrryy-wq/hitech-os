#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.base.template"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Template base para un plugin tolerante a fallos."
PLUGIN_MIN_RUNTIME = "3.0.0"


def register(api):
    api.register_guard(guard)
    api.register_before_apply(before_apply)
    api.register_after_apply(after_apply)
    api.register_support_resolver(support_resolver)


def plugin_self_test(api):
    return {"ok": True}


def guard(ctx, operations, preview_content_by_target):
    return {"allow": True}


def before_apply(ctx, operations, preview_content_by_target):
    return None


def after_apply(ctx, operations, results):
    return None


def support_resolver(ctx, target, content, operation, field_name, field_value):
    return None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Redaccion pragmatica para secretos antes de escribir bundles."""

import re
from typing import Any

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)([^\s'\"`]+)"),
    re.compile(r"(?i)(token\s*[:=]\s*)([^\s'\"`]+)"),
    re.compile(r"(?i)(password\s*[:=]\s*)([^\s'\"`]+)"),
    re.compile(r"(?i)(secret\s*[:=]\s*)([^\s'\"`]+)"),
]


def redact_text(text: str) -> str:
    value = str(text)
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub(lambda match: match.group(1) + "***REDACTED***", value)
    return value


def redact_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): redact_mapping(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_mapping(item) for item in value]
    if isinstance(value, tuple):
        return [redact_mapping(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value

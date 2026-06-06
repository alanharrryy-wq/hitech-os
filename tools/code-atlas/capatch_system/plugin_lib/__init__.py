#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Helpers reutilizables para runtime diagnostico y plugins."""

from .fs_utils import (
    atomic_write_text,
    ensure_dir,
    list_files_limited,
    read_text_safe,
    safe_file_size,
)
from .log_utils import summarize_candidate_logs, tail_file_text, tail_text
from .redaction_utils import redact_mapping, redact_text

__all__ = [
    "atomic_write_text",
    "ensure_dir",
    "list_files_limited",
    "read_text_safe",
    "safe_file_size",
    "summarize_candidate_logs",
    "tail_file_text",
    "tail_text",
    "redact_mapping",
    "redact_text",
]

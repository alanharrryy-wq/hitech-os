from __future__ import annotations

import hashlib
import re
from typing import Any

_SECRET_KEY = re.compile(r"(?i)(token|secret|password|passwd|authorization|bearer|api[_-]?key|private[_-]?key|session)")
_EMAIL = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)


def redact_value(value: Any, *, key: str = "") -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if _SECRET_KEY.search(key) or _SECRET_KEY.search(text):
        return "<REDACTED_SECRET_LIKE_VALUE>"
    if _EMAIL.search(text):
        return "sha256:" + hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()[:20]
    return text[:180] + ("…" if len(text) > 180 else "")


__all__ = ["redact_value"]

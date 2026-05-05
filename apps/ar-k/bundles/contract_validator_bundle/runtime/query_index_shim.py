
from __future__ import annotations

from .canon import PORTABLE_INDEX_NAME, QUERY_INDEX_COMPAT_ALIAS


def normalize_index_name(name: str) -> str:
    if name == QUERY_INDEX_COMPAT_ALIAS:
        return PORTABLE_INDEX_NAME
    return name

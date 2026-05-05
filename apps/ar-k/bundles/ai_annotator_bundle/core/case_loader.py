
"""Load case modules from the Python-first corpora."""

from __future__ import annotations

import importlib
from typing import Iterable

from corpora.case_index import CASE_MODULES


def load_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for module_name in CASE_MODULES:
        module = importlib.import_module(module_name)
        cases.append(dict(module.CASE))
    return cases


def iter_cases() -> Iterable[dict[str, object]]:
    yield from load_cases()

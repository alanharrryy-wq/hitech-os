
"""Shared case models for corpora and example output generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AdvisoryCase:
    case_id: str
    family: str
    title: str
    target_module: str
    upstream_state: dict[str, Any]
    advisory_expectation: dict[str, Any]
    forbidden_actions: list[str]
    path_examples: list[str]
    notes: list[str]

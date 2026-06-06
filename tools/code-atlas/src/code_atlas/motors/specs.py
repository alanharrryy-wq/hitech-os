# CODE_ATLAS_MOTOR_HUB_MODULE_V01
"""Declarative contracts for Code Atlas Motor Hub entries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MotorSpec:
    """A runnable external motor exposed by the Motor Hub UI."""

    motor_id: str
    group: str
    label: str
    description: str
    root: str
    program: str
    args: tuple[str, ...] = ()

    @property
    def root_path(self) -> Path:
        return Path(self.root)

    def command_preview(self) -> str:
        parts = [self.program]
        parts.extend(self.args)
        return " ".join(_quote_for_preview(part) for part in parts)


def _quote_for_preview(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(ch.isspace() for ch in text) or '"' in text:
        return '"' + text.replace('"', '\"') + '"'
    return text

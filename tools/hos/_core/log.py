#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, TextIO

LEVELS: tuple[str, ...] = ("DEBUG", "INFO", "WARN", "ERROR")
LEVEL_MAP: dict[str, int] = {name: idx for idx, name in enumerate(LEVELS)}


def _timestamp(deterministic: bool = False) -> str:
    fixed = os.getenv("HOS_LOG_FIXED_TIMESTAMP")
    if deterministic and fixed:
        return fixed
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


@dataclass
class ToolLogger:
    name: str
    level: str = "INFO"
    deterministic_time: bool = False
    stream: TextIO = sys.stdout

    def enabled(self, level: str) -> bool:
        return LEVEL_MAP[level] >= LEVEL_MAP[self.level]

    def _emit(self, level: str, message: str, **fields: Any) -> None:
        if level not in LEVEL_MAP:
            raise ValueError(f"unsupported log level: {level}")
        if not self.enabled(level):
            return
        payload = {
            "ts": _timestamp(deterministic=self.deterministic_time),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        for key in sorted(fields):
            payload[key] = fields[key]
        self.stream.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        self.stream.flush()

    def debug(self, message: str, **fields: Any) -> None:
        self._emit("DEBUG", message, **fields)

    def info(self, message: str, **fields: Any) -> None:
        self._emit("INFO", message, **fields)

    def warn(self, message: str, **fields: Any) -> None:
        self._emit("WARN", message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit("ERROR", message, **fields)


def create_logger(name: str, level: str = "INFO", deterministic_time: bool = False) -> ToolLogger:
    normalized = level.upper()
    if normalized not in LEVEL_MAP:
        raise ValueError(f"invalid level: {level}")
    return ToolLogger(name=name, level=normalized, deterministic_time=deterministic_time)


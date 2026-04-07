from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True, init=False)
class OpsDocument:
    source_path: str
    loaded_at: datetime | None
    metadata: dict[str, Any]
    revision: int
    content_hash: str
    updated_at: datetime | None
    _text: str = field(repr=False)

    def __init__(
        self,
        text: str = "",
        source_path: str = "",
        loaded_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        revision: int = 0,
        content_hash: str = "",
        updated_at: datetime | None = None,
    ) -> None:
        self.source_path = str(source_path or "")
        self.loaded_at = loaded_at
        self.metadata = dict(metadata or {})
        self.revision = max(0, int(revision))
        self.updated_at = updated_at or loaded_at
        self._text = ""
        self.content_hash = ""

        self._assign_text(str(text or ""), bump_revision=False, timestamp=self.updated_at)
        if content_hash:
            self.content_hash = str(content_hash)
        if self._text and self.revision == 0:
            self.revision = 1

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._assign_text(str(value or ""), bump_revision=True, timestamp=datetime.utcnow())

    @property
    def content(self) -> str:
        return self._text

    @content.setter
    def content(self, value: str) -> None:
        self._assign_text(str(value or ""), bump_revision=True, timestamp=datetime.utcnow())

    @property
    def is_loaded(self) -> bool:
        return bool(self._text.strip())

    @property
    def has_source_path(self) -> bool:
        return bool(self.source_path.strip())

    @property
    def operation_count(self) -> int:
        return len(self.operation_items())

    @property
    def has_operations(self) -> bool:
        return self.operation_count > 0

    def set_text(
        self,
        value: str,
        *,
        bump_revision: bool = True,
        timestamp: datetime | None = None,
    ) -> None:
        self._assign_text(str(value or ""), bump_revision=bump_revision, timestamp=timestamp or datetime.utcnow())

    def replace_content(
        self,
        text: str,
        *,
        source_path: str | None = None,
        loaded_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if source_path is not None:
            self.source_path = str(source_path)
        if loaded_at is not None:
            self.loaded_at = loaded_at
        if metadata is not None:
            self.metadata = dict(metadata)
        self._assign_text(str(text or ""), bump_revision=True, timestamp=datetime.utcnow())

    def parsed_payload(self) -> dict[str, Any]:
        raw_text = self._text.strip()
        if not raw_text:
            return {}

        try:
            parsed: Any = json.loads(raw_text)
        except json.JSONDecodeError:
            return {}

        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"ops": parsed}
        return {"value": parsed}

    def operation_items(self) -> list[Any]:
        payload = self.parsed_payload()
        for key in ("ops", "operations", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return list(value)
        return []

    def summary_payload(self) -> dict[str, Any]:
        payload = self.parsed_payload()
        operation_items = self.operation_items()
        return {
            "source_path": self.source_path,
            "has_source_path": self.has_source_path,
            "is_loaded": self.is_loaded,
            "revision": self.revision,
            "content_hash": self.content_hash,
            "operation_count": len(operation_items),
            "has_operations": bool(operation_items),
            "payload_keys": sorted(payload.keys()),
        }

    def _assign_text(self, value: str, *, bump_revision: bool, timestamp: datetime | None) -> None:
        changed = value != self._text
        self._text = value
        self.content_hash = self._hash_text(value)

        if bump_revision and changed:
            self.revision += 1
            self.updated_at = timestamp or datetime.utcnow()
            return

        if self.updated_at is None and value:
            self.updated_at = timestamp or datetime.utcnow()

    @staticmethod
    def _hash_text(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

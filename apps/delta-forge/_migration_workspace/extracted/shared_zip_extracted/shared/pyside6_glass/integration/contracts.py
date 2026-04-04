from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


INTEGRATION_PROTOCOL_VERSION = "1.0"


class IntegrationValidationError(ValueError):
    """Raised when an inbound integration payload is malformed."""


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(k): v for k, v in value.items()}
    raise IntegrationValidationError("expected mapping payload")


def _non_empty(value: Any, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise IntegrationValidationError(f"{field_name} is required")
    return normalized


@dataclass(frozen=True, slots=True)
class IntegrationEnvelopeMeta:
    protocol_version: str = INTEGRATION_PROTOCOL_VERSION
    request_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    timestamp_utc: str = field(default_factory=_utc_iso)
    source: str = "integration"

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> IntegrationEnvelopeMeta:
        data = _mapping(payload)
        return cls(
            protocol_version=str(data.get("protocol_version") or INTEGRATION_PROTOCOL_VERSION),
            request_id=str(data.get("request_id") or str(uuid4())),
            correlation_id=str(data.get("correlation_id")) if data.get("correlation_id") else None,
            timestamp_utc=str(data.get("timestamp_utc") or _utc_iso()),
            source=str(data.get("source") or "integration"),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "protocol_version": self.protocol_version,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "timestamp_utc": self.timestamp_utc,
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class IntegrationClientContext:
    client_id: str = "local-client"
    session_id: str | None = None
    origin: str = "local"
    workspace_id: str | None = None
    device_hint: str | None = None
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> IntegrationClientContext:
        data = _mapping(payload)
        caps = data.get("capabilities") or ()
        if isinstance(caps, str):
            capabilities = (caps,)
        elif isinstance(caps, (list, tuple, set)):
            capabilities = tuple(str(item).strip() for item in caps if str(item).strip())
        else:
            capabilities = ()
        metadata_raw = data.get("metadata")
        metadata = _mapping(metadata_raw) if isinstance(metadata_raw, Mapping) else {}
        return cls(
            client_id=str(data.get("client_id") or "local-client"),
            session_id=str(data.get("session_id")) if data.get("session_id") else None,
            origin=str(data.get("origin") or "local"),
            workspace_id=str(data.get("workspace_id")) if data.get("workspace_id") else None,
            device_hint=str(data.get("device_hint")) if data.get("device_hint") else None,
            capabilities=capabilities,
            metadata=metadata,
        )

    def has_capabilities(self, required: tuple[str, ...]) -> bool:
        if not required:
            return True
        available = set(self.capabilities)
        return set(required).issubset(available)

    def to_payload(self) -> dict[str, Any]:
        return {
            "client_id": self.client_id,
            "session_id": self.session_id,
            "origin": self.origin,
            "workspace_id": self.workspace_id,
            "device_hint": self.device_hint,
            "capabilities": list(self.capabilities),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class IntegrationCommandEnvelope:
    command: str
    payload: dict[str, Any] = field(default_factory=dict)
    context: IntegrationClientContext = field(default_factory=IntegrationClientContext)
    meta: IntegrationEnvelopeMeta = field(default_factory=IntegrationEnvelopeMeta)
    idempotency_key: str | None = None
    expected_version: str | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> IntegrationCommandEnvelope:
        data = _mapping(payload)
        command = _non_empty(data.get("command") or data.get("action"), "command")
        command_payload = _mapping(data.get("payload"))
        return cls(
            command=command,
            payload=command_payload,
            context=IntegrationClientContext.from_payload(data.get("context")),
            meta=IntegrationEnvelopeMeta.from_payload(data.get("meta")),
            idempotency_key=str(data.get("idempotency_key")) if data.get("idempotency_key") else None,
            expected_version=str(data.get("expected_version")) if data.get("expected_version") else None,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": "command",
            "command": self.command,
            "payload": dict(self.payload),
            "context": self.context.to_payload(),
            "meta": self.meta.to_payload(),
            "idempotency_key": self.idempotency_key,
            "expected_version": self.expected_version,
        }


@dataclass(frozen=True, slots=True)
class IntegrationQueryEnvelope:
    query: str
    params: dict[str, Any] = field(default_factory=dict)
    context: IntegrationClientContext = field(default_factory=IntegrationClientContext)
    meta: IntegrationEnvelopeMeta = field(default_factory=IntegrationEnvelopeMeta)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> IntegrationQueryEnvelope:
        data = _mapping(payload)
        query = _non_empty(data.get("query"), "query")
        params = _mapping(data.get("params"))
        return cls(
            query=query,
            params=params,
            context=IntegrationClientContext.from_payload(data.get("context")),
            meta=IntegrationEnvelopeMeta.from_payload(data.get("meta")),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": "query",
            "query": self.query,
            "params": dict(self.params),
            "context": self.context.to_payload(),
            "meta": self.meta.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class IntegrationSnapshotRequest:
    snapshot_id: str = "workspace"
    selector: dict[str, Any] = field(default_factory=dict)
    context: IntegrationClientContext = field(default_factory=IntegrationClientContext)
    meta: IntegrationEnvelopeMeta = field(default_factory=IntegrationEnvelopeMeta)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> IntegrationSnapshotRequest:
        data = _mapping(payload)
        snapshot_id = str(data.get("snapshot_id") or "workspace").strip() or "workspace"
        selector = _mapping(data.get("selector"))
        return cls(
            snapshot_id=snapshot_id,
            selector=selector,
            context=IntegrationClientContext.from_payload(data.get("context")),
            meta=IntegrationEnvelopeMeta.from_payload(data.get("meta")),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": "snapshot_request",
            "snapshot_id": self.snapshot_id,
            "selector": dict(self.selector),
            "context": self.context.to_payload(),
            "meta": self.meta.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class IntegrationError:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False
    status_code: int = 400

    def to_payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": dict(self.details),
            "retryable": self.retryable,
            "status_code": int(self.status_code),
        }


@dataclass(frozen=True, slots=True)
class IntegrationResponse:
    ok: bool
    kind: str
    data: dict[str, Any] = field(default_factory=dict)
    error: IntegrationError | None = None
    meta: IntegrationEnvelopeMeta = field(default_factory=IntegrationEnvelopeMeta)

    @classmethod
    def success(
        cls,
        kind: str,
        data: Mapping[str, Any] | None = None,
        *,
        meta: IntegrationEnvelopeMeta | None = None,
    ) -> IntegrationResponse:
        return cls(
            ok=True,
            kind=str(kind or "result"),
            data=_mapping(data),
            error=None,
            meta=meta or IntegrationEnvelopeMeta(),
        )

    @classmethod
    def failure(
        cls,
        kind: str,
        error: IntegrationError,
        *,
        meta: IntegrationEnvelopeMeta | None = None,
    ) -> IntegrationResponse:
        return cls(
            ok=False,
            kind=str(kind or "error"),
            data={},
            error=error,
            meta=meta or IntegrationEnvelopeMeta(),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "kind": self.kind,
            "data": dict(self.data),
            "error": self.error.to_payload() if self.error else None,
            "meta": self.meta.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class IntegrationEvent:
    sequence: int
    event: str
    topic: str
    payload: dict[str, Any] = field(default_factory=dict)
    context: IntegrationClientContext = field(default_factory=IntegrationClientContext)
    meta: IntegrationEnvelopeMeta = field(default_factory=IntegrationEnvelopeMeta)

    def to_payload(self) -> dict[str, Any]:
        return {
            "sequence": int(self.sequence),
            "event": self.event,
            "topic": self.topic,
            "payload": dict(self.payload),
            "context": self.context.to_payload(),
            "meta": self.meta.to_payload(),
        }


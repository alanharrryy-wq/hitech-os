from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable, Mapping

from .contracts import (
    INTEGRATION_PROTOCOL_VERSION,
    IntegrationClientContext,
    IntegrationCommandEnvelope,
    IntegrationEnvelopeMeta,
    IntegrationError,
    IntegrationEvent,
    IntegrationQueryEnvelope,
    IntegrationResponse,
    IntegrationSnapshotRequest,
    IntegrationValidationError,
)


IntegrationCommandHandler = Callable[[IntegrationCommandEnvelope], Mapping[str, Any] | Any]
IntegrationQueryHandler = Callable[[IntegrationQueryEnvelope], Mapping[str, Any] | Any]
IntegrationSnapshotProvider = Callable[[IntegrationSnapshotRequest], Mapping[str, Any] | Any]
IntegrationEventSubscriber = Callable[[IntegrationEvent], None]
IntegrationLogger = Callable[[str], None]
IntegrationAccessHook = Callable[
    [IntegrationClientContext, str, str, tuple[str, ...], str],
    bool,
]
IntegrationVersionHook = Callable[[IntegrationCommandEnvelope], str | None]


@dataclass(frozen=True, slots=True)
class IntegrationEndpointSpec:
    endpoint: str
    endpoint_kind: str  # command | query | snapshot
    access_mode: str  # read | write
    required_capabilities: tuple[str, ...]
    description: str
    stable: bool = True


class IntegrationService:
    """
    Neutral ingress/egress service boundary.

    External clients call commands/queries/snapshots against this service.
    Transport adapters should only forward payloads to this service.
    """

    def __init__(
        self,
        *,
        debug: bool = False,
        logger: IntegrationLogger | None = None,
        max_events: int = 500,
        access_hook: IntegrationAccessHook | None = None,
        supported_protocol_versions: tuple[str, ...] = (INTEGRATION_PROTOCOL_VERSION,),
        idempotency_cache_size: int = 256,
        version_hook: IntegrationVersionHook | None = None,
    ) -> None:
        self._commands: dict[str, tuple[IntegrationEndpointSpec, IntegrationCommandHandler]] = {}
        self._queries: dict[str, tuple[IntegrationEndpointSpec, IntegrationQueryHandler]] = {}
        self._snapshots: dict[str, tuple[IntegrationEndpointSpec, IntegrationSnapshotProvider]] = {}
        self._events: deque[IntegrationEvent] = deque(maxlen=max(32, int(max_events)))
        self._event_sequence = 0
        self._subscribers: dict[int, IntegrationEventSubscriber] = {}
        self._subscriber_sequence = 0
        self._debug = bool(debug)
        self._logger = logger
        self._access_hook = access_hook
        self._supported_protocol_versions = tuple(
            str(item).strip() for item in supported_protocol_versions if str(item).strip()
        ) or (INTEGRATION_PROTOCOL_VERSION,)
        self._idempotency_cache_size = max(32, int(idempotency_cache_size))
        self._idempotency_order: deque[str] = deque(maxlen=self._idempotency_cache_size)
        self._idempotency_results: dict[str, IntegrationResponse] = {}
        self._version_hook = version_hook
        self._lock = RLock()

    def register_command(
        self,
        command: str,
        handler: IntegrationCommandHandler,
        *,
        access_mode: str = "write",
        required_capabilities: tuple[str, ...] = (),
        description: str = "",
        stable: bool = True,
        override: bool = False,
    ) -> None:
        name = self._normalize_name(command, "command")
        if not callable(handler):
            raise ValueError("command handler must be callable")
        with self._lock:
            if not override and name in self._commands:
                raise ValueError(f"command '{name}' is already registered")
            spec = IntegrationEndpointSpec(
                endpoint=name,
                endpoint_kind="command",
                access_mode=self._normalize_access_mode(access_mode),
                required_capabilities=tuple(required_capabilities),
                description=description,
                stable=bool(stable),
            )
            self._commands[name] = (spec, handler)

    def register_query(
        self,
        query: str,
        handler: IntegrationQueryHandler,
        *,
        access_mode: str = "read",
        required_capabilities: tuple[str, ...] = (),
        description: str = "",
        stable: bool = True,
        override: bool = False,
    ) -> None:
        name = self._normalize_name(query, "query")
        if not callable(handler):
            raise ValueError("query handler must be callable")
        with self._lock:
            if not override and name in self._queries:
                raise ValueError(f"query '{name}' is already registered")
            spec = IntegrationEndpointSpec(
                endpoint=name,
                endpoint_kind="query",
                access_mode=self._normalize_access_mode(access_mode),
                required_capabilities=tuple(required_capabilities),
                description=description,
                stable=bool(stable),
            )
            self._queries[name] = (spec, handler)

    def register_snapshot_provider(
        self,
        snapshot_id: str,
        provider: IntegrationSnapshotProvider,
        *,
        access_mode: str = "read",
        required_capabilities: tuple[str, ...] = (),
        description: str = "",
        stable: bool = True,
        override: bool = False,
    ) -> None:
        name = self._normalize_name(snapshot_id, "snapshot_id")
        if not callable(provider):
            raise ValueError("snapshot provider must be callable")
        with self._lock:
            if not override and name in self._snapshots:
                raise ValueError(f"snapshot '{name}' is already registered")
            spec = IntegrationEndpointSpec(
                endpoint=name,
                endpoint_kind="snapshot",
                access_mode=self._normalize_access_mode(access_mode),
                required_capabilities=tuple(required_capabilities),
                description=description,
                stable=bool(stable),
            )
            self._snapshots[name] = (spec, provider)

    def list_endpoints(self) -> dict[str, list[dict[str, Any]]]:
        with self._lock:
            return {
                "commands": [self._spec_payload(spec) for spec, _ in self._commands.values()],
                "queries": [self._spec_payload(spec) for spec, _ in self._queries.values()],
                "snapshots": [self._spec_payload(spec) for spec, _ in self._snapshots.values()],
            }

    def dispatch_command(self, payload: IntegrationCommandEnvelope | Mapping[str, Any]) -> IntegrationResponse:
        envelope = payload if isinstance(payload, IntegrationCommandEnvelope) else IntegrationCommandEnvelope.from_payload(payload)
        protocol_error = self._validate_protocol_version(envelope.meta)
        if protocol_error is not None:
            return protocol_error

        cache_key = self._idempotency_key_for_command(envelope)
        if cache_key:
            cached = self._idempotency_results.get(cache_key)
            if cached is not None:
                self.emit_event(
                    "integration.command.deduplicated",
                    {"command": envelope.command, "idempotency_key": envelope.idempotency_key},
                    context=envelope.context,
                    correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
                )
                return cached

        endpoint = self._commands.get(envelope.command)
        if endpoint is None:
            return self._failure(
                "command_result",
                "unknown_command",
                f"unknown command '{envelope.command}'",
                status_code=404,
                meta=envelope.meta,
            )
        spec, handler = endpoint
        denial = self._check_access(spec, envelope.context)
        if denial is not None:
            return self._failure(
                "command_result",
                "permission_denied",
                denial,
                status_code=403,
                meta=envelope.meta,
            )
        version_error = self._check_expected_version(envelope)
        if version_error is not None:
            return version_error

        self._log(
            f"integration.command command={spec.endpoint} request_id={envelope.meta.request_id} "
            f"correlation_id={envelope.meta.correlation_id or '-'}"
        )
        try:
            outcome = self._mapping_or_value(handler(envelope))
        except IntegrationValidationError as exc:
            response = self._failure(
                "command_result",
                "validation_error",
                str(exc),
                status_code=422,
                meta=envelope.meta,
            )
            self.emit_event(
                "integration.command.failed",
                {
                    "command": spec.endpoint,
                    "error_code": "validation_error",
                    "message": str(exc),
                },
                context=envelope.context,
                correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
            )
            return response
        except Exception as exc:  # noqa: BLE001
            response = self._failure(
                "command_result",
                "internal_error",
                str(exc),
                status_code=500,
                meta=envelope.meta,
            )
            self.emit_event(
                "integration.command.failed",
                {
                    "command": spec.endpoint,
                    "error_code": "internal_error",
                    "message": str(exc),
                },
                context=envelope.context,
                correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
            )
            return response

        response = IntegrationResponse.success("command_result", outcome, meta=envelope.meta)
        if cache_key:
            self._remember_idempotency(cache_key, response)
        self.emit_event(
            "integration.command.completed",
            {"command": spec.endpoint, "result": outcome},
            context=envelope.context,
            correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
        )
        return response

    def dispatch_query(self, payload: IntegrationQueryEnvelope | Mapping[str, Any]) -> IntegrationResponse:
        envelope = payload if isinstance(payload, IntegrationQueryEnvelope) else IntegrationQueryEnvelope.from_payload(payload)
        protocol_error = self._validate_protocol_version(envelope.meta)
        if protocol_error is not None:
            return protocol_error
        endpoint = self._queries.get(envelope.query)
        if endpoint is None:
            return self._failure(
                "query_result",
                "unknown_query",
                f"unknown query '{envelope.query}'",
                status_code=404,
                meta=envelope.meta,
            )
        spec, handler = endpoint
        denial = self._check_access(spec, envelope.context)
        if denial is not None:
            return self._failure(
                "query_result",
                "permission_denied",
                denial,
                status_code=403,
                meta=envelope.meta,
            )

        self._log(
            f"integration.query query={spec.endpoint} request_id={envelope.meta.request_id} "
            f"correlation_id={envelope.meta.correlation_id or '-'}"
        )
        try:
            data = self._mapping_or_value(handler(envelope))
        except IntegrationValidationError as exc:
            return self._failure(
                "query_result",
                "validation_error",
                str(exc),
                status_code=422,
                meta=envelope.meta,
            )
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                "query_result",
                "internal_error",
                str(exc),
                status_code=500,
                meta=envelope.meta,
            )

        self.emit_event(
            "integration.query.completed",
            {"query": spec.endpoint},
            context=envelope.context,
            correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
        )
        return IntegrationResponse.success("query_result", data, meta=envelope.meta)

    def dispatch_snapshot(
        self,
        payload: IntegrationSnapshotRequest | Mapping[str, Any] | None = None,
    ) -> IntegrationResponse:
        envelope = (
            payload
            if isinstance(payload, IntegrationSnapshotRequest)
            else IntegrationSnapshotRequest.from_payload(payload)
        )
        protocol_error = self._validate_protocol_version(envelope.meta)
        if protocol_error is not None:
            return protocol_error
        snapshot_id = self._normalize_name(envelope.snapshot_id, "snapshot_id")
        endpoint = self._snapshots.get(snapshot_id)
        if endpoint is None:
            return self._failure(
                "snapshot_result",
                "unknown_snapshot",
                f"unknown snapshot '{snapshot_id}'",
                status_code=404,
                meta=envelope.meta,
            )
        spec, provider = endpoint
        denial = self._check_access(spec, envelope.context)
        if denial is not None:
            return self._failure(
                "snapshot_result",
                "permission_denied",
                denial,
                status_code=403,
                meta=envelope.meta,
            )

        self._log(
            f"integration.snapshot snapshot_id={snapshot_id} request_id={envelope.meta.request_id} "
            f"correlation_id={envelope.meta.correlation_id or '-'}"
        )
        try:
            data = self._mapping_or_value(provider(envelope))
        except IntegrationValidationError as exc:
            return self._failure(
                "snapshot_result",
                "validation_error",
                str(exc),
                status_code=422,
                meta=envelope.meta,
            )
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                "snapshot_result",
                "internal_error",
                str(exc),
                status_code=500,
                meta=envelope.meta,
            )

        self.emit_event(
            "integration.snapshot.provided",
            {"snapshot_id": snapshot_id},
            context=envelope.context,
            correlation_id=envelope.meta.correlation_id or envelope.meta.request_id,
        )
        return IntegrationResponse.success("snapshot_result", data, meta=envelope.meta)

    def emit_event(
        self,
        event: str,
        payload: Mapping[str, Any] | None = None,
        *,
        topic: str = "integration",
        context: IntegrationClientContext | None = None,
        correlation_id: str | None = None,
        source: str = "integration.service",
    ) -> IntegrationEvent:
        name = self._normalize_name(event, "event")
        with self._lock:
            self._event_sequence += 1
            entry = IntegrationEvent(
                sequence=self._event_sequence,
                event=name,
                topic=str(topic or "integration"),
                payload=self._mapping_or_value(payload),
                context=context or IntegrationClientContext(),
                meta=IntegrationEnvelopeMeta(correlation_id=correlation_id, source=source),
            )
            self._events.append(entry)
            subscribers = list(self._subscribers.values())

        for callback in subscribers:
            try:
                callback(entry)
            except Exception:  # noqa: BLE001
                continue
        return entry

    def subscribe(self, callback: IntegrationEventSubscriber) -> int:
        if not callable(callback):
            raise ValueError("subscriber callback must be callable")
        with self._lock:
            self._subscriber_sequence += 1
            token = self._subscriber_sequence
            self._subscribers[token] = callback
            return token

    def unsubscribe(self, token: int) -> None:
        with self._lock:
            self._subscribers.pop(int(token), None)

    def poll_events(self, *, since_sequence: int | None = None, limit: int = 100) -> list[IntegrationEvent]:
        size = max(1, min(500, int(limit)))
        with self._lock:
            events = list(self._events)
        if since_sequence is not None:
            events = [event for event in events if event.sequence > int(since_sequence)]
        if len(events) > size:
            events = events[-size:]
        return events

    def last_event_sequence(self) -> int:
        with self._lock:
            return int(self._event_sequence)

    def diagnostics_payload(self) -> dict[str, Any]:
        with self._lock:
            return {
                "commands": len(self._commands),
                "queries": len(self._queries),
                "snapshots": len(self._snapshots),
                "subscribers": len(self._subscribers),
                "event_backlog": len(self._events),
                "last_event_sequence": self._event_sequence,
                "supported_protocol_versions": list(self._supported_protocol_versions),
                "idempotency_cache_size": self._idempotency_cache_size,
                "idempotency_entries": len(self._idempotency_results),
            }

    def _check_access(self, spec: IntegrationEndpointSpec, context: IntegrationClientContext) -> str | None:
        if not context.has_capabilities(spec.required_capabilities):
            required = ", ".join(spec.required_capabilities)
            return f"missing required capabilities for '{spec.endpoint}': {required}"
        if self._access_hook is None:
            return None
        try:
            allowed = self._access_hook(
                context,
                spec.endpoint_kind,
                spec.endpoint,
                spec.required_capabilities,
                spec.access_mode,
            )
        except Exception as exc:  # noqa: BLE001
            return f"access hook failed: {exc}"
        if not bool(allowed):
            return f"access denied for '{spec.endpoint}'"
        return None

    def _spec_payload(self, spec: IntegrationEndpointSpec) -> dict[str, Any]:
        return {
            "endpoint": spec.endpoint,
            "endpoint_kind": spec.endpoint_kind,
            "access_mode": spec.access_mode,
            "required_capabilities": list(spec.required_capabilities),
            "description": spec.description,
            "stable": spec.stable,
        }

    def _failure(
        self,
        kind: str,
        code: str,
        message: str,
        *,
        status_code: int,
        meta: IntegrationEnvelopeMeta,
    ) -> IntegrationResponse:
        return IntegrationResponse.failure(
            kind,
            IntegrationError(
                code=str(code),
                message=str(message),
                status_code=int(status_code),
                retryable=False,
            ),
            meta=meta,
        )

    def _log(self, message: str) -> None:
        if self._logger is not None:
            self._logger(message)
            return
        if self._debug:
            print(message)

    def _normalize_access_mode(self, value: str) -> str:
        normalized = str(value or "read").strip().lower()
        if normalized not in {"read", "write"}:
            raise ValueError("access_mode must be 'read' or 'write'")
        return normalized

    def _normalize_name(self, value: str, field_name: str) -> str:
        normalized = str(value or "").strip().lower()
        if not normalized:
            raise ValueError(f"{field_name} is required")
        return normalized

    def _mapping_or_value(self, value: Mapping[str, Any] | Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, Mapping):
            return {str(k): v for k, v in value.items()}
        return {"value": value}

    def _validate_protocol_version(self, meta: IntegrationEnvelopeMeta) -> IntegrationResponse | None:
        protocol = str(meta.protocol_version or "").strip() or INTEGRATION_PROTOCOL_VERSION
        if protocol in self._supported_protocol_versions:
            return None
        return self._failure(
            "error",
            "unsupported_protocol_version",
            f"unsupported protocol version '{protocol}'",
            status_code=400,
            meta=meta,
        )

    def _idempotency_key_for_command(self, envelope: IntegrationCommandEnvelope) -> str | None:
        key = str(envelope.idempotency_key or "").strip()
        if not key:
            return None
        client = str(envelope.context.client_id or "anonymous").strip().lower()
        return f"{client}:{envelope.command}:{key}"

    def _remember_idempotency(self, cache_key: str, response: IntegrationResponse) -> None:
        if cache_key in self._idempotency_results:
            self._idempotency_results[cache_key] = response
            return
        if len(self._idempotency_order) >= self._idempotency_cache_size:
            oldest = self._idempotency_order.popleft()
            self._idempotency_results.pop(oldest, None)
        self._idempotency_order.append(cache_key)
        self._idempotency_results[cache_key] = response

    def _check_expected_version(self, envelope: IntegrationCommandEnvelope) -> IntegrationResponse | None:
        expected = str(envelope.expected_version or "").strip()
        if not expected:
            return None
        if self._version_hook is None:
            return None
        try:
            current = self._version_hook(envelope)
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                "command_result",
                "version_resolution_failed",
                f"version resolution failed: {exc}",
                status_code=500,
                meta=envelope.meta,
            )
        current_value = str(current or "").strip()
        if not current_value:
            return None
        if current_value == expected:
            return None
        return self._failure(
            "command_result",
            "version_conflict",
            f"expected_version '{expected}' does not match current version '{current_value}'",
            status_code=409,
            meta=envelope.meta,
        )

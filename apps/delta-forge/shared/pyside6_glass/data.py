from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from time import perf_counter
from typing import Any, Callable, Mapping, Protocol

class DataState:
    LOADING = "loading"
    READY = "ready"
    EMPTY = "empty"
    ERROR = "error"
    STALE = "stale"
    ALL: tuple[str, ...] = (LOADING, READY, EMPTY, ERROR, STALE)
    TERMINAL: tuple[str, ...] = (READY, EMPTY, ERROR, STALE)

    @classmethod
    def normalize(cls, value: str | None, *, default: str = READY) -> str:
        normalized = str(value or "").strip().lower()
        if normalized in cls.ALL:
            return normalized
        return default


DATA_STATES: tuple[str, ...] = DataState.ALL


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(k): v for k, v in value.items()}
    raise ValueError("expected mapping payload")


def _as_list_of_mapping(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError("expected list payload")
    output: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            output.append({str(k): v for k, v in item.items()})
        else:
            output.append({"value": item})
    return output


@dataclass(frozen=True, slots=True)
class RefreshPolicy:
    mode: str = "manual"  # manual | polling
    interval_ms: int = 10000
    stale_after_ms: int = 45000
    allow_manual_refresh: bool = True
    max_retries: int = 0
    jitter_ms: int = 0

    def normalized(self) -> RefreshPolicy:
        mode = str(self.mode or "manual").strip().lower()
        if mode not in {"manual", "polling"}:
            mode = "manual"
        return RefreshPolicy(
            mode=mode,
            interval_ms=max(250, int(self.interval_ms)),
            stale_after_ms=max(500, int(self.stale_after_ms)),
            allow_manual_refresh=bool(self.allow_manual_refresh),
            max_retries=max(0, int(self.max_retries)),
            jitter_ms=max(0, int(self.jitter_ms)),
        )

    def to_payload(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "mode": normalized.mode,
            "interval_ms": normalized.interval_ms,
            "stale_after_ms": normalized.stale_after_ms,
            "allow_manual_refresh": normalized.allow_manual_refresh,
            "max_retries": normalized.max_retries,
            "jitter_ms": normalized.jitter_ms,
        }


@dataclass(frozen=True, slots=True)
class DataQuery:
    provider_id: str
    query_id: str = "default"
    params: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    requested_at_utc: str = field(default_factory=_utc_iso)

    @classmethod
    def create(
        cls,
        provider_id: str,
        *,
        query_id: str = "default",
        params: Mapping[str, Any] | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> DataQuery:
        normalized_provider = str(provider_id or "").strip().lower()
        if not normalized_provider:
            raise ValueError("provider_id is required")
        normalized_query = str(query_id or "default").strip().lower() or "default"
        return cls(
            provider_id=normalized_provider,
            query_id=normalized_query,
            params=_as_mapping(params),
            context=_as_mapping(context),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "query_id": self.query_id,
            "params": dict(self.params),
            "context": dict(self.context),
            "requested_at_utc": self.requested_at_utc,
        }


@dataclass(frozen=True, slots=True)
class DataError:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": dict(self.details),
            "retryable": bool(self.retryable),
        }


@dataclass(frozen=True, slots=True)
class DataProviderMeta:
    provider_id: str
    title: str
    description: str = ""
    tags: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    requirements: tuple[str, ...] = ()
    status: str = "stable"
    supports_polling: bool = False
    source_kind: str = "in_memory"
    version: str = "1.0"

    def normalized(self) -> DataProviderMeta:
        provider_id = str(self.provider_id or "").strip().lower()
        if not provider_id:
            raise ValueError("provider_id is required")
        title = str(self.title or "").strip()
        if not title:
            raise ValueError("title is required")
        return DataProviderMeta(
            provider_id=provider_id,
            title=title,
            description=str(self.description or ""),
            tags=tuple(str(item).strip() for item in self.tags if str(item).strip()),
            keywords=tuple(str(item).strip() for item in self.keywords if str(item).strip()),
            capabilities=tuple(str(item).strip() for item in self.capabilities if str(item).strip()),
            requirements=tuple(str(item).strip() for item in self.requirements if str(item).strip()),
            status=str(self.status or "stable").strip().lower() or "stable",
            supports_polling=bool(self.supports_polling),
            source_kind=str(self.source_kind or "in_memory").strip().lower() or "in_memory",
            version=str(self.version or "1.0").strip() or "1.0",
        )

    def to_payload(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "provider_id": normalized.provider_id,
            "title": normalized.title,
            "description": normalized.description,
            "tags": list(normalized.tags),
            "keywords": list(normalized.keywords),
            "capabilities": list(normalized.capabilities),
            "requirements": list(normalized.requirements),
            "status": normalized.status,
            "supports_polling": normalized.supports_polling,
            "source_kind": normalized.source_kind,
            "version": normalized.version,
        }


@dataclass(frozen=True, slots=True)
class DataResult:
    provider_id: str
    query_id: str
    state: str
    summary: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    rows: list[dict[str, Any]] = field(default_factory=list)
    feed: list[dict[str, Any]] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    refresh_policy: RefreshPolicy = field(default_factory=RefreshPolicy)
    error: DataError | None = None
    refreshed_at_utc: str = field(default_factory=_utc_iso)
    latency_ms: float | None = None

    def normalized_state(self) -> str:
        return DataState.normalize(self.state)

    def is_stale(self) -> bool:
        if self.normalized_state() == DataState.STALE:
            return True
        if not self.refreshed_at_utc:
            return False
        try:
            refreshed = datetime.fromisoformat(self.refreshed_at_utc.replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            return False
        age_ms = (datetime.now(timezone.utc) - refreshed.astimezone(timezone.utc)).total_seconds() * 1000.0
        return age_ms >= float(self.refresh_policy.normalized().stale_after_ms)

    def with_state(self, state: str) -> DataResult:
        return DataResult(
            provider_id=self.provider_id,
            query_id=self.query_id,
            state=state,
            summary=dict(self.summary),
            metrics=dict(self.metrics),
            rows=list(self.rows),
            feed=list(self.feed),
            payload=dict(self.payload),
            diagnostics=dict(self.diagnostics),
            refresh_policy=self.refresh_policy,
            error=self.error,
            refreshed_at_utc=self.refreshed_at_utc,
            latency_ms=self.latency_ms,
        )

    def with_content(
        self,
        *,
        metrics: Mapping[str, Any] | None = None,
        rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
        feed: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
        payload: Mapping[str, Any] | None = None,
        diagnostics: Mapping[str, Any] | None = None,
    ) -> DataResult:
        return DataResult(
            provider_id=self.provider_id,
            query_id=self.query_id,
            state=self.state,
            summary=dict(self.summary),
            metrics=_as_mapping(metrics) if metrics is not None else dict(self.metrics),
            rows=_as_list_of_mapping(rows) if rows is not None else list(self.rows),
            feed=_as_list_of_mapping(feed) if feed is not None else list(self.feed),
            payload=_as_mapping(payload) if payload is not None else dict(self.payload),
            diagnostics=_as_mapping(diagnostics) if diagnostics is not None else dict(self.diagnostics),
            refresh_policy=self.refresh_policy,
            error=self.error,
            refreshed_at_utc=self.refreshed_at_utc,
            latency_ms=self.latency_ms,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "query_id": self.query_id,
            "state": self.normalized_state(),
            "summary": dict(self.summary),
            "metrics": dict(self.metrics),
            "rows": [dict(item) for item in self.rows],
            "feed": [dict(item) for item in self.feed],
            "payload": dict(self.payload),
            "diagnostics": dict(self.diagnostics),
            "refresh_policy": self.refresh_policy.to_payload(),
            "error": self.error.to_payload() if self.error else None,
            "refreshed_at_utc": self.refreshed_at_utc,
            "latency_ms": self.latency_ms,
            "is_stale": self.is_stale(),
        }

    @classmethod
    def loading(cls, query: DataQuery, *, policy: RefreshPolicy | None = None) -> DataResult:
        return cls(
            provider_id=query.provider_id,
            query_id=query.query_id,
            state=DataState.LOADING,
            refresh_policy=(policy or RefreshPolicy()).normalized(),
        )

    @classmethod
    def empty(
        cls,
        query: DataQuery,
        *,
        summary: Mapping[str, Any] | None = None,
        diagnostics: Mapping[str, Any] | None = None,
        policy: RefreshPolicy | None = None,
        latency_ms: float | None = None,
    ) -> DataResult:
        return cls(
            provider_id=query.provider_id,
            query_id=query.query_id,
            state=DataState.EMPTY,
            summary=_as_mapping(summary),
            metrics={},
            rows=[],
            feed=[],
            payload={},
            diagnostics=_as_mapping(diagnostics),
            refresh_policy=(policy or RefreshPolicy()).normalized(),
            latency_ms=latency_ms,
        )

    @classmethod
    def success(
        cls,
        query: DataQuery,
        *,
        summary: Mapping[str, Any] | None = None,
        metrics: Mapping[str, Any] | None = None,
        rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
        feed: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
        payload: Mapping[str, Any] | None = None,
        diagnostics: Mapping[str, Any] | None = None,
        policy: RefreshPolicy | None = None,
        latency_ms: float | None = None,
    ) -> DataResult:
        normalized_rows = _as_list_of_mapping(rows)
        normalized_feed = _as_list_of_mapping(feed)
        state = DataState.READY
        if not normalized_rows and not normalized_feed and not _as_mapping(metrics) and not _as_mapping(payload):
            state = DataState.EMPTY
        return cls(
            provider_id=query.provider_id,
            query_id=query.query_id,
            state=state,
            summary=_as_mapping(summary),
            metrics=_as_mapping(metrics),
            rows=normalized_rows,
            feed=normalized_feed,
            payload=_as_mapping(payload),
            diagnostics=_as_mapping(diagnostics),
            refresh_policy=(policy or RefreshPolicy()).normalized(),
            latency_ms=latency_ms,
        )

    @classmethod
    def failure(
        cls,
        query: DataQuery,
        *,
        code: str,
        message: str,
        details: Mapping[str, Any] | None = None,
        retryable: bool = False,
        diagnostics: Mapping[str, Any] | None = None,
        policy: RefreshPolicy | None = None,
        latency_ms: float | None = None,
    ) -> DataResult:
        return cls(
            provider_id=query.provider_id,
            query_id=query.query_id,
            state=DataState.ERROR,
            diagnostics=_as_mapping(diagnostics),
            refresh_policy=(policy or RefreshPolicy()).normalized(),
            error=DataError(
                code=str(code or "data_error"),
                message=str(message or "data query failed"),
                details=_as_mapping(details),
                retryable=bool(retryable),
            ),
            latency_ms=latency_ms,
        )

    @classmethod
    def stale(
        cls,
        query: DataQuery,
        *,
        summary: Mapping[str, Any] | None = None,
        metrics: Mapping[str, Any] | None = None,
        rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
        feed: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
        payload: Mapping[str, Any] | None = None,
        diagnostics: Mapping[str, Any] | None = None,
        policy: RefreshPolicy | None = None,
        refreshed_at_utc: str = "",
        latency_ms: float | None = None,
    ) -> DataResult:
        return cls(
            provider_id=query.provider_id,
            query_id=query.query_id,
            state=DataState.STALE,
            summary=_as_mapping(summary),
            metrics=_as_mapping(metrics),
            rows=_as_list_of_mapping(rows),
            feed=_as_list_of_mapping(feed),
            payload=_as_mapping(payload),
            diagnostics=_as_mapping(diagnostics),
            refresh_policy=(policy or RefreshPolicy()).normalized(),
            refreshed_at_utc=str(refreshed_at_utc or _utc_iso()),
            latency_ms=latency_ms,
        )


class DashboardDataProvider(Protocol):
    meta: DataProviderMeta

    def run_query(self, query: DataQuery) -> DataResult:
        ...


@dataclass(slots=True)
class FunctionDataProvider:
    meta: DataProviderMeta
    handler: Callable[[DataQuery], DataResult]

    def run_query(self, query: DataQuery) -> DataResult:
        return self.handler(query)


_DATA_PROVIDER_LOCK = RLock()
_DATA_PROVIDER_REGISTRY: dict[str, DashboardDataProvider] = {}
_DATA_PROVIDER_DIAGNOSTICS: dict[str, dict[str, Any]] = {}


def register_data_provider(
    provider: DashboardDataProvider,
    *,
    override: bool = False,
) -> DataProviderMeta:
    if provider is None:
        raise ValueError("provider is required")
    meta = provider.meta.normalized()
    with _DATA_PROVIDER_LOCK:
        if not override and meta.provider_id in _DATA_PROVIDER_REGISTRY:
            raise ValueError(f"data provider '{meta.provider_id}' already registered")
        _DATA_PROVIDER_REGISTRY[meta.provider_id] = provider
        _DATA_PROVIDER_DIAGNOSTICS.setdefault(
            meta.provider_id,
            {
                "provider_id": meta.provider_id,
                "queries_total": 0,
                "queries_failed": 0,
                "last_query_id": None,
                "last_refresh_utc": None,
                "last_state": None,
                "last_latency_ms": None,
            },
        )
    return meta


def get_data_provider(provider_id: str) -> DashboardDataProvider | None:
    normalized = str(provider_id or "").strip().lower()
    if not normalized:
        return None
    with _DATA_PROVIDER_LOCK:
        return _DATA_PROVIDER_REGISTRY.get(normalized)


def list_data_providers() -> list[DataProviderMeta]:
    with _DATA_PROVIDER_LOCK:
        metas = [provider.meta.normalized() for provider in _DATA_PROVIDER_REGISTRY.values()]
    metas.sort(key=lambda item: item.provider_id)
    return metas


def describe_data_provider(provider_id: str) -> dict[str, Any]:
    normalized = str(provider_id or "").strip().lower()
    if not normalized:
        return {}
    provider = get_data_provider(normalized)
    diagnostics = data_provider_diagnostics(normalized)
    payload: dict[str, Any] = {
        "provider_id": normalized,
        "registered": provider is not None,
        "diagnostics": diagnostics,
    }
    if provider is not None:
        payload["meta"] = provider.meta.normalized().to_payload()
    return payload


def execute_data_query(
    query: DataQuery,
    *,
    fallback_policy: RefreshPolicy | None = None,
) -> DataResult:
    if not isinstance(query, DataQuery):
        raise TypeError("query must be DataQuery")
    provider = get_data_provider(query.provider_id)
    if provider is None:
        return DataResult.failure(
            query,
            code="provider_not_found",
            message=f"provider '{query.provider_id}' is not registered",
            details={"provider_id": query.provider_id},
            policy=fallback_policy or RefreshPolicy(),
        )

    started = perf_counter()
    diagnostics_payload: dict[str, Any] = {}
    try:
        result = provider.run_query(query)
        if not isinstance(result, DataResult):
            raise TypeError("provider must return DataResult")
        latency = (perf_counter() - started) * 1000.0
        final = DataResult(
            provider_id=result.provider_id or query.provider_id,
            query_id=result.query_id or query.query_id,
            state=result.normalized_state(),
            summary=dict(result.summary),
            metrics=dict(result.metrics),
            rows=list(result.rows),
            feed=list(result.feed),
            payload=dict(result.payload),
            diagnostics=dict(result.diagnostics),
            refresh_policy=result.refresh_policy.normalized(),
            error=result.error,
            refreshed_at_utc=result.refreshed_at_utc or _utc_iso(),
            latency_ms=float(result.latency_ms if result.latency_ms is not None else latency),
        )
    except Exception as exc:  # noqa: BLE001
        latency = (perf_counter() - started) * 1000.0
        final = DataResult.failure(
            query,
            code="provider_query_failed",
            message=str(exc),
            details={"provider_id": query.provider_id, "query_id": query.query_id},
            policy=fallback_policy or RefreshPolicy(),
            latency_ms=latency,
        )

    diagnostics_payload.update(
        {
            "provider_id": query.provider_id,
            "query_id": query.query_id,
            "state": final.normalized_state(),
            "latency_ms": final.latency_ms,
            "refreshed_at_utc": final.refreshed_at_utc,
        }
    )
    with _DATA_PROVIDER_LOCK:
        diag = _DATA_PROVIDER_DIAGNOSTICS.setdefault(
            query.provider_id,
            {
                "provider_id": query.provider_id,
                "queries_total": 0,
                "queries_failed": 0,
                "last_query_id": None,
                "last_refresh_utc": None,
                "last_state": None,
                "last_latency_ms": None,
            },
        )
        diag["queries_total"] = int(diag.get("queries_total") or 0) + 1
        if final.normalized_state() == DataState.ERROR:
            diag["queries_failed"] = int(diag.get("queries_failed") or 0) + 1
        diag["last_query_id"] = query.query_id
        diag["last_refresh_utc"] = final.refreshed_at_utc
        diag["last_state"] = final.normalized_state()
        diag["last_latency_ms"] = final.latency_ms
        diagnostics_payload["provider_diagnostics"] = dict(diag)

    merged_diagnostics = dict(final.diagnostics)
    merged_diagnostics.update(diagnostics_payload)
    return DataResult(
        provider_id=final.provider_id,
        query_id=final.query_id,
        state=final.state,
        summary=final.summary,
        metrics=final.metrics,
        rows=final.rows,
        feed=final.feed,
        payload=final.payload,
        diagnostics=merged_diagnostics,
        refresh_policy=final.refresh_policy,
        error=final.error,
        refreshed_at_utc=final.refreshed_at_utc,
        latency_ms=final.latency_ms,
    )


def data_provider_diagnostics(provider_id: str | None = None) -> dict[str, Any]:
    with _DATA_PROVIDER_LOCK:
        if provider_id:
            normalized = str(provider_id).strip().lower()
            return dict(_DATA_PROVIDER_DIAGNOSTICS.get(normalized) or {})
        return {key: dict(value) for key, value in _DATA_PROVIDER_DIAGNOSTICS.items()}


def _clear_data_provider_registry_for_tests() -> None:
    with _DATA_PROVIDER_LOCK:
        _DATA_PROVIDER_REGISTRY.clear()
        _DATA_PROVIDER_DIAGNOSTICS.clear()

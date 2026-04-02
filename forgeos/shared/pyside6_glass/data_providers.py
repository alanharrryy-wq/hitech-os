from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .data import (
    DataProviderMeta,
    DataQuery,
    DataResult,
    DataState,
    RefreshPolicy,
    describe_data_provider,
    register_data_provider,
)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_local_dashboard_db_path() -> Path:
    return _repo_root() / "tools" / "_local" / "tmp" / "pyside6_glass_dashboard.sqlite3"


def _simulate_state(query: DataQuery) -> str:
    return str(query.params.get("simulate_state") or "").strip().lower()


def _safe_int(value: Any, *, default: int = 0, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except Exception:  # noqa: BLE001
        parsed = default
    return max(minimum, parsed)


def _maybe_simulated_result(
    query: DataQuery,
    *,
    policy: RefreshPolicy,
    provider_id: str,
) -> DataResult | None:
    simulated = _simulate_state(query)
    if simulated == DataState.LOADING:
        return DataResult.loading(query, policy=policy)
    if simulated == DataState.ERROR:
        return DataResult.failure(
            query,
            code="provider_simulated_error",
            message="provider simulated an error state",
            details={"query_id": query.query_id, "provider_id": provider_id},
            retryable=True,
            policy=policy,
        )
    if simulated == DataState.EMPTY:
        return DataResult.empty(
            query,
            summary={"source": provider_id, "query_id": query.query_id, "note": "simulated empty state"},
            diagnostics={"provider": provider_id, "simulated": True},
            policy=policy,
        )
    if simulated == DataState.STALE:
        return DataResult.stale(
            query,
            summary={"source": provider_id, "query_id": query.query_id, "note": "simulated stale state"},
            diagnostics={"provider": provider_id, "simulated": True, "stale": True},
            policy=policy,
        )
    return None


@dataclass(slots=True)
class InMemoryDashboardProvider:
    meta: DataProviderMeta = field(
        default_factory=lambda: DataProviderMeta(
            provider_id="builtin.mock_dashboard",
            title="Builtin Mock Dashboard Provider",
            description=(
                "Deterministic in-memory data source for KPI cards, health rows, "
                "alerts, queue tables, event feeds and diagnostics."
            ),
            tags=("builtin", "mock", "dashboard"),
            keywords=("kpi", "alerts", "health", "feed"),
            capabilities=("query.metrics", "query.table", "query.feed", "query.snapshot"),
            requirements=(),
            status="stable",
            supports_polling=True,
            source_kind="in_memory",
            version="1.0",
        )
    )

    def run_query(self, query: DataQuery) -> DataResult:
        query_id = str(query.query_id or "default").strip().lower()
        policy = RefreshPolicy(mode="polling", interval_ms=5000, stale_after_ms=20000, max_retries=1, jitter_ms=250)
        simulated_result = _maybe_simulated_result(query, policy=policy, provider_id=self.meta.provider_id)
        if simulated_result is not None:
            return simulated_result

        if query_id in {"live_metrics", "refreshable_kpi", "kpi"}:
            metrics = {
                "throughput_per_min": 214,
                "error_rate_pct": 0.47,
                "p95_latency_ms": 138,
                "queue_depth": 31,
            }
            return DataResult.success(
                query,
                summary={"surface": "live-metrics", "kpi_count": len(metrics)},
                metrics=metrics,
                diagnostics={"provider": self.meta.provider_id, "query_family": "metrics"},
                policy=policy,
            )

        if query_id in {"service_health", "health"}:
            rows = [
                {"service": "ingest", "status": "healthy", "latency_ms": 92, "uptime_pct": 99.99},
                {"service": "orchestrator", "status": "healthy", "latency_ms": 131, "uptime_pct": 99.93},
                {"service": "scheduler", "status": "warning", "latency_ms": 198, "uptime_pct": 99.55},
                {"service": "notifier", "status": "degraded", "latency_ms": 276, "uptime_pct": 98.91},
            ]
            healthy = sum(1 for item in rows if item["status"] == "healthy")
            degraded = sum(1 for item in rows if item["status"] in {"warning", "degraded"})
            return DataResult.success(
                query,
                summary={"services_total": len(rows), "healthy": healthy, "degraded": degraded},
                metrics={"healthy": healthy, "degraded": degraded, "services_total": len(rows)},
                rows=rows,
                diagnostics={"provider": self.meta.provider_id, "query_family": "health"},
                policy=policy,
            )

        if query_id in {"alerts_incidents", "incidents"}:
            rows = [
                {"id": "INC-1024", "severity": "critical", "service": "notifier", "status": "open"},
                {"id": "INC-1020", "severity": "warning", "service": "scheduler", "status": "investigating"},
                {"id": "INC-1018", "severity": "info", "service": "ingest", "status": "monitoring"},
            ]
            feed = [
                {"time": "09:10:04Z", "level": "critical", "message": "Notifier retries above threshold"},
                {"time": "09:08:22Z", "level": "warning", "message": "Scheduler lag reached 4 min"},
                {"time": "09:05:11Z", "level": "info", "message": "Ingest backlog normalized"},
            ]
            return DataResult.success(
                query,
                summary={"open_alerts": len(rows)},
                metrics={"critical": 1, "warning": 1, "info": 1},
                rows=rows,
                feed=feed,
                diagnostics={"provider": self.meta.provider_id, "query_family": "alerts"},
                policy=policy,
            )

        if query_id in {"jobs_queue", "queue"}:
            rows = [
                {"job_id": "job-771", "state": "running", "status": "running", "attempts": 1, "age_s": 23},
                {"job_id": "job-770", "state": "queued", "status": "queued", "attempts": 0, "age_s": 41},
                {"job_id": "job-769", "state": "retry", "status": "retry", "attempts": 2, "age_s": 86},
                {"job_id": "job-768", "state": "queued", "status": "queued", "attempts": 0, "age_s": 95},
            ]
            queued = sum(1 for item in rows if item["state"] == "queued")
            return DataResult.success(
                query,
                summary={"jobs_total": len(rows), "queued": queued},
                metrics={"jobs_total": len(rows), "queued": queued, "running": 1},
                rows=rows,
                diagnostics={"provider": self.meta.provider_id, "query_family": "queue"},
                policy=policy,
            )

        if query_id in {"table_detail", "detail"}:
            rows = [
                {"item_id": "item-001", "kind": "resource", "state": "ready", "owner": "ops"},
                {"item_id": "item-002", "kind": "resource", "state": "pending", "owner": "review"},
                {"item_id": "item-003", "kind": "resource", "state": "ready", "owner": "ops"},
            ]
            selected = str(query.params.get("item_id") or rows[0]["item_id"])
            detail = next((item for item in rows if item["item_id"] == selected), rows[0])
            payload = {"selected_item": detail, "selected_item_id": selected}
            return DataResult.success(
                query,
                summary={"rows": len(rows), "selected_item_id": selected},
                rows=rows,
                payload=payload,
                diagnostics={"provider": self.meta.provider_id, "query_family": "detail"},
                policy=policy,
            )

        if query_id in {"time_series_placeholder", "timeseries"}:
            points = [{"t": idx, "value": 72 + (idx % 4) * 5 + (idx // 3)} for idx in range(1, 25)]
            return DataResult.success(
                query,
                summary={"points": len(points), "range": "24 samples"},
                metrics={"latest": points[-1]["value"], "min": min(item["value"] for item in points), "max": max(item["value"] for item in points)},
                payload={"series": points, "kind": "placeholder_timeseries"},
                diagnostics={"provider": self.meta.provider_id, "query_family": "timeseries"},
                policy=policy,
            )

        if query_id in {"operational_overview", "overview"}:
            metrics = {"services_healthy": 3, "active_alerts": 2, "queue_depth": 31, "throughput_per_min": 214}
            rows = [
                {"domain": "services", "status": "stable"},
                {"domain": "alerts", "status": "watch"},
                {"domain": "queue", "status": "elevated"},
            ]
            feed = [
                {"time": "09:14:00Z", "level": "info", "message": "Overview refreshed from mock provider"},
                {"time": "09:10:04Z", "level": "critical", "message": "Critical alert still open"},
            ]
            return DataResult.success(
                query,
                summary={"surface": "operational-overview"},
                metrics=metrics,
                rows=rows,
                feed=feed,
                diagnostics={"provider": self.meta.provider_id, "query_family": "overview"},
                policy=policy,
            )

        if query_id in {"event_feed", "feed"}:
            feed = [
                {"time": "09:14:00Z", "level": "info", "message": "refresh completed", "source": "scheduler"},
                {"time": "09:12:19Z", "level": "warning", "message": "latency drift detected", "source": "gateway"},
                {"time": "09:10:04Z", "level": "critical", "message": "retry budget exceeded", "source": "notifier"},
                {"time": "09:07:32Z", "level": "info", "message": "queue depth normalized", "source": "orchestrator"},
            ]
            return DataResult.success(
                query,
                summary={"events": len(feed)},
                feed=feed,
                diagnostics={"provider": self.meta.provider_id, "query_family": "feed"},
                policy=policy,
            )

        if query_id in {"data_source_diagnostics", "diagnostics"}:
            payload = describe_data_provider(self.meta.provider_id)
            payload["generated_at_utc"] = _utc_iso()
            return DataResult.success(
                query,
                summary={"provider_id": self.meta.provider_id, "status": "ok"},
                payload=payload,
                diagnostics={"provider": self.meta.provider_id, "query_family": "diagnostics"},
                policy=policy,
            )

        return DataResult.empty(
            query,
            summary={"provider": self.meta.provider_id, "query_id": query_id, "note": "unsupported query id"},
            diagnostics={"provider": self.meta.provider_id, "query_family": "unsupported"},
            policy=policy,
        )


@dataclass(slots=True)
class LocalSQLiteDashboardProvider:
    db_path: Path
    meta: DataProviderMeta = field(
        default_factory=lambda: DataProviderMeta(
            provider_id="builtin.local_sqlite",
            title="Builtin Local SQLite Provider",
            description=(
                "Local-development dashboard provider backed by SQLite. "
                "Good starter for durable local dashboards without external services."
            ),
            tags=("builtin", "sqlite", "local_dev"),
            keywords=("sqlite", "local", "persistence", "dashboard"),
            capabilities=("query.metrics", "query.table", "query.feed", "query.snapshot"),
            requirements=("sqlite3",),
            status="stable",
            supports_polling=False,
            source_kind="sqlite",
            version="1.0",
        )
    )

    def __post_init__(self) -> None:
        self.db_path = Path(self.db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        connection = self._connection()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS metric_points (
                    metric_key TEXT PRIMARY KEY,
                    metric_value REAL NOT NULL,
                    trend TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS resource_records (
                    record_id TEXT PRIMARY KEY,
                    resource_type TEXT NOT NULL,
                    state TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS activity_log (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS queue_items (
                    item_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    attempts INTEGER NOT NULL,
                    updated_at_utc TEXT NOT NULL
                )
                """
            )
            if connection.execute("SELECT COUNT(1) FROM metric_points").fetchone()[0] == 0:
                now = _utc_iso()
                connection.executemany(
                    """
                    INSERT INTO metric_points(metric_key, metric_value, trend, unit, updated_at_utc)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        ("throughput_per_min", 187.0, "up", "req/min", now),
                        ("error_rate_pct", 0.61, "down", "pct", now),
                        ("p95_latency_ms", 146.0, "flat", "ms", now),
                        ("queue_depth", 22.0, "up", "count", now),
                    ],
                )
            if connection.execute("SELECT COUNT(1) FROM resource_records").fetchone()[0] == 0:
                now = _utc_iso()
                connection.executemany(
                    """
                    INSERT INTO resource_records(record_id, resource_type, state, owner, updated_at_utc)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        ("record-001", "service", "healthy", "ops", now),
                        ("record-002", "service", "warning", "ops", now),
                        ("record-003", "worker", "healthy", "runtime", now),
                        ("record-004", "worker", "degraded", "runtime", now),
                    ],
                )
            if connection.execute("SELECT COUNT(1) FROM activity_log").fetchone()[0] == 0:
                connection.executemany(
                    """
                    INSERT INTO activity_log(event_type, severity, message, created_at_utc)
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        ("refresh", "info", "local sqlite provider initialized", _utc_iso()),
                        ("health", "warning", "one service in warning state", _utc_iso()),
                        ("queue", "info", "queue monitor refresh completed", _utc_iso()),
                    ],
                )
            if connection.execute("SELECT COUNT(1) FROM queue_items").fetchone()[0] == 0:
                now = _utc_iso()
                connection.executemany(
                    """
                    INSERT INTO queue_items(item_id, state, priority, attempts, updated_at_utc)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        ("queue-201", "running", 1, 1, now),
                        ("queue-202", "queued", 2, 0, now),
                        ("queue-203", "retry", 1, 2, now),
                        ("queue-204", "queued", 3, 0, now),
                    ],
                )
            connection.commit()
        finally:
            connection.close()

    def run_query(self, query: DataQuery) -> DataResult:
        query_id = str(query.query_id or "default").strip().lower()
        policy = RefreshPolicy(mode="manual", interval_ms=10000, stale_after_ms=45000, max_retries=0, jitter_ms=0)
        simulated_result = _maybe_simulated_result(query, policy=policy, provider_id=self.meta.provider_id)
        if simulated_result is not None:
            return simulated_result

        try:
            connection = self._connection()
            try:
                if query_id in {"live_metrics", "refreshable_kpi", "sqlite_metrics", "kpi"}:
                    rows = connection.execute(
                        "SELECT metric_key, metric_value, trend, unit FROM metric_points ORDER BY metric_key"
                    ).fetchall()
                    metrics = {str(item["metric_key"]): item["metric_value"] for item in rows}
                    payload = {"metrics": [dict(item) for item in rows], "db_path": str(self.db_path)}
                    return DataResult.success(
                        query,
                        summary={"metrics_count": len(metrics), "source": "sqlite"},
                        metrics=metrics,
                        payload=payload,
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                if query_id in {"service_health", "sqlite_health", "health"}:
                    rows = connection.execute(
                        "SELECT record_id, resource_type, state, owner, updated_at_utc FROM resource_records ORDER BY record_id"
                    ).fetchall()
                    output = [dict(item) for item in rows]
                    for item in output:
                        item["status"] = item.get("state", "")
                    healthy = sum(1 for item in output if item["state"] == "healthy")
                    degraded = sum(1 for item in output if item["state"] in {"warning", "degraded"})
                    return DataResult.success(
                        query,
                        summary={"records_total": len(output), "healthy": healthy, "degraded": degraded},
                        metrics={"records_total": len(output), "healthy": healthy, "degraded": degraded},
                        rows=output,
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                if query_id in {"alerts_incidents", "sqlite_alerts", "incidents"}:
                    limit = _safe_int(query.params.get("limit"), default=10, minimum=1)
                    rows = connection.execute(
                        """
                        SELECT seq, event_type, severity, message, created_at_utc
                        FROM activity_log
                        WHERE severity IN ('warning', 'error', 'critical')
                        ORDER BY seq DESC
                        LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
                    mapped = [dict(item) for item in rows]
                    if not mapped:
                        return DataResult.empty(
                            query,
                            summary={"source": "sqlite", "alerts": 0},
                            diagnostics={"provider": self.meta.provider_id},
                            policy=policy,
                        )
                    return DataResult.success(
                        query,
                        summary={"alerts": len(mapped)},
                        rows=mapped,
                        feed=mapped,
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                if query_id in {"jobs_queue", "sqlite_queue", "queue"}:
                    rows = connection.execute(
                        """
                        SELECT item_id, state, priority, attempts, updated_at_utc
                        FROM queue_items
                        ORDER BY priority ASC, item_id ASC
                        """
                    ).fetchall()
                    output = [dict(item) for item in rows]
                    for item in output:
                        item["status"] = item.get("state", "")
                    return DataResult.success(
                        query,
                        summary={"jobs_total": len(output)},
                        rows=output,
                        metrics={"jobs_total": len(output), "queued": sum(1 for item in output if item["state"] == "queued")},
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                if query_id in {"table_detail", "sqlite_table", "detail"}:
                    rows = connection.execute(
                        """
                        SELECT record_id, resource_type, state, owner, updated_at_utc
                        FROM resource_records
                        ORDER BY record_id
                        """
                    ).fetchall()
                    output = [dict(item) for item in rows]
                    selected = str(query.params.get("record_id") or (output[0]["record_id"] if output else ""))
                    detail = next((item for item in output if item["record_id"] == selected), output[0] if output else {})
                    return DataResult.success(
                        query,
                        summary={"rows": len(output), "selected_record_id": selected},
                        rows=output,
                        payload={"selected_record": detail, "db_path": str(self.db_path)},
                        diagnostics={"provider": self.meta.provider_id},
                        policy=policy,
                    )

                if query_id in {"event_feed", "sqlite_feed", "feed"}:
                    limit = _safe_int(query.params.get("limit"), default=25, minimum=1)
                    rows = connection.execute(
                        """
                        SELECT seq, event_type, severity, message, created_at_utc
                        FROM activity_log
                        ORDER BY seq DESC
                        LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
                    output = [dict(item) for item in rows]
                    return DataResult.success(
                        query,
                        summary={"events": len(output)},
                        feed=output,
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                if query_id in {"operational_overview", "sqlite_overview", "overview"}:
                    metrics_rows = connection.execute("SELECT metric_key, metric_value FROM metric_points").fetchall()
                    queue_rows = connection.execute("SELECT item_id, state, priority FROM queue_items").fetchall()
                    health_rows = connection.execute("SELECT record_id, state FROM resource_records").fetchall()
                    metrics = {str(item["metric_key"]): item["metric_value"] for item in metrics_rows}
                    rows = [
                        {"domain": "metrics", "count": len(metrics_rows)},
                        {"domain": "queue_items", "count": len(queue_rows)},
                        {"domain": "resources", "count": len(health_rows)},
                    ]
                    return DataResult.success(
                        query,
                        summary={"source": "sqlite", "domains": len(rows)},
                        metrics=metrics,
                        rows=rows,
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                if query_id in {"time_series_placeholder", "sqlite_timeseries", "timeseries"}:
                    points = [
                        {"t": idx, "value": round(68 + idx * 1.2 + (idx % 5) * 1.8, 2)}
                        for idx in range(1, 31)
                    ]
                    return DataResult.success(
                        query,
                        summary={"points": len(points)},
                        payload={"series": points, "db_path": str(self.db_path)},
                        diagnostics={"provider": self.meta.provider_id},
                        policy=policy,
                    )

                if query_id in {"data_source_diagnostics", "sqlite_diagnostics", "diagnostics"}:
                    payload = describe_data_provider(self.meta.provider_id)
                    counts = {
                        "metric_points": connection.execute("SELECT COUNT(1) FROM metric_points").fetchone()[0],
                        "resource_records": connection.execute("SELECT COUNT(1) FROM resource_records").fetchone()[0],
                        "activity_log": connection.execute("SELECT COUNT(1) FROM activity_log").fetchone()[0],
                        "queue_items": connection.execute("SELECT COUNT(1) FROM queue_items").fetchone()[0],
                    }
                    payload["table_counts"] = counts
                    payload["db_path"] = str(self.db_path)
                    payload["generated_at_utc"] = _utc_iso()
                    return DataResult.success(
                        query,
                        summary={"provider_id": self.meta.provider_id, "tables": len(counts)},
                        payload=payload,
                        diagnostics={"provider": self.meta.provider_id, "db_path": str(self.db_path)},
                        policy=policy,
                    )

                return DataResult.empty(
                    query,
                    summary={"provider": self.meta.provider_id, "query_id": query_id, "note": "unsupported query id"},
                    diagnostics={"provider": self.meta.provider_id},
                    policy=policy,
                )
            finally:
                connection.close()
        except Exception as exc:  # noqa: BLE001
            return DataResult.failure(
                query,
                code="sqlite_query_failed",
                message=str(exc),
                details={"provider_id": self.meta.provider_id, "db_path": str(self.db_path)},
                retryable=True,
                policy=policy,
            )


def register_builtin_data_providers(
    *,
    force: bool = False,
    local_sqlite_path: str | Path | None = None,
) -> tuple[DataProviderMeta, ...]:
    sqlite_path = Path(local_sqlite_path).resolve() if local_sqlite_path else default_local_dashboard_db_path()
    providers = (
        InMemoryDashboardProvider(),
        LocalSQLiteDashboardProvider(sqlite_path),
    )
    registered: list[DataProviderMeta] = []
    for provider in providers:
        try:
            registered.append(register_data_provider(provider, override=force))
        except ValueError:
            if force:
                raise
    return tuple(registered)

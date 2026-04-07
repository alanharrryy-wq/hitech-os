
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from visuals.widgets.charts.engine import GlassChartSeries


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _day_label(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) >= 10:
        return text[:10]
    return text or "unknown"


def _moving_average(values: list[float], window: int = 3) -> list[float]:
    output: list[float] = []
    for index in range(len(values)):
        chunk = values[max(0, index - window + 1): index + 1]
        output.append(round(sum(chunk) / max(1, len(chunk)), 2))
    return output


def _volatility(values: list[float]) -> list[float]:
    output: list[float] = []
    previous = None
    for current in values:
        if previous is None:
            output.append(1.0)
        else:
            output.append(round(abs(current - previous) + 1.0, 2))
        previous = current
    return output


def normalize_result_rows(rows: Iterable[Mapping[str, Any] | dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row or {})
        item.setdefault("session_id", str(item.get("session_id") or item.get("label") or ""))
        item.setdefault("record_type", str(item.get("record_type") or item.get("kind") or "record"))
        item.setdefault("timestamp_utc", str(item.get("timestamp_utc") or item.get("day") or ""))
        item.setdefault("source_path", str(item.get("source_path") or item.get("source_ref") or ""))
        text = item.get("text") or item.get("summary") or item.get("headline") or item.get("source_path") or ""
        item["text"] = str(text)
        normalized.append(item)
    return normalized


def build_recent_results_model(rows: Iterable[Mapping[str, Any] | dict[str, Any]]) -> dict[str, Any]:
    payload = normalize_result_rows(rows)
    summary = (
        f"Latest indexed records from SQLite storage. Showing {len(payload)} rows from the newest operational memory footprint."
        if payload
        else "Storage is live, but there are no recent indexed records yet."
    )
    return {
        "rows": payload,
        "summary": summary,
        "mode_label": "Recent",
        "query": "",
        "record_type": None,
    }


def build_search_results_model(
    rows: Iterable[Mapping[str, Any] | dict[str, Any]],
    *,
    query: str,
    record_type: str | None = None,
) -> dict[str, Any]:
    payload = normalize_result_rows(rows)
    scope = f" filtered to {record_type}" if record_type else ""
    summary = (
        f"Search returned {len(payload)} indexed rows for '{query}'{scope}."
        if payload
        else f"Search for '{query}' returned no indexed rows{scope}."
    )
    return {
        "rows": payload,
        "summary": summary,
        "mode_label": "Search",
        "query": query,
        "record_type": record_type,
    }


def build_status_lines(metrics: Mapping[str, Any]) -> list[str]:
    totals = dict(metrics.get("totals") or {})
    errors = _safe_int(totals.get("errors"))
    records = _safe_int(totals.get("records"))
    sessions = _safe_int(totals.get("sessions"))
    files = _safe_int(totals.get("files"))
    quality = "steady" if errors == 0 else "watch" if errors < 5 else "degraded"
    density = 0.0 if records <= 0 else round(errors / max(1, records), 3)
    lines = [
        f"Sessions indexed: {sessions}",
        f"Records indexed: {records}",
        f"Files fingerprinted: {files}",
        f"Error density: {density}",
        f"Telemetry posture: {quality}",
    ]
    confidence = list(metrics.get("session_confidence") or [])
    if confidence:
        top = confidence[:3]
        lines.append("")
        lines.append("Session confidence snapshots:")
        for item in top:
            label = item.get("bucket") or item.get("label") or "unknown"
            count = item.get("count") or 0
            lines.append(f"- {label}: {count}")
    return lines


def build_metrics_view_model(raw_payload: Mapping[str, Any] | dict[str, Any]) -> dict[str, Any]:
    raw = dict(raw_payload or {})
    totals = dict(raw.get("totals") or {})
    activity = sorted(list(raw.get("daily_activity") or []), key=lambda item: str(item.get("day") or ""))
    counts = [_safe_float(item.get("count")) for item in activity]
    days = [_day_label(item.get("day")) for item in activity]
    x_values = tuple(float(index) for index in range(len(counts) or 6))

    if counts:
        trend = _moving_average(counts, window=3)
        volatility = _volatility(counts)
    else:
        counts = [10.0, 12.0, 16.0, 15.0, 20.0, 24.0]
        trend = _moving_average(counts, window=3)
        volatility = _volatility(counts)
        days = [f"D-{index}" for index in range(len(counts), 0, -1)]
        x_values = tuple(float(index) for index in range(len(counts)))

    records = _safe_int(totals.get("records"))
    sessions = _safe_int(totals.get("sessions"))
    errors = _safe_int(totals.get("errors"))
    tools = _safe_int(totals.get("tools"))
    files = _safe_int(totals.get("files"))
    event_count = _safe_int(totals.get("events"))

    error_density = 0.0 if records <= 0 else round(errors / max(1, records), 3)
    tool_density = 0.0 if records <= 0 else round(tools / max(1, records), 3)
    if errors >= max(5, int(records * 0.15)):
        chart_state = "error"
        tone = "warn"
        status_label = "Degraded"
    elif errors > 0:
        chart_state = "stale"
        tone = "accent"
        status_label = "Watch"
    else:
        chart_state = "ready"
        tone = "good"
        status_label = "Healthy"

    top_errors = [dict(item) for item in raw.get("top_errors") or []]
    top_tools = [dict(item) for item in raw.get("top_tools") or []]
    sequence_patterns = [dict(item) for item in raw.get("sequence_patterns") or []]

    notes = build_status_lines(raw)
    notes.extend(
        [
            "",
            f"Activity window: {len(days)} day(s)",
            f"Tools / record ratio: {tool_density}",
            f"Events tracked: {event_count}",
        ]
    )

    return {
        "raw": raw,
        "totals": totals,
        "top_errors": top_errors,
        "top_tools": top_tools,
        "sequence_patterns": sequence_patterns,
        "notes": notes,
        "status": {
            "label": status_label,
            "tone": tone,
            "error_density": error_density,
        },
        "kpis": [
            {"label": "Sessions", "value": sessions, "detail": "linked memory threads"},
            {"label": "Records", "value": records, "detail": "indexed canonical rows"},
            {"label": "Errors", "value": errors, "detail": f"density {error_density}"},
            {"label": "Files", "value": files, "detail": "fingerprinted source files"},
        ],
        "chart": {
            "title": f"Runtime Overview · {records} records / {errors} errors",
            "subtitle": f"Daily activity, smoothed trend, and volatility across the latest {len(days)}-day window.",
            "data_state": chart_state,
            "series": (
                GlassChartSeries(name="Records / day", x=x_values, y=tuple(counts), mode="area", fill_to_zero=True),
                GlassChartSeries(name="Trend", x=x_values, y=tuple(trend), mode="line", symbol="o"),
                GlassChartSeries(name="Volatility", x=x_values, y=tuple(volatility), mode="spark"),
            ),
            "labels": days,
        },
    }


def build_demo_bundle() -> dict[str, Any]:
    metrics = build_metrics_view_model(
        {
            "totals": {"sessions": 12, "records": 184, "events": 96, "errors": 7, "tools": 19, "files": 24},
            "daily_activity": [
                {"day": "2026-04-01", "count": 18},
                {"day": "2026-04-02", "count": 22},
                {"day": "2026-04-03", "count": 24},
                {"day": "2026-04-04", "count": 17},
                {"day": "2026-04-05", "count": 28},
                {"day": "2026-04-06", "count": 31},
            ],
            "top_errors": [
                {"error_type": "ImportError", "count": 3},
                {"error_type": "TimeoutError", "count": 2},
                {"error_type": "RuntimeError", "count": 2},
            ],
            "top_tools": [
                {"tool_name": "pytest", "count": 7},
                {"tool_name": "pyside6", "count": 5},
                {"tool_name": "sqlite", "count": 4},
            ],
            "sequence_patterns": [
                {"pattern": "start > ingest > failure", "count": 2},
                {"pattern": "repair > ingest > success", "count": 1},
            ],
            "session_confidence": [
                {"bucket": "high", "count": 7},
                {"bucket": "medium", "count": 4},
                {"bucket": "low", "count": 1},
            ],
        }
    )
    results = build_recent_results_model(
        [
            {
                "session_id": "demo-2026-04-06-a",
                "timestamp_utc": "2026-04-06T09:14:00Z",
                "record_type": "log",
                "source_path": "sample_inputs/demo_a.log",
                "text": "Engine booted, indexed sample data, and observed a brief import warning.",
            },
            {
                "session_id": "demo-2026-04-06-b",
                "timestamp_utc": "2026-04-06T09:41:00Z",
                "record_type": "json",
                "source_path": "sample_inputs/demo_b.json",
                "text": "Search replay completed and sequence patterns were refreshed.",
            },
            {
                "session_id": "demo-2026-04-06-c",
                "timestamp_utc": "2026-04-06T10:03:00Z",
                "record_type": "md",
                "source_path": "sample_inputs/demo_notes.md",
                "text": "Operator notes mention pyqtgraph fallback if optional chart extras are missing.",
            },
        ]
    )
    detail = {
        "session": {"session_id": "demo-2026-04-06-a", "confidence": "medium"},
        "records": [
            {"record_type": "log", "timestamp_utc": "2026-04-06T09:14:00Z", "summary": "Engine boot sequence complete."}
        ],
        "errors": [{"error_type": "ImportError", "message": "Optional chart extra missing", "severity": "warning"}],
        "tools": [{"tool_name": "pytest", "action": "smoke"}],
        "timeline": [
            {"timestamp_utc": "2026-04-06T09:14:00Z", "headline": "Boot sequence complete"},
            {"timestamp_utc": "2026-04-06T09:15:00Z", "headline": "Indexed sample data"},
        ],
        "session_insights": {
            "confidence": "medium",
            "probable_root_causes": [{"category": "optional_dependency", "confidence": "medium", "score": 0.73}],
        },
        "related_sessions": [{"session_id": "demo-2026-04-06-b"}],
    }
    return {
        "metrics": metrics,
        "results": results,
        "detail": detail,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

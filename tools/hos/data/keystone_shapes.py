#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
from dataclasses import asdict
from typing import Any

from tools.hos.data.simulator_core import SimulationBundle


def _request_id(seed: int, channel: str) -> str:
    return f"req_{channel}-{seed:010d}"


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def build_api_meta(seed: int, channel: str, generated_at: str | None = None) -> dict[str, Any]:
    return {
        "requestId": _request_id(seed=seed, channel=channel),
        "generatedAt": generated_at or _now_iso(),
        "contractVersion": "2.0.0",
    }


def to_runs_query_response(
    bundle: SimulationBundle,
    seed: int,
    page: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    start = max(0, (page - 1) * page_size)
    end = start + page_size
    items = bundle.runs[start:end]
    return {
        "meta": build_api_meta(seed=seed, channel="runs", generated_at=bundle.metadata["generatedAt"]),
        "items": items,
        "total": len(bundle.runs),
        "page": page,
        "pageSize": page_size,
    }


def to_activity_query_response(
    bundle: SimulationBundle,
    seed: int,
    limit: int = 50,
) -> dict[str, Any]:
    items = bundle.activity[:limit]
    has_more = len(bundle.activity) > limit
    cursor = items[-1]["id"] if items else None
    return {
        "meta": build_api_meta(seed=seed, channel="activity", generated_at=bundle.metadata["generatedAt"]),
        "items": items,
        "cursor": cursor,
        "hasMore": has_more,
    }


def to_widgets_query_response(bundle: SimulationBundle, seed: int) -> dict[str, Any]:
    return {
        "meta": build_api_meta(seed=seed, channel="widgets", generated_at=bundle.metadata["generatedAt"]),
        "widgets": bundle.widgets,
        "layout": bundle.layout,
    }


def to_endpoint_payloads(bundle: SimulationBundle, seed: int) -> dict[str, dict[str, Any]]:
    return {
        "runs": to_runs_query_response(bundle=bundle, seed=seed, page=1, page_size=min(25, len(bundle.runs))),
        "activity": to_activity_query_response(bundle=bundle, seed=seed, limit=50),
        "widgets": to_widgets_query_response(bundle=bundle, seed=seed),
    }


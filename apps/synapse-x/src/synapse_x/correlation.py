from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from synapse_x.models import CanonicalRecord
from synapse_x.utils import slugify


@dataclass(slots=True)
class SessionAnchor:
    session_id: str
    timestamp_utc: str
    confidence: str
    strategy: str
    date_bucket: str | None
    source_family: str
    stem_tokens: set[str]
    signal_keywords: set[str]
    topic_tokens: set[str]
    error_types: set[str]
    error_signatures: set[str]
    tool_names: set[str]
    summary_signature: str
    session_root: str
    source_path: str


def resolve_record_sessions(records: list[CanonicalRecord], existing_anchors: Iterable[SessionAnchor] | None = None) -> list[CanonicalRecord]:
    if not records:
        return records

    anchors: list[SessionAnchor] = list(existing_anchors or [])
    unresolved: list[CanonicalRecord] = []

    for record in records:
        heuristics = record.metadata.get("heuristics", {})
        confidence = str(heuristics.get("session_confidence", "low"))
        strategy = str(heuristics.get("session_strategy", "unknown"))
        if confidence in {"high", "medium"} and not strategy.startswith("derived"):
            anchors.append(anchor_from_record(record))
        else:
            unresolved.append(record)

    for record in unresolved:
        best_anchor = None
        best_score = -999
        for anchor in anchors:
            score = correlation_score(anchor_from_record(record), anchor)
            if score > best_score:
                best_score = score
                best_anchor = anchor
        threshold = adoption_threshold(best_anchor)
        if best_anchor and best_score >= threshold:
            _adopt_session(record, best_anchor.session_id, strategy="correlated-to-anchor", score=best_score)
            anchors.append(anchor_from_record(record))

    remaining = [
        record
        for record in records
        if str(record.metadata.get("heuristics", {}).get("session_strategy", "")).startswith("derived")
    ]
    if remaining:
        _cluster_remaining_records(remaining)

    return records


def adoption_threshold(anchor: SessionAnchor | None) -> int:
    if anchor is None:
        return 999
    if anchor.confidence == "high":
        return 42
    if anchor.confidence == "medium":
        return 48
    return 54


def anchor_from_record(record: CanonicalRecord) -> SessionAnchor:
    heuristics = record.metadata.get("heuristics", {})
    correlation = record.metadata.get("correlation", {})
    return SessionAnchor(
        session_id=record.session_id,
        timestamp_utc=record.timestamp_utc,
        confidence=str(heuristics.get("session_confidence", "low")),
        strategy=str(heuristics.get("session_strategy", "unknown")),
        date_bucket=correlation.get("date_bucket"),
        source_family=str(correlation.get("source_family") or ""),
        stem_tokens=set(correlation.get("stem_tokens") or []),
        signal_keywords=set(correlation.get("signal_keywords") or []),
        topic_tokens=set(correlation.get("topic_tokens") or []),
        error_types=set(correlation.get("error_types") or []),
        error_signatures=set(correlation.get("error_signatures") or []),
        tool_names=set(correlation.get("tool_names") or []),
        summary_signature=str(correlation.get("summary_signature") or ""),
        session_root=str(correlation.get("session_root") or ""),
        source_path=record.source_path,
    )


def anchors_from_rows(rows: Iterable[dict[str, Any]]) -> list[SessionAnchor]:
    anchors: list[SessionAnchor] = []
    for row in rows:
        metadata_raw = row.get("metadata_json") or "{}"
        try:
            metadata = json.loads(metadata_raw)
        except Exception:
            metadata = {}
        heuristics = metadata.get("heuristics", {})
        correlation = metadata.get("correlation", {})
        anchors.append(
            SessionAnchor(
                session_id=str(row.get("session_id") or ""),
                timestamp_utc=str(row.get("timestamp_utc") or ""),
                confidence=str(heuristics.get("session_confidence", "medium")),
                strategy=str(heuristics.get("session_strategy", "existing-record")),
                date_bucket=correlation.get("date_bucket") or (str(row.get("timestamp_utc") or "")[:10] or None),
                source_family=str(correlation.get("source_family") or _derive_family_from_path(str(row.get("source_path") or ""))),
                stem_tokens=set(correlation.get("stem_tokens") or []),
                signal_keywords=set(correlation.get("signal_keywords") or []),
                topic_tokens=set(correlation.get("topic_tokens") or []),
                error_types=set(_coerce_iterable_strings(correlation.get("error_types")) | _coerce_iterable_strings([row.get("primary_error")])),
                error_signatures=set(_coerce_iterable_strings(correlation.get("error_signatures"))),
                tool_names=set(_coerce_iterable_strings(correlation.get("tool_names")) | _coerce_iterable_strings([row.get("primary_tool")])),
                summary_signature=str(correlation.get("summary_signature") or slugify(str(row.get("summary") or "")[:80].lower())),
                session_root=str(correlation.get("session_root") or slugify(str(row.get("session_id") or "").split("-", 1)[0])),
                source_path=str(row.get("source_path") or ""),
            )
        )
    return anchors


def correlation_score(left: SessionAnchor, right: SessionAnchor) -> int:
    score = 0

    if left.date_bucket and right.date_bucket:
        day_distance = _date_distance(left.date_bucket, right.date_bucket)
        if day_distance == 0:
            score += 18
        elif day_distance == 1:
            score += 4
        elif day_distance is not None and day_distance >= 3:
            score -= 18

    minutes = _abs_minutes(left.timestamp_utc, right.timestamp_utc)
    if minutes is not None:
        if minutes <= 15:
            score += 24
        elif minutes <= 60:
            score += 20
        elif minutes <= 180:
            score += 14
        elif minutes <= 720:
            score += 8
        elif minutes > 1440:
            score -= 10

    shared_error_signatures = left.error_signatures & right.error_signatures
    if shared_error_signatures:
        score += min(36, 22 + 6 * len(shared_error_signatures))

    shared_errors = left.error_types & right.error_types
    if shared_errors:
        score += min(24, 12 + 5 * len(shared_errors))

    shared_tools = left.tool_names & right.tool_names
    if shared_tools:
        score += min(22, 10 + 4 * len(shared_tools))

    shared_topics = left.topic_tokens & right.topic_tokens
    if shared_topics:
        score += min(14, 2 * len(shared_topics))

    shared_keywords = left.signal_keywords & right.signal_keywords
    if shared_keywords:
        score += min(12, 2 * len(shared_keywords))

    shared_stem = left.stem_tokens & right.stem_tokens
    if shared_stem:
        score += min(12, 3 * len(shared_stem))

    if left.source_family and left.source_family == right.source_family:
        score += 8

    if left.summary_signature and left.summary_signature == right.summary_signature:
        score += 12

    if left.session_root and right.session_root and left.session_root == right.session_root:
        score += 5

    if left.confidence == "low" and right.confidence in {"medium", "high"}:
        score += 6
    if right.confidence == "low" and left.confidence in {"medium", "high"}:
        score += 6

    if left.session_id and right.session_id and left.session_id == right.session_id:
        score += 100

    return score


def _cluster_remaining_records(records: list[CanonicalRecord]) -> None:
    parent = list(range(len(records)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra = find(a)
        rb = find(b)
        if ra != rb:
            parent[rb] = ra

    anchors = [anchor_from_record(record) for record in records]
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            threshold = 38 if anchors[i].date_bucket and anchors[i].date_bucket == anchors[j].date_bucket else 44
            if correlation_score(anchors[i], anchors[j]) >= threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for idx in range(len(records)):
        groups.setdefault(find(idx), []).append(idx)

    for indices in groups.values():
        if not indices:
            continue
        derived = _derive_cluster_session_id([records[idx] for idx in indices])
        for idx in indices:
            _adopt_session(records[idx], derived, strategy="correlated-cluster", score=42)


def _derive_cluster_session_id(records: list[CanonicalRecord]) -> str:
    dates = [record.timestamp_utc[:10] for record in records if record.timestamp_utc]
    date_part = max(set(dates), key=dates.count) if dates else "unknown-date"

    error_pool: list[str] = []
    tool_pool: list[str] = []
    family_pool: list[str] = []
    topic_pool: list[str] = []
    for record in records:
        correlation = record.metadata.get("correlation", {})
        error_pool.extend(correlation.get("error_signatures") or correlation.get("error_types") or [])
        tool_pool.extend(correlation.get("tool_names") or [])
        family_pool.append(str(correlation.get("source_family") or ""))
        topic_pool.extend(correlation.get("topic_tokens") or [])

    error_part = max(set(error_pool), key=error_pool.count) if error_pool else "signal"
    tool_part = max(set(tool_pool), key=tool_pool.count) if tool_pool else "artifact"
    family_part = max(set(family_pool), key=family_pool.count) if family_pool else "cluster"
    topic_part = max(set(topic_pool), key=topic_pool.count) if topic_pool else "topic"

    return f"cluster-{slugify(date_part)}-{slugify(error_part)}-{slugify(tool_part)}-{slugify(family_part)}-{slugify(topic_part)}"


def _adopt_session(record: CanonicalRecord, session_id: str, *, strategy: str, score: int) -> None:
    old_session = record.session_id
    record.session_id = session_id
    for collection in (record.events, record.errors, record.tools):
        for item in collection:
            item["session_id"] = session_id

    heuristics = record.metadata.setdefault("heuristics", {})
    heuristics["session_strategy"] = strategy
    heuristics["session_confidence"] = "high" if score >= 60 else "medium"
    heuristics["correlation_score"] = score
    heuristics["previous_session_id"] = old_session

    correlation = record.metadata.setdefault("correlation", {})
    correlation["session_root"] = slugify(session_id.split("-", 1)[0])
    lineage = correlation.setdefault("lineage", [])
    lineage.append({"adopted_from": old_session, "adopted_to": session_id, "score": score, "strategy": strategy})


def _derive_family_from_path(path: str) -> str:
    stem = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].rsplit(".", 1)[0].lower()
    tokens = [token for token in stem.replace("_", "-").split("-") if token and not token.isdigit()]
    return slugify("-".join(tokens[:2]) if tokens else stem)


def _coerce_iterable_strings(values: Iterable[Any] | None) -> set[str]:
    if not values:
        return set()
    out: set[str] = set()
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            out.add(text)
    return out


def _abs_minutes(left: str, right: str) -> int | None:
    try:
        left_dt = datetime.fromisoformat(left.replace("Z", "+00:00"))
        right_dt = datetime.fromisoformat(right.replace("Z", "+00:00"))
    except Exception:
        return None
    return int(abs((left_dt - right_dt).total_seconds()) // 60)


def _date_distance(left: str, right: str) -> int | None:
    try:
        left_dt = datetime.fromisoformat(left)
        right_dt = datetime.fromisoformat(right)
    except Exception:
        return None
    return abs((left_dt.date() - right_dt.date()).days)

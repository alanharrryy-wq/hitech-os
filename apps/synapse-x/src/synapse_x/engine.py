from __future__ import annotations

import json
import logging
import shutil
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from synapse_x.config import Settings
from synapse_x.correlation import anchors_from_rows, resolve_record_sessions
from synapse_x.logging_setup import configure_logging
from synapse_x.models import FileFingerprint
from synapse_x.normalization import normalize_raw
from synapse_x.parsers import SUPPORTED_EXTENSIONS, parse_path
from synapse_x.storage import (
    connect,
    create_ingest_run,
    finalize_ingest_run,
    get_file_state,
    has_fts,
    init_db,
    integrity_check,
    rebuild_search_indexes,
    store_record,
    upsert_file_state,
)
from synapse_x.utils import (
    file_mtime_iso,
    keyword_tokens,
    semantic_text_fingerprint,
    sha256_file,
    slugify,
    utc_now_iso,
)

LOGGER = logging.getLogger(__name__)


class SynapseEngine:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.settings.ensure_dirs()
        configure_logging(self.settings.log_dir)

    def init_storage(self) -> None:
        init_db(self.settings.db_path)

    def ingest(self, paths: list[str | Path] | None = None, full: bool = False) -> dict[str, Any]:
        self.init_storage()
        source_paths = [Path(p) for p in paths] if paths else list(self.settings.source_paths)
        conn = connect(self.settings.db_path)
        run_id = create_ingest_run(conn, "full" if full else "incremental")
        files_seen = 0
        files_processed = 0
        errors_count = 0
        failures: list[dict[str, str]] = []

        try:
            pending = self._collect_pending_files(conn, source_paths, full=full)
            files_seen = len(pending)
            staged: list[tuple[Path, FileFingerprint, Any, Any]] = []
            for path in pending:
                try:
                    fingerprint = self._fingerprint(path)
                    raw = parse_path(path)
                    record = normalize_raw(raw, path)
                    staged.append((path, fingerprint, raw, record))
                except Exception as exc:  # noqa: BLE001
                    LOGGER.exception("Failed parsing file: %s", path)
                    failures.append({"path": str(path), "error": str(exc)})
                    errors_count += 1
                    upsert_file_state(
                        conn,
                        path=str(path),
                        record_type=path.suffix.lower().lstrip(".") or "unknown",
                        size_bytes=path.stat().st_size if path.exists() else 0,
                        mtime_utc=file_mtime_iso(path) if path.exists() else utc_now_iso(),
                        content_hash=self._safe_hash(path),
                        ingest_status="failed",
                    )

            existing_anchors = self._fetch_existing_anchors(conn)
            resolve_record_sessions([record for _, _, _, record in staged], existing_anchors=existing_anchors)

            for path, fingerprint, _raw, record in staged:
                try:
                    store_record(conn, record)
                    self._write_cache(record.to_dict(), record.session_id, path)
                    self._copy_raw(path)
                    upsert_file_state(
                        conn,
                        path=str(path),
                        record_type=record.record_type,
                        size_bytes=fingerprint.size_bytes,
                        mtime_utc=fingerprint.mtime_utc,
                        content_hash=fingerprint.content_hash,
                        ingest_status="ok",
                    )
                    files_processed += 1
                except Exception as exc:  # noqa: BLE001
                    LOGGER.exception("Failed storing file: %s", path)
                    failures.append({"path": str(path), "error": str(exc)})
                    errors_count += 1
                    upsert_file_state(
                        conn,
                        path=str(path),
                        record_type=record.record_type,
                        size_bytes=fingerprint.size_bytes,
                        mtime_utc=fingerprint.mtime_utc,
                        content_hash=fingerprint.content_hash,
                        ingest_status="failed",
                    )

            finalize_ingest_run(
                conn,
                run_id,
                status="ok" if not failures else "partial",
                files_seen=files_seen,
                files_processed=files_processed,
                errors_count=errors_count,
                diagnostics={"failures": failures},
            )
            conn.commit()
            return {
                "status": "ok" if not failures else "partial",
                "files_seen": files_seen,
                "files_processed": files_processed,
                "errors_count": errors_count,
                "failures": failures,
            }
        except Exception as exc:  # noqa: BLE001
            finalize_ingest_run(
                conn,
                run_id,
                status="failed",
                files_seen=files_seen,
                files_processed=files_processed,
                errors_count=errors_count + 1,
                diagnostics={"fatal": str(exc), "failures": failures},
            )
            conn.commit()
            raise
        finally:
            conn.close()

    def search(
        self,
        query: str,
        *,
        record_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        self.init_storage()
        conn = connect(self.settings.db_path)
        try:
            return _search(conn, query, record_type=record_type, date_from=date_from, date_to=date_to, limit=limit)
        finally:
            conn.close()

    def get_session_detail(self, session_id: str) -> dict[str, Any]:
        self.init_storage()
        conn = connect(self.settings.db_path)
        try:
            session = conn.execute(
                "SELECT session_id, first_seen_at, last_seen_at, source_count, status FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if not session:
                return {
                    "session": None,
                    "timeline": [],
                    "events": [],
                    "errors": [],
                    "tools": [],
                    "records": [],
                    "session_insights": {},
                }

            records = [_deserialize_record(row) for row in conn.execute(
                "SELECT record_id, session_id, timestamp_utc, record_type, source_path, source_hash, title, summary, metadata_json FROM records WHERE session_id = ? ORDER BY timestamp_utc",
                (session_id,),
            ).fetchall()]
            events = [dict(row) for row in conn.execute(
                "SELECT event_id, session_id, timestamp_utc, category, message, tool_name, raw_ref FROM events WHERE session_id = ? ORDER BY timestamp_utc",
                (session_id,),
            ).fetchall()]
            errors = [dict(row) for row in conn.execute(
                "SELECT error_id, session_id, timestamp_utc, error_type, message, severity, raw_ref FROM errors WHERE session_id = ? ORDER BY timestamp_utc",
                (session_id,),
            ).fetchall()]
            tools = [dict(row) for row in conn.execute(
                "SELECT tool_id, session_id, timestamp_utc, tool_name, action, raw_ref FROM tools WHERE session_id = ? ORDER BY timestamp_utc",
                (session_id,),
            ).fetchall()]
            timeline = _build_timeline(records, events, errors, tools)
            insights = _build_session_insights(records, errors, tools, timeline)
            related_sessions = _find_related_sessions(conn, session_id, records, errors, tools, timeline, insights)
            session_payload = dict(session)
            session_payload["confidence"] = insights["confidence"]
            return {
                "session": session_payload,
                "records": records,
                "timeline": timeline,
                "events": events,
                "errors": errors,
                "tools": tools,
                "session_insights": insights,
                "related_sessions": related_sessions,
            }
        finally:
            conn.close()

    def get_metrics(self, days: int = 7) -> dict[str, Any]:
        self.init_storage()
        conn = connect(self.settings.db_path)
        try:
            totals = {
                "sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
                "records": conn.execute("SELECT COUNT(*) FROM records").fetchone()[0],
                "events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                "errors": conn.execute("SELECT COUNT(*) FROM errors").fetchone()[0],
                "tools": conn.execute("SELECT COUNT(*) FROM tools").fetchone()[0],
                "files": conn.execute("SELECT COUNT(*) FROM files").fetchone()[0],
            }
            daily_activity = [dict(row) for row in conn.execute(
                '''
                SELECT substr(timestamp_utc, 1, 10) AS day, COUNT(*) AS count
                FROM records
                GROUP BY substr(timestamp_utc, 1, 10)
                ORDER BY day DESC
                LIMIT ?
                ''',
                (max(days, 1),),
            ).fetchall()]
            top_errors = [dict(row) for row in conn.execute(
                '''
                SELECT error_type, COUNT(*) AS count
                FROM errors
                GROUP BY error_type
                ORDER BY count DESC, error_type ASC
                LIMIT 10
                '''
            ).fetchall()]
            top_tools = [dict(row) for row in conn.execute(
                '''
                SELECT tool_name, COUNT(*) AS count
                FROM tools
                GROUP BY tool_name
                ORDER BY count DESC, tool_name ASC
                LIMIT 10
                '''
            ).fetchall()]
            rows = [dict(row) for row in conn.execute(
                "SELECT session_id, timestamp_utc, summary, metadata_json FROM records ORDER BY timestamp_utc DESC LIMIT 1000"
            ).fetchall()]
            session_confidence = _summarize_session_confidence(rows)
            top_error_groups = _summarize_error_groups([dict(row) for row in conn.execute(
                "SELECT session_id, timestamp_utc, error_type, message, severity FROM errors ORDER BY timestamp_utc DESC LIMIT 2000"
            ).fetchall()])
            phase_activity = _phase_activity_from_records(rows)
            sequence_patterns = _summarize_global_sequences(conn)
            return {
                "totals": totals,
                "daily_activity": daily_activity,
                "top_errors": top_errors,
                "top_tools": top_tools,
                "session_confidence": session_confidence,
                "top_error_groups": top_error_groups[:10],
                "phase_activity": phase_activity,
                "sequence_patterns": sequence_patterns,
            }
        finally:
            conn.close()

    def repair(self) -> dict[str, Any]:
        self.init_storage()
        conn = connect(self.settings.db_path)
        try:
            integrity = integrity_check(conn)
            rebuild_search_indexes(conn)
            conn.commit()
            fts_enabled = has_fts(conn)
            return {
                "status": "ok" if integrity == "ok" else "warning",
                "integrity_check": integrity,
                "fts_enabled": fts_enabled,
            }
        finally:
            conn.close()

    def _fetch_existing_anchors(self, conn) -> list:
        rows = conn.execute(
            """
            SELECT
                r.session_id,
                r.timestamp_utc,
                r.source_path,
                r.summary,
                r.metadata_json,
                (
                    SELECT e.error_type
                    FROM errors e
                    WHERE e.record_id = r.record_id
                    ORDER BY e.timestamp_utc ASC, e.error_id ASC
                    LIMIT 1
                ) AS primary_error,
                (
                    SELECT t.tool_name
                    FROM tools t
                    WHERE t.record_id = r.record_id
                    ORDER BY t.timestamp_utc ASC, t.tool_id ASC
                    LIMIT 1
                ) AS primary_tool
            FROM records r
            ORDER BY r.timestamp_utc DESC
            LIMIT 500
            """
        ).fetchall()
        return anchors_from_rows([dict(row) for row in rows])

    def _collect_pending_files(self, conn, source_paths: list[Path], *, full: bool) -> list[Path]:
        candidates: list[Path] = []
        for source in source_paths:
            source = source.expanduser().resolve()
            if source.is_file():
                if source.suffix.lower() in SUPPORTED_EXTENSIONS:
                    candidates.append(source)
                continue
            if source.is_dir():
                for path in source.rglob("*"):
                    if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                        candidates.append(path)
        pending: list[Path] = []
        for path in sorted(candidates):
            if full:
                pending.append(path)
                continue
            fingerprint = self._fingerprint(path)
            state = get_file_state(conn, str(path))
            if state is None:
                pending.append(path)
                continue
            if (
                state["size_bytes"] != fingerprint.size_bytes
                or state["mtime_utc"] != fingerprint.mtime_utc
                or state["content_hash"] != fingerprint.content_hash
                or state["ingest_status"] != "ok"
            ):
                pending.append(path)
        return pending

    def _fingerprint(self, path: Path) -> FileFingerprint:
        stat = path.stat()
        return FileFingerprint(
            path=str(path),
            size_bytes=stat.st_size,
            mtime_utc=file_mtime_iso(path),
            content_hash=sha256_file(path),
        )

    def _safe_hash(self, path: Path) -> str:
        try:
            return sha256_file(path)
        except Exception:
            return "unavailable"

    def _write_cache(self, payload: dict[str, Any], session_id: str, source_path: Path) -> Path:
        base = slugify(f"{session_id}_{source_path.stem}")
        target = self.settings.cache_dir / f"{base}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def _copy_raw(self, source_path: Path) -> Path:
        base = slugify(source_path.name)
        target = self.settings.raw_dir / base
        if target.resolve() != source_path.resolve():
            shutil.copy2(source_path, target)
        return target


def _search(conn, query: str, *, record_type: str | None, date_from: str | None, date_to: str | None, limit: int) -> list[dict[str, Any]]:
    params: list[Any] = []
    clauses: list[str] = []

    use_fts = has_fts(conn)
    if use_fts:
        tokens = [token for token in query.replace('"', ' ').split() if token.strip()]
        fts_query = " OR ".join(tokens) if tokens else query
        sql = "SELECT session_id, timestamp_utc, record_type, text, source_path FROM search_index_fts WHERE search_index_fts MATCH ?"
        params.append(fts_query)
    else:
        sql = "SELECT session_id, timestamp_utc, record_type, text, source_path FROM search_index_plain WHERE text LIKE ?"
        params.append(f"%{query}%")

    if record_type:
        clauses.append("record_type = ?")
        params.append(record_type)
    if date_from:
        clauses.append("timestamp_utc >= ?")
        params.append(date_from)
    if date_to:
        clauses.append("timestamp_utc <= ?")
        params.append(date_to)
    if clauses:
        sql += " AND " + " AND ".join(clauses)

    sql += " ORDER BY timestamp_utc DESC LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(sql, params).fetchall()
    except Exception:
        fallback_sql = "SELECT session_id, timestamp_utc, record_type, text, source_path FROM search_index_plain WHERE text LIKE ?"
        fallback_params: list[Any] = [f"%{query}%"]
        if record_type:
            fallback_sql += " AND record_type = ?"
            fallback_params.append(record_type)
        if date_from:
            fallback_sql += " AND timestamp_utc >= ?"
            fallback_params.append(date_from)
        if date_to:
            fallback_sql += " AND timestamp_utc <= ?"
            fallback_params.append(date_to)
        fallback_sql += " ORDER BY timestamp_utc DESC LIMIT ?"
        fallback_params.append(limit)
        rows = conn.execute(fallback_sql, fallback_params).fetchall()

    return [dict(row) for row in rows]


def _deserialize_record(row: Any) -> dict[str, Any]:
    payload = dict(row)
    metadata_raw = payload.get("metadata_json") or "{}"
    try:
        payload["metadata"] = json.loads(metadata_raw)
    except Exception:
        payload["metadata"] = {}
    return payload


def _build_timeline(records: list[dict[str, Any]], events: list[dict[str, Any]], errors: list[dict[str, Any]], tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []

    for row in records:
        timeline.append({
            "kind": "record",
            "timestamp_utc": row.get("timestamp_utc"),
            "headline": row.get("summary") or row.get("title") or row.get("record_type"),
            "message": row.get("summary") or "",
            "phase": _infer_phase(row.get("summary") or row.get("title") or row.get("record_type") or ""),
            "severity": _infer_entry_severity(row.get("summary") or ""),
            "source_path": row.get("source_path"),
            "source_ref": f"record:{row.get('record_id')}",
        })
    for row in events:
        timeline.append({
            "kind": "event",
            "timestamp_utc": row.get("timestamp_utc"),
            "headline": row.get("message", "")[:160],
            "message": row.get("message", ""),
            "phase": _infer_phase(row.get("message") or row.get("category") or ""),
            "severity": _infer_entry_severity(row.get("message") or row.get("category") or ""),
            "tool_name": row.get("tool_name"),
            "source_ref": row.get("raw_ref"),
        })
    for row in errors:
        timeline.append({
            "kind": "error",
            "timestamp_utc": row.get("timestamp_utc"),
            "headline": f"{row.get('error_type', 'error')}: {(row.get('message') or '').splitlines()[0][:140]}",
            "message": row.get("message", ""),
            "phase": _infer_phase(row.get("message") or row.get("error_type") or "error"),
            "severity": row.get("severity") or "error",
            "error_type": row.get("error_type"),
            "source_ref": row.get("raw_ref"),
        })
    for row in tools:
        action = row.get("action") or "observed"
        headline = f"tool {row.get('tool_name', 'unknown')} {action}".strip()
        timeline.append({
            "kind": "tool",
            "timestamp_utc": row.get("timestamp_utc"),
            "headline": headline,
            "message": headline,
            "phase": _infer_phase(headline),
            "severity": "info",
            "tool_name": row.get("tool_name"),
            "source_ref": row.get("raw_ref"),
        })

    timeline.sort(key=lambda item: (item.get("timestamp_utc", ""), item.get("kind", "")))
    return _collapse_timeline(timeline)


def _collapse_timeline(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collapsed: list[dict[str, Any]] = []
    for item in items:
        if not item.get("headline"):
            continue
        time_bucket = str(item.get("timestamp_utc") or "")[:16]
        signature = semantic_text_fingerprint(item.get("headline") or item.get("message") or "", max_tokens=8)
        key = (item.get("kind"), time_bucket, signature)
        if collapsed:
            prev = collapsed[-1]
            prev_key = (prev.get("kind"), str(prev.get("timestamp_utc") or "")[:16], prev.get("signature"))
            if key == prev_key:
                prev["count"] = int(prev.get("count", 1)) + 1
                prev["headline"] = f"{prev['headline']} (x{prev['count']})"
                continue
        item = dict(item)
        item["signature"] = signature
        item["count"] = 1
        collapsed.append(item)
    return collapsed


def _build_session_insights(records: list[dict[str, Any]], errors: list[dict[str, Any]], tools: list[dict[str, Any]], timeline: list[dict[str, Any]]) -> dict[str, Any]:
    confidence = _session_confidence_from_records(records)
    error_groups = _summarize_error_groups(errors)
    tool_counter = Counter(tool.get("tool_name") for tool in tools if tool.get("tool_name"))
    phases = Counter(item.get("phase") for item in timeline if item.get("phase"))
    dominant_phase = phases.most_common(1)[0][0] if phases else None
    sequence_patterns = _detect_sequence_patterns(timeline)
    probable_root_causes = _rank_probable_root_causes(records, errors, tools, timeline, error_groups)
    topic_counter = Counter(_session_topic_tokens(records, errors, timeline))
    source_families = Counter(_session_source_families(records))
    return {
        "confidence": confidence,
        "dominant_phase": dominant_phase,
        "timeline_items": len(timeline),
        "error_groups": error_groups,
        "tool_summary": [{"tool_name": name, "count": count} for name, count in tool_counter.most_common(10)],
        "phase_breakdown": [{"phase": name, "count": count} for name, count in phases.most_common()],
        "sequence_patterns": sequence_patterns,
        "probable_root_causes": probable_root_causes,
        "topic_summary": [{"token": name, "count": count} for name, count in topic_counter.most_common(12)],
        "source_families": [{"name": name, "count": count} for name, count in source_families.most_common(8)],
    }



ROOT_CAUSE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("dependency_or_import", ("modulenotfounderror", "importerror", "no module named", "dll load failed", "library not loaded", "cannot import")),
    ("filesystem_or_path", ("filenotfounderror", "no such file", "path not found", "permission denied", "access is denied", "read-only file system")),
    ("network_or_remote", ("timeout", "timed out", "connection refused", "connection reset", "dns", "ssl", "certificate", "proxy", "http ", "https ", "download failed")),
    ("resource_or_memory", ("out of memory", "memoryerror", "cannot allocate", "oom", "disk full", "no space left")),
    ("parsing_or_data", ("jsondecodeerror", "yaml", "parse error", "unexpected token", "invalid syntax", "malformed", "decode error")),
    ("build_or_configuration", ("cmake", "ninja", "msbuild", "linker", "undefined reference", "compile error", "build failed", "configuration")),
    ("test_assertion", ("assertionerror", "expected", "actual", "pytest", "test failed", "assert ")) ,
    ("ui_or_rendering", ("pyside6", "qt", "qml", "widget", "render", "paint", "window", "gui")),
    ("runtime_crash", ("runtimeerror", "segmentation fault", "access violation", "panic", "null pointer", "traceback", "exception")),
)

def _session_topic_tokens(records: list[dict[str, Any]], errors: list[dict[str, Any]], timeline: list[dict[str, Any]]) -> list[str]:
    tokens: list[str] = []
    seen: set[str] = set()
    texts: list[str] = []
    texts.extend(str(record.get("summary") or record.get("title") or "") for record in records)
    texts.extend(str(error.get("message") or error.get("error_type") or "") for error in errors)
    texts.extend(str(item.get("headline") or item.get("message") or "") for item in timeline[:50])
    for text in texts:
        for token in keyword_tokens(text, max_tokens=10):
            if token not in seen:
                seen.add(token)
                tokens.append(token)
    return tokens

def _session_source_families(records: list[dict[str, Any]]) -> list[str]:
    families: list[str] = []
    for record in records:
        metadata = record.get("metadata") or {}
        correlation = metadata.get("correlation") or {}
        family = str(correlation.get("source_family") or "").strip()
        if family:
            families.append(family)
    return families

def _detect_sequence_patterns(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phases = [str(item.get("phase") or "") for item in timeline if item.get("phase")]
    compressed: list[str] = []
    for phase in phases:
        if not compressed or compressed[-1] != phase:
            compressed.append(phase)
    patterns: Counter[tuple[str, ...]] = Counter()
    for width in (2, 3, 4):
        for idx in range(0, max(0, len(compressed) - width + 1)):
            chunk = tuple(compressed[idx: idx + width])
            if any(part in {"failure", "repair", "test", "build", "ingest"} for part in chunk):
                patterns[chunk] += 1
    labels = {
        ("build", "test", "failure"): "build_to_test_failure",
        ("ingest", "failure"): "ingest_failure",
        ("ingest", "repair"): "ingest_repair",
        ("test", "failure", "repair"): "test_failure_repair",
        ("build", "failure", "repair"): "build_failure_repair",
        ("start", "build", "test", "failure"): "startup_build_test_failure",
    }
    out: list[dict[str, Any]] = []
    for pattern, count in patterns.most_common(10):
        label = labels.get(pattern)
        severity = "error" if "failure" in pattern else "info"
        out.append({
            "pattern": " > ".join(pattern),
            "count": count,
            "label": label or slugify("_".join(pattern)),
            "severity": severity,
        })
    return out

def _rank_probable_root_causes(
    records: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
    error_groups: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    score_map: dict[str, float] = {}
    evidence_map: dict[str, list[str]] = {}
    corpus: list[str] = []
    corpus.extend(str(record.get("summary") or "") for record in records)
    corpus.extend(str(error.get("message") or error.get("error_type") or "") for error in errors)
    dominant_tools = {str(tool.get("tool_name") or "") for tool in tools if tool.get("tool_name")}
    phase_names = [str(item.get("phase") or "") for item in timeline if item.get("phase")]
    severity_bonus = 1.8 if any((error.get("severity") or "") == "fatal" for error in errors) else 0.8

    lowered_corpus = [text.lower() for text in corpus if text]
    for category, patterns in ROOT_CAUSE_RULES:
        score = 0.0
        evidence: list[str] = []
        for text in lowered_corpus:
            for pattern in patterns:
                if pattern in text:
                    score += 2.6
                    if len(evidence) < 3:
                        evidence.append(text.splitlines()[0][:180])
        if category == "test_assertion" and "pytest" in dominant_tools:
            score += 1.8
        if category == "build_or_configuration" and any(tool in dominant_tools for tool in {"cmake", "make", "ninja", "msbuild"}):
            score += 1.8
        if category == "ui_or_rendering" and any(tool in dominant_tools for tool in {"pyside6", "qt"}):
            score += 1.4
        if category == "runtime_crash" and "failure" in phase_names:
            score += 1.0
        if category == "parsing_or_data" and "ingest" in phase_names:
            score += 1.0
        if score:
            score *= severity_bonus
            score_map[category] = score
            evidence_map[category] = evidence

    for group in error_groups[:5]:
        signature = str(group.get("signature") or group.get("error_type") or "")
        sample = str(group.get("sample_message") or "")
        if any(token in signature for token in ("json", "parse", "yaml", "decode")):
            score_map["parsing_or_data"] = score_map.get("parsing_or_data", 0.0) + 2.0
            evidence_map.setdefault("parsing_or_data", []).append(sample[:180])
        if any(token in signature for token in ("widget", "qt", "pyside", "render")):
            score_map["ui_or_rendering"] = score_map.get("ui_or_rendering", 0.0) + 2.0
            evidence_map.setdefault("ui_or_rendering", []).append(sample[:180])
        if any(token in signature for token in ("timeout", "connect", "proxy", "ssl")):
            score_map["network_or_remote"] = score_map.get("network_or_remote", 0.0) + 2.0
            evidence_map.setdefault("network_or_remote", []).append(sample[:180])
        if any(token in signature for token in ("memory", "oom", "allocate")):
            score_map["resource_or_memory"] = score_map.get("resource_or_memory", 0.0) + 2.0
            evidence_map.setdefault("resource_or_memory", []).append(sample[:180])

    out: list[dict[str, Any]] = []
    for category, score in sorted(score_map.items(), key=lambda item: (-item[1], item[0]))[:8]:
        evidence = []
        seen_evidence: set[str] = set()
        for item in evidence_map.get(category, []):
            normalized = item.strip()
            if normalized and normalized not in seen_evidence:
                seen_evidence.add(normalized)
                evidence.append(normalized)
            if len(evidence) >= 3:
                break
        out.append({
            "category": category,
            "score": round(score, 2),
            "confidence": "high" if score >= 8.5 else "medium" if score >= 4.5 else "low",
            "evidence": evidence,
        })
    if not out and error_groups:
        top = error_groups[0]
        out.append({
            "category": "unknown_runtime_issue",
            "score": 2.0,
            "confidence": "low",
            "evidence": [str(top.get("sample_message") or top.get("signature") or "")[:180]],
        })
    return out

def _build_session_profile(session_id: str, records: list[dict[str, Any]], errors: list[dict[str, Any]], tools: list[dict[str, Any]], timeline: list[dict[str, Any]], insights: dict[str, Any] | None = None) -> dict[str, Any]:
    insights = insights or _build_session_insights(records, errors, tools, timeline)
    error_group_signatures = {str(group.get("signature") or "") for group in insights.get("error_groups", []) if group.get("signature")}
    tool_names = {str(item.get("tool_name") or "") for item in insights.get("tool_summary", []) if item.get("tool_name")}
    phase_set = {str(item.get("phase") or "") for item in insights.get("phase_breakdown", []) if item.get("phase")}
    topic_tokens = {str(item.get("token") or "") for item in insights.get("topic_summary", []) if item.get("token")}
    source_families = {str(item.get("name") or "") for item in insights.get("source_families", []) if item.get("name")}
    metadata_roots: list[str] = []
    for record in records:
        correlation = (record.get("metadata") or {}).get("correlation") or {}
        root = str(correlation.get("session_root") or "").strip()
        if root:
            metadata_roots.append(root)
    summary = next((str(record.get("summary") or "") for record in records if record.get("summary")), "")
    date_bucket = next((str(record.get("timestamp_utc") or "")[:10] for record in records if record.get("timestamp_utc")), None)
    dominant_phase = insights.get("dominant_phase")
    return {
        "session_id": session_id,
        "confidence": insights.get("confidence") or {"label": "unknown", "score": 0.0},
        "error_group_signatures": error_group_signatures,
        "tool_names": tool_names,
        "phase_set": phase_set,
        "topic_tokens": topic_tokens,
        "source_families": source_families,
        "session_roots": set(metadata_roots),
        "date_bucket": date_bucket,
        "dominant_phase": dominant_phase,
        "summary": summary,
        "error_groups": insights.get("error_groups") or [],
    }

def _session_profile_similarity(left: dict[str, Any], right: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    shared_error_groups = sorted(left["error_group_signatures"] & right["error_group_signatures"])
    if shared_error_groups:
        score += 32.0 + min(12.0, 5.0 * (len(shared_error_groups) - 1))
        reasons.append(f"shared error groups: {', '.join(shared_error_groups[:3])}")

    shared_tools = sorted(left["tool_names"] & right["tool_names"])
    if shared_tools:
        score += 14.0 + min(10.0, 3.0 * (len(shared_tools) - 1))
        reasons.append(f"shared tools: {', '.join(shared_tools[:3])}")

    shared_topics = sorted(left["topic_tokens"] & right["topic_tokens"])
    if shared_topics:
        score += min(16.0, 2.0 * len(shared_topics))
        reasons.append(f"shared topics: {', '.join(shared_topics[:4])}")

    shared_phases = sorted(left["phase_set"] & right["phase_set"])
    if shared_phases:
        score += min(10.0, 3.0 * len(shared_phases))
        reasons.append(f"shared phases: {', '.join(shared_phases[:3])}")

    shared_families = sorted(left["source_families"] & right["source_families"])
    if shared_families:
        score += 8.0
        reasons.append(f"same source family: {', '.join(shared_families[:2])}")

    shared_roots = sorted(left["session_roots"] & right["session_roots"])
    if shared_roots:
        score += 6.0
        reasons.append(f"same session root: {', '.join(shared_roots[:2])}")

    left_date = left.get("date_bucket")
    right_date = right.get("date_bucket")
    if left_date and right_date:
        try:
            left_dt = date.fromisoformat(left_date)
            right_dt = date.fromisoformat(right_date)
            delta = abs((left_dt - right_dt).days)
        except Exception:
            delta = None
        if delta == 0:
            score += 6.0
        elif delta == 1:
            score += 2.0

    confidence_bonus = {"high": 3.0, "medium": 1.5, "low": 0.0}
    score += confidence_bonus.get(str(right["confidence"].get("label", "low")), 0.0)

    return score, reasons[:4]

def _find_related_sessions(conn, session_id: str, records: list[dict[str, Any]], errors: list[dict[str, Any]], tools: list[dict[str, Any]], timeline: list[dict[str, Any]], insights: dict[str, Any]) -> list[dict[str, Any]]:
    current_profile = _build_session_profile(session_id, records, errors, tools, timeline, insights)
    candidate_sessions = conn.execute(
        "SELECT session_id FROM sessions WHERE session_id != ? ORDER BY last_seen_at DESC LIMIT 60",
        (session_id,),
    ).fetchall()
    related: list[dict[str, Any]] = []
    for row in candidate_sessions:
        other_session_id = str(row["session_id"])
        other_records = [_deserialize_record(item) for item in conn.execute(
            "SELECT record_id, session_id, timestamp_utc, record_type, source_path, source_hash, title, summary, metadata_json FROM records WHERE session_id = ? ORDER BY timestamp_utc",
            (other_session_id,),
        ).fetchall()]
        other_errors = [dict(item) for item in conn.execute(
            "SELECT error_id, session_id, timestamp_utc, error_type, message, severity, raw_ref FROM errors WHERE session_id = ? ORDER BY timestamp_utc",
            (other_session_id,),
        ).fetchall()]
        other_tools = [dict(item) for item in conn.execute(
            "SELECT tool_id, session_id, timestamp_utc, tool_name, action, raw_ref FROM tools WHERE session_id = ? ORDER BY timestamp_utc",
            (other_session_id,),
        ).fetchall()]
        other_timeline = _build_timeline(other_records, [], other_errors, other_tools)
        other_insights = _build_session_insights(other_records, other_errors, other_tools, other_timeline)
        other_profile = _build_session_profile(other_session_id, other_records, other_errors, other_tools, other_timeline, other_insights)
        score, reasons = _session_profile_similarity(current_profile, other_profile)
        if score < 18:
            continue
        primary_error = next((group.get("error_type") or group.get("signature") for group in other_insights.get("error_groups", [])), None)
        related.append({
            "session_id": other_session_id,
            "score": round(score, 2),
            "confidence": other_profile["confidence"],
            "dominant_phase": other_profile.get("dominant_phase"),
            "primary_error": primary_error,
            "summary": other_profile.get("summary") or primary_error or other_session_id,
            "reasons": reasons,
        })
    related.sort(key=lambda item: (-item["score"], item["session_id"]))
    return related[:8]

def _summarize_global_sequences(conn) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT session_id, timestamp_utc, summary, metadata_json FROM records ORDER BY timestamp_utc"
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["session_id"]), []).append(_row_with_metadata(dict(row)))
    counter: Counter[str] = Counter()
    for session_rows in grouped.values():
        pseudo_timeline = []
        for row in session_rows:
            text = str(row.get("summary") or row.get("record_type") or "")
            pseudo_timeline.append({
                "phase": _infer_phase(text),
                "timestamp_utc": row.get("timestamp_utc"),
                "headline": text,
            })
        for pattern in _detect_sequence_patterns(pseudo_timeline):
            counter[pattern["pattern"]] += max(1, int(pattern.get("count") or 1))
    return [{"pattern": pattern, "count": count} for pattern, count in counter.most_common(12)]

def _session_confidence_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"label": "unknown", "score": 0.0}
    weights = {"low": 0.35, "medium": 0.72, "high": 0.93}
    weighted_scores: list[float] = []
    explicit_count = 0
    correlated_count = 0
    for record in records:
        heuristics = (record.get("metadata") or {}).get("heuristics", {})
        confidence = str(heuristics.get("session_confidence", "low"))
        strategy = str(heuristics.get("session_strategy", "unknown"))
        score = weights.get(confidence, 0.35)
        if strategy.startswith("payload") or strategy.startswith("text") or strategy == "filename-pattern":
            explicit_count += 1
            score += 0.05
        if strategy.startswith("correlated"):
            correlated_count += 1
        correlation_score = float(heuristics.get("correlation_score") or 0)
        if correlation_score:
            score += min(0.12, correlation_score / 1000.0)
        weighted_scores.append(min(score, 0.99))
    avg = sum(weighted_scores) / len(weighted_scores)
    if explicit_count:
        avg += min(0.05, explicit_count / max(len(records), 1) * 0.05)
    if correlated_count and not explicit_count:
        avg -= min(0.08, correlated_count / max(len(records), 1) * 0.08)
    avg = max(0.0, min(avg, 0.99))
    if avg >= 0.85:
        label = "high"
    elif avg >= 0.62:
        label = "medium"
    else:
        label = "low"
    return {"label": label, "score": round(avg, 3), "records": len(records), "explicit_records": explicit_count, "correlated_records": correlated_count}


def _summarize_session_confidence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    session_map: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        session_map.setdefault(str(row.get("session_id") or "unknown"), []).append(_row_with_metadata(row))
    labels = Counter()
    samples: list[dict[str, Any]] = []
    for session_id, session_rows in session_map.items():
        confidence = _session_confidence_from_records(session_rows)
        labels[confidence["label"]] += 1
        samples.append({"session_id": session_id, **confidence})
    samples.sort(key=lambda item: (-item["score"], item["session_id"]))
    return {"distribution": dict(labels), "samples": samples[:20]}


def _summarize_error_groups(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for error in errors:
        message = error.get("message") or error.get("summary") or error.get("text") or ""
        error_type = error.get("error_type") or "error"
        signature = _error_group_signature(message, error_type)
        group = groups.setdefault(signature, {
            "signature": signature,
            "error_type": error_type,
            "error_types": set(),
            "count": 0,
            "severity": error.get("severity") or "error",
            "sample_message": message.splitlines()[0][:180],
        })
        group["count"] += 1
        group["error_types"].add(error_type)
        if len(message) > len(group.get("sample_message", "")):
            group["sample_message"] = message.splitlines()[0][:180]
        if (error.get("severity") or "") == "fatal":
            group["severity"] = "fatal"
    out = []
    for value in groups.values():
        value["error_types"] = sorted(value["error_types"])
        out.append(value)
    return sorted(out, key=lambda item: (-item["count"], item["error_type"], item["signature"]))


def _error_group_signature(message: str, error_type: str) -> str:
    generic = {"error", "errors", "failure", "failed", "fatal", "warning", "traceback", "exception", "python", "pytest", "pyside6", "line", "path", "str"}
    tokens = [
        token
        for token in keyword_tokens(message, max_tokens=12)
        if token not in generic and not token.endswith("error") and not token.endswith("exception")
    ]
    if tokens:
        return slugify("-".join(tokens[:4]))
    return semantic_text_fingerprint(message or error_type, max_tokens=6)


def _phase_activity_from_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter = Counter()
    for row in rows:
        payload = _row_with_metadata(row)
        summary = str(payload.get("summary") or "")
        phase = _infer_phase(summary)
        counter[phase] += 1
    return [{"phase": name, "count": count} for name, count in counter.most_common()]


def _row_with_metadata(row: dict[str, Any]) -> dict[str, Any]:
    if "metadata" in row:
        return row
    metadata_raw = row.get("metadata_json") or "{}"
    try:
        metadata = json.loads(metadata_raw)
    except Exception:
        metadata = {}
    payload = dict(row)
    payload["metadata"] = metadata
    return payload


def _infer_phase(text: str) -> str:
    lowered = (text or "").lower()
    if any(token in lowered for token in ("build", "compile", "cmake", "make")):
        return "build"
    if any(token in lowered for token in ("test", "pytest", "assert")):
        return "test"
    if any(token in lowered for token in ("repair", "recover", "integrity", "rebuild index")):
        return "repair"
    if any(token in lowered for token in ("ingest", "scan", "parse", "normalize")):
        return "ingest"
    if any(token in lowered for token in ("export", "write", "save", "copy")):
        return "output"
    if any(token in lowered for token in ("error", "exception", "fatal", "fail", "panic", "traceback")):
        return "failure"
    if any(token in lowered for token in ("start", "begin", "boot", "launch")):
        return "start"
    if any(token in lowered for token in ("finish", "complete", "done", "success")):
        return "finish"
    tokens = keyword_tokens(lowered, max_tokens=1)
    return tokens[0] if tokens else "event"


def _infer_entry_severity(text: str) -> str:
    lowered = (text or "").lower()
    if any(token in lowered for token in ("fatal", "panic", "segmentation fault")):
        return "fatal"
    if any(token in lowered for token in ("error", "exception", "fail", "traceback")):
        return "error"
    if "warn" in lowered:
        return "warning"
    return "info"

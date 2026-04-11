from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable
from typing import Any

from synapse_x.models import CanonicalRecord
from synapse_x.utils import compact_json, utc_now_iso


SCHEMA_SQL = '''
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    type TEXT,
    size_bytes INTEGER NOT NULL,
    mtime_utc TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    last_ingested_at TEXT,
    ingest_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    first_seen_at TEXT,
    last_seen_at TEXT,
    source_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'ok'
);

CREATE TABLE IF NOT EXISTS records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    record_type TEXT NOT NULL,
    source_path TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    title TEXT,
    summary TEXT,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    category TEXT NOT NULL,
    message TEXT NOT NULL,
    tool_name TEXT,
    raw_ref TEXT,
    FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS errors (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    error_type TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT,
    raw_ref TEXT,
    FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tools (
    tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    action TEXT,
    raw_ref TEXT,
    FOREIGN KEY(record_id) REFERENCES records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ingest_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    files_seen INTEGER NOT NULL DEFAULT 0,
    files_processed INTEGER NOT NULL DEFAULT 0,
    errors_count INTEGER NOT NULL DEFAULT 0,
    diagnostics_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_records_session_ts ON records(session_id, timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_events_session_ts ON events(session_id, timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_errors_session_ts ON errors(session_id, timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_tools_session_ts ON tools(session_id, timestamp_utc);

CREATE TABLE IF NOT EXISTS search_index_plain (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    record_type TEXT NOT NULL,
    text TEXT NOT NULL,
    source_path TEXT NOT NULL
);
'''

FTS_SQL = '''
CREATE VIRTUAL TABLE IF NOT EXISTS search_index_fts USING fts5(
    session_id,
    timestamp_utc,
    record_type,
    text,
    source_path
);
'''


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        try:
            conn.executescript(FTS_SQL)
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
        conn.close()


def has_fts(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='search_index_fts'"
    ).fetchone()
    return bool(row)


def get_file_state(conn: sqlite3.Connection, path: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT path, size_bytes, mtime_utc, content_hash, ingest_status FROM files WHERE path = ?",
        (path,),
    ).fetchone()
    return dict(row) if row else None


def upsert_file_state(
    conn: sqlite3.Connection,
    *,
    path: str,
    record_type: str,
    size_bytes: int,
    mtime_utc: str,
    content_hash: str,
    ingest_status: str,
) -> None:
    conn.execute(
        '''
        INSERT INTO files(path, type, size_bytes, mtime_utc, content_hash, last_ingested_at, ingest_status)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            type=excluded.type,
            size_bytes=excluded.size_bytes,
            mtime_utc=excluded.mtime_utc,
            content_hash=excluded.content_hash,
            last_ingested_at=excluded.last_ingested_at,
            ingest_status=excluded.ingest_status
        ''',
        (path, record_type, size_bytes, mtime_utc, content_hash, utc_now_iso(), ingest_status),
    )


def delete_record_data_for_source(conn: sqlite3.Connection, source_path: str) -> set[str]:
    session_rows = conn.execute(
        "SELECT DISTINCT session_id FROM records WHERE source_path = ?",
        (source_path,),
    ).fetchall()
    impacted_sessions = {str(row["session_id"]) for row in session_rows}
    record_rows = conn.execute(
        "SELECT record_id FROM records WHERE source_path = ?",
        (source_path,),
    ).fetchall()
    record_ids = [row["record_id"] for row in record_rows]
    if record_ids:
        placeholders = ",".join("?" for _ in record_ids)
        conn.execute(f"DELETE FROM events WHERE record_id IN ({placeholders})", record_ids)
        conn.execute(f"DELETE FROM errors WHERE record_id IN ({placeholders})", record_ids)
        conn.execute(f"DELETE FROM tools WHERE record_id IN ({placeholders})", record_ids)
    conn.execute("DELETE FROM records WHERE source_path = ?", (source_path,))
    conn.execute("DELETE FROM search_index_plain WHERE source_path = ?", (source_path,))
    if has_fts(conn):
        conn.execute("DELETE FROM search_index_fts WHERE source_path = ?", (source_path,))
    return impacted_sessions


def refresh_session_rollups(conn: sqlite3.Connection, session_ids: Iterable[str]) -> None:
    normalized = {str(session_id).strip() for session_id in session_ids if str(session_id).strip()}
    for session_id in normalized:
        row = conn.execute(
            "SELECT MIN(timestamp_utc) AS first_seen_at, MAX(timestamp_utc) AS last_seen_at, COUNT(*) AS source_count FROM records WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row or int(row["source_count"] or 0) == 0:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            continue
        conn.execute(
            '''
            INSERT INTO sessions(session_id, first_seen_at, last_seen_at, source_count, status)
            VALUES(?, ?, ?, ?, 'ok')
            ON CONFLICT(session_id) DO UPDATE SET
                first_seen_at=excluded.first_seen_at,
                last_seen_at=excluded.last_seen_at,
                source_count=excluded.source_count,
                status='ok'
            ''',
            (session_id, row["first_seen_at"], row["last_seen_at"], int(row["source_count"] or 0)),
        )


def store_record(conn: sqlite3.Connection, record: CanonicalRecord) -> int:
    impacted_sessions = delete_record_data_for_source(conn, record.source_path)

    cursor = conn.execute(
        '''
        INSERT INTO records(session_id, timestamp_utc, record_type, source_path, source_hash, title, summary, metadata_json)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            record.session_id,
            record.timestamp_utc,
            record.record_type,
            record.source_path,
            record.source_hash,
            record.title,
            record.summary,
            compact_json(record.metadata),
        ),
    )
    record_id = int(cursor.lastrowid)

    for event in record.events:
        conn.execute(
            '''
            INSERT INTO events(record_id, session_id, timestamp_utc, category, message, tool_name, raw_ref)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                record_id,
                record.session_id,
                event.get("timestamp_utc", record.timestamp_utc),
                event.get("category", "event"),
                event.get("message", ""),
                event.get("tool_name"),
                event.get("raw_ref"),
            ),
        )

    for error in record.errors:
        conn.execute(
            '''
            INSERT INTO errors(record_id, session_id, timestamp_utc, error_type, message, severity, raw_ref)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                record_id,
                record.session_id,
                error.get("timestamp_utc", record.timestamp_utc),
                error.get("error_type", "error"),
                error.get("message", ""),
                error.get("severity", "error"),
                error.get("raw_ref"),
            ),
        )

    for tool in record.tools:
        conn.execute(
            '''
            INSERT INTO tools(record_id, session_id, timestamp_utc, tool_name, action, raw_ref)
            VALUES(?, ?, ?, ?, ?, ?)
            ''',
            (
                record_id,
                record.session_id,
                tool.get("timestamp_utc", record.timestamp_utc),
                tool.get("tool_name", "unknown"),
                tool.get("action", "observed"),
                tool.get("raw_ref"),
            ),
        )

    _index_record(conn, record)
    impacted_sessions.add(record.session_id)
    refresh_session_rollups(conn, impacted_sessions)
    return record_id


def _index_record(conn: sqlite3.Connection, record: CanonicalRecord) -> None:
    chunks = [
        (record.session_id, record.timestamp_utc, record.record_type, record.summary or record.title or "", record.source_path)
    ]
    for event in record.events:
        chunks.append((record.session_id, event.get("timestamp_utc", record.timestamp_utc), "event", event.get("message", ""), record.source_path))
    for error in record.errors:
        chunks.append((record.session_id, error.get("timestamp_utc", record.timestamp_utc), "error", error.get("message", ""), record.source_path))
    for tool in record.tools:
        chunks.append((record.session_id, tool.get("timestamp_utc", record.timestamp_utc), "tool", f"{tool.get('tool_name', '')} {tool.get('action', '')}".strip(), record.source_path))

    conn.executemany(
        "INSERT INTO search_index_plain(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)",
        chunks,
    )

    if has_fts(conn):
        conn.executemany(
            "INSERT INTO search_index_fts(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)",
            chunks,
        )


def create_ingest_run(conn: sqlite3.Connection, mode: str) -> int:
    cursor = conn.execute(
        "INSERT INTO ingest_runs(started_at, mode, status, diagnostics_json) VALUES(?, ?, 'running', '{}')",
        (utc_now_iso(), mode),
    )
    return int(cursor.lastrowid)


def finalize_ingest_run(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    status: str,
    files_seen: int,
    files_processed: int,
    errors_count: int,
    diagnostics: dict[str, Any],
) -> None:
    conn.execute(
        '''
        UPDATE ingest_runs
        SET finished_at = ?, status = ?, files_seen = ?, files_processed = ?, errors_count = ?, diagnostics_json = ?
        WHERE run_id = ?
        ''',
        (utc_now_iso(), status, files_seen, files_processed, errors_count, json.dumps(diagnostics, ensure_ascii=False), run_id),
    )


def rebuild_search_indexes(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM search_index_plain")
    if has_fts(conn):
        conn.execute("DELETE FROM search_index_fts")

    rows = conn.execute("SELECT session_id, timestamp_utc, record_type, summary, source_path FROM records").fetchall()
    for row in rows:
        payload = (row["session_id"], row["timestamp_utc"], row["record_type"], row["summary"] or "", row["source_path"])
        conn.execute("INSERT INTO search_index_plain(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)
        if has_fts(conn):
            conn.execute("INSERT INTO search_index_fts(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)

    event_rows = conn.execute("SELECT session_id, timestamp_utc, message, raw_ref FROM events").fetchall()
    for row in event_rows:
        payload = (row["session_id"], row["timestamp_utc"], "event", row["message"], row["raw_ref"] or "")
        conn.execute("INSERT INTO search_index_plain(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)
        if has_fts(conn):
            conn.execute("INSERT INTO search_index_fts(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)

    error_rows = conn.execute("SELECT session_id, timestamp_utc, message, raw_ref FROM errors").fetchall()
    for row in error_rows:
        payload = (row["session_id"], row["timestamp_utc"], "error", row["message"], row["raw_ref"] or "")
        conn.execute("INSERT INTO search_index_plain(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)
        if has_fts(conn):
            conn.execute("INSERT INTO search_index_fts(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)

    tool_rows = conn.execute("SELECT session_id, timestamp_utc, tool_name, action, raw_ref FROM tools").fetchall()
    for row in tool_rows:
        text = f"{row['tool_name']} {row['action'] or ''}".strip()
        payload = (row["session_id"], row["timestamp_utc"], "tool", text, row["raw_ref"] or "")
        conn.execute("INSERT INTO search_index_plain(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)
        if has_fts(conn):
            conn.execute("INSERT INTO search_index_fts(session_id, timestamp_utc, record_type, text, source_path) VALUES(?, ?, ?, ?, ?)", payload)


def integrity_check(conn: sqlite3.Connection) -> str:
    row = conn.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "unknown"

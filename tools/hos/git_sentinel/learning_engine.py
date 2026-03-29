#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .git_utils import git_top_modified_files
from .config import SentinelConfig
from .utils import now_utc_iso


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS artifact_patterns (
  pattern TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  count INTEGER NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  last_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS folder_activity (
  folder TEXT PRIMARY KEY,
  artifact_count INTEGER NOT NULL,
  source_count INTEGER NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS telemetry_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  repo_size_bytes INTEGER NOT NULL,
  artifact_count INTEGER NOT NULL,
  health_score INTEGER NOT NULL,
  cleanup_deleted INTEGER NOT NULL,
  error_count INTEGER NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prediction_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  kind TEXT NOT NULL,
  risk TEXT NOT NULL,
  score REAL NOT NULL,
  detail TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS security_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  severity TEXT NOT NULL,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  fingerprint TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS file_churn (
  path TEXT PRIMARY KEY,
  commit_count INTEGER NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL
);
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    return connection


def ensure_schema(config: SentinelConfig) -> None:
    with _connect(config.db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()


def update_learning_database(
    config: SentinelConfig,
    artifact_result: dict[str, Any],
    scan_state: dict[str, Any],
) -> dict[str, Any]:
    ensure_schema(config)
    now = now_utc_iso()

    artifact_rows = artifact_result.get("artifacts", [])
    source_rows = artifact_result.get("sourceFiles", [])
    folders: dict[str, dict[str, int]] = {}

    with _connect(config.db_path) as connection:
        cursor = connection.cursor()
        for row in artifact_rows:
            pattern = str(row.get("pattern", "")).strip()
            category = str(row.get("category", "unknown")).strip() or "unknown"
            rel_path = str(row.get("path", "")).strip()
            if not pattern:
                continue
            cursor.execute(
                """
                INSERT INTO artifact_patterns(pattern, category, count, first_seen, last_seen, last_path)
                VALUES(?, ?, 1, ?, ?, ?)
                ON CONFLICT(pattern) DO UPDATE SET
                  category=excluded.category,
                  count=artifact_patterns.count + 1,
                  last_seen=excluded.last_seen,
                  last_path=excluded.last_path
                """,
                (pattern, category, now, now, rel_path),
            )
            folder = rel_path.split("/", 1)[0] if "/" in rel_path else rel_path
            bucket = folders.setdefault(folder, {"artifact": 0, "source": 0})
            bucket["artifact"] += 1

        for path in source_rows:
            folder = str(path).split("/", 1)[0] if "/" in str(path) else str(path)
            bucket = folders.setdefault(folder, {"artifact": 0, "source": 0})
            bucket["source"] += 1

        for folder, counts in folders.items():
            cursor.execute(
                """
                INSERT INTO folder_activity(folder, artifact_count, source_count, first_seen, last_seen)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(folder) DO UPDATE SET
                  artifact_count=folder_activity.artifact_count + excluded.artifact_count,
                  source_count=folder_activity.source_count + excluded.source_count,
                  last_seen=excluded.last_seen
                """,
                (folder, counts["artifact"], counts["source"], now, now),
            )

        # Commit modification patterns (90-day window) for adaptive stability learning.
        top_modified = git_top_modified_files(config.repo_root, days=90, limit=2000)
        for row in top_modified:
            path = str(row.get("path", ""))
            commits = int(row.get("commits", 0))
            if not path:
                continue
            cursor.execute(
                """
                INSERT INTO file_churn(path, commit_count, first_seen, last_seen)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                  commit_count=excluded.commit_count,
                  last_seen=excluded.last_seen
                """,
                (path, commits, now, now),
            )

        connection.commit()

        top_patterns = cursor.execute(
            """
            SELECT pattern, category, count, last_seen
            FROM artifact_patterns
            ORDER BY count DESC, pattern ASC
            LIMIT 50
            """
        ).fetchall()

        stable_rows = cursor.execute(
            """
            SELECT path, commit_count
            FROM file_churn
            WHERE commit_count <= 1
            ORDER BY path ASC
            LIMIT 200
            """
        ).fetchall()

    return {
        "updatedAt": now,
        "artifactRowsObserved": len(artifact_rows),
        "sourceRowsObserved": len(source_rows),
        "folderBucketsTouched": len(folders),
        "topPatterns": [
            {
                "pattern": row[0],
                "category": row[1],
                "count": int(row[2]),
                "lastSeen": row[3],
            }
            for row in top_patterns
        ],
        "rarelyChangedFiles": [row[0] for row in stable_rows],
        "scanSummary": scan_state.get("summary", {}),
    }


def read_learned_patterns(config: SentinelConfig, min_count: int = 2, limit: int = 200) -> list[dict[str, Any]]:
    ensure_schema(config)
    with _connect(config.db_path) as connection:
        rows = connection.execute(
            """
            SELECT pattern, category, count, last_seen
            FROM artifact_patterns
            WHERE count >= ?
            ORDER BY count DESC, pattern ASC
            LIMIT ?
            """,
            (max(1, min_count), max(1, limit)),
        ).fetchall()
    return [
        {
            "pattern": row[0],
            "category": row[1],
            "count": int(row[2]),
            "lastSeen": row[3],
        }
        for row in rows
    ]


def write_telemetry_snapshot(config: SentinelConfig, payload: dict[str, Any]) -> None:
    ensure_schema(config)
    ts = str(payload.get("timestamp", now_utc_iso()))
    repo_size = int(payload.get("repositorySizeBytes", 0))
    artifact_count = int(payload.get("artifactCount", 0))
    health_score = int(payload.get("healthScore", 0))
    cleanup_deleted = int(payload.get("cleanupDeleted", 0))
    error_count = int(payload.get("errorCount", 0))
    payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    with _connect(config.db_path) as connection:
        connection.execute(
            """
            INSERT INTO telemetry_history(
              ts, repo_size_bytes, artifact_count, health_score, cleanup_deleted, error_count, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, repo_size, artifact_count, health_score, cleanup_deleted, error_count, payload_json),
        )
        connection.commit()


def read_telemetry_history(config: SentinelConfig, limit: int = 30) -> list[dict[str, Any]]:
    ensure_schema(config)
    with _connect(config.db_path) as connection:
        rows = connection.execute(
            """
            SELECT ts, payload_json
            FROM telemetry_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()
    history: list[dict[str, Any]] = []
    for ts, payload_json in reversed(rows):
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError:
            payload = {"timestamp": ts}
        history.append(payload)
    return history


def write_prediction_history(config: SentinelConfig, predictions: list[dict[str, Any]]) -> None:
    if not predictions:
        return
    ensure_schema(config)
    ts = now_utc_iso()
    with _connect(config.db_path) as connection:
        for row in predictions:
            connection.execute(
                """
                INSERT INTO prediction_history(ts, kind, risk, score, detail)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    str(row.get("kind", "unknown")),
                    str(row.get("risk", "low")),
                    float(row.get("score", 0.0)),
                    str(row.get("detail", "")),
                ),
            )
        connection.commit()


def write_security_history(config: SentinelConfig, findings: list[dict[str, Any]]) -> None:
    if not findings:
        return
    ensure_schema(config)
    ts = now_utc_iso()
    with _connect(config.db_path) as connection:
        for row in findings:
            connection.execute(
                """
                INSERT INTO security_history(ts, severity, kind, path, fingerprint)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    str(row.get("severity", "low")),
                    str(row.get("kind", "unknown")),
                    str(row.get("path", "")),
                    str(row.get("fingerprint", "")),
                ),
            )
        connection.commit()


def read_folder_activity(config: SentinelConfig, limit: int = 100) -> list[dict[str, Any]]:
    ensure_schema(config)
    with _connect(config.db_path) as connection:
        rows = connection.execute(
            """
            SELECT folder, artifact_count, source_count, last_seen
            FROM folder_activity
            ORDER BY artifact_count DESC, folder ASC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()
    return [
        {
            "folder": row[0],
            "artifactCount": int(row[1]),
            "sourceCount": int(row[2]),
            "lastSeen": row[3],
        }
        for row in rows
    ]


def read_file_churn(config: SentinelConfig, limit: int = 200) -> list[dict[str, Any]]:
    ensure_schema(config)
    with _connect(config.db_path) as connection:
        rows = connection.execute(
            """
            SELECT path, commit_count, last_seen
            FROM file_churn
            ORDER BY commit_count DESC, path ASC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()
    return [
        {
            "path": row[0],
            "commitCount90d": int(row[1]),
            "lastSeen": row[2],
        }
        for row in rows
    ]


@dataclass(frozen=True)
class HealthTrend:
    size_delta: int
    artifact_delta: int
    health_delta: int


def compute_health_trend(history: list[dict[str, Any]]) -> HealthTrend:
    if len(history) < 2:
        return HealthTrend(size_delta=0, artifact_delta=0, health_delta=0)
    start = history[0]
    end = history[-1]
    return HealthTrend(
        size_delta=int(end.get("repositorySizeBytes", 0)) - int(start.get("repositorySizeBytes", 0)),
        artifact_delta=int(end.get("artifactCount", 0)) - int(start.get("artifactCount", 0)),
        health_delta=int(end.get("healthScore", 0)) - int(start.get("healthScore", 0)),
    )

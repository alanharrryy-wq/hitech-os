#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


TERMINAL_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_ROOT = TERMINAL_ROOT / "prisma" / "migrations"
DEFAULT_DB = TERMINAL_ROOT.parents[1] / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db"


def parse_database_url(value: str) -> Path:
    if not value.startswith("file:"):
        raise ValueError("Only sqlite file: DATABASE_URL values are supported by this runner.")
    raw = value.removeprefix("file:")
    path = Path(raw)
    if not path.is_absolute():
        path = (TERMINAL_ROOT / "prisma" / path).resolve()
    return path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_migration_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS "_prisma_migrations" (
          "id" TEXT NOT NULL PRIMARY KEY,
          "checksum" TEXT NOT NULL,
          "finished_at" DATETIME,
          "migration_name" TEXT NOT NULL UNIQUE,
          "logs" TEXT,
          "rolled_back_at" DATETIME,
          "started_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          "applied_steps_count" INTEGER NOT NULL DEFAULT 0
        )
        """
    )


def applied_migrations(conn: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in conn.execute(
            "SELECT migration_name FROM _prisma_migrations WHERE finished_at IS NOT NULL AND rolled_back_at IS NULL"
        ).fetchall()
    }


def migration_dirs() -> list[Path]:
    return sorted(path for path in MIGRATIONS_ROOT.iterdir() if path.is_dir() and (path / "migration.sql").exists())


def apply_migration(conn: sqlite3.Connection, path: Path) -> dict:
    sql_path = path / "migration.sql"
    sql = sql_path.read_text(encoding="utf-8")
    checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
    started = now()
    migration_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO _prisma_migrations
          (id, checksum, migration_name, started_at, applied_steps_count)
        VALUES (?, ?, ?, ?, 0)
        """,
        (migration_id, checksum, path.name, started),
    )
    try:
        conn.executescript(sql)
    except Exception as exc:
        conn.execute(
            """
            UPDATE _prisma_migrations
            SET logs = ?
            WHERE id = ?
            """,
            (str(exc), migration_id),
        )
        raise
    conn.execute(
        """
        UPDATE _prisma_migrations
        SET finished_at = ?, applied_steps_count = 1
        WHERE id = ?
        """,
        (now(), migration_id),
    )
    return {"migration_name": path.name, "checksum": checksum, "applied": True}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply canonical Prisma SQLite migrations deterministically.")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL", ""))
    args = parser.parse_args()

    database_url = args.database_url or "file:" + DEFAULT_DB.resolve().as_posix()
    db_path = parse_database_url(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    report = {"database": str(db_path), "migrations": []}
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        ensure_migration_table(conn)
        applied = applied_migrations(conn)
        for migration in migration_dirs():
            if migration.name in applied:
                report["migrations"].append({"migration_name": migration.name, "applied": False, "reason": "already_applied"})
                continue
            report["migrations"].append(apply_migration(conn, migration))
        conn.commit()

    report["pass"] = True
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"pass": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)

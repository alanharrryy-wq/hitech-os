#!/usr/bin/env python3
"""Focused verifier for PRISMA Tri-DB UPSERT conflict targets.

The production failure this guards against is SQLite rejecting an UPSERT where
the conflict target only matches a partial unique index.
"""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "tools" / "prisma" / "tri_db_bridge.py"


def load_bridge():
    spec = importlib.util.spec_from_file_location("tri_db_bridge_under_test", BRIDGE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No pude cargar {BRIDGE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["tri_db_bridge_under_test"] = module
    spec.loader.exec_module(module)
    return module


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn


def create_cash_session_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE CashSession (
          id TEXT NOT NULL PRIMARY KEY,
          businessId TEXT NOT NULL,
          storeId TEXT NOT NULL,
          terminalId TEXT NOT NULL,
          cashierId TEXT NOT NULL,
          cashier TEXT NOT NULL,
          openedAt DATETIME NOT NULL,
          closedAt DATETIME,
          cashStartCents INTEGER NOT NULL,
          cashEndCents INTEGER,
          expectedCashCents INTEGER,
          varianceCents INTEGER,
          status TEXT NOT NULL,
          createdAt DATETIME NOT NULL,
          updatedAt DATETIME NOT NULL,
          UNIQUE(id, businessId)
        );
        CREATE UNIQUE INDEX uq_cashsession_single_open_per_terminal
          ON CashSession(businessId, terminalId)
          WHERE status = 'OPEN';
        """
    )


def insert_source_cash_session(conn: sqlite3.Connection) -> None:
    now = "2026-05-10T19:30:00.000Z"
    conn.execute(
        """
        INSERT INTO CashSession (
          id, businessId, storeId, terminalId, cashierId, cashier, openedAt,
          closedAt, cashStartCents, cashEndCents, expectedCashCents,
          varianceCents, status, createdAt, updatedAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "cash_01",
            "biz_tablet_standalone",
            "store_01",
            "terminal_tablet_local_01",
            "cashier_01",
            "Caja",
            now,
            None,
            50000,
            None,
            51500,
            None,
            "OPEN",
            now,
            now,
        ),
    )


def main() -> int:
    bridge = load_bridge()
    src = connect()
    dst = connect()
    try:
        create_cash_session_schema(src)
        create_cash_session_schema(dst)
        insert_source_cash_session(src)

        common = [c for c in bridge.columns(src, "CashSession") if c in bridge.columns(dst, "CashSession")]
        pk = bridge.primary_key_columns(dst, "CashSession")
        unique_sets = bridge.unique_index_columns(dst, "CashSession")
        conflict = bridge.choose_conflict_keys(dst, "CashSession", common, pk)

        if ["businessId", "terminalId"] in unique_sets:
            raise AssertionError("Partial unique index was exposed as a valid UPSERT target")
        if conflict != ["id"]:
            raise AssertionError(f"Expected CashSession conflict target ['id'], got {conflict!r}")

        id_maps: dict[str, dict[str, str]] = {}
        first = bridge.copy_table(src, dst, "CashSession", id_maps)
        second = bridge.copy_table(src, dst, "CashSession", id_maps)
        row_count = bridge.count_rows(dst, "CashSession")
        if row_count != 1:
            raise AssertionError(f"Expected idempotent row count 1, got {row_count}")

        print(
            json.dumps(
                {
                    "ok": True,
                    "bridge": str(BRIDGE_PATH),
                    "table": "CashSession",
                    "partialUniqueIgnored": True,
                    "conflictTarget": conflict,
                    "firstCopyRows": first.inserted_or_updated,
                    "secondCopyRows": second.inserted_or_updated,
                    "rowCount": row_count,
                },
                indent=2,
            )
        )
        return 0
    finally:
        src.close()
        dst.close()


if __name__ == "__main__":
    raise SystemExit(main())

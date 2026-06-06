#!/usr/bin/env python3
"""
PRISMA Tri-DB Bridge v04

Purpose:
  rescue/backfill/diagnostic projection from the Tablet local SQLite DB into the
  PC canonical SQLite DB. This bridge is not the primary PRISMA sync path.
  Normal business sync must use Tablet semantic outbox events -> PC ingest ->
  Prisma ORM projectors -> canonical DB.

Design:
  - Tablet remains the local POS write owner for sales, stock movements, and outbox.
  - PC receives an emergency row projection by common table/column shape.
  - Mobile keeps reading Tablet/PC APIs; it does not get a local DB bolted on.
  - A bridge-side "acked" update is a compatibility marker only; it is not proof
    that PC governance validated, projected, and reconciled the event.

Safety:
  - No deletes.
  - Backups before DB writes.
  - Rollback on any sync failure.
  - Explicit paths, no cwd assumptions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

VERSION = "20260506_v04"
DEFAULT_OUT_ROOT = Path(r"F:\descargasf")

NATURAL_CONFLICT_KEYS: dict[str, list[list[str]]] = {
    # Prefer business-scoped natural keys when PC already has the same logical row
    # with different local ids. v04 maps Tablet source ids to PC destination ids and
    # rewrites child foreign keys before insert/update.
    "Store": [["businessId", "code"]],
    "Terminal": [["businessId", "code"]],
    "TaxRate": [["businessId", "name"]],
    "Product": [["businessId", "sku"]],
    "Barcode": [["businessId", "code"]],
    "CashSession": [["businessId", "terminalId"]],
    "PriceList": [["businessId", "name"]],
    "PriceListItem": [["businessId", "priceListId", "productId", "startsAt"]],
    "StockSnapshot": [["businessId", "productId", "location"]],
    "Supplier": [["businessId", "name"]],
    "PurchaseOrder": [["businessId", "folio"]],
    "GoodsReceipt": [["businessId", "folio"]],
    "Sale": [["businessId", "folio"], ["businessId", "clientRequestId"]],
}

FK_ID_COLUMNS: dict[str, dict[str, str]] = {
    "Terminal": {"storeId": "Store"},
    "Product": {"taxRateId": "TaxRate"},
    "Barcode": {"productId": "Product"},
    "PriceListItem": {"priceListId": "PriceList", "productId": "Product"},
    "StockSnapshot": {"productId": "Product"},
    "PurchaseOrderLine": {"purchaseOrderId": "PurchaseOrder", "productId": "Product"},
    "GoodsReceiptLine": {"receiptId": "GoodsReceipt", "productId": "Product"},
    "ReplenishmentSignal": {"productId": "Product"},
    "CashSession": {"terminalId": "Terminal"},
    "CashMovement": {"cashSessionId": "CashSession"},
    "Sale": {"terminalId": "Terminal", "cashSessionId": "CashSession"},
    "SaleLine": {"saleId": "Sale", "productId": "Product"},
    "SaleReturn": {"saleId": "Sale"},
    "StockMovement": {"productId": "Product"},
}

TABLE_ORDER = [
    "Business",
    "Store",
    "Terminal",
    "TaxRate",
    "Product",
    "Barcode",
    "PriceList",
    "PriceListItem",
    "StockSnapshot",
    "Supplier",
    "PurchaseOrder",
    "PurchaseOrderLine",
    "GoodsReceipt",
    "GoodsReceiptLine",
    "ReplenishmentSignal",
    "CashSession",
    "CashMovement",
    "Sale",
    "SaleLine",
    "SaleReturn",
    "AuditCount",
    "StockMovement",
    "OutboxEvent",
]
REQUIRED_TABLES_MINIMUM = ["Business", "Store", "Terminal", "Product", "Sale", "SaleLine", "OutboxEvent"]
TABLET_DB_CANDIDATES = [
    Path("products/tablet/app/data/tablet-pos.db"),
    Path("products/tablet/app/prisma/data/tablet-pos.db"),
    Path("products/tablet/data/tablet-pos.db"),
]


class BridgeError(RuntimeError):
    pass


@dataclass
class RootInfo:
    target_root: str
    terminal_root: str
    repo_root: str
    tablet_db: str
    pc_db: str


@dataclass
class TableCopyResult:
    table: str
    source_rows: int
    inserted_or_updated: int
    common_columns: list[str]
    skipped: bool = False
    reason: str | None = None


@dataclass
class BridgeSummary:
    version: str
    mode: str
    status: str
    generated_at: str
    roots: RootInfo
    backup_dir: str | None
    tables: list[TableCopyResult]
    tablet_outbox_acknowledged: int
    governance_reconciled: int
    bridge_role: str
    warnings: list[str]


def now_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def resolve_terminal_root(target_root: Path) -> Path:
    root = target_root.expanduser().resolve()
    if (root / "terminal_de_venta.cmd").exists() and (root / "products").exists():
        return root
    nested = root / "apps" / "terminal-de-venta-system"
    if (nested / "terminal_de_venta.cmd").exists() and (nested / "products").exists():
        return nested.resolve()
    raise BridgeError(
        "No encontré terminal_de_venta.cmd. Usa --target-root con F:\\repos\\hitech-os "
        "o con F:\\repos\\hitech-os\\apps\\terminal-de-venta-system."
    )


def resolve_repo_root(terminal_root: Path) -> Path:
    # terminal_root = <repo>/apps/terminal-de-venta-system
    if terminal_root.parent.name.lower() == "apps":
        return terminal_root.parent.parent.resolve()
    return terminal_root.resolve()


def pick_tablet_db(terminal_root: Path, explicit: str | None) -> Path:
    if explicit:
        db = Path(explicit).expanduser().resolve()
        if not db.exists():
            raise BridgeError(f"Tablet DB explícita no existe: {db}")
        if db.stat().st_size <= 0:
            raise BridgeError(f"Tablet DB explícita está vacía: {db}")
        return db
    candidates = [(terminal_root / rel).resolve() for rel in TABLET_DB_CANDIDATES]
    non_empty = [p for p in candidates if p.exists() and p.stat().st_size > 0]
    if not non_empty:
        found = ", ".join(str(p) for p in candidates if p.exists()) or "ninguna"
        raise BridgeError(f"No encontré una Tablet DB no vacía. Encontradas: {found}")
    # Prefer the runtime data DB over Prisma scratch DB.
    return non_empty[0]


def resolve_pc_db(terminal_root: Path, repo_root: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    candidates = [
        terminal_root / "products" / "pc" / "app" / "data" / "canonical.db",
        repo_root / "apps" / "terminal-de-venta-system" / "products" / "pc" / "app" / "data" / "canonical.db",
        repo_root / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate.resolve()
    return candidates[0].resolve()


def resolve_roots(target_root: str, tablet_db: str | None, pc_db: str | None) -> RootInfo:
    terminal_root = resolve_terminal_root(Path(target_root))
    repo_root = resolve_repo_root(terminal_root)
    src_db = pick_tablet_db(terminal_root, tablet_db)
    dst_db = resolve_pc_db(terminal_root, repo_root, pc_db)
    return RootInfo(
        target_root=str(Path(target_root).expanduser().resolve()),
        terminal_root=str(terminal_root),
        repo_root=str(repo_root),
        tablet_db=str(src_db),
        pc_db=str(dst_db),
    )


def connect(db_path: Path, readonly: bool = False) -> sqlite3.Connection:
    if readonly:
        uri = f"file:{db_path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
    else:
        conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn




@contextmanager
def open_db(db_path: Path, readonly: bool = False) -> Iterable[sqlite3.Connection]:
    """Open a SQLite connection and always close it.

    sqlite3.Connection used as a context manager only commits or rolls back;
    it does not close the OS handle. On Windows that leaves .db files locked
    long enough for tempfile cleanup to fail with WinError 32.
    """
    conn = connect(db_path, readonly=readonly)
    try:
        yield conn
    finally:
        conn.close()

def table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {str(row["name"]) for row in rows if not str(row["name"]).startswith("sqlite_")}


def table_info(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return list(conn.execute(f'PRAGMA table_info("{table}")').fetchall())


def columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row["name"]) for row in table_info(conn, table)]


def primary_key_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = sorted((row for row in table_info(conn, table) if int(row["pk"]) > 0), key=lambda row: int(row["pk"]))
    return [str(row["name"]) for row in rows]


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'SELECT COUNT(*) AS c FROM "{table}"').fetchone()["c"])


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def validate_databases(src: sqlite3.Connection, dst: sqlite3.Connection) -> list[str]:
    warnings: list[str] = []
    src_tables = table_names(src)
    dst_tables = table_names(dst)
    missing_src = [t for t in REQUIRED_TABLES_MINIMUM if t not in src_tables]
    missing_dst = [t for t in REQUIRED_TABLES_MINIMUM if t not in dst_tables]
    if missing_src:
        raise BridgeError(f"Tablet DB no trae tablas mínimas: {', '.join(missing_src)}")
    if missing_dst:
        raise BridgeError(
            "PC canonical DB no trae tablas mínimas: "
            + ", ".join(missing_dst)
            + ". Inicializa PC canonical antes de sincronizar."
        )
    for table in TABLE_ORDER:
        if table in src_tables and table not in dst_tables:
            warnings.append(f"PC no tiene tabla {table}; se omitirá esa proyección.")
        if table in dst_tables and table not in src_tables:
            warnings.append(f"Tablet no tiene tabla {table}; no se proyectará desde Tablet.")
    return warnings


def select_rows(conn: sqlite3.Connection, table: str, cols: Sequence[str]) -> list[sqlite3.Row]:
    col_sql = ", ".join(quote_ident(c) for c in cols)
    return list(conn.execute(f'SELECT {col_sql} FROM {quote_ident(table)}').fetchall())


def unique_index_columns(conn: sqlite3.Connection, table: str) -> list[list[str]]:
    indexes: list[list[str]] = []
    for idx in conn.execute(f"PRAGMA index_list({quote_ident(table)})").fetchall():
        # PRAGMA index_list returns: seq, name, unique, origin, partial
        is_unique = len(idx) >= 3 and int(idx[2]) == 1
        is_partial = len(idx) >= 5 and int(idx[4]) == 1
        if is_unique and not is_partial:
            name = idx[1]
            cols = [row[2] for row in conn.execute(f"PRAGMA index_info({quote_ident(name)})").fetchall()]
            if cols:
                indexes.append(cols)
    return indexes


def choose_conflict_keys(dst: sqlite3.Connection, table: str, common: Sequence[str], pk_cols: Sequence[str]) -> list[str] | None:
    common_set = set(common)
    unique_sets = [tuple(cols) for cols in unique_index_columns(dst, table)]
    for candidate in NATURAL_CONFLICT_KEYS.get(table, []):
        if all(col in common_set for col in candidate) and tuple(candidate) in unique_sets:
            return list(candidate)
    if pk_cols and all(pk in common_set for pk in pk_cols):
        return list(pk_cols)
    return None


def key_has_usable_values(row: dict[str, Any], key_cols: Sequence[str]) -> bool:
    return all(col in row and row[col] is not None for col in key_cols)


def fetch_id_by_key(dst: sqlite3.Connection, table: str, key_cols: Sequence[str], row: dict[str, Any]) -> str | None:
    if "id" not in columns(dst, table):
        return None
    if not key_has_usable_values(row, key_cols):
        return None
    where = " AND ".join(f"{quote_ident(col)} = ?" for col in key_cols)
    values = [row[col] for col in key_cols]
    hit = dst.execute(f"SELECT id FROM {quote_ident(table)} WHERE {where} LIMIT 1", values).fetchone()
    if not hit:
        return None
    return str(hit["id"])


def destination_id_exists(dst: sqlite3.Connection, table: str, value: Any) -> bool:
    if value is None or "id" not in columns(dst, table):
        return False
    hit = dst.execute(f"SELECT 1 FROM {quote_ident(table)} WHERE id = ? LIMIT 1", [value]).fetchone()
    return hit is not None


def stable_projected_id(table: str, source_id: Any, row: dict[str, Any]) -> str:
    business = row.get("businessId") or "global"
    seed = f"{table}|{business}|{source_id}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:18]
    prefix = ''.join(ch for ch in table.lower() if ch.isalnum())[:10] or "row"
    return f"bridge_{prefix}_{digest}"


def ensure_available_projected_id(dst: sqlite3.Connection, table: str, source_id: Any, row: dict[str, Any]) -> str:
    base = stable_projected_id(table, source_id, row)
    if not destination_id_exists(dst, table, base):
        return base
    # Stable repeated sync should land on the same projected row. If the generated
    # id exists, use it as the conflict target instead of making endless clones.
    return base


def apply_foreign_key_maps(table: str, row: dict[str, Any], id_maps: dict[str, dict[Any, Any]]) -> None:
    for col, ref_table in FK_ID_COLUMNS.get(table, {}).items():
        if col not in row:
            continue
        old_value = row[col]
        if old_value is None:
            continue
        mapped = id_maps.get(ref_table, {}).get(old_value)
        if mapped is not None:
            row[col] = mapped


def resolve_row_identity(
    dst: sqlite3.Connection,
    table: str,
    row: dict[str, Any],
    conflict_cols: Sequence[str],
    pk_cols: Sequence[str],
    id_maps: dict[str, dict[Any, Any]],
) -> None:
    if "id" not in row:
        return
    source_id = row.get("id")
    if source_id is None:
        return

    natural_conflict = bool(conflict_cols) and list(conflict_cols) != list(pk_cols)

    if natural_conflict:
        existing_by_natural = fetch_id_by_key(dst, table, conflict_cols, row)
        if existing_by_natural is not None:
            row["id"] = existing_by_natural
            id_maps.setdefault(table, {})[source_id] = existing_by_natural
            return

    if destination_id_exists(dst, table, source_id):
        if not natural_conflict:
            # The chosen conflict target is the destination primary key. Repeated
            # bridge runs must update that same projected row instead of minting
            # a second id that can collide with other unique constraints.
            id_maps.setdefault(table, {})[source_id] = source_id
            return
        if table == "Business":
            # Business is the tenant root; repeat sync must reuse it so child businessId values stay stable.
            id_maps.setdefault(table, {})[source_id] = source_id
            return
        # The source id already exists in PC, but it did not match the natural row
        # above. Do not overwrite PC-owned identity; project the Tablet row under a
        # deterministic bridge id and rewrite children to that id.
        projected = ensure_available_projected_id(dst, table, source_id, row)
        row["id"] = projected
        id_maps.setdefault(table, {})[source_id] = projected
        return

    id_maps.setdefault(table, {})[source_id] = source_id


def build_upsert_sql(table: str, common: Sequence[str], conflict_cols: Sequence[str], immutable_cols: set[str]) -> str:
    placeholders = ", ".join("?" for _ in common)
    col_sql = ", ".join(quote_ident(c) for c in common)
    conflict_sql = ", ".join(quote_ident(c) for c in conflict_cols)
    update_cols = [c for c in common if c not in immutable_cols and c not in conflict_cols]
    if update_cols:
        update_sql = ", ".join(f"{quote_ident(c)}=excluded.{quote_ident(c)}" for c in update_cols)
        return f"INSERT INTO {quote_ident(table)} ({col_sql}) VALUES ({placeholders}) ON CONFLICT({conflict_sql}) DO UPDATE SET {update_sql}"
    return f"INSERT OR IGNORE INTO {quote_ident(table)} ({col_sql}) VALUES ({placeholders})"


def copy_table(src: sqlite3.Connection, dst: sqlite3.Connection, table: str, id_maps: dict[str, dict[Any, Any]]) -> TableCopyResult:
    src_tables = table_names(src)
    dst_tables = table_names(dst)
    if table not in src_tables or table not in dst_tables:
        return TableCopyResult(table=table, source_rows=0, inserted_or_updated=0, common_columns=[], skipped=True, reason="missing_table")
    src_cols = columns(src, table)
    dst_cols = columns(dst, table)
    common = [c for c in src_cols if c in dst_cols]
    pk_cols = primary_key_columns(dst, table)
    if not common:
        return TableCopyResult(table=table, source_rows=count_rows(src, table), inserted_or_updated=0, common_columns=[], skipped=True, reason="no_common_columns")

    conflict_cols = choose_conflict_keys(dst, table, common, pk_cols)
    if not conflict_cols:
        return TableCopyResult(table=table, source_rows=count_rows(src, table), inserted_or_updated=0, common_columns=common, skipped=True, reason="no_usable_conflict_key")

    rows = select_rows(src, table, common)
    if not rows:
        return TableCopyResult(table=table, source_rows=0, inserted_or_updated=0, common_columns=common)

    immutable_cols = set(pk_cols)
    sql = build_upsert_sql(table, common, conflict_cols, immutable_cols)
    values: list[list[Any]] = []
    for raw in rows:
        row = {c: raw[c] for c in common}
        apply_foreign_key_maps(table, row, id_maps)
        resolve_row_identity(dst, table, row, conflict_cols, pk_cols, id_maps)
        values.append([row.get(c) for c in common])

    try:
        dst.executemany(sql, values)
    except sqlite3.IntegrityError as exc:
        raise BridgeError(
            f"No pude proyectar {table} con llave de conflicto {conflict_cols}. "
            f"La DB destino tiene otra restricción única en choque: {exc}. "
            "v04 ya hace mapeo de ids; si este mensaje aparece, hace falta revisar "
            "la restricción concreta y decidir una regla de reconciliación explícita."
        ) from exc
    except sqlite3.OperationalError as exc:
        if "ON CONFLICT clause does not match" in str(exc):
            raise BridgeError(
                f"No pude proyectar {table}: la llave de conflicto {conflict_cols} "
                "no coincide con una restricción PRIMARY KEY/UNIQUE completa en la DB destino. "
                "Los índices únicos parciales no son candidatos válidos para este UPSERT."
            ) from exc
        raise
    return TableCopyResult(table=table, source_rows=len(rows), inserted_or_updated=len(rows), common_columns=common)


def acknowledge_tablet_outbox(src: sqlite3.Connection) -> int:
    src_tables = table_names(src)
    if "OutboxEvent" not in src_tables:
        return 0
    cols = set(columns(src, "OutboxEvent"))
    if "status" not in cols:
        return 0
    synced_at_sql = ", syncedAt = ?" if "syncedAt" in cols else ""
    params: list[Any] = []
    if synced_at_sql:
        params.append(now_iso())
    params.extend(["pending", "sent", "failed", "PENDING", "SENT", "FAILED"])
    sql = f"UPDATE OutboxEvent SET status = 'acked'{synced_at_sql} WHERE status IN (?, ?, ?, ?, ?, ?)"
    cur = src.execute(sql, params)
    return int(cur.rowcount if cur.rowcount is not None else 0)


def make_backup(src_db: Path, dst_db: Path, out_root: Path) -> Path:
    backup_dir = out_root / "prisma_tri_db_bridge_backups" / now_id()
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_db, backup_dir / "tablet-pos.db.bak")
    if dst_db.exists():
        shutil.copy2(dst_db, backup_dir / "canonical.db.bak")
    return backup_dir


def restore_backup(src_db: Path, dst_db: Path, backup_dir: Path) -> None:
    src_bak = backup_dir / "tablet-pos.db.bak"
    dst_bak = backup_dir / "canonical.db.bak"
    if src_bak.exists():
        shutil.copy2(src_bak, src_db)
    if dst_bak.exists():
        dst_db.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst_bak, dst_db)


def run_plan(roots: RootInfo) -> BridgeSummary:
    src_db = Path(roots.tablet_db)
    dst_db = Path(roots.pc_db)
    if not dst_db.exists() or dst_db.stat().st_size <= 0:
        raise BridgeError(f"PC canonical DB no existe o está vacía: {dst_db}")
    with open_db(src_db, readonly=True) as src, open_db(dst_db, readonly=True) as dst:
        warnings = validate_databases(src, dst)
        tables = []
        for table in TABLE_ORDER:
            src_rows = count_rows(src, table) if table in table_names(src) else 0
            common = sorted(set(columns(src, table)) & set(columns(dst, table))) if table in table_names(src) and table in table_names(dst) else []
            tables.append(TableCopyResult(table=table, source_rows=src_rows, inserted_or_updated=0, common_columns=common, skipped=not bool(common), reason=None if common else "not_projectable"))
        return BridgeSummary(VERSION, "plan", "READY", now_iso(), roots, None, tables, 0, 0, "rescue_backfill_diagnostic", warnings)


def run_sync(roots: RootInfo, out_root: Path, ack_outbox: bool = True) -> BridgeSummary:
    src_db = Path(roots.tablet_db)
    dst_db = Path(roots.pc_db)
    if not dst_db.exists() or dst_db.stat().st_size <= 0:
        raise BridgeError(f"PC canonical DB no existe o está vacía: {dst_db}")
    backup_dir = make_backup(src_db, dst_db, out_root)
    tables: list[TableCopyResult] = []
    acked = 0
    warnings: list[str] = []
    try:
        with open_db(src_db, readonly=False) as src, open_db(dst_db, readonly=False) as dst:
            src.execute("PRAGMA foreign_keys = ON")
            dst.execute("PRAGMA foreign_keys = ON")
            warnings = validate_databases(src, dst)
            dst.execute("BEGIN")
            id_maps: dict[str, dict[Any, Any]] = {}
            for table in TABLE_ORDER:
                result = copy_table(src, dst, table, id_maps)
                tables.append(result)
            dst.commit()
            if ack_outbox:
                src.execute("BEGIN")
                acked = acknowledge_tablet_outbox(src)
                src.commit()
        warnings.append("TRI_DB_BRIDGE_COMPAT_ACK_ONLY: acked means copied by bridge, not PC event-governance reconciliation.")
        return BridgeSummary(VERSION, "sync", "READY", now_iso(), roots, str(backup_dir), tables, acked, 0, "rescue_backfill_diagnostic", warnings)
    except Exception:
        try:
            restore_backup(src_db, dst_db, backup_dir)
        finally:
            pass
        raise


def write_summary(summary: BridgeSummary, out_root: Path) -> Path:
    out_root.mkdir(parents=True, exist_ok=True)
    path = out_root / f"prisma_tri_db_bridge_{now_id()}.json"
    payload = asdict(summary)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def print_summary(summary: BridgeSummary, summary_path: Path | None) -> None:
    total_rows = sum(t.inserted_or_updated for t in summary.tables)
    print(f"PRISMA Tri-DB Bridge {summary.version}")
    print(f"Estado: {summary.status}")
    print(f"Modo: {summary.mode}")
    print(f"Tablet DB: {summary.roots.tablet_db}")
    print(f"PC DB: {summary.roots.pc_db}")
    print(f"Tablas proyectables: {sum(1 for t in summary.tables if not t.skipped)}")
    print(f"Filas copiadas/actualizadas: {total_rows}")
    print(f"Bridge role: {summary.bridge_role}")
    print(f"Outbox Tablet compat-acked: {summary.tablet_outbox_acknowledged}")
    print(f"PC governance reconciled by bridge: {summary.governance_reconciled}")
    if summary.backup_dir:
        print(f"Backup: {summary.backup_dir}")
    if summary.warnings:
        print("Advertencias:")
        for warning in summary.warnings:
            print(f"- {warning}")
    if summary_path:
        print(f"Resumen JSON: {summary_path}")


def create_demo_db(path: Path, include_tablet_extra: bool) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE Business (id TEXT PRIMARY KEY, name TEXT NOT NULL, taxId TEXT, currency TEXT NOT NULL DEFAULT 'MXN', createdAt DATETIME NOT NULL, updatedAt DATETIME NOT NULL);
            CREATE TABLE Store (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL, createdAt DATETIME NOT NULL, updatedAt DATETIME NOT NULL, UNIQUE(businessId, code), UNIQUE(id, businessId));
            CREATE TABLE Terminal (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, storeId TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL, isActive BOOLEAN NOT NULL DEFAULT 1, createdAt DATETIME NOT NULL, updatedAt DATETIME NOT NULL, UNIQUE(id, businessId));
            CREATE TABLE Product (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, sku TEXT NOT NULL, name TEXT NOT NULL, category TEXT NOT NULL, priceCents INTEGER NOT NULL, costCents INTEGER NOT NULL, stockOnHand INTEGER NOT NULL DEFAULT 0, taxRateId TEXT, isActive BOOLEAN NOT NULL DEFAULT 1, createdAt DATETIME NOT NULL, updatedAt DATETIME NOT NULL, UNIQUE(id, businessId));
            CREATE TABLE CashSession (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, storeId TEXT NOT NULL, terminalId TEXT NOT NULL, cashierId TEXT NOT NULL, cashier TEXT NOT NULL, openedAt DATETIME NOT NULL, closedAt DATETIME, cashStartCents INTEGER NOT NULL, cashEndCents INTEGER, expectedCashCents INTEGER, varianceCents INTEGER, status TEXT NOT NULL, createdAt DATETIME NOT NULL, updatedAt DATETIME NOT NULL, UNIQUE(id, businessId));
            CREATE UNIQUE INDEX uq_cashsession_single_open_per_terminal ON CashSession(businessId, terminalId) WHERE status = 'OPEN';
            CREATE TABLE Sale (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, terminalId TEXT NOT NULL, cashSessionId TEXT, folio TEXT NOT NULL, cashier TEXT NOT NULL, totalCents INTEGER NOT NULL, status TEXT NOT NULL, createdAt DATETIME NOT NULL, UNIQUE(id, businessId));
            CREATE TABLE SaleLine (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, saleId TEXT NOT NULL, productId TEXT NOT NULL, sku TEXT NOT NULL, productName TEXT NOT NULL, qty INTEGER NOT NULL, priceCents INTEGER NOT NULL, totalCents INTEGER NOT NULL, createdAt DATETIME NOT NULL);
            CREATE TABLE OutboxEvent (id TEXT PRIMARY KEY, businessId TEXT NOT NULL, topic TEXT NOT NULL, aggregateId TEXT NOT NULL, payloadJson TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, createdAt DATETIME NOT NULL, sentAt DATETIME, lastError TEXT);
            """
        )
        if include_tablet_extra:
            conn.executescript(
                """
                ALTER TABLE Sale ADD COLUMN clientRequestId TEXT;
                ALTER TABLE Sale ADD COLUMN subtotalCents INTEGER DEFAULT 0;
                ALTER TABLE Sale ADD COLUMN discountCents INTEGER DEFAULT 0;
                ALTER TABLE Sale ADD COLUMN completedAt DATETIME;
                ALTER TABLE Sale ADD COLUMN paymentMethod TEXT DEFAULT 'cash';
                ALTER TABLE Sale ADD COLUMN cashReceivedCents INTEGER;
                ALTER TABLE Sale ADD COLUMN changeCents INTEGER DEFAULT 0;
                ALTER TABLE OutboxEvent ADD COLUMN terminalId TEXT;
                ALTER TABLE OutboxEvent ADD COLUMN source TEXT;
                ALTER TABLE OutboxEvent ADD COLUMN schemaVersion TEXT;
                ALTER TABLE OutboxEvent ADD COLUMN syncedAt DATETIME;
                """
            )
            now = "2026-05-06T15:18:06.000Z"
            conn.execute("INSERT INTO Business VALUES (?, ?, ?, ?, ?, ?)", ("biz_tablet_standalone", "PRISMA Demo", None, "MXN", now, now))
            conn.execute("INSERT INTO Store VALUES (?, ?, ?, ?, ?, ?)", ("store_01", "biz_tablet_standalone", "S01", "Tienda", now, now))
            conn.execute("INSERT INTO Terminal VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ("terminal_tablet_local_01", "biz_tablet_standalone", "store_01", "T01", "Tablet", 1, now, now))
            conn.execute("INSERT INTO Product VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("prod_01", "biz_tablet_standalone", "SKU-1", "Refresco", "Bebidas", 1500, 900, 9, None, 1, now, now))
            conn.execute("INSERT INTO CashSession VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("cash_01", "biz_tablet_standalone", "store_01", "terminal_tablet_local_01", "cashier_01", "Caja", now, None, 50000, None, 51500, None, "OPEN", now, now))
            conn.execute("INSERT INTO Sale (id,businessId,terminalId,cashSessionId,folio,cashier,totalCents,status,createdAt,clientRequestId,subtotalCents,discountCents,completedAt,paymentMethod,cashReceivedCents,changeCents) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("sale_01", "biz_tablet_standalone", "terminal_tablet_local_01", "cash_01", "T-1", "Caja", 1500, "COMPLETED", now, "req_01", 1500, 0, now, "cash", 2000, 500))
            conn.execute("INSERT INTO SaleLine VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("line_01", "biz_tablet_standalone", "sale_01", "prod_01", "SKU-1", "Refresco", 1, 1500, 1500, now))
            event = {"eventId":"evt_01","topic":"sale.completed","businessId":"biz_tablet_standalone","terminalId":"terminal_tablet_local_01","actorId":"Caja","source":"tablet-pos","occurredAt":now,"schemaVersion":"1.0.0","aggregateId":"sale_01","payload":{"saleId":"sale_01","totalCents":1500}}
            conn.execute("INSERT INTO OutboxEvent (id,businessId,topic,aggregateId,payloadJson,status,attempts,createdAt,sentAt,lastError,terminalId,source,schemaVersion,syncedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("evt_01", "biz_tablet_standalone", "sale.completed", "sale_01", json.dumps(event), "pending", 0, now, None, None, "terminal_tablet_local_01", "tablet-pos", "1.0.0", None))
        conn.commit()
    finally:
        conn.close()


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="prisma_tri_db_bridge_test_") as tmp:
        base = Path(tmp)
        terminal_root = base / "apps" / "terminal-de-venta-system"
        terminal_root.mkdir(parents=True)
        (terminal_root / "terminal_de_venta.cmd").write_text("@echo off\n", encoding="utf-8")
        src_db = terminal_root / "products" / "tablet" / "app" / "data" / "tablet-pos.db"
        dst_db = base / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db"
        src_db.parent.mkdir(parents=True)
        dst_db.parent.mkdir(parents=True)
        create_demo_db(src_db, include_tablet_extra=True)
        create_demo_db(dst_db, include_tablet_extra=False)
        roots = resolve_roots(str(base), str(src_db), str(dst_db))
        summary = run_sync(roots, base, ack_outbox=True)
        with open_db(dst_db, readonly=True) as dst, open_db(src_db, readonly=True) as src:
            assert count_rows(dst, "Business") == 1
            assert count_rows(dst, "Product") == 1
            assert count_rows(dst, "CashSession") == 1
            assert count_rows(dst, "Sale") == 1
            assert count_rows(dst, "SaleLine") == 1
            assert count_rows(dst, "OutboxEvent") == 1
            status = src.execute("SELECT status FROM OutboxEvent WHERE id='evt_01'").fetchone()[0]
            assert status == "acked"
        run_sync(roots, base, ack_outbox=True)
        with open_db(dst_db, readonly=True) as dst:
            assert count_rows(dst, "Business") == 1
        print("SELF_TEST_READY")
        print_summary(summary, None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRISMA Tri-DB Bridge: herramienta secundaria de rescate/backfill/diagnostico; no es el sync primario.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="Valida rutas y muestra qué se copiaría. No modifica DBs.")
    mode.add_argument("--run", action="store_true", help="Copia/actualiza datos de Tablet en PC canonical con backup y rollback automatico para rescate/backfill.")
    mode.add_argument("--self-test", action="store_true", help="Ejecuta una prueba funcional aislada con DBs temporales.")
    parser.add_argument("--target-root", default=str(Path.cwd()), help="Root del repo hitech-os o de apps/terminal-de-venta-system.")
    parser.add_argument("--tablet-db", default=None, help="Ruta explícita a tablet-pos.db. Opcional.")
    parser.add_argument("--pc-db", default=None, help="Ruta explícita a canonical.db. Opcional.")
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT), help="Directorio para logs/resúmenes/backups. Default: F:\\descargasf")
    parser.add_argument("--no-ack-tablet-outbox", action="store_true", help="No marcar OutboxEvent de Tablet como acked compat tras bridge exitoso.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        out_root = Path(args.out_root).expanduser().resolve()
        roots = resolve_roots(args.target_root, args.tablet_db, args.pc_db)
        if args.plan:
            summary = run_plan(roots)
        else:
            summary = run_sync(roots, out_root, ack_outbox=not args.no_ack_tablet_outbox)
        summary_path = write_summary(summary, out_root)
        print_summary(summary, summary_path)
        return 0
    except BridgeError as error:
        eprint(f"BLOCKED: {error}")
        return 2
    except Exception as error:
        eprint(f"FAILED: {error}")
        eprint(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

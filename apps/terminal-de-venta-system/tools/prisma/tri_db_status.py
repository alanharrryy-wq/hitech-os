#!/usr/bin/env python3
"""
PRISMA Tri-DB Status v06.

Read-only health/status reporter for the Tablet -> PC canonical projection.
It reads the latest bridge summary JSON, inspects Tablet and PC SQLite DBs,
and writes a consumable status artifact for PC/Mobile surfaces.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "20260506_v06"
DEFAULT_TARGET_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_OUT_ROOT = Path(r"F:\descargasf")
KEY_TABLES = [
    "Business",
    "Store",
    "Terminal",
    "Product",
    "Barcode",
    "StockSnapshot",
    "CashSession",
    "CashMovement",
    "Sale",
    "SaleLine",
    "StockMovement",
    "OutboxEvent",
]
REFERENCE_CHECKS = [
    ("Barcode", "productId", "Product", "id"),
    ("StockSnapshot", "productId", "Product", "id"),
    ("StockMovement", "productId", "Product", "id"),
    ("SaleLine", "productId", "Product", "id"),
    ("SaleLine", "saleId", "Sale", "id"),
    ("Sale", "terminalId", "Terminal", "id"),
    ("CashMovement", "cashSessionId", "CashSession", "id"),
]


class StatusError(RuntimeError):
    pass


@dataclass
class Roots:
    target_root: str
    terminal_root: str
    repo_root: str
    tablet_db: str
    pc_db: str


@dataclass
class DbStatus:
    path: str
    exists: bool
    readable: bool
    table_counts: dict[str, int]
    outbox_by_status: dict[str, int]
    sales_total_cents: int
    product_count: int
    barcode_count: int
    low_stock_count: int
    reference_errors: dict[str, int]
    error: str | None = None


@dataclass
class StatusSummary:
    version: str
    status: str
    generated_at: str
    roots: dict[str, str]
    latest_bridge_summary: str | None
    latest_bridge_status: str | None
    last_sync_generated_at: str | None
    bridge_tables_projected: int
    bridge_rows_inserted_or_updated: int
    bridge_outbox_acknowledged: int
    tablet: dict[str, Any]
    pc: dict[str, Any]
    parity: dict[str, Any]
    warnings: list[str]
    evidence: dict[str, str | None]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_terminal_root(target_root: Path) -> Path:
    root = target_root.expanduser().resolve()
    if (root / "terminal_de_venta.cmd").exists() and (root / "products").exists():
        return root
    nested = root / "apps" / "terminal-de-venta-system"
    if (nested / "terminal_de_venta.cmd").exists() and (nested / "products").exists():
        return nested.resolve()
    raise StatusError(
        "No encontré apps/terminal-de-venta-system. Usa --target-root con F:\\repos\\hitech-os "
        "o con F:\\repos\\hitech-os\\apps\\terminal-de-venta-system."
    )


def build_roots(target_root: Path) -> Roots:
    terminal_root = resolve_terminal_root(target_root)
    repo_root = terminal_root.parent.parent if terminal_root.parent.name.lower() == "apps" else terminal_root
    tablet_db = terminal_root / "products" / "tablet" / "app" / "data" / "tablet-pos.db"
    pc_db = repo_root / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db"
    return Roots(
        target_root=str(target_root.expanduser().resolve()),
        terminal_root=str(terminal_root),
        repo_root=str(repo_root),
        tablet_db=str(tablet_db),
        pc_db=str(pc_db),
    )


def connect_ro(path: Path) -> sqlite3.Connection:
    # URI read-only keeps this reporter from accidentally mutating production DBs.
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    if not table_exists(conn, table):
        return False
    rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    return any(row[1] == column for row in rows)


def count_table(conn: sqlite3.Connection, table: str) -> int:
    if not table_exists(conn, table):
        return 0
    return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def outbox_status_counts(conn: sqlite3.Connection) -> dict[str, int]:
    if not table_exists(conn, "OutboxEvent") or not column_exists(conn, "OutboxEvent", "status"):
        return {}
    rows = conn.execute('SELECT COALESCE(status, "") AS status, COUNT(*) FROM "OutboxEvent" GROUP BY status').fetchall()
    return {str(status or "unknown"): int(count) for status, count in rows}


def sales_total(conn: sqlite3.Connection) -> int:
    if not table_exists(conn, "Sale") or not column_exists(conn, "Sale", "totalCents"):
        return 0
    row = conn.execute('SELECT COALESCE(SUM(totalCents), 0) FROM "Sale"').fetchone()
    return int(row[0] or 0)


def low_stock_count(conn: sqlite3.Connection) -> int:
    if not table_exists(conn, "Product") or not column_exists(conn, "Product", "stockOnHand"):
        return 0
    # Keep this conservative. If a lowStockThreshold column exists later, use it.
    if column_exists(conn, "Product", "lowStockThreshold"):
        row = conn.execute(
            'SELECT COUNT(*) FROM "Product" WHERE COALESCE(stockOnHand, 0) <= COALESCE(lowStockThreshold, 0)'
        ).fetchone()
    else:
        row = conn.execute('SELECT COUNT(*) FROM "Product" WHERE COALESCE(stockOnHand, 0) <= 0').fetchone()
    return int(row[0] or 0)


def missing_reference_count(conn: sqlite3.Connection, child: str, child_col: str, parent: str, parent_col: str) -> int:
    if not table_exists(conn, child) or not table_exists(conn, parent):
        return 0
    if not column_exists(conn, child, child_col) or not column_exists(conn, parent, parent_col):
        return 0
    sql = (
        f'SELECT COUNT(*) FROM "{child}" c '
        f'LEFT JOIN "{parent}" p ON c."{child_col}" = p."{parent_col}" '
        f'WHERE c."{child_col}" IS NOT NULL AND p."{parent_col}" IS NULL'
    )
    row = conn.execute(sql).fetchone()
    return int(row[0] or 0)


def inspect_db(path: Path) -> DbStatus:
    if not path.exists():
        return DbStatus(
            path=str(path),
            exists=False,
            readable=False,
            table_counts={},
            outbox_by_status={},
            sales_total_cents=0,
            product_count=0,
            barcode_count=0,
            low_stock_count=0,
            reference_errors={},
            error=f"DB no existe: {path}",
        )
    conn: sqlite3.Connection | None = None
    try:
        # Do not rely on sqlite3.Connection as a context manager here.
        # It commits or rolls back, but does not guarantee the file handle is
        # closed on Windows. That leaves temp SQLite files locked during
        # self-test cleanup, which is exactly the tiny clown car this script
        # exists to avoid.
        conn = connect_ro(path)
        counts = {table: count_table(conn, table) for table in KEY_TABLES}
        ref_errors: dict[str, int] = {}
        for child, child_col, parent, parent_col in REFERENCE_CHECKS:
            missing = missing_reference_count(conn, child, child_col, parent, parent_col)
            if missing:
                ref_errors[f"{child}.{child_col}->{parent}.{parent_col}"] = missing
        return DbStatus(
            path=str(path),
            exists=True,
            readable=True,
            table_counts=counts,
            outbox_by_status=outbox_status_counts(conn),
            sales_total_cents=sales_total(conn),
            product_count=counts.get("Product", 0),
            barcode_count=counts.get("Barcode", 0),
            low_stock_count=low_stock_count(conn),
            reference_errors=ref_errors,
        )
    except Exception as exc:
        return DbStatus(
            path=str(path),
            exists=True,
            readable=False,
            table_counts={},
            outbox_by_status={},
            sales_total_cents=0,
            product_count=0,
            barcode_count=0,
            low_stock_count=0,
            reference_errors={},
            error=str(exc),
        )
    finally:
        if conn is not None:
            conn.close()


def find_latest_bridge_summary(out_root: Path, explicit: Path | None = None) -> Path | None:
    if explicit:
        return explicit.expanduser().resolve() if explicit.exists() else explicit.expanduser().resolve()
    candidates = []
    if out_root.exists():
        candidates = [p for p in out_root.glob("prisma_tri_db_bridge_*.json") if p.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_bridge_summary(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if path is None:
        return None, None
    if not path.exists():
        return None, f"Resumen de bridge no existe: {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"No pude leer resumen de bridge {path}: {exc}"


def bridge_row_total(summary: dict[str, Any] | None) -> int:
    if not summary:
        return 0
    return sum(int(item.get("inserted_or_updated") or 0) for item in summary.get("tables", []))


def projected_table_count(summary: dict[str, Any] | None) -> int:
    if not summary:
        return 0
    return sum(1 for item in summary.get("tables", []) if not item.get("skipped"))


def build_parity(tablet: DbStatus, pc: DbStatus) -> dict[str, Any]:
    tables: dict[str, dict[str, Any]] = {}
    all_ok = True
    for table in KEY_TABLES:
        tablet_count = tablet.table_counts.get(table, 0)
        pc_count = pc.table_counts.get(table, 0)
        ok = pc_count >= tablet_count
        all_ok = all_ok and ok
        tables[table] = {
            "tablet_rows": tablet_count,
            "pc_rows": pc_count,
            "pc_covers_tablet": ok,
            "delta_pc_minus_tablet": pc_count - tablet_count,
        }
    return {"pc_covers_tablet": all_ok, "tables": tables}


def make_status(target_root: Path, out_root: Path, bridge_summary_path: Path | None = None) -> StatusSummary:
    roots = build_roots(target_root)
    latest_summary_path = find_latest_bridge_summary(out_root, bridge_summary_path)
    bridge_summary, bridge_error = load_bridge_summary(latest_summary_path)
    tablet = inspect_db(Path(roots.tablet_db))
    pc = inspect_db(Path(roots.pc_db))

    warnings: list[str] = []
    if bridge_error:
        warnings.append(bridge_error)
    if not tablet.readable:
        warnings.append(f"Tablet DB no legible: {tablet.error}")
    if not pc.readable:
        warnings.append(f"PC canonical DB no legible: {pc.error}")
    if bridge_summary and bridge_summary.get("status") != "READY":
        warnings.append(f"Último bridge no está READY: {bridge_summary.get('status')}")
    for label, missing in pc.reference_errors.items():
        warnings.append(f"Referencia rota en PC: {label} faltantes={missing}")

    parity = build_parity(tablet, pc)
    if not parity["pc_covers_tablet"]:
        warnings.append("PC no cubre todos los conteos clave de Tablet. Ejecuta el bridge antes de exponer estado como listo.")

    status = "READY" if not warnings and tablet.readable and pc.readable else "READY_WITH_CAVEATS"
    if not tablet.exists or not pc.exists or not tablet.readable or not pc.readable:
        status = "BLOCKED"

    evidence_latest: str | None = None
    return StatusSummary(
        version=VERSION,
        status=status,
        generated_at=utc_now(),
        roots=asdict(roots),
        latest_bridge_summary=str(latest_summary_path) if latest_summary_path else None,
        latest_bridge_status=str(bridge_summary.get("status")) if bridge_summary else None,
        last_sync_generated_at=str(bridge_summary.get("generated_at")) if bridge_summary else None,
        bridge_tables_projected=projected_table_count(bridge_summary),
        bridge_rows_inserted_or_updated=bridge_row_total(bridge_summary),
        bridge_outbox_acknowledged=int((bridge_summary or {}).get("tablet_outbox_acknowledged") or 0),
        tablet=asdict(tablet),
        pc=asdict(pc),
        parity=parity,
        warnings=warnings,
        evidence={"latest_status_json": evidence_latest},
    )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def print_human(summary: StatusSummary) -> None:
    print(f"PRISMA Tri-DB Status {VERSION}")
    print(f"Estado: {summary.status}")
    print(f"Último bridge: {summary.latest_bridge_status or 'NO_ENCONTRADO'}")
    print(f"Tablas proyectadas: {summary.bridge_tables_projected}")
    print(f"Filas copiadas/actualizadas: {summary.bridge_rows_inserted_or_updated}")
    print(f"Outbox acked: {summary.bridge_outbox_acknowledged}")
    print(f"Tablet Product/Sale/Outbox: {summary.tablet['table_counts'].get('Product', 0)}/{summary.tablet['table_counts'].get('Sale', 0)}/{summary.tablet['table_counts'].get('OutboxEvent', 0)}")
    print(f"PC Product/Sale/Outbox: {summary.pc['table_counts'].get('Product', 0)}/{summary.pc['table_counts'].get('Sale', 0)}/{summary.pc['table_counts'].get('OutboxEvent', 0)}")
    if summary.warnings:
        print("Advertencias:")
        for warning in summary.warnings:
            print(f"- {warning}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="prisma_tri_db_status_test_", ignore_cleanup_errors=True) as tmp_raw:
        tmp = Path(tmp_raw)
        target_root = tmp / "repo"
        terminal = target_root / "apps" / "terminal-de-venta-system"
        out_root = tmp / "out"
        (terminal / "products" / "tablet" / "app" / "data").mkdir(parents=True)
        (target_root / "tools" / "_local" / "data" / "terminal-de-venta-system").mkdir(parents=True)
        (terminal / "terminal_de_venta.cmd").write_text("@echo off\n", encoding="utf-8")
        (terminal / "products").mkdir(exist_ok=True)
        tablet_db = terminal / "products" / "tablet" / "app" / "data" / "tablet-pos.db"
        pc_db = target_root / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db"
        for db in (tablet_db, pc_db):
            conn = sqlite3.connect(db)
            try:
                conn.executescript(
                    """
                    CREATE TABLE Product(id TEXT PRIMARY KEY, businessId TEXT, sku TEXT, name TEXT, stockOnHand INTEGER);
                    CREATE TABLE Barcode(id TEXT PRIMARY KEY, businessId TEXT, productId TEXT, code TEXT);
                    CREATE TABLE Terminal(id TEXT PRIMARY KEY, businessId TEXT, code TEXT);
                    CREATE TABLE Sale(id TEXT PRIMARY KEY, businessId TEXT, terminalId TEXT, folio TEXT, totalCents INTEGER);
                    CREATE TABLE SaleLine(id TEXT PRIMARY KEY, businessId TEXT, saleId TEXT, productId TEXT, sku TEXT, productName TEXT, qty INTEGER, totalCents INTEGER);
                    CREATE TABLE OutboxEvent(id TEXT PRIMARY KEY, businessId TEXT, topic TEXT, status TEXT);
                    """
                )
                conn.execute("INSERT INTO Product VALUES('p1','b1','sku1','Agua',5)")
                conn.execute("INSERT INTO Barcode VALUES('bc1','b1','p1','7500001')")
                conn.execute("INSERT INTO Terminal VALUES('t1','b1','tablet01')")
                conn.execute("INSERT INTO Sale VALUES('s1','b1','t1','F001',1200)")
                conn.execute("INSERT INTO SaleLine VALUES('sl1','b1','s1','p1','sku1','Agua',1,1200)")
                conn.execute("INSERT INTO OutboxEvent VALUES('e1','b1','sale.completed','acked')")
                conn.commit()
            finally:
                conn.close()
        out_root.mkdir(parents=True)
        bridge = {
            "status": "READY",
            "generated_at": utc_now(),
            "tables": [
                {"table": "Product", "inserted_or_updated": 1, "skipped": False},
                {"table": "OutboxEvent", "inserted_or_updated": 1, "skipped": False},
            ],
            "tablet_outbox_acknowledged": 1,
        }
        write_json(out_root / "prisma_tri_db_bridge_20990101_000000.json", bridge)
        summary = make_status(target_root, out_root)
        if summary.status != "READY":
            raise StatusError(f"Self-test esperaba READY y obtuvo {summary.status}: {summary.warnings}")
        print("SELF_TEST_READY")
        print_human(summary)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRISMA Tri-DB Status v06")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true", help="Genera status real de Tablet/PC/bridge.")
    mode.add_argument("--self-test", action="store_true", help="Ejecuta prueba funcional aislada.")
    parser.add_argument("--target-root", default=str(DEFAULT_TARGET_ROOT), help="Root hitech-os o terminal-de-venta-system.")
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT), help="Directorio de salida, default F:\\descargasf.")
    parser.add_argument("--bridge-summary", default=None, help="Resumen JSON específico del bridge. Si no se pasa, usa el más reciente en out-root.")
    parser.add_argument("--output-json", default=None, help="Ruta exacta para escribir status JSON timestamped.")
    parser.add_argument("--latest-json", default=None, help="Ruta estable para status.latest.json consumible por PC/Mobile.")
    parser.add_argument("--fail-on-blocked", action="store_true", help="Sale con error si el status queda BLOCKED.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        target_root = Path(args.target_root).expanduser().resolve()
        out_root = Path(args.out_root).expanduser().resolve()
        bridge_summary = Path(args.bridge_summary).expanduser().resolve() if args.bridge_summary else None
        summary = make_status(target_root, out_root, bridge_summary)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_json = Path(args.output_json).expanduser().resolve() if args.output_json else out_root / f"prisma_tri_db_status_{timestamp}.json"
        latest_json = Path(args.latest_json).expanduser().resolve() if args.latest_json else Path(summary.roots["terminal_root"]) / "shared" / "tri-db" / "status.latest.json"
        data = asdict(summary)
        data["evidence"]["latest_status_json"] = str(latest_json)
        write_json(output_json, data)
        write_json(latest_json, data)
        print_human(summary)
        print(f"Status JSON: {output_json}")
        print(f"Latest JSON: {latest_json}")
        if args.fail_on_blocked and summary.status == "BLOCKED":
            return 2
        return 0
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

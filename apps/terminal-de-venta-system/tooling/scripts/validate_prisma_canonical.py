#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


TERMINAL_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = TERMINAL_ROOT.parents[1]
PC_APP = TERMINAL_ROOT / "products" / "pc" / "app"
TABLET_APP = TERMINAL_ROOT / "products" / "tablet" / "app"
SCHEMA = TERMINAL_ROOT / "prisma" / "schema.prisma"
SEED_JSON = TERMINAL_ROOT / "prisma" / "seeds" / "canonical.seed.json"
PROCUREMENT_SQL = TERMINAL_ROOT / "prisma" / "sql" / "seed-procurement.sql"
SMOKE_SCRIPT = TERMINAL_ROOT / "prisma" / "runtime-smoke.mjs"
SEED_SCRIPT = TERMINAL_ROOT / "prisma" / "seed.mjs"
APPLY_MIGRATIONS = TERMINAL_ROOT / "tooling" / "scripts" / "apply_prisma_migrations_sqlite.py"


def win(path: Path) -> str:
    return str(path.resolve())


def prisma_file_url(path: Path) -> str:
    return "file:" + path.resolve().as_posix()


def cached_schema_for(app_root: Path) -> Path:
    cache = app_root / "node_modules" / ".cache" / "hitech-prisma-canonical"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / "schema.prisma"
    target.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def run_command(command: list[str], cwd: Path, env: dict[str, str]) -> dict:
    executable = shutil.which(command[0]) or shutil.which(command[0] + ".cmd")
    if not executable:
        return {
            "command": " ".join(command),
            "cwd": win(cwd),
            "returncode": 127,
            "stdout_tail": "",
            "stderr_tail": f"Executable not found: {command[0]}",
            "pass": False,
        }
    command = [executable, *command[1:]]
    result = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    return {
        "command": " ".join(command),
        "cwd": win(cwd),
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-4000:],
        "pass": result.returncode == 0,
    }


def load_seed() -> dict:
    return json.loads(SEED_JSON.read_text(encoding="utf-8"))


def line_sums(rows: list[dict]) -> dict[str, int]:
    return {
        "subtotalCents": sum(int(row["lineSubtotalCents"]) for row in rows),
        "taxCents": sum(int(row["lineTaxCents"]) for row in rows),
        "totalCents": sum(int(row["lineTotalCents"]) for row in rows),
    }


def check_seed_procurement(seed: dict) -> dict:
    po = seed["purchaseOrders"][0]
    gr = seed["goodsReceipts"][0]
    po_sums = line_sums(seed["purchaseOrderLines"])
    gr_sums = line_sums(seed["goodsReceiptLines"])
    po_header = {key: int(po[key]) for key in po_sums}
    gr_header = {key: int(gr[key]) for key in gr_sums}
    return {
        "purchase_order": {"header": po_header, "line_sums": po_sums, "match": po_header == po_sums},
        "goods_receipt": {"header": gr_header, "line_sums": gr_sums, "match": gr_header == gr_sums},
        "pass": po_header == po_sums and gr_header == gr_sums,
    }


def check_sql_procurement(seed_check: dict) -> dict:
    sql = PROCUREMENT_SQL.read_text(encoding="utf-8")
    po = seed_check["purchase_order"]["line_sums"]
    gr = seed_check["goods_receipt"]["line_sums"]
    po_match = re.search(
        r"'po_demo_001'.*?,\s*(\d+),\s*(\d+),\s*(\d+),\s*CURRENT_TIMESTAMP",
        sql,
        flags=re.DOTALL,
    )
    gr_match = re.search(
        r"'gr_demo_001'.*?,\s*(\d+),\s*(\d+),\s*(\d+),\s*CURRENT_TIMESTAMP",
        sql,
        flags=re.DOTALL,
    )
    po_sql = tuple(int(value) for value in po_match.groups()) if po_match else None
    gr_sql = tuple(int(value) for value in gr_match.groups()) if gr_match else None
    expected_po = (po["subtotalCents"], po["taxCents"], po["totalCents"])
    expected_gr = (gr["subtotalCents"], gr["taxCents"], gr["totalCents"])
    return {
        "purchase_order_sql": po_sql,
        "goods_receipt_sql": gr_sql,
        "expected_purchase_order": expected_po,
        "expected_goods_receipt": expected_gr,
        "pass": po_sql == expected_po and gr_sql == expected_gr,
    }


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def fetch_all(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def check_db_procurement(conn: sqlite3.Connection) -> dict:
    purchase_orders = fetch_all(
        conn,
        """
        SELECT
          po.id,
          po.subtotalCents AS headerSubtotalCents,
          po.taxCents AS headerTaxCents,
          po.totalCents AS headerTotalCents,
          COALESCE(SUM(pol.lineSubtotalCents), 0) AS lineSubtotalCents,
          COALESCE(SUM(pol.lineTaxCents), 0) AS lineTaxCents,
          COALESCE(SUM(pol.lineTotalCents), 0) AS lineTotalCents
        FROM PurchaseOrder po
        LEFT JOIN PurchaseOrderLine pol ON pol.purchaseOrderId = po.id
        GROUP BY po.id
        """,
    )
    goods_receipts = fetch_all(
        conn,
        """
        SELECT
          gr.id,
          gr.subtotalCents AS headerSubtotalCents,
          gr.taxCents AS headerTaxCents,
          gr.totalCents AS headerTotalCents,
          COALESCE(SUM(grl.lineSubtotalCents), 0) AS lineSubtotalCents,
          COALESCE(SUM(grl.lineTaxCents), 0) AS lineTaxCents,
          COALESCE(SUM(grl.lineTotalCents), 0) AS lineTotalCents
        FROM GoodsReceipt gr
        LEFT JOIN GoodsReceiptLine grl ON grl.goodsReceiptId = gr.id
        GROUP BY gr.id
        """,
    )

    def rows_match(rows: list[dict]) -> bool:
        return all(
            row["headerSubtotalCents"] == row["lineSubtotalCents"]
            and row["headerTaxCents"] == row["lineTaxCents"]
            and row["headerTotalCents"] == row["lineTotalCents"]
            for row in rows
        )

    return {
        "purchase_orders": purchase_orders,
        "goods_receipts": goods_receipts,
        "pass": rows_match(purchase_orders) and rows_match(goods_receipts),
    }


def check_uniqueness(conn: sqlite3.Connection) -> dict:
    price_default_violations = fetch_all(
        conn,
        """
        SELECT businessId, COUNT(*) AS total
        FROM PriceList
        WHERE isDefault = 1
        GROUP BY businessId
        HAVING COUNT(*) > 1
        """,
    )
    tax_default_violations = fetch_all(
        conn,
        """
        SELECT businessId, COUNT(*) AS total
        FROM TaxRate
        WHERE isDefault = 1
        GROUP BY businessId
        HAVING COUNT(*) > 1
        """,
    )
    cash_session_violations = fetch_all(
        conn,
        """
        SELECT businessId, terminalId, COUNT(*) AS total
        FROM CashSession
        WHERE status = 'OPEN'
        GROUP BY businessId, terminalId
        HAVING COUNT(*) > 1
        """,
    )
    barcode_mismatches = fetch_all(
        conn,
        """
        SELECT b.id, b.businessId AS barcodeBusinessId, p.businessId AS productBusinessId
        FROM Barcode b
        LEFT JOIN Product p ON p.id = b.productId
        WHERE p.id IS NULL OR b.businessId != p.businessId
        """,
    )
    return {
        "price_default_violations": price_default_violations,
        "tax_default_violations": tax_default_violations,
        "open_cash_session_violations": cash_session_violations,
        "barcode_product_business_mismatches": barcode_mismatches,
        "pass": not price_default_violations
        and not tax_default_violations
        and not cash_session_violations
        and not barcode_mismatches,
    }


def expect_integrity_error(conn: sqlite3.Connection, label: str, statements: list[tuple[str, tuple]]) -> dict:
    try:
        conn.execute("BEGIN")
        for sql, params in statements:
            conn.execute(sql, params)
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        return {"label": label, "pass": True, "error": str(exc)}
    except sqlite3.DatabaseError as exc:
        conn.execute("ROLLBACK")
        return {"label": label, "pass": True, "error": str(exc)}
    else:
        conn.execute("ROLLBACK")
        return {"label": label, "pass": False, "error": "invalid write was accepted"}


def check_constraint_enforcement(conn: sqlite3.Connection) -> dict:
    checks = [
        expect_integrity_error(
            conn,
            "single default PriceList per business",
            [
                (
                    """
                    INSERT INTO PriceList
                      (id, businessId, name, currency, isDefault, isActive, startsAt, createdAt, updatedAt)
                    VALUES
                      ('pl_invalid_second_default', 'biz_hitech_default', 'Invalid second default', 'MXN', 1, 1,
                       '2026-04-25T00:00:00.000Z', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (),
                )
            ],
        ),
        expect_integrity_error(
            conn,
            "single default TaxRate per business",
            [
                (
                    """
                    INSERT INTO TaxRate
                      (id, businessId, name, rateBps, isDefault, isActive, createdAt, updatedAt)
                    VALUES
                      ('tax_invalid_second_default', 'biz_hitech_default', 'IVA invalid', 1600, 1, 1,
                       CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (),
                )
            ],
        ),
        expect_integrity_error(
            conn,
            "single open CashSession per terminal",
            [
                (
                    """
                    INSERT INTO CashSession
                      (id, businessId, storeId, terminalId, cashierId, cashier, openedAt, cashStartCents,
                       status, createdAt, updatedAt)
                    VALUES
                      ('cash_session_invalid_second_open', 'biz_hitech_default', 'store_obrera_04',
                       'terminal_tablet_01', 'usr_invalid', 'Invalid', '2026-04-25T08:00:00.000Z',
                       100000, 'OPEN', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (),
                )
            ],
        ),
        expect_integrity_error(
            conn,
            "Barcode business must match Product business",
            [
                (
                    """
                    INSERT INTO Business (id, name, currency, createdAt, updatedAt)
                    VALUES ('biz_validation_other', 'Validation Other', 'MXN', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (),
                ),
                (
                    """
                    INSERT INTO Barcode (id, businessId, productId, code, createdAt)
                    VALUES ('bc_invalid_business_mismatch', 'biz_validation_other', 'prd_ref_355',
                            'INVALID-MISMATCH', CURRENT_TIMESTAMP)
                    """,
                    (),
                ),
            ],
        ),
        expect_integrity_error(
            conn,
            "PurchaseOrder header totals cannot diverge from lines",
            [
                (
                    """
                    UPDATE PurchaseOrder
                    SET totalCents = totalCents + 1
                    WHERE id = 'po_demo_001'
                    """,
                    (),
                )
            ],
        ),
        expect_integrity_error(
            conn,
            "GoodsReceipt header totals cannot diverge from lines",
            [
                (
                    """
                    UPDATE GoodsReceipt
                    SET totalCents = totalCents + 1
                    WHERE id = 'gr_demo_001'
                    """,
                    (),
                )
            ],
        ),
    ]
    return {"checks": checks, "pass": all(check["pass"] for check in checks)}


def check_migrations(conn: sqlite3.Connection) -> dict:
    rows = fetch_all(
        conn,
        """
        SELECT migration_name, finished_at, rolled_back_at
        FROM _prisma_migrations
        ORDER BY finished_at
        """,
    )
    return {
        "applied": rows,
        "pass": any(row["migration_name"] == "20260425000000_canonical_foundation" and row["finished_at"] for row in rows)
        and all(row["rolled_back_at"] is None for row in rows),
    }


def check_seed_counts(conn: sqlite3.Connection) -> dict:
    tables = [
        "Business",
        "Product",
        "Barcode",
        "PriceList",
        "TaxRate",
        "PurchaseOrder",
        "PurchaseOrderLine",
        "GoodsReceipt",
        "GoodsReceiptLine",
        "CashSession",
        "Sale",
        "SaleLine",
        "SaleReturn",
        "OutboxEvent",
    ]
    counts = {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}
    return {"counts": counts, "pass": all(total > 0 for total in counts.values())}


def check_runtime_sources() -> dict:
    forbidden_imports = [
        "@/lib/i02/catalog-stock-data",
        "@/lib/i04/procurement-data",
        "@/lib/i05/replenishment-sync-data",
        "@/lib/data/demo",
    ]
    critical_files = [
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "catalogo-activo" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "existencias-criticas" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "ordenes-compra" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "recepcion-proveedor" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "incidencias-recepcion" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "outbox-operativo" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "senal-reabasto" / "page.tsx",
        TERMINAL_ROOT / "products" / "pc" / "app" / "app" / "sync-operativo" / "page.tsx",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "app" / "page.tsx",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "app" / "sales" / "page.tsx",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "app" / "shift" / "page.tsx",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "app" / "returns" / "page.tsx",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "app" / "stock" / "page.tsx",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "app" / "sync" / "page.tsx",
    ]
    violations = []
    for file in critical_files:
        text = file.read_text(encoding="utf-8")
        for forbidden in forbidden_imports:
            if forbidden in text:
                violations.append({"file": win(file), "forbidden_import": forbidden})
    service_files = [
        TERMINAL_ROOT / "products" / "pc" / "app" / "src" / "lib" / "services" / "dashboard.ts",
        TERMINAL_ROOT / "products" / "pc" / "app" / "src" / "lib" / "services" / "catalog.ts",
        TERMINAL_ROOT / "products" / "pc" / "app" / "src" / "lib" / "services" / "procurement.ts",
        TERMINAL_ROOT / "products" / "pc" / "app" / "src" / "lib" / "services" / "sync.ts",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "src" / "lib" / "services" / "sales.ts",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "src" / "lib" / "services" / "shift.ts",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "src" / "lib" / "services" / "returns.ts",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "src" / "lib" / "services" / "stock.ts",
        TERMINAL_ROOT / "products" / "tablet" / "app" / "src" / "lib" / "services" / "sync.ts",
    ]
    missing = [win(file) for file in service_files if not file.exists()]
    return {
        "critical_files_checked": [win(file) for file in critical_files],
        "service_files_checked": [win(file) for file in service_files],
        "forbidden_demo_import_violations": violations,
        "missing_service_files": missing,
        "pass": not violations and not missing,
    }


def parse_smoke(stdout: str) -> dict:
    try:
        payload = json.loads(stdout[stdout.find("{") :])
        return payload
    except Exception as exc:
        return {"pass": False, "parse_error": str(exc), "stdout": stdout[-1000:]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate canonical Prisma foundation for Terminal de Venta.")
    parser.add_argument("--out", default="", help="Optional JSON report path")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    db_dir = REPO_ROOT / "tools" / "_local" / "tmp" / "terminal-de-venta-prisma"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / f"canonical-validation-{stamp}.db"
    database_url = prisma_file_url(db_path)

    env = dict(**{k: v for k, v in dict(__import__("os").environ).items()})
    env["DATABASE_URL"] = database_url

    pc_schema = cached_schema_for(PC_APP)
    tablet_schema = cached_schema_for(TABLET_APP)
    commands = {
        "generate_pc": run_command(["pnpm", "exec", "prisma", "generate", "--schema", win(pc_schema)], PC_APP, env),
        "generate_tablet": None,
        "migrate_apply": None,
        "seed": None,
        "runtime_smoke": None,
    }
    if commands["generate_pc"]["pass"]:
        commands["generate_tablet"] = run_command(
                ["pnpm", "exec", "prisma", "generate", "--schema", win(tablet_schema)],
            TABLET_APP,
            env,
        )
    if commands["generate_tablet"] and commands["generate_tablet"]["pass"]:
        commands["migrate_apply"] = run_command(
            [sys.executable, win(APPLY_MIGRATIONS)],
            TERMINAL_ROOT,
            env,
        )
    if commands["migrate_apply"] and commands["migrate_apply"]["pass"]:
        commands["seed"] = run_command(["node", win(SEED_SCRIPT)], PC_APP, env)
    if commands["seed"] and commands["seed"]["pass"]:
        commands["runtime_smoke"] = run_command(["node", win(SMOKE_SCRIPT)], PC_APP, env)

    seed = load_seed()
    seed_procurement = check_seed_procurement(seed)
    sql_procurement = check_sql_procurement(seed_procurement)
    runtime_sources = check_runtime_sources()

    db_checks = {}
    if commands["seed"] and commands["seed"]["pass"]:
        with connect(db_path) as conn:
            db_checks = {
                "migrations": check_migrations(conn),
                "seed_counts": check_seed_counts(conn),
                "procurement": check_db_procurement(conn),
                "uniqueness": check_uniqueness(conn),
                "constraint_enforcement": check_constraint_enforcement(conn),
            }

    runtime_smoke = (
        parse_smoke(commands["runtime_smoke"]["stdout_tail"])
        if commands.get("runtime_smoke") and commands["runtime_smoke"]["pass"]
        else {"pass": False, "command": commands.get("runtime_smoke")}
    )

    command_pass = all(value and value["pass"] for value in commands.values())
    db_pass = bool(db_checks) and all(section["pass"] for section in db_checks.values())
    report = {
        "status": "PASS" if command_pass and db_pass and seed_procurement["pass"] and sql_procurement["pass"] and runtime_sources["pass"] and runtime_smoke.get("pass") else "FAIL",
        "generatedAt": stamp,
        "canonicalPrisma": win(SCHEMA),
        "validationDatabase": win(db_path),
        "commands": commands,
        "seed_procurement": seed_procurement,
        "sql_procurement": sql_procurement,
        "db_checks": db_checks,
        "runtime_smoke": runtime_smoke,
        "runtime_sources": runtime_sources,
    }
    report["pass"] = report["status"] == "PASS"

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    print(payload)
    if args.out:
      out_path = Path(args.out)
      out_path.parent.mkdir(parents=True, exist_ok=True)
      out_path.write_text(payload + "\n", encoding="utf-8")

    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

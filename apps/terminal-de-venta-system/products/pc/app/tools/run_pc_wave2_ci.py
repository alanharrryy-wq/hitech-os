#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

APP_REL = Path("apps/terminal-de-venta-system/products/pc/app")
SEED_REL = Path("apps/terminal-de-venta-system/prisma/seeds/canonical.seed.json")
SCHEMA_REL_FROM_APP = "../../../prisma/schema.prisma"
SEED_ORDER = (
    ("businesses", "Business"),
    ("stores", "Store"),
    ("terminals", "Terminal"),
    ("taxRates", "TaxRate"),
    ("priceLists", "PriceList"),
    ("products", "Product"),
    ("barcodes", "Barcode"),
    ("priceListItems", "PriceListItem"),
    ("stockSnapshots", "StockSnapshot"),
    ("stockMovements", "StockMovement"),
    ("suppliers", "Supplier"),
    ("purchaseOrders", "PurchaseOrder"),
    ("purchaseOrderLines", "PurchaseOrderLine"),
    ("goodsReceipts", "GoodsReceipt"),
    ("goodsReceiptLines", "GoodsReceiptLine"),
    ("replenishmentSignals", "ReplenishmentSignal"),
    ("cashSessions", "CashSession"),
    ("cashMovements", "CashMovement"),
    ("sales", "Sale"),
    ("saleLines", "SaleLine"),
    ("saleReturns", "SaleReturn"),
    ("auditCounts", "AuditCount"),
    ("outboxEvents", "OutboxEvent"),
)
FORBIDDEN_LOG_PATTERNS = (
    r"PrismaClientKnownRequestError",
    r"unhandledRejection",
    r"no such table",
    r"SQLITE_ERROR",
    r"Error: ENOENT",
    r"code[^A-Za-z0-9]+ENOENT",
)


def run(cmd: list[str], *, cwd: Path, env: dict[str, str], stdout=None) -> None:
    printable = " ".join(cmd)
    print(f"[wave2] $ {printable}", flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True, stdout=stdout)


def normalize_seed_value(value: Any) -> Any:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def seed_database(database: Path, seed_path: Path, out: Path) -> None:
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    inserted: dict[str, int] = {}
    conn = sqlite3.connect(database)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        for collection, table in SEED_ORDER:
            rows = seed.get(collection, []) or []
            table_columns = {
                row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')
            }
            if not table_columns:
                raise RuntimeError(f"missing migrated table during canonical seed: {table}")
            count = 0
            for row in rows:
                payload = {
                    key: normalize_seed_value(value)
                    for key, value in row.items()
                    if key in table_columns
                }
                if not payload:
                    continue
                columns = list(payload)
                quoted = ",".join(f'"{column}"' for column in columns)
                placeholders = ",".join("?" for _ in columns)
                conn.execute(
                    f'INSERT INTO "{table}" ({quoted}) VALUES ({placeholders})',
                    [payload[column] for column in columns],
                )
                count += 1
            inserted[table] = count
        conn.commit()
        violations = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
        required_nonempty = (
            "Business",
            "Product",
            "Supplier",
            "StockSnapshot",
            "StockMovement",
            "AuditCount",
        )
        observed = {
            table: conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in required_nonempty
        }
        missing = {table: count for table, count in observed.items() if count <= 0}
        report = {
            "database": str(database),
            "seed": str(seed_path),
            "inserted": inserted,
            "observed": observed,
            "foreignKeyViolations": violations,
            "pass": not missing and not violations,
        }
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2), flush=True)
        if missing:
            raise RuntimeError(f"canonical fixture did not populate required tables: {missing}")
        if violations:
            raise RuntimeError(f"canonical fixture produced FK violations: {violations[:5]}")
    finally:
        conn.close()


def write_license(path: Path, mode: str) -> None:
    now = datetime.now(timezone.utc)
    common = {
        "schemaVersion": "1.0.0",
        "customerId": f"cust_wave2_{mode}_ci",
        "businessId": "biz_hitech_default",
        "storeId": "store_obrera_04",
        "state": "active",
        "validFrom": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "validUntil": (now + timedelta(days=30)).isoformat().replace("+00:00", "Z"),
        "assignmentState": "assigned",
        "features": {},
        "capabilities": {},
        "notes": [f"Wave 2 isolated {mode} PC runtime evidence fixture"],
    }
    if mode == "entitled":
        payload = {
            **common,
            "licenseId": "lic_wave2_runtime_ci",
            "plan": "TABLET_PC_MANAGED",
            "limits": {"maxDevices": 2},
        }
    else:
        payload = {
            **common,
            "licenseId": "lic_wave2_restricted_ci",
            "deviceId": "pc_wave2_restricted_ci",
            "plan": "TABLET_SOLO",
            "authorizedDevices": [
                {
                    "deviceId": "pc_wave2_restricted_ci",
                    "role": "pc",
                    "storeId": "store_obrera_04",
                }
            ],
            "limits": {"maxDevices": 1},
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[wave2] license fixture: {path}", flush=True)


def wait_for_runtime(url: str, process: subprocess.Popen[Any], log_path: Path) -> None:
    for _ in range(120):
        if process.poll() is not None:
            break
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(1)
    log_tail = ""
    if log_path.is_file():
        log_tail = log_path.read_text(encoding="utf-8", errors="replace")[-12000:]
    raise RuntimeError(f"PC runtime did not become ready at {url}\n{log_tail}")


def stop_runtime(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    try:
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=12)
    except Exception:
        process.kill()
        process.wait(timeout=8)


def assert_clean_log(log_path: Path, copied_log: Path) -> None:
    if not log_path.is_file():
        raise RuntimeError("PC server log was not created")
    shutil.copy2(log_path, copied_log)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    hits = [pattern for pattern in FORBIDDEN_LOG_PATTERNS if re.search(pattern, text, re.I)]
    report = {
        "log": str(log_path),
        "forbiddenPatterns": list(FORBIDDEN_LOG_PATTERNS),
        "matches": hits,
        "pass": not hits,
    }
    copied_log.with_suffix(".scan.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if hits:
        raise RuntimeError(f"forbidden runtime log patterns found: {hits}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("entitled", "restricted"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(os.environ.get("GITHUB_WORKSPACE") or Path.cwd()).resolve()
    app = repo / APP_REL
    seed = repo / SEED_REL
    out = (repo / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    runner_temp = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()).resolve()
    runtime_root = Path(tempfile.mkdtemp(prefix=f"pc-wave2-{args.mode}-", dir=runner_temp))
    database = runtime_root / "canonical.db"
    license_path = runtime_root / "license.json"
    canonical_ddl = out / "CANONICAL_SCHEMA_FROM_EMPTY.sql"
    server_log = out / "pc-3130.log"

    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": f"file:{database.as_posix()}",
            "PRISMA_LICENSE_PATH": str(license_path),
            "PRISMA_LICENSE_ALLOW_UNSIGNED": "1",
            "PRISMA_RUNTIME_MODE": "dev",
            "PRISMA_RUNTIME_ROLE": "pc",
        }
    )
    if args.mode == "restricted":
        env["PRISMA_LICENSE_DEVICE_ID"] = "pc_wave2_restricted_ci"

    process: subprocess.Popen[Any] | None = None
    log_handle = None
    try:
        run(["pnpm", "-C", str(APP_REL), "run", "prisma:generate"], cwd=repo, env=env)
        run(["pnpm", "-C", str(APP_REL), "run", "db:canonical:migrate"], cwd=repo, env=env)

        with canonical_ddl.open("w", encoding="utf-8") as ddl_out:
            run(
                [
                    "pnpm",
                    "-C",
                    str(APP_REL),
                    "exec",
                    "prisma",
                    "migrate",
                    "diff",
                    "--from-empty",
                    "--to-schema-datamodel",
                    SCHEMA_REL_FROM_APP,
                    "--script",
                ],
                cwd=repo,
                env=env,
                stdout=ddl_out,
            )

        run(
            [
                sys.executable,
                str(APP_REL / "tools/verify_pc_wave2_schema_parity.py"),
                "--database",
                str(database),
                "--canonical-ddl",
                str(canonical_ddl),
                "--out",
                str(out / "PC_WAVE2_SCHEMA_PARITY.json"),
            ],
            cwd=repo,
            env=env,
        )

        seed_database(database, seed, out / "CANONICAL_FIXTURE_SEED.json")
        write_license(license_path, args.mode)

        log_handle = (runtime_root / "pc-3130.log").open("w", encoding="utf-8")
        process = subprocess.Popen(
            ["pnpm", "-C", str(APP_REL), "dev"],
            cwd=repo,
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        wait_for_runtime("http://127.0.0.1:3130/catalog", process, runtime_root / "pc-3130.log")

        verifier = (
            "tools/visual/verify_pc_customer_experience_wave2_runtime.mjs"
            if args.mode == "entitled"
            else "tools/visual/verify_pc_customer_experience_wave2_license.mjs"
        )
        run(
            [
                "node",
                str(APP_REL / verifier),
                "--base-url",
                "http://127.0.0.1:3130",
                "--out",
                str(out),
            ],
            cwd=repo,
            env=env,
        )
    finally:
        if process is not None:
            stop_runtime(process)
        if log_handle is not None:
            log_handle.close()
        source_log = runtime_root / "pc-3130.log"
        if source_log.is_file():
            assert_clean_log(source_log, server_log)

    manifest = {
        "verifier": "PC_WAVE2_CI_RUNNER_V1",
        "mode": args.mode,
        "repoHead": os.environ.get("GITHUB_SHA"),
        "databaseIsIsolatedRunnerTemp": True,
        "liveDatabaseMutated": False,
        "runtimeProcessOwnedByThisRunner": True,
        "output": str(out),
        "pass": True,
    }
    (out / "PC_WAVE2_CI_RUNNER_RESULT.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

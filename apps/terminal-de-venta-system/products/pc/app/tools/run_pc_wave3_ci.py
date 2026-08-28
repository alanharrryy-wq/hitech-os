#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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

APP_REL = Path("apps/terminal-de-venta-system/products/pc/app")
SEED_REL = Path("apps/terminal-de-venta-system/prisma/seeds/canonical.seed.json")
RETRY_EVENT_ID = "outbox_wave3_retry_ci"
FORBIDDEN_LOG_PATTERNS = (
    r"PrismaClientKnownRequestError",
    r"unhandledRejection",
    r"no such table",
    r"SQLITE_ERROR",
    r"Error: ENOENT",
    r"code[^A-Za-z0-9]+ENOENT",
)
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
SOURCE_SNAPSHOT = (
    ".github/workflows/pc-wave3-certification.yml",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/sync/export-pc-to-tablet/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/sync/retry/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/catalog/products/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/catalog/products/[productId]/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/suppliers/records/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/suppliers/records/[supplierId]/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/inventory/adjustments/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/counts/records/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/counts/records/[countId]/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/devices/claims/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/app/api/backoffice/settings/business/route.ts",
    "apps/terminal-de-venta-system/products/pc/app/src/server/services/catalog-mutations.service.ts",
    "apps/terminal-de-venta-system/products/pc/app/src/server/services/supplier-records.service.ts",
    "apps/terminal-de-venta-system/products/pc/app/src/server/services/inventory-mutations.service.ts",
    "apps/terminal-de-venta-system/products/pc/app/src/server/services/device-claims.service.ts",
    "apps/terminal-de-venta-system/products/pc/app/src/server/services/business-settings.service.ts",
    "apps/terminal-de-venta-system/products/pc/app/src/server/services/wave3-mutation-audit.ts",
    "apps/terminal-de-venta-system/products/pc/app/tools/visual/verify_pc_enterprise_mutations_wave3_runtime.mjs",
    "apps/terminal-de-venta-system/products/pc/app/tools/run_pc_wave3_ci.py",
)


def progress(percent: int, message: str) -> None:
    remaining = max(0, 100 - percent)
    width = 28
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    print(f"[wave3] [{bar}] {percent:3d}% | falta {remaining:3d}% | {message}", flush=True)


def run(cmd: list[str], *, cwd: Path, env: dict[str, str], stdout=None) -> None:
    print(f"[wave3] $ {' '.join(cmd)}", flush=True)
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
            table_columns = {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}
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
        business_count = conn.execute('SELECT COUNT(*) FROM "Business"').fetchone()[0]
        product_count = conn.execute('SELECT COUNT(*) FROM "Product"').fetchone()[0]
        violations = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
        report = {
            "database": str(database),
            "seed": str(seed_path),
            "inserted": inserted,
            "businessCount": business_count,
            "productCount": product_count,
            "foreignKeyViolations": violations,
            "pass": business_count > 0 and product_count > 0 and not violations,
        }
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if not report["pass"]:
            raise RuntimeError(f"canonical seed failed Wave 3 prerequisites: {report}")
    finally:
        conn.close()


def seed_retry_event(database: Path, out: Path) -> None:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    conn = sqlite3.connect(database)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        business = conn.execute('SELECT "id" FROM "Business" ORDER BY "createdAt" ASC LIMIT 1').fetchone()
        if not business:
            raise RuntimeError("Wave 3 retry fixture requires a canonical Business row")
        business_id = str(business[0])
        conn.execute('DELETE FROM "OutboxEvent" WHERE "id" = ?', (RETRY_EVENT_ID,))
        conn.execute(
            '''INSERT INTO "OutboxEvent" (
                "id", "businessId", "terminalId", "topic", "eventType", "aggregateId",
                "idempotencyKey", "correlationId", "payloadJson", "source", "schemaVersion",
                "status", "lifecycleStatus", "attempts", "createdAt", "failedAt", "lastError"
            ) VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                RETRY_EVENT_ID,
                business_id,
                "catalog.product.updated",
                "wave3.retry.fixture",
                "wave3-ci-aggregate",
                "wave3-ci-retry-idempotency",
                "wave3-ci-correlation",
                json.dumps({"fixture": "wave3-replay", "safe": True}, separators=(",", ":")),
                "pc-wave3-ci",
                "1.0.0",
                "failed",
                "failed",
                1,
                now,
                now,
                "isolated-ci-seeded-failure",
            ),
        )
        conn.commit()
        row = conn.execute(
            'SELECT "id", "businessId", "status", "lifecycleStatus", "attempts", "lastError" FROM "OutboxEvent" WHERE "id" = ?',
            (RETRY_EVENT_ID,),
        ).fetchone()
        report = {
            "id": row[0],
            "businessId": row[1],
            "status": row[2],
            "lifecycleStatus": row[3],
            "attempts": row[4],
            "lastError": row[5],
            "isolatedSyntheticFixture": True,
            "pass": row[2] == "failed" and row[3] == "failed" and row[4] == 1,
        }
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if not report["pass"]:
            raise RuntimeError(f"retry fixture invalid: {report}")
    finally:
        conn.close()


def write_license(path: Path) -> None:
    now = datetime.now(timezone.utc)
    payload = {
        "schemaVersion": "1.0.0",
        "licenseId": "lic_pc_wave3_runtime_ci",
        "customerId": "cust_pc_wave3_runtime_ci",
        "businessId": "biz_hitech_default",
        "storeId": "store_obrera_04",
        "plan": "TABLET_PC_MANAGED",
        "state": "active",
        "validFrom": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "validUntil": (now + timedelta(days=30)).isoformat().replace("+00:00", "Z"),
        "assignmentState": "assigned",
        "limits": {"maxDevices": 4},
        "features": {},
        "capabilities": {},
        "notes": ["Wave 3 isolated enterprise mutation runtime certification fixture"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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
    tail = log_path.read_text(encoding="utf-8", errors="replace")[-16000:] if log_path.is_file() else ""
    raise RuntimeError(f"PC Wave 3 runtime did not become ready at {url}\n{tail}")


def stop_runtime(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    try:
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=12)
    except Exception:
        process.kill()
        process.wait(timeout=8)


def scan_log(log_path: Path, output_log: Path) -> dict[str, Any]:
    if not log_path.is_file():
        raise RuntimeError("PC Wave 3 server log was not created")
    shutil.copy2(log_path, output_log)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    hits = [pattern for pattern in FORBIDDEN_LOG_PATTERNS if re.search(pattern, text, re.I)]
    report = {"patterns": list(FORBIDDEN_LOG_PATTERNS), "matches": hits, "pass": not hits}
    output_log.with_suffix(".scan.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def query_one(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return conn.execute(sql, params).fetchone()


def postvalidate(database: Path, runtime_result_path: Path, out: Path) -> dict[str, Any]:
    runtime = json.loads(runtime_result_path.read_text(encoding="utf-8"))
    ids = runtime.get("ids") or {}
    expected = runtime.get("expected") or {}
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, observed: Any = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "observed": observed})

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        check("catalog CRUD product deleted", query_one(conn, 'SELECT COUNT(*) AS n FROM "Product" WHERE "id"=?', (ids.get("catalogProductId"),))["n"] == 0)
        check("supplier CRUD record deleted", query_one(conn, 'SELECT COUNT(*) AS n FROM "Supplier" WHERE "id"=?', (ids.get("supplierId"),))["n"] == 0)

        stock = query_one(conn, 'SELECT "stockOnHand" FROM "Product" WHERE "id"=?', (ids.get("stockProductId"),))
        check("stock product persisted", stock is not None and stock["stockOnHand"] == expected.get("stockOnHand"), dict(stock) if stock else None)
        snapshot = query_one(conn, 'SELECT "onHand", "available", "location" FROM "StockSnapshot" WHERE "id"=?', (ids.get("stockSnapshotId"),))
        check("stock snapshot persisted", snapshot is not None and snapshot["onHand"] == expected.get("stockLocationOnHand") and snapshot["location"] == "W3-CI", dict(snapshot) if snapshot else None)
        movement = query_one(conn, 'SELECT "movement", "qty", "reason" FROM "StockMovement" WHERE "id"=?', (ids.get("stockMovementId"),))
        check("stock movement persisted", movement is not None and movement["movement"] == "adjust_up" and movement["qty"] == 5, dict(movement) if movement else None)

        count = query_one(conn, 'SELECT "status", "variance", "countedBy" FROM "AuditCount" WHERE "id"=?', (ids.get("countId"),))
        check("count lifecycle persisted closed", count is not None and count["status"] == expected.get("countStatus") and count["variance"] == expected.get("countVariance"), dict(count) if count else None)

        retry = query_one(conn, 'SELECT "status", "lifecycleStatus", "attempts", "failedAt", "deadLetterAt", "lastError" FROM "OutboxEvent" WHERE "id"=?', (ids.get("retryEventId"),))
        check(
            "sync replay persisted",
            retry is not None and retry["status"] == expected.get("retryStatus") and retry["lifecycleStatus"] == expected.get("retryLifecycleStatus") and retry["attempts"] == expected.get("retryAttempts") and retry["failedAt"] is None and retry["deadLetterAt"] is None and retry["lastError"] is None,
            dict(retry) if retry else None,
        )

        device = query_one(conn, 'SELECT "status", "health", "syncStatus", "metadataJson" FROM "DeviceHeartbeat" WHERE "id"=?', (ids.get("deviceHeartbeatId"),))
        check("device revoke persisted", device is not None and device["status"] == expected.get("deviceStatus") and device["health"] == "revoked" and device["syncStatus"] == "revoked", dict(device) if device else None)

        settings = query_one(conn, 'SELECT "name", "taxId", "currency" FROM "Business" WHERE "id"=?', (ids.get("businessId"),))
        expected_settings = expected.get("settings") or {}
        check("settings write persisted", settings is not None and settings["name"] == expected_settings.get("name") and settings["taxId"] == expected_settings.get("taxId") and settings["currency"] == expected_settings.get("currency"), dict(settings) if settings else None)

        dispatch_audit = query_one(conn, 'SELECT "topic", "id" FROM "AuditEvent" WHERE "id"=?', (ids.get("syncDispatchAuditEventId"),))
        check("sync dispatch audit persisted", dispatch_audit is not None and dispatch_audit["topic"] == "pc.catalog.delta.exported", dict(dispatch_audit) if dispatch_audit else None)

        required_topics = [
            "catalog.product.created",
            "catalog.product.updated",
            "catalog.product.deleted",
            "supplier.created",
            "supplier.updated",
            "supplier.deleted",
            "inventory.stock.adjusted",
            "inventory.count.opened",
            "inventory.count.reviewed",
            "inventory.count.closed",
            "pc.catalog.delta.exported",
            "pc.sync.retry.requested",
            "device.claimed",
            "device.revoked",
            "settings.business.updated",
        ]
        for topic in required_topics:
            row = query_one(conn, 'SELECT COUNT(*) AS n FROM "AuditEvent" WHERE "topic"=?', (topic,))
            topic_count = int(row["n"] if row else 0)
            check(f"audit topic {topic}", topic_count >= 1, topic_count)

        violations = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
        check("foreign key check empty", not violations, violations[:10])
    finally:
        conn.close()

    report = {
        "schemaVersion": "prisma.pc-wave3.persistence-certification.v1",
        "result": "PASS_PC_ENTERPRISE_MUTATIONS_WAVE3_PERSISTENCE" if all(row["pass"] for row in checks) else "FAIL_PC_ENTERPRISE_MUTATIONS_WAVE3_PERSISTENCE",
        "databaseIsIsolatedRunnerTemp": True,
        "liveDatabaseMutated": False,
        "checks": checks,
        "pass": all(row["pass"] for row in checks),
    }
    (out / "PC_WAVE3_PERSISTENCE_RESULT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def snapshot_sources(repo: Path, out: Path) -> None:
    target = out / "source_snapshot"
    manifest = []
    for rel in SOURCE_SNAPSHOT:
        src = repo / rel
        if not src.is_file():
            manifest.append({"path": rel, "present": False})
            continue
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        manifest.append({"path": rel, "present": True, "sha256": digest, "bytes": src.stat().st_size})
    (out / "SOURCE_SNAPSHOT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(os.environ.get("GITHUB_WORKSPACE") or Path.cwd()).resolve()
    seed = repo / SEED_REL
    out = (repo / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    snapshot_sources(repo, out)

    runner_temp = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()).resolve()
    runtime_root = Path(tempfile.mkdtemp(prefix="pc-wave3-", dir=runner_temp))
    database = runtime_root / "canonical-wave3.db"
    license_path = runtime_root / "license.json"
    source_log = runtime_root / "pc-3130.log"
    output_log = out / "pc-3130.log"
    runtime_result_path = out / "PC_WAVE3_RUNTIME_RESULT.json"

    env = os.environ.copy()
    env.update({
        "DATABASE_URL": f"file:{database.as_posix()}",
        "PRISMA_LICENSE_PATH": str(license_path),
        "PRISMA_LICENSE_ALLOW_UNSIGNED": "1",
        "PRISMA_RUNTIME_MODE": "dev",
        "PRISMA_RUNTIME_ROLE": "pc",
        "PRISMA_WAVE3_RETRY_EVENT_ID": RETRY_EVENT_ID,
    })

    process: subprocess.Popen[Any] | None = None
    log_handle = None
    failure: dict[str, Any] | None = None
    persistence_report: dict[str, Any] | None = None
    log_report: dict[str, Any] | None = None

    try:
        progress(5, "generando Prisma en runner aislado")
        run(["pnpm", "-C", str(APP_REL), "run", "prisma:generate"], cwd=repo, env=env)

        progress(15, "aplicando migraciones canónicas a SQLite temporal")
        run(["pnpm", "-C", str(APP_REL), "run", "db:canonical:migrate"], cwd=repo, env=env)

        progress(25, "sembrando fixture canónica")
        seed_database(database, seed, out / "CANONICAL_FIXTURE_SEED.json")
        seed_retry_event(database, out / "WAVE3_RETRY_FIXTURE.json")
        write_license(license_path)

        progress(35, "levantando runtime PC poseído por este runner")
        log_handle = source_log.open("w", encoding="utf-8")
        process = subprocess.Popen(
            ["pnpm", "-C", str(APP_REL), "dev"],
            cwd=repo,
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        wait_for_runtime("http://127.0.0.1:3130/catalog", process, source_log)

        progress(50, "ejecutando siete journeys Wave 3 por HTTP")
        try:
            run([
                "node",
                str(APP_REL / "tools/visual/verify_pc_enterprise_mutations_wave3_runtime.mjs"),
                "--base-url", "http://127.0.0.1:3130",
                "--out", str(out),
            ], cwd=repo, env=env)
        except subprocess.CalledProcessError as error:
            failure = {"stage": "runtime_verifier", "returncode": error.returncode, "command": error.cmd}
    except Exception as error:
        failure = failure or {"stage": "runner_setup_or_runtime", "type": type(error).__name__, "message": str(error)}
    finally:
        progress(70, "cerrando únicamente el runtime poseído por el runner")
        stop_runtime(process)
        if log_handle is not None:
            log_handle.close()
        try:
            if source_log.is_file():
                log_report = scan_log(source_log, output_log)
                if not log_report["pass"] and failure is None:
                    failure = {"stage": "runtime_log_scan", "matches": log_report["matches"]}
        except Exception as error:
            if failure is None:
                failure = {"stage": "runtime_log_capture", "type": type(error).__name__, "message": str(error)}

    progress(80, "validando persistencia y auditoría directamente en SQLite aislado")
    if runtime_result_path.is_file():
        try:
            persistence_report = postvalidate(database, runtime_result_path, out)
            if not persistence_report["pass"] and failure is None:
                failure = {"stage": "persistence_postvalidation", "result": persistence_report["result"]}
        except Exception as error:
            if failure is None:
                failure = {"stage": "persistence_postvalidation", "type": type(error).__name__, "message": str(error)}
    else:
        failure = failure or {"stage": "runtime_result_missing"}

    if database.is_file():
        shutil.copy2(database, out / "canonical-wave3-evidence.db")

    progress(90, "cerrando manifest y no-fake-green")
    runtime_result = None
    if runtime_result_path.is_file():
        try:
            runtime_result = json.loads(runtime_result_path.read_text(encoding="utf-8"))
        except Exception:
            runtime_result = None

    passed = (
        failure is None
        and runtime_result is not None
        and runtime_result.get("result") == "PASS_PC_ENTERPRISE_MUTATIONS_WAVE3_RUNTIME"
        and persistence_report is not None
        and persistence_report.get("pass") is True
        and log_report is not None
        and log_report.get("pass") is True
    )
    manifest = {
        "schemaVersion": "prisma.pc-wave3.ci-runner.v1",
        "result": "PASS_PC_ENTERPRISE_MUTATIONS_WAVE3_CERTIFICATION" if passed else "FAIL_PC_ENTERPRISE_MUTATIONS_WAVE3_CERTIFICATION",
        "repoHead": os.environ.get("GITHUB_SHA") or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "database": str(database),
        "databaseIsIsolatedRunnerTemp": True,
        "liveDatabaseMutated": False,
        "runtimeProcessOwnedByThisRunner": True,
        "runtimeResult": runtime_result.get("result") if runtime_result else None,
        "persistenceResult": persistence_report.get("result") if persistence_report else None,
        "logPass": log_report.get("pass") if log_report else False,
        "failure": failure,
        "productionCertified": False,
        "pass": passed,
    }
    (out / "PC_WAVE3_CI_RUNNER_RESULT.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if failure:
        (out / "ERROR.txt").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        (out / "CONTINUATION.md").write_text(
            "# PC Wave 3 continuation\n\nCertification did not pass. Use `PC_WAVE3_CI_RUNNER_RESULT.json`, runtime/persistence reports, `pc-3130.log`, the isolated evidence DB, and `source_snapshot/` to identify one reproducible root cause before any repair. A fresh Authority Mesh is required before another source mutation.\n",
            encoding="utf-8",
        )

    progress(100, manifest["result"])
    print(json.dumps(manifest, indent=2), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

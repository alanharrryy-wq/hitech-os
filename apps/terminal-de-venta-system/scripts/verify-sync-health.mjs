#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, run, statusRank, terminalRoot, writeJson, writeText } from "./prisma-codex-utils.mjs";

const strict = process.argv.includes("--strict");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const dbs = [
  path.join(terminalRoot, "products", "tablet", "app", "data", "tablet-pos.db"),
  path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db")
];
const requiredObservabilityTables = ["SyncAttempt", "SyncConflict", "DeviceHeartbeat", "SyncCheckpoint", "SyncOutboxStatusBucket", "DataSourceFreshness"];

const py = String.raw`
import sqlite3, json, sys, os
required=sys.argv[1].split(",")
dbs=sys.argv[2:]
out=[]
for db in dbs:
  item={"path":db,"exists":os.path.exists(db),"checks":[],"readiness":"missing"}
  if not item["exists"]:
    item["checks"].append({"status":"WARN","message":"DB missing"})
    out.append(item); continue
  con=sqlite3.connect(db); cur=con.cursor()
  tables=[r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
  item["tables"]=tables
  if "OutboxEvent" in tables:
    cols=[r[1] for r in cur.execute('PRAGMA table_info("OutboxEvent")').fetchall()]
    statusCounts={}
    if "status" in cols:
      statusCounts={str(k):v for k,v in cur.execute('SELECT status, COUNT(*) FROM "OutboxEvent" GROUP BY status').fetchall()}
    item["outboxStatusCounts"]=statusCounts
    item["outboxTotal"]=cur.execute('SELECT COUNT(*) FROM "OutboxEvent"').fetchone()[0]
    item["checks"].append({"status":"PASS","message":"OutboxEvent available for sync health base"})
  else:
    item["checks"].append({"status":"FAIL","message":"OutboxEvent missing"})
  missing=[t for t in required if t not in tables]
  item["missingObservabilityTables"]=missing
  for t in missing:
    item["checks"].append({"status":"WARN","message":f"{t} real table missing in live DB"})
  item["readiness"]="ready" if not missing else ("partial" if "OutboxEvent" in tables else "missing")
  con.close()
  out.append(item)
print(json.dumps(out, ensure_ascii=False))
`;

const result = run("python", ["-c", py, requiredObservabilityTables.join(","), ...dbs]);
const dbReports = result.status === 0 ? JSON.parse(result.stdout || "[]") : [{ path: "python", checks: [{ status: "FAIL", message: result.stderr || result.stdout }], readiness: "missing" }];
for (const report of dbReports) {
  const isTabletLocalDb = String(report.path || "").includes(`${path.join("products", "tablet", "app", "data", "tablet-pos.db")}`);
  if (!isTabletLocalDb) continue;
  report.checks = (report.checks || []).filter((check) => !String(check.message || "").includes("real table missing in live DB"));
  report.missingObservabilityTables = [];
  if (report.tables?.includes("OutboxEvent")) {
    report.readiness = "ready";
    report.checks.push({ status: "PASS", message: "Tablet local DB stays standalone; root observability tables are canonical/PC-only" });
  }
}

const rootSchemaPath = path.join(terminalRoot, "prisma", "schema.prisma");
const tabletSchemaPath = path.join(terminalRoot, "products", "tablet", "app", "prisma", "schema.prisma");
const syncMigrationPath = path.join(terminalRoot, "prisma", "migrations", "20260512000100_sync_observability_tables", "migration.sql");
const tabletMigrationPath = path.join(terminalRoot, "products", "tablet", "app", "prisma", "migrations", "20260512000200_outbox_idempotency_key", "migration.sql");
function readSafe(file) { return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : ""; }
const rootSchema = readSafe(rootSchemaPath);
const tabletSchema = readSafe(tabletSchemaPath);
const syncMigration = readSafe(syncMigrationPath);
const tabletMigration = readSafe(tabletMigrationPath);
const staticChecks = [];
for (const table of requiredObservabilityTables) {
  staticChecks.push({ status: rootSchema.includes(`model ${table}`) ? "PASS" : "FAIL", message: `root schema model ${table}` });
  staticChecks.push({ status: syncMigration.includes(`"${table}"`) && /CREATE TABLE/i.test(syncMigration) ? "PASS" : "FAIL", message: `migration creates ${table}` });
}
staticChecks.push({ status: /model\s+OutboxEvent[\s\S]*idempotencyKey/.test(rootSchema) ? "PASS" : "FAIL", message: "root OutboxEvent.idempotencyKey" });
staticChecks.push({ status: /model\s+OutboxEvent[\s\S]*idempotencyKey/.test(tabletSchema) ? "PASS" : "FAIL", message: "tablet OutboxEvent.idempotencyKey" });
staticChecks.push({ status: tabletMigration.includes('ADD COLUMN "idempotencyKey"') ? "PASS" : "FAIL", message: "tablet idempotency migration" });

const triDbStatusPath = path.join(terminalRoot, "shared", "tri-db", "status.latest.json");
const triDb = fs.existsSync(triDbStatusPath) ? JSON.parse(fs.readFileSync(triDbStatusPath, "utf8")) : null;
const checks = [...staticChecks, ...dbReports.flatMap((db) => db.checks)];
if (strict) {
  for (const db of dbReports) {
    if (String(db.path || "").includes(`${path.join("products", "tablet", "app", "data", "tablet-pos.db")}`)) continue;
    for (const table of db.missingObservabilityTables || []) checks.push({ status: "FAIL", message: `strict requires real table ${table} in ${db.path}` });
  }
}
if (triDb?.status) checks.push({ status: triDb.status === "READY" ? "PASS" : "WARN", message: `shared tri-db status ${triDb.status}` });
else checks.push({ status: "WARN", message: "shared tri-db status missing" });

const overall = statusRank(checks.map((item) => item.status));
const report = { generatedAt: new Date().toISOString(), strict, overall, triDbStatusPath, triDbSummary: triDb ? { status: triDb.status, generated_at: triDb.generated_at, latest_bridge_status: triDb.latest_bridge_status } : null, staticChecks, dbReports };
const paths = reportPaths("SYNC_HEALTH_REPORT");
writeJson(paths.json, report);
writeText(paths.md, [
  "# Sync Health Report",
  "",
  `Overall: ${overall}`,
  `Strict: ${strict}`,
  `Tri-DB status: ${triDb?.status || "missing"}`,
  "",
  ...dbReports.flatMap((db) => [`- DB: ${db.path}`, `  - readiness: ${db.readiness}`, `  - outbox: ${JSON.stringify(db.outboxStatusCounts || {})}`, `  - missing observability tables: ${(db.missingObservabilityTables || []).join(", ") || "none"}`, ...db.checks.map((check) => `  - ${check.status}: ${check.message}`)])
].join("\n") + "\n");

console.log(`${overall} sync health report: ${paths.md}`);
if (overall === "FAIL") process.exit(1);

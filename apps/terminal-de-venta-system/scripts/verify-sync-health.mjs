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
const futureTables = ["SyncAttempt", "SyncConflict", "DeviceHeartbeat", "SyncCheckpoint", "SyncOutboxStatusBucket", "DataSourceFreshness"];

const py = String.raw`
import sqlite3, json, sys, os
future=sys.argv[1].split(",")
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
  missing=[t for t in future if t not in tables]
  item["missingFutureTables"]=missing
  for t in missing:
    item["checks"].append({"status":"WARN","message":f"{t} table/read model missing"})
  item["readiness"]="ready" if not missing else ("partial" if "OutboxEvent" in tables else "missing")
  con.close()
  out.append(item)
print(json.dumps(out, ensure_ascii=False))
`;

const result = run("python", ["-c", py, futureTables.join(","), ...dbs]);
const dbReports = result.status === 0 ? JSON.parse(result.stdout || "[]") : [{ path: "python", checks: [{ status: "FAIL", message: result.stderr || result.stdout }], readiness: "missing" }];
const triDbStatusPath = path.join(terminalRoot, "shared", "tri-db", "status.latest.json");
const triDb = fs.existsSync(triDbStatusPath) ? JSON.parse(fs.readFileSync(triDbStatusPath, "utf8")) : null;
const checks = dbReports.flatMap((db) => db.checks);
if (strict) {
  for (const db of dbReports) {
    for (const table of db.missingFutureTables || []) checks.push({ status: "FAIL", message: `strict requires ${table} in ${db.path}` });
  }
}
if (triDb?.status) checks.push({ status: triDb.status === "READY" ? "PASS" : "WARN", message: `shared tri-db status ${triDb.status}` });
else checks.push({ status: "WARN", message: "shared tri-db status missing" });

const overall = statusRank(checks.map((item) => item.status));
const report = { generatedAt: new Date().toISOString(), strict, overall, triDbStatusPath, triDbSummary: triDb ? { status: triDb.status, generated_at: triDb.generated_at, latest_bridge_status: triDb.latest_bridge_status } : null, dbReports };
const paths = reportPaths("SYNC_HEALTH_REPORT");
writeJson(paths.json, report);
writeText(paths.md, [
  "# Sync Health Report",
  "",
  `Overall: ${overall}`,
  `Strict: ${strict}`,
  `Tri-DB status: ${triDb?.status || "missing"}`,
  "",
  ...dbReports.flatMap((db) => [`- DB: ${db.path}`, `  - readiness: ${db.readiness}`, `  - outbox: ${JSON.stringify(db.outboxStatusCounts || {})}`, `  - missing: ${(db.missingFutureTables || []).join(", ") || "none"}`, ...db.checks.map((check) => `  - ${check.status}: ${check.message}`)])
].join("\n") + "\n");

console.log(`${overall} sync health report: ${paths.md}`);
if (overall === "FAIL") process.exit(1);

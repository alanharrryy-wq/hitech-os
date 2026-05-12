#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, run, statusRank, terminalRoot, writeJson, writeText } from "./prisma-codex-utils.mjs";

const repoRoot = path.resolve(terminalRoot, "..", "..");
const dbs = [
  path.join(terminalRoot, "products", "tablet", "app", "data", "tablet-pos.db"),
  path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db")
];
const schemaPaths = [
  path.join(terminalRoot, "prisma", "schema.prisma"),
  path.join(terminalRoot, "products", "tablet", "app", "prisma", "schema.prisma")
];

const py = String.raw`
import sqlite3, json, sys, os
allowed=set(["pending","sent","failed","acked","conflict"])
reports=[]
for db in sys.argv[1:]:
  item={"path":db,"exists":os.path.exists(db),"checks":[],"warnings":[]}
  if not item["exists"]:
    item["checks"].append({"status":"WARN","message":"DB missing"})
    reports.append(item); continue
  try:
    con=sqlite3.connect(db); cur=con.cursor()
    table=cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='OutboxEvent'").fetchone()
    if not table:
      item["checks"].append({"status":"FAIL","message":"OutboxEvent table missing"})
      reports.append(item); continue
    cols=[r[1] for r in cur.execute('PRAGMA table_info("OutboxEvent")').fetchall()]
    item["columns"]=cols
    required=["id","businessId","aggregateId","payloadJson","status","attempts","createdAt"]
    for col in required:
      item["checks"].append({"status":"PASS" if col in cols else "FAIL","message":f"column {col}"})
    if "topic" not in cols and "eventType" not in cols:
      item["checks"].append({"status":"FAIL","message":"topic/eventType column missing"})
    else:
      item["checks"].append({"status":"PASS","message":"topic/eventType alias available"})
    if "idempotencyKey" not in cols:
      item["checks"].append({"status":"WARN","message":"idempotencyKey column missing in live DB"})
    total=cur.execute('SELECT COUNT(*) FROM "OutboxEvent"').fetchone()[0]
    item["total"]=total
    status_rows=cur.execute('SELECT status, COUNT(*) FROM "OutboxEvent" GROUP BY status').fetchall() if "status" in cols else []
    item["statusCounts"]={str(k):v for k,v in status_rows}
    for status,_ in status_rows:
      item["checks"].append({"status":"PASS" if status in allowed else "FAIL","message":f"status {status}"})
    if "payloadJson" in cols:
      bad=0
      for rowid,payload in cur.execute('SELECT id, payloadJson FROM "OutboxEvent" WHERE payloadJson IS NOT NULL AND payloadJson != ""'):
        try: json.loads(payload)
        except Exception: bad += 1
      item["checks"].append({"status":"PASS" if bad==0 else "FAIL","message":f"payloadJson parseable bad={bad}"})
    if "idempotencyKey" in cols:
      dup=cur.execute('SELECT COUNT(*) FROM (SELECT idempotencyKey FROM "OutboxEvent" WHERE idempotencyKey IS NOT NULL AND idempotencyKey != "" GROUP BY businessId,idempotencyKey HAVING COUNT(*)>1)').fetchone()[0]
      item["checks"].append({"status":"PASS" if dup==0 else "FAIL","message":f"duplicate idempotencyKey groups={dup}"})
    if "createdAt" in cols and "status" in cols:
      oldest=cur.execute('SELECT MIN(createdAt) FROM "OutboxEvent" WHERE status="pending"').fetchone()[0]
      item["oldestPendingAt"]=oldest
    con.close()
  except Exception as exc:
    item["checks"].append({"status":"FAIL","message":str(exc)})
  reports.append(item)
print(json.dumps(reports, ensure_ascii=False))
`;

const result = run("python", ["-c", py, ...dbs]);
const dbReports = result.status === 0 ? JSON.parse(result.stdout || "[]") : [{ path: "python", checks: [{ status: "FAIL", message: result.stderr || result.stdout }] }];
const schemaChecks = [];
for (const schemaPath of schemaPaths) {
  const text = fs.existsSync(schemaPath) ? fs.readFileSync(schemaPath, "utf8") : "";
  schemaChecks.push({ path: schemaPath, status: text.includes("model OutboxEvent") ? "PASS" : "FAIL", message: "schema contains model OutboxEvent" });
}

const allStatuses = [...schemaChecks.map((item) => item.status), ...dbReports.flatMap((item) => item.checks.map((check) => check.status))];
const overall = statusRank(allStatuses);
const report = { generatedAt: new Date().toISOString(), overall, schemaChecks, dbReports };
const paths = reportPaths("OUTBOX_INTEGRITY_REPORT");
writeJson(paths.json, report);
writeText(paths.md, [
  "# Outbox Integrity Report",
  "",
  `Overall: ${overall}`,
  "",
  "## Schema",
  ...schemaChecks.map((item) => `- ${item.status}: ${item.path} - ${item.message}`),
  "",
  "## Databases",
  ...dbReports.flatMap((db) => [`- DB: ${db.path}`, `  - total: ${db.total ?? "n/a"}`, `  - statuses: ${JSON.stringify(db.statusCounts || {})}`, ...db.checks.map((check) => `  - ${check.status}: ${check.message}`)])
].join("\n") + "\n");

console.log(`${overall} outbox integrity report: ${paths.md}`);
if (overall === "FAIL") process.exit(1);

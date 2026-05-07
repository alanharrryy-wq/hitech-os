#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const args = process.argv.slice(2);
function arg(name, fallback) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}
const root = path.resolve(arg("--root", process.cwd()));
const logDir = path.resolve(arg("--log-dir", "F:/descargasf"));

const groups = {
  i02_catalogo: [
    "app/catalog/page.tsx",
    "components/catalog/catalog-dashboard.tsx",
    "src/server/repositories/catalog.repository.ts",
    "src/server/services/catalog.service.ts",
    "src/server/validators/catalog-quality.ts",
    "tools/verify_pc_catalog_02.mjs"
  ],
  i03_inventario: [
    "app/stock/page.tsx",
    "app/counts/page.tsx",
    "app/audit/page.tsx",
    "components/inventory/inventory-workspace.tsx",
    "src/server/services/inventory-ledger.service.ts",
    "src/server/validators/inventory-integrity.ts",
    "tools/verify_pc_stock_counts_audit_03.mjs"
  ],
  i04_operacion: [
    "app/purchasing/page.tsx",
    "app/receiving/page.tsx",
    "app/replenishment/page.tsx",
    "app/dashboard/page.tsx",
    "components/operations/operation-workspace.tsx",
    "src/server/services/operation-control.service.ts",
    "src/server/services/kpi-formulas.ts",
    "src/server/validators/procurement-integrity.ts",
    "tools/verify_pc_operation_04.mjs"
  ],
  i05_sync_release: [
    "app/sync/page.tsx",
    "app/api/sync/ingest/route.ts",
    "components/sync/sync-release-workspace.tsx",
    "src/server/services/sync-ingest.service.ts",
    "src/server/services/sync-release.service.ts",
    "src/server/validators/sync-event-contract.ts",
    "tools/verify_pc_sync_release_05.mjs"
  ]
};

const requiredLogs = ["pc_i02_", "pc_i03_", "pc_i04_", "pc_i05_"];
const findings = [];
const files = [];

for (const [group, rels] of Object.entries(groups)) {
  for (const rel of rels) {
    const abs = path.join(root, rel);
    const exists = fs.existsSync(abs);
    const size = exists ? fs.statSync(abs).size : 0;
    files.push({ group, rel, exists, size });
    if (!exists || size <= 0) {
      findings.push({ severity: "BLOCKER", code: "MISSING_OR_EMPTY_FILE", group, rel, message: `Falta o esta vacio: ${rel}` });
    }
  }
}

function hasReadyLog(prefix) {
  if (!fs.existsSync(logDir)) return { ok: false, reason: `No existe logDir ${logDir}` };
  const candidates = fs.readdirSync(logDir)
    .filter((name) => name.startsWith(prefix) && name.endsWith(".log"))
    .sort();
  const ready = [];
  const blocked = [];
  for (const name of candidates) {
    const full = path.join(logDir, name);
    const text = fs.readFileSync(full, "utf8");
    if (text.includes("FINAL STATUS: READY") || text.includes('"finalStatus": "READY"') || text.includes('"finalStatus":"READY"')) {
      ready.push(name);
    }
    if (text.includes("FINAL STATUS: BLOCKED") || text.includes('"finalStatus": "BLOCKED"') || text.includes('"finalStatus":"BLOCKED"')) {
      blocked.push(name);
    }
  }
  return { ok: ready.length > 0, candidates, ready, blocked };
}

const logs = {};
for (const prefix of requiredLogs) {
  const result = hasReadyLog(prefix);
  logs[prefix] = result;
  if (!result.ok) {
    findings.push({ severity: "BLOCKER", code: "READY_LOG_NOT_FOUND", prefix, message: `No encontre log READY para ${prefix} en ${logDir}` });
  }
}

const ok = findings.every((f) => f.severity !== "BLOCKER");
const result = {
  verifier: "verify_pc_release_complete_06_v3",
  ok,
  state: ok ? "PASS" : "FAIL",
  root,
  logDir,
  files,
  logs,
  findings,
  checkedAt: new Date().toISOString(),
  note: "Este gate valida la arquitectura real instalada por I02-I05 y no exige sync.repository.ts. Logs BLOCKED de I06 se ignoran para decidir I02-I05."
};
console.log(JSON.stringify(result, null, 2));
process.exit(ok ? 0 : 1);

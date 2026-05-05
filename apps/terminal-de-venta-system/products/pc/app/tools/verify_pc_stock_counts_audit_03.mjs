#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const args = process.argv.slice(2);
const rootIndex = args.indexOf("--root");
const root = path.resolve(rootIndex >= 0 && args[rootIndex + 1] ? args[rootIndex + 1] : process.cwd());

const requiredFiles = [
  "app/stock/page.tsx",
  "app/counts/page.tsx",
  "app/audit/page.tsx",
  "components/inventory/inventory-workspace.tsx",
  "src/modules/inventory/types.ts",
  "src/server/repositories/inventory.repository.ts",
  "src/server/services/inventory-ledger.service.ts",
  "src/server/validators/inventory-integrity.ts",
  "docs/modules/stock.md",
  "docs/modules/counts.md",
  "docs/modules/audit.md"
];

function exists(rel) {
  const abs = path.join(root, rel);
  return { rel, exists: fs.existsSync(abs), size: fs.existsSync(abs) ? fs.statSync(abs).size : 0 };
}

function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}

const files = requiredFiles.map(exists);
const missing = files.filter((file) => !file.exists).map((file) => file.rel);
const empty = files.filter((file) => file.exists && file.size <= 0).map((file) => file.rel);
const findings = [];

if (missing.length) findings.push({ severity: "BLOCKER", code: "MISSING_FILES", message: `Faltan archivos I03: ${missing.join(", ")}` });
if (empty.length) findings.push({ severity: "BLOCKER", code: "EMPTY_FILES", message: `Archivos vacíos I03: ${empty.join(", ")}` });

for (const route of ["stock", "counts", "audit"]) {
  const page = `app/${route}/page.tsx`;
  if (!missing.includes(page)) {
    const text = read(page);
    if (text.includes("ModuleOverviewPage")) findings.push({ severity: "BLOCKER", code: "STILL_OVERVIEW", message: `/${route} todavía usa ModuleOverviewPage.` });
    if (!text.includes("getInventoryWorkspace")) findings.push({ severity: "BLOCKER", code: "NO_SERVICE", message: `/${route} no consume servicio de inventario.` });
  }
}

if (!missing.includes("src/server/repositories/inventory.repository.ts")) {
  const repo = read("src/server/repositories/inventory.repository.ts");
  for (const token of ["stockSnapshot.findMany", "stockMovement.findMany", "auditCount.findMany", "include: { product: true }"]) {
    if (!repo.includes(token)) findings.push({ severity: "BLOCKER", code: "REPOSITORY_TOKEN_MISSING", message: `Repositorio no contiene ${token}.` });
  }
}

if (!missing.includes("src/server/services/inventory-ledger.service.ts")) {
  const service = read("src/server/services/inventory-ledger.service.ts");
  for (const token of ["beforeQty", "afterQty", "actor", "source", "buildInventoryFindings", "inventoryAccuracy"]) {
    if (!service.includes(token)) findings.push({ severity: "BLOCKER", code: "SERVICE_TOKEN_MISSING", message: `Servicio no contiene ${token}.` });
  }
}

if (!missing.includes("src/server/validators/inventory-integrity.ts")) {
  const validator = read("src/server/validators/inventory-integrity.ts");
  for (const token of ["stockState", "signedMovementDelta", "buildInventoryFindings", "stock_negativo", "movimiento_sin_motivo"]) {
    if (!validator.includes(token)) findings.push({ severity: "BLOCKER", code: "VALIDATOR_TOKEN_MISSING", message: `Validador no contiene ${token}.` });
  }
}

if (!missing.includes("components/inventory/inventory-workspace.tsx")) {
  const ui = read("components/inventory/inventory-workspace.tsx");
  for (const label of ["Existencias por ubicación", "Movimientos recientes", "Conteos físicos", "Hallazgos de integridad", "acciones sensibles"]) {
    if (!ui.includes(label)) findings.push({ severity: "BLOCKER", code: "UI_LABEL_MISSING", message: `UI no contiene etiqueta ${label}.` });
  }
}

const ok = findings.every((finding) => finding.severity !== "BLOCKER");
const result = {
  verifier: "verify_pc_stock_counts_audit_03",
  iteration: "pc_i03_inventario",
  state: ok ? "PASS" : "FAIL",
  ok,
  root,
  routes: ["/stock", "/counts", "/audit"],
  files,
  missing,
  empty,
  findings,
  checkedAt: new Date().toISOString()
};

console.log(JSON.stringify(result, null, 2));
process.exit(ok ? 0 : 1);

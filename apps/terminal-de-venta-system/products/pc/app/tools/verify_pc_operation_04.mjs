#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const args = process.argv.slice(2);
const rootArgIndex = args.indexOf("--root");
const root = path.resolve(rootArgIndex >= 0 && args[rootArgIndex + 1] ? args[rootArgIndex + 1] : process.cwd());
const requiredFiles = [
  "app/purchasing/page.tsx",
  "app/receiving/page.tsx",
  "app/replenishment/page.tsx",
  "app/dashboard/page.tsx",
  "components/operations/operation-workspace.tsx",
  "src/modules/operations/types.ts",
  "src/server/repositories/operation.repository.ts",
  "src/server/services/operation-control.service.ts",
  "src/server/validators/procurement-integrity.ts",
  "src/server/services/kpi-formulas.ts",
  "docs/modules/purchasing.md",
  "docs/modules/receiving.md",
  "docs/modules/replenishment.md",
  "docs/modules/dashboard-kpi.md"
];
function read(rel) { return fs.readFileSync(path.join(root, rel), "utf8"); }
const files = requiredFiles.map((rel) => ({ rel, exists: fs.existsSync(path.join(root, rel)), size: fs.existsSync(path.join(root, rel)) ? fs.statSync(path.join(root, rel)).size : 0 }));
const findings = [];
for (const file of files) {
  if (!file.exists) findings.push({ severity: "BLOCKER", code: "MISSING_FILE", message: `Falta ${file.rel}` });
  if (file.exists && file.size <= 0) findings.push({ severity: "BLOCKER", code: "EMPTY_FILE", message: `Vacío ${file.rel}` });
}
for (const route of ["purchasing", "receiving", "replenishment", "dashboard"]) {
  const rel = `app/${route}/page.tsx`;
  if (fs.existsSync(path.join(root, rel))) {
    const page = read(rel);
    if (page.includes("ModuleOverviewPage")) findings.push({ severity: "BLOCKER", code: "STILL_OVERVIEW", message: `${route} sigue usando ModuleOverviewPage.` });
    if (!page.includes("getOperationWorkspace")) findings.push({ severity: "BLOCKER", code: "NO_SERVICE", message: `${route} no usa getOperationWorkspace.` });
  }
}
const servicePath = "src/server/services/operation-control.service.ts";
if (fs.existsSync(path.join(root, servicePath))) {
  const service = read(servicePath);
  for (const token of ["PurchaseOrder", "GoodsReceipt", "ReplenishmentSignal", "Ventas netas", "Ticket promedio", "fillRate", "formula", "confidence"]) {
    if (!service.includes(token)) findings.push({ severity: "BLOCKER", code: "SERVICE_TOKEN_MISSING", message: `Servicio no contiene ${token}.` });
  }
}
const validatorPath = "src/server/validators/procurement-integrity.ts";
if (fs.existsSync(path.join(root, validatorPath))) {
  const validator = read(validatorPath);
  for (const token of ["classifyPurchaseRisk", "classifyReceiptDiscrepancy", "validateReplenishmentSignal", "buildOperationAlerts", "suggestedReplenishment"]) {
    if (!validator.includes(token)) findings.push({ severity: "BLOCKER", code: "VALIDATOR_TOKEN_MISSING", message: `Validador no contiene ${token}.` });
  }
}
const componentPath = "components/operations/operation-workspace.tsx";
if (fs.existsSync(path.join(root, componentPath))) {
  const component = read(componentPath);
  for (const label of ["Fórmula", "Fuente", "Confianza", "Recepción contra orden", "Señales de reabasto", "Órdenes de compra"]) {
    if (!component.includes(label)) findings.push({ severity: "BLOCKER", code: "UI_LABEL_MISSING", message: `UI no contiene ${label}.` });
  }
}
const ok = findings.every((finding) => finding.severity !== "BLOCKER");
console.log(JSON.stringify({ verifier: "verify_pc_operation_04", iteration: "pc_i04_operacion", ok, state: ok ? "PASS" : "FAIL", root, files, findings, checkedAt: new Date().toISOString() }, null, 2));
process.exit(ok ? 0 : 1);

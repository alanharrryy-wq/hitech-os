#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const serviceFile = "src/server/services/pc-data-mode-contract.service.ts";
const apiFile = "app/api/backoffice/dropdowns/route.ts";
const customerFiles = [
  "components/uiux/decision-screen.tsx",
  "app/dashboard/page.tsx",
  "app/metricas-dia/page.tsx",
  "components/control/cash-sessions-operational-view.tsx",
  "components/control/sales-control-branch-view.tsx",
  "components/control/pc-command-center-page.tsx",
  "app/proveedores/page.tsx",
  "app/settings/license/page.tsx"
];
const retiredFilterRoutes = ["app/filtros-avanzados/page.tsx", "app/filtros-fecha/page.tsx"];
const failures = [];

function read(file) {
  const full = path.join(appRoot, file);
  if (!fs.existsSync(full)) {
    failures.push(`Missing file: ${file}`);
    return "";
  }
  return fs.readFileSync(full, "utf8");
}

const service = read(serviceFile);
const api = read(apiFile);

for (const key of ["branches", "devices", "users", "suppliers", "products", "categories"]) {
  if (!service.includes(`key: "${key}"`)) failures.push(`Missing DB-backed catalog spec: ${key}`);
}
if (!api.includes("getPcDropdownContract")) failures.push("Dropdown API contract must remain available for scoped/internal consumers.");

for (const file of customerFiles) {
  const text = read(file);
  if (text.includes("SmartDropdownDock")) failures.push(`Global SmartDropdownDock leaked into customer surface: ${file}`);
  if (text.includes("!" + "important")) failures.push(`Forbidden bang-important in ${file}`);
}

for (const file of retiredFilterRoutes) {
  const text = read(file);
  if (!text.includes("notFound()")) failures.push(`Retired customer filter route must fail closed with notFound(): ${file}`);
}

if (failures.length) {
  console.error("PCFUNC SURFACE FILTERS VERIFY FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PCFUNC SURFACE FILTERS VERIFY OK");
console.log(`Checked ${customerFiles.length} customer files; global SmartDropdownDock exposure is zero.`);

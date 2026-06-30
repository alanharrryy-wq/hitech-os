#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const requiredFiles = [
  "src/server/services/pc-data-mode-contract.service.ts",
  "components/uiux/smart-dropdown-dock.tsx",
  "components/uiux/smart-dropdown-dock.module.css",
  "components/uiux/decision-screen.tsx",
  "components/control/pc-command-center-page.tsx",
  "components/control/sales-control-branch-view.tsx",
  "app/proveedores/page.tsx"
];

const requiredTokens = [
  ["src/server/services/pc-data-mode-contract.service.ts", "GLOBAL_DROPDOWN_SPECS"],
  ["src/server/services/pc-data-mode-contract.service.ts", "pcfunc-dd1-global-dropdowns"],
  ["src/server/services/pc-data-mode-contract.service.ts", "readDatabaseCatalog"],
  ["components/uiux/smart-dropdown-dock.tsx", "SmartDropdownDock"],
  ["components/uiux/smart-dropdown-dock.tsx", "getPcDropdownContract"],
  ["components/uiux/decision-screen.tsx", "<SmartDropdownDock currentPath={currentPath} />"],
  ["components/control/pc-command-center-page.tsx", "<SmartDropdownDock currentPath={model.currentPath} />"],
  ["components/control/sales-control-branch-view.tsx", "<SmartDropdownDock currentPath={model.currentPath}"],
  ["app/proveedores/page.tsx", "<SmartDropdownDock currentPath=\"/proveedores\""]
];

const failures = [];

for (const file of requiredFiles) {
  const full = path.join(appRoot, file);
  if (!fs.existsSync(full)) failures.push(`Missing file: ${file}`);
}

for (const [file, token] of requiredTokens) {
  const full = path.join(appRoot, file);
  const text = fs.existsSync(full) ? fs.readFileSync(full, "utf8") : "";
  if (!text.includes(token)) failures.push(`Missing token in ${file}: ${token}`);
}

for (const file of requiredFiles) {
  const full = path.join(appRoot, file);
  if (!fs.existsSync(full)) continue;
  const text = fs.readFileSync(full, "utf8");
  if (text.includes("!" + "important")) failures.push(`Forbidden bang-important in ${file}`);
}

const service = fs.readFileSync(path.join(appRoot, "src/server/services/pc-data-mode-contract.service.ts"), "utf8");
const catalogKeys = ["branches", "devices", "users", "suppliers", "products", "categories"];
for (const key of catalogKeys) {
  if (!service.includes(`key: "${key}"`)) failures.push(`Missing DB-backed catalog spec: ${key}`);
}

if (failures.length) {
  console.error("PCFUNC DROPDOWNS VERIFY FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PCFUNC DROPDOWNS VERIFY OK");
console.log(`Checked ${requiredFiles.length} files and ${catalogKeys.length} DB-backed catalog specs.`);

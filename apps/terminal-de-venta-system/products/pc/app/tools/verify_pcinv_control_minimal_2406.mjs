import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const rootArgIndex = process.argv.indexOf("--root");
const root = rootArgIndex >= 0 ? process.argv[rootArgIndex + 1] : process.cwd();
const directAppRoot = existsSync(join(root, "components")) && existsSync(join(root, "app"));
const appRoot = root.endsWith("products/pc/app") || directAppRoot ? root : join(root, "products", "pc", "app");

const targets = {
  catalogDashboard: join(appRoot, "components", "catalog", "catalog-dashboard.tsx"),
  inventoryWorkspace: join(appRoot, "components", "inventory", "inventory-workspace.tsx"),
  cssModule: join(appRoot, "components", "inventory", "pc-inventory-master-detail.module.css"),
  criticalPage: join(appRoot, "app", "existencias-criticas", "page.tsx"),
  barcodePage: join(appRoot, "app", "salud-barcodes", "page.tsx"),
  validationPage: join(appRoot, "app", "validacion-catalogo", "page.tsx")
};

const failures = [];

function read(label) {
  const path = targets[label];
  if (!existsSync(path)) {
    failures.push(`missing ${label}: ${path}`);
    return "";
  }
  return readFileSync(path, "utf8");
}

function must(label, haystack, needle) {
  if (!haystack.includes(needle)) failures.push(`${label} missing marker: ${needle}`);
}

function mustNot(label, haystack, needle, reason) {
  if (haystack.includes(needle)) failures.push(`${label} still contains ${reason}`);
}

const files = Object.fromEntries(Object.keys(targets).map((label) => [label, read(label)]));

must("catalogDashboard", files.catalogDashboard, "data-pcinv-ux-minimal-controls=\"catalog\"");
must("catalogDashboard", files.catalogDashboard, "data-pcinv-search-first=\"catalog\"");
must("catalogDashboard", files.catalogDashboard, "data-pcinv-chip-controls=\"catalog-status\"");
must("catalogDashboard", files.catalogDashboard, "data-pcinv-chip-controls=\"catalog-issues\"");
must("inventoryWorkspace", files.inventoryWorkspace, "data-pcinv-ux-minimal-controls=\"inventory\"");
must("inventoryWorkspace", files.inventoryWorkspace, "data-pcinv-search-first=\"stock\"");
must("inventoryWorkspace", files.inventoryWorkspace, "data-pcinv-chip-controls=\"stock-state\"");
must("inventoryWorkspace", files.inventoryWorkspace, "data-pcinv-timeline=\"audit\"");
must("criticalPage", files.criticalPage, "data-pcinv-ux-minimal-controls=\"critical-stock\"");
must("criticalPage", files.criticalPage, "data-pcinv-chip-controls=\"critical-urgency\"");
must("barcodePage", files.barcodePage, "data-pcinv-ux-minimal-controls=\"barcodes\"");
must("barcodePage", files.barcodePage, "data-pcinv-chip-controls=\"barcode-problems\"");
must("validationPage", files.validationPage, "data-pcinv-ux-minimal-controls=\"validation\"");
must("validationPage", files.validationPage, "data-pcinv-chip-controls=\"validation-severity\"");
must("cssModule", files.cssModule, ".intentBar");
must("cssModule", files.cssModule, ".searchBox");
must("cssModule", files.cssModule, ".chipStack");
must("cssModule", files.cssModule, ".timelineEvent");

for (const [label, text] of Object.entries(files)) {
  mustNot(label, text, "SmartDropdownDock", "global dropdown dock in minimal-control inventory UX");
  if (text.includes("!" + "important")) failures.push(`${label} contains forbidden bang-important override`);
}

const totalSelects = Object.values(files).reduce((count, text) => count + (text.match(/<select\b|SelectTrigger|combobox/gi) ?? []).length, 0);
if (totalSelects > 0) failures.push(`minimal-control inventory UX should not introduce visible select spam; found ${totalSelects}`);

if (failures.length) {
  console.error("PCINV minimal controls verification failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PCINV minimal controls verification OK");

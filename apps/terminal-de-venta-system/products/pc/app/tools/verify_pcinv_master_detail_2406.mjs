import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const rootArgIndex = process.argv.indexOf("--root");
const root = rootArgIndex >= 0 ? process.argv[rootArgIndex + 1] : process.cwd();
const directAppRoot = existsSync(join(root, "components")) && existsSync(join(root, "app"));
const appRoot = root.endsWith("products/pc/app") || directAppRoot ? root : join(root, "products", "pc", "app");

const targets = {
  catalogPage: join(appRoot, "app", "catalog", "page.tsx"),
  stockPage: join(appRoot, "app", "stock", "page.tsx"),
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

const catalogPage = read("catalogPage");
const stockPage = read("stockPage");
const catalogDashboard = read("catalogDashboard");
const inventoryWorkspace = read("inventoryWorkspace");
const cssModule = read("cssModule");
const criticalPage = read("criticalPage");
const barcodePage = read("barcodePage");
const validationPage = read("validationPage");

if (catalogPage.includes("DecisionScreen")) failures.push("catalog page still uses generic DecisionScreen");
if (stockPage.includes("DecisionScreen")) failures.push("stock page still uses generic DecisionScreen");

must("catalogPage", catalogPage, "getCatalogWorkspace");
must("stockPage", stockPage, "getInventoryWorkspace");
must("catalogDashboard", catalogDashboard, "data-pcinv-master-detail=\"catalog\"");
must("catalogDashboard", catalogDashboard, "data-pcinv-product-ficha=\"catalog\"");
must("catalogDashboard", catalogDashboard, "data-pcinv-dense-product-list=\"catalog\"");
must("catalogDashboard", catalogDashboard, "data-pcinv-ux-minimal-controls=\"catalog\"");
must("catalogDashboard", catalogDashboard, "data-pcinv-search-first=\"catalog\"");
must("inventoryWorkspace", inventoryWorkspace, "data-pcinv-master-detail=\"inventory\"");
must("inventoryWorkspace", inventoryWorkspace, "data-pcinv-dense-product-list=\"stock\"");
must("inventoryWorkspace", inventoryWorkspace, "data-pcinv-product-ficha=\"stock\"");
must("inventoryWorkspace", inventoryWorkspace, "data-pcinv-count-console=\"counts\"");
must("inventoryWorkspace", inventoryWorkspace, "data-pcinv-audit-workbench=\"inventory\"");
must("inventoryWorkspace", inventoryWorkspace, "data-pcinv-ux-minimal-controls=\"inventory\"");
must("cssModule", cssModule, ".masterDetailTight");
must("cssModule", cssModule, ".productFicha");
must("cssModule", cssModule, ".tableFrame");
must("cssModule", cssModule, ".intentBar");
must("criticalPage", criticalPage, "data-pcinv-priority-queue=\"critical-stock\"");
must("criticalPage", criticalPage, "data-pcinv-ux-minimal-controls=\"critical-stock\"");
must("barcodePage", barcodePage, "data-pcinv-barcode-workbench=\"health\"");
must("barcodePage", barcodePage, "data-pcinv-ux-minimal-controls=\"barcodes\"");
must("validationPage", validationPage, "data-pcinv-quality-workbench=\"validation\"");
must("validationPage", validationPage, "data-pcinv-ux-minimal-controls=\"validation\"");

for (const [label, text] of Object.entries({ catalogPage, stockPage, catalogDashboard, inventoryWorkspace, cssModule, criticalPage, barcodePage, validationPage })) {
  if (text.includes("!" + "important")) failures.push(`${label} contains forbidden bang-important override`);
}

if (failures.length) {
  console.error("PCINV master-detail verification failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PCINV master-detail verification OK");

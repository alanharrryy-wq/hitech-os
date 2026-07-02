#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const appRoot = fs.existsSync(path.join(cwd, "package.json")) && fs.existsSync(path.join(cwd, "components"))
  ? cwd
  : path.join(cwd, "apps", "terminal-de-venta-system", "products", "tablet", "app");
const checks = [];

function read(rel) {
  const file = path.join(appRoot, rel);
  if (!fs.existsSync(file)) {
    checks.push({ name: `exists ${rel}`, ok: false });
    return "";
  }
  checks.push({ name: `exists ${rel}`, ok: true });
  return fs.readFileSync(file, "utf8");
}

function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), detail });
}

const stock = read("components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx");
const report = read("components/reports/contextual-export-actions.tsx");
const offline = read("components/offline/offline-export-audit-screen.tsx");
const reportCss = read("components/reports/contextual-export.module.css");
const offlineCss = read("components/offline/offline-export-audit.module.css");

check("stock export is a closed details menu", stock.includes("function StockExportMenu()") && stock.includes("<details className={styles.exportMenu}>") && stock.includes("<summary>Exportar</summary>"));
check("stock export has no default open attribute", !/details[^>]*open/i.test(stock));
check("sales contextual export is details", report.includes("<details className={styles.card}") && report.includes("<summary className={styles.summary}>"));
check("sales contextual export hides actions while closed", reportCss.includes(".card:not([open]) .actions"));
check("offline export is details", offline.includes("<details className={styles.exportCard}>") && offline.includes("<summary className={styles.exportSummary}>"));
check("offline diagnostics are details", offline.includes("<details className={styles.panel}>") && offline.includes("Detalle de respaldo"));
check("offline export hides actions while closed", offlineCss.includes(".exportCard:not([open]) .actions"));
check("old prominent export copy absent", !report.includes("Exportar datos") && !offline.includes("Exportar evidencia"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("TABREST_INVENTORY_EXPORT_SECONDARY_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}
console.log(`TABREST_INVENTORY_EXPORT_SECONDARY_0207 PASS ${checks.length} checks`);

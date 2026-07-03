import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const failures = [];
const bangImportant = "!" + "important";

const preexistingDirty = new Set([
  "apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_BACKOUT.md",
  "apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_CHANGED_FILES.md",
  "apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_FINAL_REPORT.md",
  "apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_VERIFIER_SUMMARY.json",
  "apps/terminal-de-venta-system/prisma-control-center/internal/config/prismo_brain100_improvements.json",
  "apps/terminal-de-venta-system/prisma-control-center/internal/config/prismo_visual_response_contract.json",
  "apps/terminal-de-venta-system/prisma-control-center/internal/py/panel_3150.py",
  "apps/terminal-de-venta-system/prisma-control-center/internal/py/prismo_ai_bridge.py",
  "apps/terminal-de-venta-system/prisma-control-center/internal/web/prismo_console.js",
  "apps/terminal-de-venta-system/tools/quality/verify_tabnp1_tablet_non_pos_0207.mjs"
]);

const allowedPrefixes = [
  "apps/terminal-de-venta-system/products/tablet/app/",
  "apps/terminal-de-venta-system/docs/product/tablet-mamastrophic/",
  "tools/quality/verify_tablet_mamastrophic_full_surface_0207.mjs",
  "tools/quality/verify_tablet_interactive_jewel_system_0207.mjs",
  "tools/quality/verify_tablet_quick_create_tiles_0207.mjs"
];

function relPath(...parts) {
  return path.join(root, ...parts);
}

function read(rel) {
  const file = relPath(rel);
  if (!fs.existsSync(file)) {
    failures.push(`${rel} missing`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
}

function has(rel, token) {
  const content = read(rel);
  if (!content.includes(token)) failures.push(`${rel} missing token: ${token}`);
}

function lacks(rel, token) {
  const content = read(rel);
  if (content.includes(token)) failures.push(`${rel} contains forbidden token: ${token}`);
}

function check(condition, message) {
  if (!condition) failures.push(message);
}

function normalizeStatusPath(line) {
  const raw = line.slice(3).trim();
  if (raw.includes(" -> ")) return raw.split(" -> ").at(-1).trim();
  return raw;
}

function verifyDirtyScope() {
  const output = execFileSync("git", ["status", "--short", "--untracked-files=all"], { cwd: root, encoding: "utf8" });
  for (const line of output.split(/\r?\n/).filter(Boolean)) {
    if (line.startsWith("## ")) continue;
    const rel = normalizeStatusPath(line).replaceAll("\\", "/");
    const allowed = preexistingDirty.has(rel) || allowedPrefixes.some((prefix) => rel === prefix || rel.startsWith(prefix));
    if (!allowed) failures.push(`dirty file outside Tablet mamastrophic scope: ${rel}`);
  }
}

verifyDirtyScope();

const surfaceFiles = {
  home: "apps/terminal-de-venta-system/products/tablet/app/components/tablet-home/tablet-home-screen.tsx",
  shell: "apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx",
  shellCss: "apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css",
  catalog: "apps/terminal-de-venta-system/products/tablet/app/components/catalog/catalog-screen.tsx",
  stock: "apps/terminal-de-venta-system/products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx",
  shift: "apps/terminal-de-venta-system/products/tablet/app/components/shift/shift-cash-closure-screen.tsx",
  salesToday: "apps/terminal-de-venta-system/products/tablet/app/components/sales/sales-today-screen.tsx",
  salesHistory: "apps/terminal-de-venta-system/products/tablet/app/components/sales/sales-history-screen.tsx",
  returns: "apps/terminal-de-venta-system/products/tablet/app/components/returns/return-from-ticket-screen.tsx",
  sync: "apps/terminal-de-venta-system/products/tablet/app/components/sync/pending-offline-sync-panel-screen.tsx",
  offline: "apps/terminal-de-venta-system/products/tablet/app/components/offline/offline-export-audit-screen.tsx",
  license: "apps/terminal-de-venta-system/products/tablet/app/app/settings/license/page.tsx",
  exportSettings: "apps/terminal-de-venta-system/products/tablet/app/components/tablet-pos/touch-pos-ui.tsx"
};

for (const rel of Object.values(surfaceFiles)) read(rel);

for (const rel of [
  surfaceFiles.home,
  surfaceFiles.catalog,
  surfaceFiles.stock,
  surfaceFiles.shift,
  surfaceFiles.salesToday,
  surfaceFiles.salesHistory,
  surfaceFiles.returns,
  surfaceFiles.sync,
  surfaceFiles.offline,
  surfaceFiles.license,
  surfaceFiles.exportSettings
]) {
  const content = read(rel);
  check(/QuickAction(Grid|Strip|Tile)/.test(content), `${rel} lacks quick action tile system`);
  check(!content.includes(bangImportant), `${rel} contains priority CSS token`);
}

has(surfaceFiles.home, "Acciones rapidas");
has(surfaceFiles.home, "/catalog?new=1");
has(surfaceFiles.catalog, "beginNewProduct");
has(surfaceFiles.catalog, "/api/pos/products/create");
has(surfaceFiles.stock, "data-prisma-search-expanded");
has(surfaceFiles.shift, "/api/pos/shift/open");
has(surfaceFiles.shift, "/api/pos/shift/close");
has(surfaceFiles.salesToday, "Nueva venta");
has(surfaceFiles.salesHistory, "Crear devolucion");
has(surfaceFiles.returns, "Nueva devolucion");
has(surfaceFiles.sync, "/api/pos/sync/dispatch");
has(surfaceFiles.sync, "/api/pos/sync/retry");
has(surfaceFiles.offline, "/api/pos/offline/audit?limit=40");
has(surfaceFiles.license, "Importar licencia");
has(surfaceFiles.exportSettings, "/api/pos/export/sales-today?format=csv");
has(surfaceFiles.exportSettings, "/api/pos/export/events?format=csv");
has(surfaceFiles.exportSettings, "/api/pos/export/inventory-movements?format=csv");

for (const forbidden of ["/release-gate", "Visual OS", "visual-os", "Laboratorio visual", "release gate"]) {
  lacks(surfaceFiles.shell, forbidden);
  lacks(surfaceFiles.home, forbidden);
}

has(surfaceFiles.shell, "moreLinks");
has(surfaceFiles.shell, "/settings/export");
has(surfaceFiles.shell, "/offline");
has(surfaceFiles.shell, "/sales/history");
has(surfaceFiles.shellCss, ".moreMenuPanel");

if (failures.length) {
  console.error("FAIL TABLET_MAMASTROPHIC_FULL_SURFACE_0207");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PASS TABLET_MAMASTROPHIC_FULL_SURFACE_0207");

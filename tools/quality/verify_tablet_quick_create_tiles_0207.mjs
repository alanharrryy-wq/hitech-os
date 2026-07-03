import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const failures = [];

function read(rel) {
  const file = path.join(root, rel);
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
  if (content.toLowerCase().includes(token.toLowerCase())) failures.push(`${rel} contains forbidden token: ${token}`);
}

function check(condition, message) {
  if (!condition) failures.push(message);
}

const files = {
  tiles: "apps/terminal-de-venta-system/products/tablet/app/components/tablet-action-tiles/tablet-action-tiles.tsx",
  home: "apps/terminal-de-venta-system/products/tablet/app/components/tablet-home/tablet-home-screen.tsx",
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

for (const rel of Object.values(files)) {
  read(rel);
  lacks(rel, "coming soon");
  lacks(rel, "alert(");
}

has(files.tiles, "deferredReason");
has(files.tiles, "data-action-owner");
has(files.tiles, "data-action-kind");
has(files.tiles, "data-action-target");

const quickCreateExpectations = [
  [files.home, "Nuevo producto"],
  [files.home, "kind={tool.title === \"Nuevo producto\" ? \"quick-create\" : \"surface-action\"}"],
  [files.catalog, "beginNewProduct"],
  [files.catalog, "kind=\"quick-create\""],
  [files.stock, "/catalog?new=1"],
  [files.salesToday, "Nueva venta"],
  [files.salesToday, "kind=\"quick-create\""],
  [files.salesToday, "Nueva devolucion"],
  [files.salesHistory, "Crear devolucion"],
  [files.returns, "Nueva devolucion"],
  [files.exportSettings, "Tipos de exportacion local"]
];

for (const [rel, token] of quickCreateExpectations) has(rel, token);

for (const [rel, token] of [
  [files.catalog, "Ajustar stock"],
  [files.catalog, "Nueva categoria"],
  [files.stock, "Ajustar stock"],
  [files.stock, "Importar catalogo"],
  [files.license, "Importar licencia"],
  [files.shift, "Exportar corte"],
  [files.exportSettings, "Turno y caja"]
]) {
  const content = read(rel);
  check(content.includes(token) && content.includes("deferredReason"), `${rel} must mark ${token} as deferred`);
}

for (const [rel, token] of [
  [files.catalog, "/api/pos/products/create"],
  [files.shift, "/api/pos/shift/open"],
  [files.shift, "/api/pos/shift/close"],
  [files.sync, "/api/pos/sync/dispatch"],
  [files.sync, "/api/pos/sync/retry"],
  [files.offline, "/api/pos/offline/audit?limit=40"],
  [files.exportSettings, "/api/pos/export/sales-today?format=csv"],
  [files.exportSettings, "/api/pos/export/events?format=json"],
  [files.exportSettings, "/api/pos/export/inventory-movements?format=csv"]
]) {
  has(rel, token);
}

if (failures.length) {
  console.error("FAIL TABLET_QUICK_CREATE_TILES_0207");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PASS TABLET_QUICK_CREATE_TILES_0207");

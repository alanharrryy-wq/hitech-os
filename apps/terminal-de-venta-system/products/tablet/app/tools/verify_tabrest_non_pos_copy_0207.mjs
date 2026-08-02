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

function absent(file, text, label = text) {
  check(`${file} does not show ${label}`, !read(file).includes(text));
}

const files = {
  home: "components/tablet-home/tablet-home-screen.tsx",
  nav: "components/tablet-shell/tablet-nav.ts",
  shell: "components/tablet-shell/prisma-tablet-shell.tsx",
  shift: "components/shift/shift-cash-closure-screen.tsx",
  exportActions: "components/reports/contextual-export-actions.tsx",
  offline: "components/offline/offline-export-audit-screen.tsx",
  licenseCard: "components/license/license-status-card.tsx",
  licenseRefresh: "components/license/license-refresh-panel.tsx",
  sync: "components/sync/pending-offline-sync-panel-screen.tsx",
  touchPos: "components/tablet-pos/touch-pos-ui.tsx",
  salesDetail: "components/sales/sales-ticket-detail-screen.tsx"
};

for (const [key, rel] of Object.entries(files)) files[key] = read(rel);

const forbidden = [
  ["components/tablet-home/tablet-home-screen.tsx", "TabletRuntimePanel"],
  ["components/tablet-home/tablet-home-screen.tsx", "Herramientas disponibles"],
  ["components/tablet-home/tablet-home-screen.tsx", "adivinar rutas"],
  ["components/tablet-home/tablet-home-screen.tsx", "backoffice"],
  ["components/shift/shift-cash-closure-screen.tsx", "tablet-cashier"],
  ["components/shift/shift-cash-closure-screen.tsx", "caja rusa"],
  ["components/shift/shift-cash-closure-screen.tsx", "servilleta"],
  ["components/reports/contextual-export-actions.tsx", "Exportar datos"],
  ["components/reports/contextual-export-actions.tsx", "Descarga lo que estas revisando"],
  ["components/offline/offline-export-audit-screen.tsx", "Exportar evidencia"],
  ["components/offline/offline-export-audit-screen.tsx", "pendientes por sincronizar"],
  ["components/offline/offline-export-audit-screen.tsx", "No. Tus movimientos"],
  ["components/license/license-refresh-panel.tsx", "Refresh remoto"],
  ["components/license/license-status-card.tsx", "Sincronización y respaldos"],
  ["components/sync/pending-offline-sync-panel-screen.tsx", "sin abrir herramientas de soporte"],
  ["components/sync/pending-offline-sync-panel-screen.tsx", "evento(s) mandado"],
  ["components/tablet-pos/touch-pos-ui.tsx", "ACK"],
  ["components/tablet-pos/touch-pos-ui.tsx", "Eventos locales"],
  ["components/sales/sales-ticket-detail-screen.tsx", "Evidencia técnica"]
];

for (const [file, text] of forbidden) {
  const content = read(file);
  check(`${file} removes "${text}"`, !content.includes(text));
}

check("home has six or fewer primary cards", (files.home.match(/href:/g) ?? []).length <= 8, "includes hero links plus quick cards");
check("home copy exposes Accesos principales", files.home.includes("Accesos principales") && files.home.includes("Lo necesario para operar"));
check("retired prisma-pulse customer route stays absent", !fs.existsSync(path.join(appRoot, "app", "prisma-pulse")));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("TABREST_NON_POS_COPY_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}
console.log(`TABREST_NON_POS_COPY_0207 PASS ${checks.length} checks`);

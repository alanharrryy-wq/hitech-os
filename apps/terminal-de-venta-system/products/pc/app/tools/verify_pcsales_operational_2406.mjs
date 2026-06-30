import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();

const files = {
  salesView: path.join(appRoot, "components", "control", "sales-control-branch-view.tsx"),
  salesCss: path.join(appRoot, "components", "control", "sales-control-branch-view.module.css"),
  cashView: path.join(appRoot, "components", "control", "cash-sessions-operational-view.tsx"),
  cashCss: path.join(appRoot, "components", "control", "cash-sessions-operational-view.module.css"),
  commandCenter: path.join(appRoot, "components", "control", "pc-command-center-page.tsx"),
  metricsDay: path.join(appRoot, "app", "metricas-dia", "page.tsx"),
  dropdown: path.join(appRoot, "components", "uiux", "smart-dropdown-dock.tsx")
};

function fail(message, details = {}) {
  console.error(JSON.stringify({ ok: false, message, details }, null, 2));
  process.exit(1);
}

function readRequired(filePath) {
  if (!fs.existsSync(filePath)) fail("Missing required file", { filePath });
  return fs.readFileSync(filePath, "utf8");
}

const source = Object.fromEntries(Object.entries(files).map(([key, filePath]) => [key, readRequired(filePath)]));

const requiredMarkers = {
  salesView: [
    'data-prisma-component="PcSalesActionDock"',
    'data-prisma-component="PcSalesTicketDrawer"',
    'data-prisma-component="PcSalesGuidedClose"',
    'Dropdown Accion de caja',
    'Marcar revisado requiere endpoint auditable',
    'href="/cash-sessions"',
    'href="/sync-operativo"',
    'firstTenderLabel(ticket)'
  ],
  cashView: [
    'data-prisma-component="PcCashGuidedClose"',
    'data-prisma-component="PcCashEvidenceSteps"',
    'Cierre de caja guiado',
    'Confirmar cierre requiere endpoint auditable',
    'SmartDropdownDock currentPath={model.currentPath}',
    'DataTable columns={table.columns}'
  ],
  commandCenter: [
    'CashSessionsOperationalView',
    'model.currentPath === "/cash-sessions" || model.mode === "cash"'
  ],
  metricsDay: [
    'title="Métricas del día"',
    'Abrir ventas y caja',
    'Revisar sesiones de caja',
    'Indicadores accionables del día',
    'currentPath="/metricas-dia"'
  ],
  dropdown: [
    'currentPath === "/sales-control" || currentPath === "/cash-sessions" || currentPath === "/metricas-dia"',
    'GROUP_CATALOG_KEYS["ventas-caja"]'
  ]
};

for (const [key, markers] of Object.entries(requiredMarkers)) {
  for (const marker of markers) {
    if (!source[key].includes(marker)) {
      fail("Required marker missing", { file: key, marker });
    }
  }
}

const forceOverridePattern = new RegExp("!" + "important", "g");
for (const [key, text] of Object.entries(source)) {
  const match = text.match(forceOverridePattern);
  if (match) fail("Forbidden forced override found", { file: key, count: match.length });
}

const forbiddenNewRoutes = [
  /\/sales-control\/detalle/g,
  /\/cash-sessions\/cerrar/g,
  /\/metricas-dia\/detalle/g
];

for (const [key, text] of Object.entries(source)) {
  for (const pattern of forbiddenNewRoutes) {
    const match = text.match(pattern);
    if (match) fail("Forbidden new primary route found", { file: key, pattern: String(pattern), match });
  }
}

console.log(JSON.stringify({
  ok: true,
  verifier: "verify_pcsales_operational_2406",
  checks: {
    salesControlActionDock: true,
    ticketDrawer: true,
    cashGuidedClose: true,
    cashSessionsOperationalView: true,
    metricasDiaOperational: true,
    dropdownsForSalesCashMetrics: true,
    noNewPrimaryScreens: true,
    noForcedOverrides: true
  }
}, null, 2));

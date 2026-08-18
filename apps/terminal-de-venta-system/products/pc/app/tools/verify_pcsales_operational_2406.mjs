import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const files = {
  salesView: path.join(appRoot, "components", "control", "sales-control-branch-view.tsx"),
  salesCss: path.join(appRoot, "components", "control", "sales-control-branch-view.module.css"),
  cashView: path.join(appRoot, "components", "control", "cash-sessions-operational-view.tsx"),
  cashCss: path.join(appRoot, "components", "control", "cash-sessions-operational-view.module.css"),
  commandCenter: path.join(appRoot, "components", "control", "pc-command-center-page.tsx"),
  metricsDay: path.join(appRoot, "app", "metricas-dia", "page.tsx")
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
  salesView: ['data-prisma-component="PcSalesTicketActions"', 'data-prisma-component="PcSalesTicketDrawer"', 'data-prisma-component="PcSalesGuidedClose"', 'SalesSearchFilter', 'href="/cash-sessions"', 'href="/sync-operativo"', 'firstTenderLabel(ticket)'],
  cashView: ['data-prisma-component="PcCashGuidedClose"', 'data-prisma-component="PcCashEvidenceSteps"', 'data-prisma-component="PcCashBalanceHierarchy"', 'DataTable columns={table.columns}', 'Cierre guiado, evidencia y acciones de caja'],
  commandCenter: ['CashSessionsOperationalView', 'model.currentPath === "/cash-sessions" || model.mode === "cash"'],
  metricsDay: ['getBackofficeDashboard', 'Métricas del día', 'Sin cifras simuladas ni filtros globales', 'DataTable columns={["Indicador", "Valor", "Estado", "Fuente", "Nota"]}', 'currentPath="/metricas-dia"']
};
for (const [key, markers] of Object.entries(requiredMarkers)) {
  for (const marker of markers) if (!source[key].includes(marker)) fail("Required marker missing", { file: key, marker });
}
for (const [key, text] of Object.entries(source)) {
  if (text.includes("SmartDropdownDock")) fail("Global SmartDropdownDock must not be mounted on sales/cash/metrics customer surfaces", { file: key });
  const match = text.match(new RegExp("!" + "important", "g"));
  if (match) fail("Forbidden forced override found", { file: key, count: match.length });
  for (const pattern of [/\/sales-control\/detalle/g, /\/cash-sessions\/cerrar/g, /\/metricas-dia\/detalle/g]) {
    const routeMatch = text.match(pattern);
    if (routeMatch) fail("Forbidden new primary route found", { file: key, pattern: String(pattern), match: routeMatch });
  }
}
console.log(JSON.stringify({ ok: true, verifier: "verify_pcsales_operational_2406", checks: { salesLedger: true, contextualSearch: true, cashGuidedClose: true, metricasDiaRealData: true, globalSmartDropdownRemoved: true, noNewPrimaryScreens: true, noForcedOverrides: true } }, null, 2));

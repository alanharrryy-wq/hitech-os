import fs from "node:fs";
import path from "node:path";

const repoRoot = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();

const files = {
  salesTsx: "apps/terminal-de-venta-system/products/pc/app/components/control/sales-control-branch-view.tsx",
  salesCss: "apps/terminal-de-venta-system/products/pc/app/components/control/sales-control-branch-view.module.css",
  cashTsx: "apps/terminal-de-venta-system/products/pc/app/components/control/cash-sessions-operational-view.tsx",
  cashCss: "apps/terminal-de-venta-system/products/pc/app/components/control/cash-sessions-operational-view.module.css",
  metricsTsx: "apps/terminal-de-venta-system/products/pc/app/app/metricas-dia/page.tsx",
  metricsCss: "apps/terminal-de-venta-system/products/pc/app/app/metricas-dia/metricas-dia.module.css"
};

function read(rel) {
  const abs = path.join(repoRoot, rel);
  if (!fs.existsSync(abs)) {
    throw new Error(`Missing required file: ${rel}`);
  }
  return fs.readFileSync(abs, "utf8");
}

function requireIncludes(label, text, needles) {
  for (const needle of needles) {
    if (!text.includes(needle)) {
      throw new Error(`${label} missing marker: ${needle}`);
    }
  }
}

function requireExcludes(label, text, needles) {
  for (const needle of needles) {
    if (text.includes(needle)) {
      throw new Error(`${label} still contains forbidden marker: ${needle}`);
    }
  }
}

const bangImportant = "!" + "important";

const salesTsx = read(files.salesTsx);
const salesCss = read(files.salesCss);
const cashTsx = read(files.cashTsx);
const cashCss = read(files.cashCss);
const metricsTsx = read(files.metricsTsx);
const metricsCss = read(files.metricsCss);

for (const [label, content] of Object.entries({ salesTsx, salesCss, cashTsx, cashCss, metricsTsx, metricsCss })) {
  if (content.includes(bangImportant)) {
    throw new Error(`${label} contains forbidden priority override`);
  }
}

requireIncludes("sales-control tsx", salesTsx, [
  'data-prisma-surface="pcsales-operational-ledger"',
  'data-prisma-component="PcSalesDenseTicketLedger"',
  'data-prisma-component="PcSalesFinancialStrip"',
  'data-prisma-component="PcSalesCashActionRail"',
  "function BranchRail",
  "function PaymentMethodStrip",
  "La tabla de tickets es la pieza principal"
]);
requireExcludes("sales-control tsx", salesTsx, [
  "function MetricTile"
]);

requireIncludes("sales-control css", salesCss, [
  ".ledgerShell",
  ".operationRail",
  ".financialStrip",
  ".ticketTable",
  ".paymentStrip",
  ".branchRail",
  "grid-template-columns: minmax(280px, 360px) minmax(0, 1fr)"
]);

requireIncludes("cash-sessions tsx", cashTsx, [
  'data-prisma-surface="pc-cash-drawer-console"',
  'data-prisma-component="PcCashBalanceHierarchy"',
  'data-prisma-component="PcCashGuidedClose"',
  'data-prisma-component="PcCashRiskStack"',
  "function CashMetricStack",
  "function PanelStack"
]);
requireExcludes("cash-sessions tsx", cashTsx, [
  "function MetricCard"
]);

requireIncludes("cash-sessions css", cashCss, [
  ".consoleGrid",
  ".cashRail",
  ".cashBalanceStrip",
  ".primaryBalance",
  ".panelStack",
  ".tableCard :global(table)"
]);

requireIncludes("metricas-dia tsx", metricsTsx, [
  'data-prisma-surface="pc-daily-finance-readout"',
  'data-prisma-component="PcDailyFinanceStrip"',
  'data-prisma-component="PcDailyCashDifferenceRibbon"',
  'data-prisma-component="PcDailyMetricLedger"',
  "SmartDropdownDock",
  "AppShell"
]);
requireExcludes("metricas-dia tsx", metricsTsx, [
  "DecisionScreen",
  "summaryCards={",
  "recommendedAction={"
]);

requireIncludes("metricas-dia css", metricsCss, [
  ".dailyFinanceCanvas",
  ".canvasGrid",
  ".filterRail",
  ".financeStrip",
  ".analysisTable",
  ".cashRibbon"
]);

const salesCardMatches = (salesTsx.match(/MetricTile/g) ?? []).length;
const cashCardMatches = (cashTsx.match(/MetricCard/g) ?? []).length;
if (salesCardMatches > 0 || cashCardMatches > 0) {
  throw new Error("Generic metric card layout markers remain in sales/cash views.");
}

console.log("PCSALES VISUAL DIVERSITY VERIFY OK");

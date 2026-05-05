import fs from 'node:fs';
import path from 'node:path';

const repoArg = process.argv[2] || process.cwd();
const repoRoot = repoArg.endsWith('hitech-os') ? repoArg : process.cwd();
const systemRoot = path.join(repoRoot, 'apps', 'terminal-de-venta-system');
const seedFile = path.join(systemRoot, 'tools', 'visual-pos-seeds', 'PRISMA_VISUAL_POS_MINIMAL_SEEDS_02.json');

function fail(message, detail = undefined) {
  const payload = {
    ok: false,
    package: 'PRISMA_VISUAL_POS_MINIMAL_SEEDS_02',
    message,
    detail
  };
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}

if (!fs.existsSync(seedFile)) {
  fail('Seed file missing', seedFile);
}

const seed = JSON.parse(fs.readFileSync(seedFile, 'utf8'));
const checks = [];

function check(name, ok, detail = undefined) {
  const row = { name, ok: Boolean(ok) };
  if (detail !== undefined) row.detail = detail;
  checks.push(row);
}

const catalog = Array.isArray(seed.catalog) ? seed.catalog : [];
const sales = Array.isArray(seed.salesToday) ? seed.salesToday : [];
const events = Array.isArray(seed.events) ? seed.events : [];

const netSales = sales.reduce((sum, sale) => sum + Number(sale.totalCents || 0), 0);
const declaredNetSales = Number(seed.pcDashboard?.kpis?.netSalesCents || 0);
const ticketCount = sales.length;
const declaredTicketCount = Number(seed.pcDashboard?.kpis?.ticketCount || 0);
const unitsSold = sales.flatMap((sale) => sale.lines || []).reduce((sum, line) => sum + Number(line.qty || 0), 0);
const declaredUnitsSold = Number(seed.pcDashboard?.kpis?.unitsSold || 0);

const lowStock = catalog.filter((item) => Number(item.stockOnHand) <= Number(item.lowStockThreshold));
const stockout = catalog.filter((item) => Number(item.stockOnHand) === 0);
const pendingEvents = events.filter((event) => event.status === 'pending');

check('package marker', seed.package === 'PRISMA_VISUAL_POS_MINIMAL_SEEDS_02');
check('tablet base url', seed.surfaces?.tablet?.baseUrl === 'http://127.0.0.1:3120');
check('pc base url', seed.surfaces?.pc?.baseUrl === 'http://127.0.0.1:3130');
check('mobile base url', seed.surfaces?.mobile?.baseUrl === 'http://127.0.0.1:3140');
check('catalog has at least 5 products', catalog.length >= 5, catalog.length);
check('all active products have barcode', catalog.every((item) => item.isActive && item.barcode), catalog.map((item) => item.sku));
check('sales today has at least 3 tickets', ticketCount >= 3, ticketCount);
check('net sales matches KPI', netSales === declaredNetSales, { netSales, declaredNetSales });
check('ticket count matches KPI', ticketCount === declaredTicketCount, { ticketCount, declaredTicketCount });
check('units sold matches KPI', unitsSold === declaredUnitsSold, { unitsSold, declaredUnitsSold });
check('low stock has at least 2 SKUs', lowStock.length >= 2, lowStock.map((item) => item.sku));
check('stockout has exactly 1 SKU', stockout.length === 1, stockout.map((item) => item.sku));
check('pending events matches KPI', pendingEvents.length === Number(seed.pcDashboard?.kpis?.pendingOutboxEvents || 0), pendingEvents.length);
check('mobile brief has headline', Boolean(seed.mobileBrief?.headline));
check('acceptance has tablet pc mobile', Boolean(seed.acceptance?.tablet && seed.acceptance?.pc && seed.acceptance?.mobile));

const failed = checks.filter((row) => !row.ok);

const payload = {
  ok: failed.length === 0,
  package: 'PRISMA_VISUAL_POS_MINIMAL_SEEDS_02',
  seedFile,
  summary: {
    products: catalog.length,
    tickets: ticketCount,
    netSalesCents: netSales,
    unitsSold,
    lowStockSkuCount: lowStock.length,
    stockoutSkuCount: stockout.length,
    pendingEvents: pendingEvents.length
  },
  failed,
  checks
};

if (failed.length) {
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}

console.log(JSON.stringify(payload, null, 2));

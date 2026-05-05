import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const defaultDbPath = path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db");

function toPrismaFileUrl(dbPath) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

const databaseUrl = process.env.DATABASE_URL || toPrismaFileUrl(defaultDbPath);
const requireFromCaller = createRequire(path.join(process.cwd(), "package.json"));
const { PrismaClient } = requireFromCaller("@prisma/client");
const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });

function cents(value) {
  return Number(value || 0);
}

async function main() {
  const [
    activeProducts,
    recentSales,
    openCashSessions,
    recentReturns,
    pendingOutbox,
    openPurchaseOrders,
    postedReceipts
  ] = await Promise.all([
    prisma.product.findMany({ where: { isActive: true }, take: 5, orderBy: { updatedAt: "desc" } }),
    prisma.sale.findMany({ include: { lines: true }, take: 5, orderBy: { createdAt: "desc" } }),
    prisma.cashSession.findMany({ where: { status: "OPEN" }, take: 5, orderBy: { openedAt: "desc" } }),
    prisma.saleReturn.findMany({ take: 5, orderBy: { createdAt: "desc" } }),
    prisma.outboxEvent.findMany({ where: { status: { in: ["pending", "failed"] } }, take: 5, orderBy: { createdAt: "asc" } }),
    prisma.purchaseOrder.findMany({ where: { status: { in: ["ordered", "partial"] } }, include: { lines: true }, take: 5 }),
    prisma.goodsReceipt.findMany({ include: { lines: true }, take: 5 })
  ]);

  const report = {
    databaseUrl,
    activeProducts: activeProducts.map((row) => ({ sku: row.sku, businessId: row.businessId })),
    recentSales: recentSales.map((sale) => ({
      folio: sale.folio,
      totalCents: sale.totalCents,
      lineTotalCents: sale.lines.reduce((acc, line) => acc + cents(line.totalCents), 0)
    })),
    openCashSessions: openCashSessions.map((session) => ({
      id: session.id,
      terminalId: session.terminalId,
      status: session.status
    })),
    recentReturns: recentReturns.map((row) => ({ id: row.id, saleFolio: row.saleFolio, amountCents: row.amountCents })),
    pendingOutbox: pendingOutbox.map((row) => ({ id: row.id, topic: row.topic, status: row.status })),
    openPurchaseOrders: openPurchaseOrders.map((order) => ({
      id: order.id,
      totalCents: order.totalCents,
      lineTotalCents: order.lines.reduce((acc, line) => acc + cents(line.lineTotalCents), 0)
    })),
    postedReceipts: postedReceipts.map((receipt) => ({
      id: receipt.id,
      totalCents: receipt.totalCents,
      lineTotalCents: receipt.lines.reduce((acc, line) => acc + cents(line.lineTotalCents), 0)
    }))
  };

  const pass =
    report.activeProducts.length > 0 &&
    report.recentSales.length > 0 &&
    report.openCashSessions.length > 0 &&
    report.recentReturns.length > 0 &&
    report.pendingOutbox.length > 0 &&
    report.openPurchaseOrders.every((order) => order.totalCents === order.lineTotalCents) &&
    report.postedReceipts.every((receipt) => receipt.totalCents === receipt.lineTotalCents);

  console.log(JSON.stringify({ pass, ...report }, null, 2));
  if (!pass) process.exitCode = 1;
}

main()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

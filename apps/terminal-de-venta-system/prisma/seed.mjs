import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const defaultDbPath = path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db");
const seedPath = path.join(__dirname, "seeds", "canonical.seed.json");

function toPrismaFileUrl(dbPath) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

function resolveDatabaseUrl() {
  return process.env.DATABASE_URL || toPrismaFileUrl(defaultDbPath);
}

function assertLocalSeedTarget(databaseUrl) {
  const normalized = databaseUrl.replace(/\\/g, "/").toLowerCase();
  const explicitNonLocal = process.env.HITECH_PRISMA_ALLOW_NONLOCAL_SEED === "1";
  if (!normalized.includes("/tools/_local/") && !explicitNonLocal) {
    throw new Error(
      "Refusing to seed a non-local database. Set HITECH_PRISMA_ALLOW_NONLOCAL_SEED=1 only for an intentional persistent seed."
    );
  }
}

const databaseUrl = resolveDatabaseUrl();
assertLocalSeedTarget(databaseUrl);
fs.mkdirSync(path.dirname(databaseUrl.replace(/^file:/, "")), { recursive: true });

const requireFromCaller = createRequire(path.join(process.cwd(), "package.json"));
const { PrismaClient } = requireFromCaller("@prisma/client");
const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });
const seed = JSON.parse(fs.readFileSync(seedPath, "utf8"));

const deleteOrder = [
  "outboxEvent",
  "auditCount",
  "saleReturn",
  "saleLine",
  "sale",
  "cashMovement",
  "cashSession",
  "replenishmentSignal",
  "goodsReceiptLine",
  "goodsReceipt",
  "purchaseOrderLine",
  "purchaseOrder",
  "supplier",
  "stockMovement",
  "stockSnapshot",
  "priceListItem",
  "barcode",
  "product",
  "priceList",
  "taxRate",
  "terminal",
  "store",
  "business"
];

const insertOrder = [
  ["business", "businesses"],
  ["store", "stores"],
  ["terminal", "terminals"],
  ["taxRate", "taxRates"],
  ["priceList", "priceLists"],
  ["product", "products"],
  ["barcode", "barcodes"],
  ["priceListItem", "priceListItems"],
  ["stockSnapshot", "stockSnapshots"],
  ["stockMovement", "stockMovements"],
  ["supplier", "suppliers"],
  ["purchaseOrder", "purchaseOrders"],
  ["purchaseOrderLine", "purchaseOrderLines"],
  ["goodsReceipt", "goodsReceipts"],
  ["goodsReceiptLine", "goodsReceiptLines"],
  ["replenishmentSignal", "replenishmentSignals"],
  ["cashSession", "cashSessions"],
  ["cashMovement", "cashMovements"],
  ["sale", "sales"],
  ["saleLine", "saleLines"],
  ["saleReturn", "saleReturns"],
  ["auditCount", "auditCounts"],
  ["outboxEvent", "outboxEvents"]
];

async function main() {
  await prisma.$executeRawUnsafe("PRAGMA foreign_keys=ON");

  for (const delegate of deleteOrder) {
    await prisma[delegate].deleteMany();
  }

  const inserted = {};
  for (const [delegate, collection] of insertOrder) {
    const rows = seed[collection] || [];
    inserted[collection] = rows.length;
    for (const row of rows) {
      await prisma[delegate].create({ data: row });
    }
  }

  const purchaseOrder = await prisma.purchaseOrder.findUniqueOrThrow({
    where: { id: "po_demo_001" },
    include: { lines: true }
  });
  const goodsReceipt = await prisma.goodsReceipt.findUniqueOrThrow({
    where: { id: "gr_demo_001" },
    include: { lines: true }
  });

  console.log(
    JSON.stringify(
      {
        status: "seeded",
        databaseUrl,
        inserted,
        procurementTotals: {
          purchaseOrder: {
            header: {
              subtotalCents: purchaseOrder.subtotalCents,
              taxCents: purchaseOrder.taxCents,
              totalCents: purchaseOrder.totalCents
            },
            lineSums: sumLineTotals(purchaseOrder.lines)
          },
          goodsReceipt: {
            header: {
              subtotalCents: goodsReceipt.subtotalCents,
              taxCents: goodsReceipt.taxCents,
              totalCents: goodsReceipt.totalCents
            },
            lineSums: sumLineTotals(goodsReceipt.lines)
          }
        }
      },
      null,
      2
    )
  );
}

function sumLineTotals(lines) {
  return lines.reduce(
    (acc, line) => ({
      subtotalCents: acc.subtotalCents + line.lineSubtotalCents,
      taxCents: acc.taxCents + line.lineTaxCents,
      totalCents: acc.totalCents + line.lineTotalCents
    }),
    { subtotalCents: 0, taxCents: 0, totalCents: 0 }
  );
}

main()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

// PRISMA_PC_TABLET_CATALOG_MIRROR_04D verifier.
// Reads canonical PC database by default and validates that the mirrored SKUs are present.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pcAppRoot = path.resolve(__dirname, "..");
const terminalRoot = path.resolve(pcAppRoot, "..", "..", "..");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const seedPath = path.join(terminalRoot, "prisma", "seeds", "pc_mass_catalog_04d.json");
const defaultDbPath = path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db");

function toPrismaFileUrl(dbPath) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

const databaseUrl = process.env.DATABASE_URL || toPrismaFileUrl(defaultDbPath);
const seed = JSON.parse(fs.readFileSync(seedPath, "utf8"));
const products = seed.products || [];

async function main() {
  const staticOnly = process.argv.includes("--static");
  const duplicateSkus = findDuplicates(products.map((product) => product.sku));
  const duplicateCodes = findDuplicates(products.map((product) => product.barcode));
  if (products.length < 120) throw new Error(`Expected at least 120 products, found ${products.length}`);
  if (duplicateSkus.length) throw new Error(`Duplicate SKUs in seed: ${duplicateSkus.join(", ")}`);
  if (duplicateCodes.length) throw new Error(`Duplicate barcodes in seed: ${duplicateCodes.join(", ")}`);

  if (staticOnly) {
    console.log(JSON.stringify({
      ok: true,
      mode: "static",
      products: products.length,
      publicBarcodeReferences: seed.summary?.publicBarcodeReferences ?? null,
      internalOperationalCodes: seed.summary?.internalOperationalCodes ?? null
    }, null, 2));
    return;
  }

  const requireFromPc = createRequire(path.join(pcAppRoot, "package.json"));
  const { PrismaClient } = requireFromPc("@prisma/client");
  const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });
  try {
    const businessId = seed.businessId || "biz_hitech_default";
    const skus = products.map((product) => product.sku);
    const codes = products.map((product) => product.barcode);
    const productRows = await prisma.product.findMany({
      where: { businessId, sku: { in: skus } },
      select: { id: true }
    });
    const productIds = productRows.map((product) => product.id);
    const productCount = productRows.length;
    const barcodeCount = await prisma.barcode.count({ where: { businessId, code: { in: codes } } });
    const snapshotCount = await prisma.stockSnapshot.count({ where: { businessId, productId: { in: productIds } } });
    const movementCount = await prisma.stockMovement.count({ where: { businessId, reason: { contains: "seed_pc_mass_catalog_04d" } } });

    if (productCount !== products.length) throw new Error(`PC product mirror incomplete: ${productCount}/${products.length}`);
    if (barcodeCount !== products.length) throw new Error(`PC barcode mirror incomplete: ${barcodeCount}/${products.length}`);
    if (snapshotCount < products.length) throw new Error(`PC stock snapshots incomplete: ${snapshotCount}/${products.length}`);

    console.log(JSON.stringify({
      ok: true,
      mode: "database",
      databaseUrl,
      products: productCount,
      barcodes: barcodeCount,
      stockSnapshots: snapshotCount,
      seedMovements: movementCount,
      publicBarcodeReferences: seed.summary?.publicBarcodeReferences ?? null,
      internalOperationalCodes: seed.summary?.internalOperationalCodes ?? null
    }, null, 2));
  } finally {
    await prisma.$disconnect();
  }
}

function findDuplicates(values) {
  const seen = new Set();
  const dupes = new Set();
  for (const value of values) {
    if (seen.has(value)) dupes.add(value);
    seen.add(value);
  }
  return Array.from(dupes);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

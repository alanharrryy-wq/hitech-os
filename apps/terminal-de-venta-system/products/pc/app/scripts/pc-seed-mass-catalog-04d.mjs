// PRISMA_PC_TABLET_CATALOG_MIRROR_04D
// Mirrors the 04B Tablet convenience-store catalog into the canonical PC/backoffice database.
// Safe by default: product labels/prices/barcodes/snapshots are updated, but existing stock is preserved unless --reset-stock is explicit.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pcAppRoot = path.resolve(__dirname, "..");
const terminalRoot = path.resolve(pcAppRoot, "..", "..", "..");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const defaultDbPath = path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db");
const seedPath = path.join(terminalRoot, "prisma", "seeds", "pc_mass_catalog_04d.json");

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

function moneyCents(value) {
  return Number.isFinite(value) ? value : 0;
}

function daysCoverFor(stockOnHand) {
  return Math.max(1, Math.min(14, Number((stockOnHand / 12).toFixed(1)))) || 7;
}

async function main() {
  const resetStock = process.argv.includes("--reset-stock");
  const databaseUrl = resolveDatabaseUrl();
  assertLocalSeedTarget(databaseUrl);

  const dbFile = databaseUrl.replace(/^file:/, "");
  fs.mkdirSync(path.dirname(dbFile), { recursive: true });
  if (!fs.existsSync(seedPath)) throw new Error(`Missing seed data: ${seedPath}`);

  const seed = JSON.parse(fs.readFileSync(seedPath, "utf8"));
  const requireFromPc = createRequire(path.join(pcAppRoot, "package.json"));
  const { PrismaClient } = requireFromPc("@prisma/client");
  const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });

  const businessId = seed.businessId || "biz_hitech_default";
  const storeId = seed.storeId || "store_obrera_04";
  const location = seed.location || "SUCURSAL_CENTRO";
  const taxRateId = seed.taxRateId || "tax_mx_iva_16";
  const products = seed.products || [];

  try {
    await prisma.$executeRawUnsafe("PRAGMA foreign_keys=ON");

    await prisma.business.upsert({
      where: { id: businessId },
      update: { name: "HITECH Demo Business", currency: "MXN" },
      create: { id: businessId, name: "HITECH Demo Business", taxId: "HTD260425MX1", currency: "MXN" }
    });

    await prisma.store.upsert({
      where: { businessId_code: { businessId, code: "OBR-04" } },
      update: { name: "Sucursal Obrera 04" },
      create: { id: storeId, businessId, code: "OBR-04", name: "Sucursal Obrera 04" }
    });

    await prisma.terminal.upsert({
      where: { businessId_code: { businessId, code: "TBL-01" } },
      update: { storeId, name: "Tablet caja 01", isActive: true },
      create: { id: "terminal_tablet_01", businessId, storeId, code: "TBL-01", name: "Tablet caja 01", isActive: true }
    });

    await prisma.taxRate.upsert({
      where: { businessId_name: { businessId, name: "IVA 16%" } },
      update: { rateBps: 1600, isDefault: true, isActive: true },
      create: { id: taxRateId, businessId, name: "IVA 16%", rateBps: 1600, isDefault: true, isActive: true }
    });

    let upsertedProducts = 0;
    let upsertedBarcodes = 0;
    let upsertedSnapshots = 0;
    let upsertedMovements = 0;

    for (const product of products) {
      const saved = await prisma.product.upsert({
        where: { businessId_sku: { businessId, sku: product.sku } },
        update: {
          name: product.name,
          category: product.category,
          priceCents: moneyCents(product.priceCents),
          costCents: moneyCents(product.costCents),
          ...(resetStock ? { stockOnHand: product.stockOnHand } : {}),
          taxRateId,
          isActive: true
        },
        create: {
          id: product.id,
          businessId,
          sku: product.sku,
          name: product.name,
          category: product.category,
          priceCents: moneyCents(product.priceCents),
          costCents: moneyCents(product.costCents),
          stockOnHand: product.stockOnHand,
          taxRateId,
          isActive: true
        }
      });
      upsertedProducts += 1;

      await prisma.barcode.upsert({
        where: { businessId_code: { businessId, code: product.barcode } },
        update: { productId: saved.id },
        create: { id: `bc_pc_${product.id}`, businessId, productId: saved.id, code: product.barcode }
      });
      upsertedBarcodes += 1;

      await prisma.stockSnapshot.upsert({
        where: { businessId_productId_location: { businessId, productId: saved.id, location } },
        update: {
          ...(resetStock ? { onHand: product.stockOnHand, reserved: 0, available: product.stockOnHand } : {}),
          daysCover: daysCoverFor(product.stockOnHand),
          snapshotAt: new Date()
        },
        create: {
          id: `stk_pc_${product.id}_${location.toLowerCase()}`,
          businessId,
          productId: saved.id,
          location,
          onHand: product.stockOnHand,
          reserved: 0,
          available: product.stockOnHand,
          daysCover: daysCoverFor(product.stockOnHand),
          snapshotAt: new Date()
        }
      });
      upsertedSnapshots += 1;

      await prisma.stockMovement.upsert({
        where: { id: `mov_pc_${product.id}_seed_04d` },
        update: {
          qty: product.stockOnHand,
          reason: resetStock ? "seed_pc_mass_catalog_04d_reset" : "seed_pc_mass_catalog_04d",
          location
        },
        create: {
          id: `mov_pc_${product.id}_seed_04d`,
          businessId,
          productId: saved.id,
          movement: "IN",
          qty: product.stockOnHand,
          reason: "seed_pc_mass_catalog_04d",
          location,
          createdAt: new Date()
        }
      });
      upsertedMovements += 1;
    }

    const activeProducts = await prisma.product.count({ where: { businessId, isActive: true } });
    const barcodeCount = await prisma.barcode.count({ where: { businessId } });
    const mirrorSkus = await prisma.product.count({ where: { businessId, sku: { in: products.map((product) => product.sku) } } });

    console.log(JSON.stringify({
      ok: true,
      databaseUrl,
      businessId,
      location,
      resetStock,
      upsertedProducts,
      upsertedBarcodes,
      upsertedSnapshots,
      upsertedMovements,
      activeProducts,
      barcodeCount,
      mirrorSkus,
      expectedMirrorSkus: products.length,
      publicBarcodeReferences: seed.summary?.publicBarcodeReferences ?? null,
      internalOperationalCodes: seed.summary?.internalOperationalCodes ?? null
    }, null, 2));
  } finally {
    await prisma.$disconnect();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

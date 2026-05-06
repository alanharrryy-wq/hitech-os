#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { TABLET_CONVENIENCE_PRODUCTS_04B } from "./tablet-seed-catalog.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptDir, "..");
const schemaPath = path.join(appRoot, "prisma", "schema.prisma");
const dbPath = process.env.TABLET_DATABASE_PATH
  ? path.resolve(process.env.TABLET_DATABASE_PATH)
  : path.join(appRoot, "data", "tablet-pos.db");
const databaseUrl = process.env.TABLET_DATABASE_URL ?? `file:${dbPath.replace(/\\/g, "/")}`;
const command = process.argv[2] ?? "help";

function printHelp() {
  console.log(`Tablet DB helper

Usage:
  node scripts/tablet-db.mjs init
  node scripts/tablet-db.mjs generate
  node scripts/tablet-db.mjs push
  node scripts/tablet-db.mjs seed
  node scripts/tablet-db.mjs info

Environment:
  TABLET_DATABASE_URL   Full Prisma datasource URL. Highest priority.
  TABLET_DATABASE_PATH  Local SQLite file path. Used when TABLET_DATABASE_URL is absent.

Default DB:
  ${dbPath}
`);
}

function buildPrismaLaunches(args) {
  const prismaArgs = ["exec", "prisma", ...args];
  const launches = [];

  // PRISMA HOTFIX 00C: when launched from a pnpm script, npm_execpath points
  // at pnpm's JS entrypoint. Running that through the current Node executable
  // avoids Windows spawnSync(pnpm.cmd) EINVAL.
  const npmExecPath = process.env.npm_execpath;
  if (npmExecPath && npmExecPath.toLowerCase().includes("pnpm")) {
    launches.push({
      label: `node ${npmExecPath} ${prismaArgs.join(" ")}`,
      bin: process.execPath,
      args: [npmExecPath, ...prismaArgs],
      shell: false
    });
  }

  // Fallback for direct manual execution. On Windows, shell:true lets cmd.exe
  // resolve pnpm.cmd safely instead of asking spawnSync to execute the .cmd file directly.
  launches.push({
    label: `pnpm exec prisma ${args.join(" ")}`,
    bin: "pnpm",
    args: prismaArgs,
    shell: process.platform === "win32"
  });

  return launches;
}

function runPrisma(args) {
  if (!existsSync(schemaPath)) {
    console.error(`[tablet-db] Missing schema: ${schemaPath}`);
    process.exit(2);
  }

  mkdirSync(path.dirname(dbPath), { recursive: true });

  console.log(`[tablet-db] appRoot: ${appRoot}`);
  console.log(`[tablet-db] schema: ${schemaPath}`);
  console.log(`[tablet-db] databaseUrl: ${databaseUrl}`);

  let lastError = null;
  for (const launch of buildPrismaLaunches(args)) {
    console.log(`[tablet-db] running: ${launch.label}`);
    const result = spawnSync(launch.bin, launch.args, {
      cwd: appRoot,
      stdio: "inherit",
      shell: launch.shell,
      env: {
        ...process.env,
        DATABASE_URL: databaseUrl,
        TABLET_DATABASE_URL: databaseUrl,
        TABLET_APP_ROOT: appRoot
      }
    });

    if (result.error) {
      lastError = result.error;
      console.error(`[tablet-db] Prisma launcher failed: ${result.error.message}`);
      continue;
    }

    if (result.status !== 0) {
      console.error(`[tablet-db] Prisma command failed with exit code ${result.status ?? 1}.`);
      process.exit(result.status ?? 1);
    }

    return;
  }

  console.error("[tablet-db] Failed to launch Prisma through pnpm exec.");
  if (lastError) {
    console.error(`[tablet-db] Last launcher error: ${lastError.message}`);
  }
  console.error("[tablet-db] Verify that pnpm is available in PATH and dependencies are installed in the Tablet app.");
  process.exit(1);
}

function configureDatabaseEnv() {
  process.env.DATABASE_URL = databaseUrl;
  process.env.TABLET_DATABASE_URL = databaseUrl;
  process.env.TABLET_APP_ROOT = appRoot;
}

async function ensureSaleClientRequestIdSchema() {
  configureDatabaseEnv();

  const { PrismaClient } = await import("@prisma/client");
  const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });

  try {
    const columns = await prisma.$queryRawUnsafe(`PRAGMA table_info("Sale")`).catch(() => []);
    if (!Array.isArray(columns) || columns.length === 0) return;

    const hasClientRequestId = columns.some((column) => column?.name === "clientRequestId");
    if (!hasClientRequestId) {
      await prisma.$executeRawUnsafe(`ALTER TABLE "Sale" ADD COLUMN "clientRequestId" TEXT`);
      console.log("[tablet-db] Added nullable Sale.clientRequestId for idempotent local sales.");
    }

    await prisma.$executeRawUnsafe(`CREATE UNIQUE INDEX IF NOT EXISTS "Sale_businessId_clientRequestId_key" ON "Sale" ("businessId", "clientRequestId")`);
    console.log("[tablet-db] Sale businessId + clientRequestId uniqueness is present.");
  } finally {
    await prisma.$disconnect();
  }
}

async function seed() {
  // PRISMA_TABLET_SEED_STORE_UPSERT_HOTFIX_04C: Store/Terminal/TaxRate seed uses compound unique upserts.
  // PRISMA HARDENING 01: safe seed, no stock reset after operation unless --reset-demo-stock is explicit.
  const resetDemoStock = process.argv.includes("--reset-demo-stock");
  configureDatabaseEnv();

  const { PrismaClient } = await import("@prisma/client");
  const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });

  try {
    const businessId = "biz_tablet_standalone";
    const defaultStoreId = "store_tablet_local";
    const defaultTerminalId = "terminal_tablet_local_01";
    const defaultTaxRateId = "tax_mx_iva_16";

    await prisma.business.upsert({
      where: { id: businessId },
      update: { name: "PRISMA Tablet Standalone", currency: "MXN" },
      create: { id: businessId, name: "PRISMA Tablet Standalone", taxId: null, currency: "MXN" }
    });

    const localStore = await prisma.store.upsert({
      where: { businessId_code: { businessId, code: "LOCAL" } },
      update: { name: "Tienda local" },
      create: { id: defaultStoreId, businessId, code: "LOCAL", name: "Tienda local" }
    });
    const storeId = localStore.id;

    const localTerminal = await prisma.terminal.upsert({
      where: { businessId_code: { businessId, code: "TBL-LOCAL" } },
      update: { storeId, name: "Tablet POS local", isActive: true },
      create: { id: defaultTerminalId, businessId, storeId, code: "TBL-LOCAL", name: "Tablet POS local", isActive: true }
    });
    const terminalId = localTerminal.id;

    const ivaTaxRate = await prisma.taxRate.upsert({
      where: { businessId_name: { businessId, name: "IVA 16%" } },
      update: { rateBps: 1600, isDefault: true, isActive: true },
      create: { id: defaultTaxRateId, businessId, name: "IVA 16%", rateBps: 1600, isDefault: true, isActive: true }
    });
    const taxRateId = ivaTaxRate.id;

    const products = TABLET_CONVENIENCE_PRODUCTS_04B;
    const publicBarcodeCount = products.filter((product) => product.barcodeSource === "public").length;
    const internalBarcodeCount = products.length - publicBarcodeCount;

    const operationalSales = await prisma.sale.count().catch(() => 0);
    const operationalMovements = await prisma.stockMovement.count().catch(() => 0);
    const canResetDemoStock = resetDemoStock && operationalSales === 0 && operationalMovements === 0;

    for (const product of products) {
      await prisma.product.upsert({
        where: { id: product.id },
        update: {
          sku: product.sku,
          name: product.name,
          category: product.category,
          priceCents: product.priceCents,
          costCents: product.costCents,
          ...(canResetDemoStock ? { stockOnHand: product.stockOnHand } : {}),
          taxRateId,
          isActive: true
        },
        create: {
          id: product.id,
          businessId,
          sku: product.sku,
          name: product.name,
          category: product.category,
          priceCents: product.priceCents,
          costCents: product.costCents,
          stockOnHand: product.stockOnHand,
          taxRateId,
          isActive: true
        }
      });

      await prisma.barcode.upsert({
        where: { businessId_code: { businessId, code: product.barcode } },
        update: { productId: product.id },
        create: { id: `bc_${product.id}`, businessId, productId: product.id, code: product.barcode }
      });

      await prisma.stockSnapshot.upsert({
        where: { businessId_productId_location: { businessId, productId: product.id, location: "LOCAL" } },
        update: {
          ...(canResetDemoStock ? { onHand: product.stockOnHand, reserved: 0, available: product.stockOnHand } : {}),
          daysCover: 7,
          snapshotAt: new Date()
        },
        create: {
          id: `stk_${product.id}_local`,
          businessId,
          productId: product.id,
          location: "LOCAL",
          onHand: product.stockOnHand,
          reserved: 0,
          available: product.stockOnHand,
          daysCover: 7,
          snapshotAt: new Date()
        }
      });
    }

    console.log(`[tablet-db] Seed OK: ${dbPath}`);
    console.log(`[tablet-db] Catalogo operativo: ${products.length} productos (${publicBarcodeCount} codigos publicos, ${internalBarcodeCount} codigos internos validos).`);
    if (!canResetDemoStock) console.log('[tablet-db] Safe seed preserved existing operational stock. New products still receive initial stock. Use --reset-demo-stock only on empty demo DB.');
  } finally {
    await prisma.$disconnect();
  }
}

async function main() {
  switch (command) {
    case "help":
    case "--help":
    case "-h":
      printHelp();
      return;
    case "info":
      console.log(JSON.stringify({ appRoot, schemaPath, dbPath, databaseUrl }, null, 2));
      return;
    case "generate":
      runPrisma(["generate", "--schema", schemaPath]);
      return;
    case "push":
      await ensureSaleClientRequestIdSchema();
      runPrisma(["db", "push", "--schema", schemaPath]);
      return;
    case "seed":
      await seed();
      return;
    case "init":
      runPrisma(["generate", "--schema", schemaPath]);
      await ensureSaleClientRequestIdSchema();
      runPrisma(["db", "push", "--schema", schemaPath]);
      await seed();
      return;
    default:
      console.error(`[tablet-db] Unknown command: ${command}`);
      printHelp();
      process.exit(2);
  }
}

main().catch((error) => {
  console.error("[tablet-db] Fatal error:");
  console.error(error);
  process.exit(1);
});

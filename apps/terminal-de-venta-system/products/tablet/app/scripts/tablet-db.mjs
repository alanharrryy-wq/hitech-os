#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

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

async function seed() {
  process.env.DATABASE_URL = databaseUrl;
  process.env.TABLET_DATABASE_URL = databaseUrl;
  process.env.TABLET_APP_ROOT = appRoot;

  const { PrismaClient } = await import("@prisma/client");
  const prisma = new PrismaClient({ datasources: { db: { url: databaseUrl } } });

  try {
    const businessId = "biz_tablet_standalone";
    const storeId = "store_tablet_local";
    const terminalId = "terminal_tablet_local_01";
    const taxRateId = "tax_mx_iva_16";

    await prisma.business.upsert({
      where: { id: businessId },
      update: { name: "PRISMA Tablet Standalone", currency: "MXN" },
      create: { id: businessId, name: "PRISMA Tablet Standalone", taxId: null, currency: "MXN" }
    });

    await prisma.store.upsert({
      where: { id: storeId },
      update: { name: "Tienda local", code: "LOCAL" },
      create: { id: storeId, businessId, code: "LOCAL", name: "Tienda local" }
    });

    await prisma.terminal.upsert({
      where: { id: terminalId },
      update: { name: "Tablet POS local", code: "TBL-LOCAL", isActive: true },
      create: { id: terminalId, businessId, storeId, code: "TBL-LOCAL", name: "Tablet POS local", isActive: true }
    });

    await prisma.taxRate.upsert({
      where: { id: taxRateId },
      update: { name: "IVA 16%", rateBps: 1600, isDefault: true, isActive: true },
      create: { id: taxRateId, businessId, name: "IVA 16%", rateBps: 1600, isDefault: true, isActive: true }
    });

    const products = [
      { id: "prd_demo_refresco_355", sku: "REF-355", name: "Refresco 355 ml", category: "Bebidas", priceCents: 3000, costCents: 1600, stockOnHand: 24, barcode: "7501000000011" },
      { id: "prd_demo_papas_45", sku: "PAP-045", name: "Papas 45 g", category: "Botanas", priceCents: 2200, costCents: 1200, stockOnHand: 18, barcode: "7501000000028" },
      { id: "prd_demo_galleta", sku: "GAL-001", name: "Galleta individual", category: "Dulces", priceCents: 1500, costCents: 700, stockOnHand: 30, barcode: "7501000000035" }
    ];

    for (const product of products) {
      await prisma.product.upsert({
        where: { id: product.id },
        update: {
          sku: product.sku,
          name: product.name,
          category: product.category,
          priceCents: product.priceCents,
          costCents: product.costCents,
          stockOnHand: product.stockOnHand,
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
          onHand: product.stockOnHand,
          reserved: 0,
          available: product.stockOnHand,
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
      runPrisma(["db", "push", "--schema", schemaPath]);
      return;
    case "seed":
      await seed();
      return;
    case "init":
      runPrisma(["generate", "--schema", schemaPath]);
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

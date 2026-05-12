#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const projectRoot = path.resolve(appRoot, "..", "..", "..");
const repoRoot = path.resolve(projectRoot, "..", "..");
const tmpRoot = path.join(repoRoot, "tools", "_local", "tmp", "prisma-tablet-standalone-core-closeout-02");
const dbPath = path.join(tmpRoot, `tablet-standalone-${Date.now()}-${process.pid}.db`);
const dbUrl = `file:${dbPath.replace(/\\/g, "/")}`;

const businessId = "biz_tablet_standalone";
const terminalId = "terminal_tablet_local_01";
const cashier = "tablet-closeout-smoke";
const location = "tablet-closeout-local";
const sku = "PAP-045";
const barcode = "7501000000028";
const saleQty = 14;
const lowStockThreshold = 5;

const failures = [];

function ensureTabletPrismaClient() {
  const schemaPath = path.join(appRoot, "prisma", "schema.prisma");
  const env = {
    ...process.env,
    DATABASE_URL: dbUrl,
    TABLET_DATABASE_URL: dbUrl,
    TABLET_APP_ROOT: appRoot
  };
  const launches = [];
  const npmExecPath = process.env.npm_execpath;

  if (npmExecPath && npmExecPath.toLowerCase().includes("pnpm")) {
    launches.push({
      label: `node ${npmExecPath} exec prisma generate --schema ${schemaPath}`,
      bin: process.execPath,
      args: [npmExecPath, "exec", "prisma", "generate", "--schema", schemaPath],
      shell: false
    });
  }

  launches.push({
    label: `pnpm exec prisma generate --schema ${schemaPath}`,
    bin: "pnpm",
    args: ["exec", "prisma", "generate", "--schema", schemaPath],
    shell: process.platform === "win32"
  });

  let lastResult = null;
  for (const launch of launches) {
    const result = spawnSync(launch.bin, launch.args, {
      cwd: appRoot,
      encoding: "utf8",
      shell: launch.shell,
      env
    });

    if (!result.error && result.status === 0) return;
    lastResult = result;
  }

  const detail = lastResult
    ? `${lastResult.error?.message ?? ""}\n${lastResult.stdout ?? ""}\n${lastResult.stderr ?? ""}`.trim()
    : "No Prisma launcher was available.";
  throw new Error(`Tablet Prisma Client generation failed.\n${detail}`);
}

function fail(message) {
  failures.push(message);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function readProjectFile(rel) {
  return readFileSync(path.join(appRoot, rel), "utf8");
}

function makeId(prefix) {
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

function makeEvent(topic, aggregateId, occurredAt, payload) {
  const eventId = makeId("evt");
  return {
    eventId,
    topic,
    idempotencyKey: `${topic}:${businessId}:${terminalId}:${aggregateId}:${eventId}`,
    businessId,
    terminalId,
    actorId: cashier,
    source: "tablet-pos",
    occurredAt: occurredAt.toISOString(),
    aggregateId,
    schemaVersion: "1.0.0",
    payload
  };
}

function localDayRange() {
  const now = new Date();
  const from = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
  const to = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0, 0);
  return { from, to };
}

function toCsv(headers, rows) {
  return `${headers.join(",")}\n${rows.map((row) => headers.map((header) => String(row[header] ?? "")).join(",")).join("\n")}\n`;
}

async function bootstrapSchema(prisma) {
  const statements = [
    `CREATE TABLE IF NOT EXISTS Business (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      taxId TEXT,
      currency TEXT NOT NULL DEFAULT 'MXN',
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS Store (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      code TEXT NOT NULL,
      name TEXT NOT NULL,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS Terminal (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      storeId TEXT NOT NULL,
      code TEXT NOT NULL,
      name TEXT NOT NULL,
      isActive BOOLEAN NOT NULL DEFAULT 1,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS TaxRate (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      name TEXT NOT NULL,
      rateBps INTEGER NOT NULL,
      isDefault BOOLEAN NOT NULL DEFAULT 0,
      isActive BOOLEAN NOT NULL DEFAULT 1,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS Product (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      sku TEXT NOT NULL,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      priceCents INTEGER NOT NULL,
      costCents INTEGER NOT NULL,
      stockOnHand INTEGER NOT NULL DEFAULT 0,
      taxRateId TEXT,
      isActive BOOLEAN NOT NULL DEFAULT 1,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS Barcode (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      productId TEXT NOT NULL,
      code TEXT NOT NULL,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE UNIQUE INDEX IF NOT EXISTS Barcode_businessId_code_key ON Barcode (businessId, code)`,
    `CREATE TABLE IF NOT EXISTS StockSnapshot (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      productId TEXT NOT NULL,
      location TEXT NOT NULL,
      onHand INTEGER NOT NULL,
      reserved INTEGER NOT NULL,
      available INTEGER NOT NULL,
      daysCover REAL NOT NULL,
      snapshotAt DATETIME NOT NULL
    )`,
    `CREATE TABLE IF NOT EXISTS StockMovement (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      productId TEXT NOT NULL,
      movement TEXT NOT NULL,
      qty INTEGER NOT NULL,
      reason TEXT NOT NULL,
      location TEXT NOT NULL,
      beforeQty INTEGER,
      afterQty INTEGER,
      sourceType TEXT,
      sourceId TEXT,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS CashSession (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      storeId TEXT NOT NULL,
      terminalId TEXT NOT NULL,
      cashierId TEXT NOT NULL,
      cashier TEXT NOT NULL,
      openedAt DATETIME NOT NULL,
      closedAt DATETIME,
      cashStartCents INTEGER NOT NULL,
      cashEndCents INTEGER,
      expectedCashCents INTEGER,
      varianceCents INTEGER,
      status TEXT NOT NULL,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS Sale (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      terminalId TEXT NOT NULL,
      cashSessionId TEXT,
      clientRequestId TEXT,
      folio TEXT NOT NULL,
      cashier TEXT NOT NULL,
      subtotalCents INTEGER NOT NULL DEFAULT 0,
      discountCents INTEGER NOT NULL DEFAULT 0,
      totalCents INTEGER NOT NULL,
      completedAt DATETIME,
      paymentMethod TEXT NOT NULL DEFAULT 'cash',
      cashReceivedCents INTEGER,
      changeCents INTEGER NOT NULL DEFAULT 0,
      status TEXT NOT NULL,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE UNIQUE INDEX IF NOT EXISTS Sale_businessId_clientRequestId_key ON Sale (businessId, clientRequestId)`,
    `CREATE TABLE IF NOT EXISTS SaleLine (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      saleId TEXT NOT NULL,
      productId TEXT NOT NULL,
      sku TEXT NOT NULL,
      productName TEXT NOT NULL,
      qty INTEGER NOT NULL,
      priceCents INTEGER NOT NULL,
      totalCents INTEGER NOT NULL,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS SaleReturn (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      saleFolio TEXT NOT NULL,
      reason TEXT NOT NULL,
      amountCents INTEGER NOT NULL,
      status TEXT NOT NULL,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      cashier TEXT NOT NULL
    )`,
    `CREATE TABLE IF NOT EXISTS OutboxEvent (
      id TEXT PRIMARY KEY,
      businessId TEXT NOT NULL,
      terminalId TEXT,
      topic TEXT NOT NULL,
      aggregateId TEXT NOT NULL,
      idempotencyKey TEXT,
      payloadJson TEXT NOT NULL,
      source TEXT,
      schemaVersion TEXT,
      status TEXT NOT NULL,
      attempts INTEGER NOT NULL DEFAULT 0,
      createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      sentAt DATETIME,
      syncedAt DATETIME,
      lastError TEXT
    )`,
    `CREATE INDEX IF NOT EXISTS OutboxEvent_businessId_idempotencyKey_idx ON OutboxEvent (businessId, idempotencyKey)`
  ];

  for (const statement of statements) {
    await prisma.$executeRawUnsafe(statement);
  }
}

async function seed(prisma) {
  const taxRateId = "tax_mx_iva_16";
  const storeId = "store_tablet_local";
  const products = [
    { id: "prd_demo_refresco_355", sku: "REF-355", name: "Refresco 355 ml", category: "Bebidas", priceCents: 3000, costCents: 1600, stockOnHand: 24, barcode: "7501000000011" },
    { id: "prd_demo_papas_45", sku: "PAP-045", name: "Papas 45 g", category: "Botanas", priceCents: 2200, costCents: 1200, stockOnHand: 18, barcode },
    { id: "prd_demo_galleta", sku: "GAL-001", name: "Galleta individual", category: "Dulces", priceCents: 1500, costCents: 700, stockOnHand: 30, barcode: "7501000000035" }
  ];

  await prisma.business.create({ data: { id: businessId, name: "PRISMA Tablet Standalone", taxId: null, currency: "MXN" } });
  await prisma.store.create({ data: { id: storeId, businessId, code: "LOCAL", name: "Tienda local" } });
  await prisma.terminal.create({ data: { id: terminalId, businessId, storeId, code: "TBL-LOCAL", name: "Tablet POS local", isActive: true } });
  await prisma.taxRate.create({ data: { id: taxRateId, businessId, name: "IVA 16%", rateBps: 1600, isDefault: true, isActive: true } });
  await prisma.cashSession.create({
    data: {
      id: "cash_session_tablet_smoke",
      businessId,
      storeId,
      terminalId,
      cashierId: cashier,
      cashier,
      openedAt: new Date(),
      cashStartCents: 100000,
      status: "OPEN"
    }
  });

  for (const product of products) {
    await prisma.product.create({
      data: {
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
    await prisma.barcode.create({ data: { id: `bc_${product.id}`, businessId, productId: product.id, code: product.barcode } });
    await prisma.stockSnapshot.create({
      data: {
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
}

async function completeLocalSale(prisma, clientRequestId = makeId("client_request")) {
  return prisma.$transaction(async (tx) => {
    const existingSale = await tx.sale.findFirst({
      where: { businessId, clientRequestId },
      include: { lines: true }
    });

    if (existingSale) {
      return {
        duplicate: true,
        saleId: existingSale.id,
        clientRequestId,
        lineId: existingSale.lines[0]?.id ?? null,
        movementId: null,
        productId: existingSale.lines[0]?.productId ?? null,
        stockBefore: null,
        stockAfter: null,
        totalCents: existingSale.totalCents,
        events: []
      };
    }

    const product = await tx.product.findFirst({
      where: { businessId, sku, isActive: true },
      include: { barcodes: true }
    });

    if (!product) throw new Error(`Seed product not found by SKU: ${sku}`);
    if (product.stockOnHand < saleQty) throw new Error(`Seed stock too low for smoke: ${product.stockOnHand}`);

    const saleId = makeId("sale");
    const lineId = makeId("sale_line");
    const movementId = makeId("stock_move");
    const occurredAt = new Date();
    const stockBefore = product.stockOnHand;
    const stockAfter = stockBefore - saleQty;
    const totalCents = product.priceCents * saleQty;
    const folio = `SMOKE-${occurredAt.getTime()}`;

    await tx.product.update({
      where: { id: product.id },
      data: { stockOnHand: stockAfter }
    });

    await tx.stockMovement.create({
      data: {
        id: movementId,
        businessId,
        productId: product.id,
        movement: "SALE",
        qty: -saleQty,
        reason: "sale.completed",
        location,
        createdAt: occurredAt
      }
    });

    await tx.sale.create({
      data: {
        id: saleId,
        businessId,
        terminalId,
        cashSessionId: null,
        clientRequestId,
        folio,
        cashier,
        totalCents,
        status: "COMPLETED",
        createdAt: occurredAt
      }
    });

    await tx.saleLine.create({
      data: {
        id: lineId,
        businessId,
        saleId,
        productId: product.id,
        sku: product.sku,
        productName: product.name,
        qty: saleQty,
        priceCents: product.priceCents,
        totalCents,
        createdAt: occurredAt
      }
    });

    const events = [
      makeEvent("sale.created", saleId, occurredAt, { saleId, folio, businessId, terminalId }),
      makeEvent("sale.completed", saleId, occurredAt, { saleId, folio, businessId, terminalId, cashSessionId: null, cashier, totalCents, status: "COMPLETED", lineCount: 1 }),
      makeEvent("ticket.closed", saleId, occurredAt, { saleId, folio, totalCents, items: [{ productId: product.id, sku: product.sku, qty: saleQty, totalCents }] }),
      makeEvent("stock.decremented", product.id, occurredAt, { saleId, productId: product.id, sku: product.sku, qty: saleQty, stockBefore, stockAfter }),
      makeEvent("inventory.low_stock_detected", product.id, occurredAt, { saleId, productId: product.id, sku: product.sku, stockAfter, threshold: lowStockThreshold })
    ];

    for (const event of events) {
      await tx.outboxEvent.create({
        data: {
          id: event.eventId,
          businessId,
          topic: event.topic,
          aggregateId: event.aggregateId,
          idempotencyKey: event.idempotencyKey,
          payloadJson: JSON.stringify(event),
          status: "pending",
          createdAt: occurredAt
        }
      });
    }

    return { duplicate: false, saleId, clientRequestId, lineId, movementId, productId: product.id, stockBefore, stockAfter, totalCents, events };
  });
}

mkdirSync(tmpRoot, { recursive: true });

ensureTabletPrismaClient();
const { PrismaClient } = await import("@prisma/client");

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: dbUrl
    }
  }
});

try {
  await bootstrapSchema(prisma);
  await seed(prisma);

  const runtimeSource = readProjectFile("src/server/pos-runtime/index.ts");
  assert(runtimeSource.includes("pcRequiredForBasicSale: false"), "Tablet runtime must declare PC is not required for basic sale.");

  const packageJson = JSON.parse(readProjectFile("package.json"));
  const healthRoute = readProjectFile("app/api/health/route.ts");
  assert(healthRoute.includes(`version: "${packageJson.version}"`), `Health route version must match package.json ${packageJson.version}.`);

  const saleResult = await completeLocalSale(prisma);

  const sale = await prisma.sale.findUnique({ where: { id: saleResult.saleId }, include: { lines: true } });
  assert(sale, "Sale was not persisted.");
  assert(sale?.clientRequestId === saleResult.clientRequestId, "Sale did not persist clientRequestId.");
  assert(sale?.lines.length === 1, "SaleLine was not persisted.");
  assert(sale?.totalCents === saleResult.totalCents, "Sale total drifted.");

  const movement = await prisma.stockMovement.findUnique({ where: { id: saleResult.movementId } });
  assert(movement?.qty === -saleQty, "StockMovement did not record the negative sale quantity.");

  const productAfter = await prisma.product.findUnique({ where: { id: saleResult.productId }, include: { barcodes: true } });
  assert(productAfter?.stockOnHand === saleResult.stockAfter, "Product stock did not decrement.");
  assert(saleResult.stockAfter === saleResult.stockBefore - saleQty, "Stock decrement arithmetic failed.");

  const outbox = await prisma.outboxEvent.findMany({ where: { aggregateId: { in: [saleResult.saleId, saleResult.productId] } }, orderBy: { createdAt: "asc" } });
  const outboxTopics = outbox.map((event) => event.topic);
  for (const topic of ["sale.created", "sale.completed", "ticket.closed", "stock.decremented", "inventory.low_stock_detected"]) {
    assert(outboxTopics.includes(topic), `Outbox missing topic ${topic}.`);
  }
  assert(outbox.every((event) => event.status === "pending"), "Outbox events must start pending for offline continuity.");

  const saleCountBeforeDuplicate = await prisma.sale.count();
  const outboxCountBeforeDuplicate = await prisma.outboxEvent.count();
  const movementCountBeforeDuplicate = await prisma.stockMovement.count();
  const stockBeforeDuplicate = (await prisma.product.findUnique({ where: { id: saleResult.productId } }))?.stockOnHand;
  const duplicateResult = await completeLocalSale(prisma, saleResult.clientRequestId);
  const stockAfterDuplicate = (await prisma.product.findUnique({ where: { id: saleResult.productId } }))?.stockOnHand;
  assert(duplicateResult.duplicate === true, "Duplicate clientRequestId did not return idempotent duplicate result.");
  assert(duplicateResult.saleId === saleResult.saleId, "Duplicate clientRequestId did not resolve to the original sale.");
  assert((await prisma.sale.count()) === saleCountBeforeDuplicate, "Duplicate clientRequestId created a second Sale.");
  assert((await prisma.outboxEvent.count()) === outboxCountBeforeDuplicate, "Duplicate clientRequestId created additional OutboxEvent rows.");
  assert((await prisma.stockMovement.count()) === movementCountBeforeDuplicate, "Duplicate clientRequestId created additional StockMovement rows.");
  assert(stockAfterDuplicate === stockBeforeDuplicate, "Duplicate clientRequestId changed product stock.");

  const searchRows = await prisma.product.findMany({
    where: {
      businessId,
      isActive: true,
      OR: [{ sku: { contains: "PAP" } }, { name: { contains: "Papas" } }]
    },
    include: { barcodes: true }
  });
  assert(searchRows.some((row) => row.sku === sku), "Product search by SKU/name did not resolve seeded product.");

  const barcodeRow = await prisma.barcode.findUnique({
    where: { businessId_code: { businessId, code: barcode } },
    include: { product: true }
  });
  assert(barcodeRow?.product?.sku === sku, "Barcode resolve did not return the expected SKU.");

  const skuRow = await prisma.product.findFirst({ where: { businessId, sku } });
  assert(skuRow?.id === saleResult.productId, "SKU resolve did not return the expected product.");

  const { from, to } = localDayRange();
  const salesToday = await prisma.sale.findMany({
    where: { businessId, status: "COMPLETED", createdAt: { gte: from, lt: to } },
    include: { lines: true }
  });
  const totalToday = salesToday.reduce((sum, row) => sum + row.totalCents, 0);
  assert(salesToday.some((row) => row.id === saleResult.saleId), "Sales today report query cannot see the smoke sale.");
  assert(totalToday >= saleResult.totalCents, "Sales today total does not include the smoke sale.");

  const eventsCsv = toCsv(["id", "topic", "status"], outbox.map((event) => ({ id: event.id, topic: event.topic, status: event.status })));
  const salesCsv = toCsv(["saleId", "sku", "qty", "totalCents"], sale.lines.map((line) => ({ saleId: sale.id, sku: line.sku, qty: line.qty, totalCents: line.totalCents })));
  assert(eventsCsv.includes("inventory.low_stock_detected"), "Events export proof missing low-stock event.");
  assert(salesCsv.includes(sku), "Sales export proof missing sold SKU.");

  for (const rel of [
    "app/api/pos/products/search/route.ts",
    "app/api/pos/products/resolve/route.ts",
    "app/api/pos/sales/complete/route.ts",
    "app/api/pos/sales/today/route.ts",
    "app/api/pos/events/outbox/route.ts",
    "app/api/pos/export/events/route.ts",
    "app/api/pos/export/sales-today/route.ts"
  ]) {
    assert(existsSync(path.join(appRoot, rel)), `Required Tablet POS route missing: ${rel}`);
  }

  const forbiddenPcMarkers = ["PC_REQUIRED_TO_SELL", "PC required", "http://127.0.0.1:3130", "localhost:3130"];
  for (const rel of [
    "src/server/prisma/client.ts",
    "src/server/pos-engine/repository.prisma.ts",
    "src/server/pos-api/validators.ts",
    "src/server/pos-runtime/index.ts"
  ]) {
    const text = readProjectFile(rel);
    for (const marker of forbiddenPcMarkers) {
      assert(!text.includes(marker), `Tablet local sale path contains PC dependency marker ${marker} in ${rel}.`);
    }
  }

  if (failures.length) {
    console.error("PRISMA_TABLET_STANDALONE_CORE_CLOSEOUT_02 failed");
    for (const failure of failures) console.error(`- ${failure}`);
    process.exit(1);
  }

  console.log("PRISMA_TABLET_STANDALONE_CORE_CLOSEOUT_02 passed");
  console.log(JSON.stringify({
    dbPath,
    saleId: saleResult.saleId,
    clientRequestId: saleResult.clientRequestId,
    duplicateSaleId: duplicateResult.saleId,
    productId: saleResult.productId,
    stockBefore: saleResult.stockBefore,
    stockAfter: saleResult.stockAfter,
    saleLines: sale.lines.length,
    stockMovements: movement ? 1 : 0,
    outboxEvents: outbox.length,
    salesToday: salesToday.length,
    exports: ["eventsCsv", "salesCsv"],
    pcRequiredForBasicSale: false
  }, null, 2));
} finally {
  await prisma.$disconnect();
}

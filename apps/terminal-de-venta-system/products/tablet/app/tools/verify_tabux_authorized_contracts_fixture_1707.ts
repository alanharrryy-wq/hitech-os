import fs from "node:fs";
import path from "node:path";
import { PrismaClient } from "../.generated/prisma-client";
import { InventoryOperationsRepository } from "../src/server/inventory-operations/repository.prisma";
import { TabletPermissionError } from "../src/server/pos-security/permissions.prisma";
import { PrismaShiftCashRepository } from "../src/server/pos-shift/repository.prisma";

function requiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Required fixture environment variable is missing: ${name}`);
  return value;
}

const tabletDbUrl = requiredEnv("DATABASE_URL");
const reportPath = requiredEnv("TRIAPP_FIXTURE_REPORT_PATH");
const envelopesPath = requiredEnv("TRIAPP_FIXTURE_ENVELOPES_PATH");

const BUSINESS_ID = "fixture-business";
const STORE_ID = "fixture-store";
const TERMINAL_ID = "fixture-terminal";
const ACTOR_ID = "fixture-operator";
const PRODUCT_A = "fixture-product-a";
const PRODUCT_B = "fixture-product-b";
const PURCHASE_ORDER_ID = "fixture-po-1";
const PURCHASE_ORDER_LINE_ID = "fixture-po-line-1";

const tabletDb = new PrismaClient({ datasources: { db: { url: tabletDbUrl } } });
const cashRepository = new PrismaShiftCashRepository(tabletDb);
const inventoryRepository = new InventoryOperationsRepository(tabletDb);

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`ASSERTION_FAILED: ${message}`);
}

async function expectPermissionDenied(run: () => Promise<unknown>) {
  try {
    await run();
  } catch (error) {
    assert(error instanceof TabletPermissionError, "permission denial must use TabletPermissionError");
    assert(error.code === "TABLET_OPERATION_PERMISSION_DENIED", `unexpected permission code ${error.code}`);
    return error.code;
  }
  throw new Error("ASSERTION_FAILED: operation should have been denied");
}

async function seed(db: PrismaClient) {
  await db.business.create({ data: { id: BUSINESS_ID, name: "Fixture Business", currency: "MXN" } });
  await db.store.create({ data: { id: STORE_ID, businessId: BUSINESS_ID, code: "FIX", name: "Fixture Store" } });
  await db.terminal.create({ data: { id: TERMINAL_ID, businessId: BUSINESS_ID, storeId: STORE_ID, code: "TAB-FIX", name: "Fixture Tablet" } });
  await db.product.createMany({
    data: [
      { id: PRODUCT_A, businessId: BUSINESS_ID, sku: "FIX-A", name: "Fixture A", category: "Fixture", priceCents: 1000, costCents: 200, stockOnHand: 10 },
      { id: PRODUCT_B, businessId: BUSINESS_ID, sku: "FIX-B", name: "Fixture B", category: "Fixture", priceCents: 800, costCents: 150, stockOnHand: 4 }
    ]
  });
  await db.user.create({ data: { id: ACTOR_ID, businessId: BUSINESS_ID, displayName: "Fixture Operator", status: "ACTIVE" } });
  await db.permission.createMany({
    data: [
      { id: "fixture-perm-cash", businessId: BUSINESS_ID, code: "cash:adjust", label: "Cash adjust" },
      { id: "fixture-perm-inventory", businessId: BUSINESS_ID, code: "inventory:adjust", label: "Inventory adjust" }
    ]
  });
  await db.role.create({
    data: {
      id: "fixture-role",
      businessId: BUSINESS_ID,
      code: "fixture_supervisor",
      label: "Fixture Supervisor",
      permissions: { connect: [{ id: "fixture-perm-cash" }, { id: "fixture-perm-inventory" }] },
      users: { connect: { id: ACTOR_ID } }
    }
  });
  await db.supplier.create({ data: { id: "fixture-supplier", businessId: BUSINESS_ID, name: "Fixture Supplier" } });
  await db.purchaseOrder.create({
    data: {
      id: PURCHASE_ORDER_ID,
      businessId: BUSINESS_ID,
      supplierId: "fixture-supplier",
      folio: "PO-FIX-001",
      status: "APPROVED",
      createdAt: new Date("2026-07-17T08:00:00.000Z"),
      expectedAt: new Date("2026-07-18T08:00:00.000Z"),
      subtotalCents: 1200,
      taxCents: 192,
      totalCents: 1392
    }
  });
  await db.purchaseOrderLine.create({
    data: {
      id: PURCHASE_ORDER_LINE_ID,
      businessId: BUSINESS_ID,
      purchaseOrderId: PURCHASE_ORDER_ID,
      productId: PRODUCT_A,
      sku: "FIX-A",
      name: "Fixture A",
      qtyOrdered: 6,
      unitCostCents: 200,
      lineSubtotalCents: 1200,
      lineTaxCents: 192,
      lineTotalCents: 1392
    }
  });
}

async function run() {
  await seed(tabletDb);

  const opened = await cashRepository.open({ businessId: BUSINESS_ID, terminalId: TERMINAL_ID, cashierId: ACTOR_ID, cashier: "Fixture Operator", cashStartCents: 10000 });
  assert(opened.status === "OPEN", "cash shift must open");
  const cashInInput = { businessId: BUSINESS_ID, terminalId: TERMINAL_ID, actorId: ACTOR_ID, clientRequestId: "fixture-cash-in-001", movement: "CASH_IN" as const, amountCents: 5000, reason: "Fondo adicional autorizado" };
  const cashIn = await cashRepository.recordMovement(cashInInput);
  const cashInReplay = await cashRepository.recordMovement(cashInInput);
  assert(!cashIn.movement.deduplicated && cashInReplay.movement.deduplicated, "cash replay must deduplicate");
  const cashOut = await cashRepository.recordMovement({ businessId: BUSINESS_ID, terminalId: TERMINAL_ID, actorId: ACTOR_ID, clientRequestId: "fixture-cash-out-001", movement: "CASH_OUT", amountCents: 1200, reason: "Retiro operativo autorizado" });
  assert(cashOut.shift.expectedCashCents === 13800, "cash balance must include signed movements");

  const adjustInput = { action: "adjust" as const, businessId: BUSINESS_ID, terminalId: TERMINAL_ID, actorId: ACTOR_ID, clientRequestId: "fixture-adjust-001", location: "tablet-floor", productId: PRODUCT_A, targetQty: 12, reason: "Ajuste por conteo de anaquel" };
  const adjusted = await inventoryRepository.execute(adjustInput);
  const adjustedReplay = await inventoryRepository.execute(adjustInput);
  assert(!adjusted.deduplicated && adjustedReplay.deduplicated, "adjust replay must deduplicate");

  const countInput = { action: "count" as const, businessId: BUSINESS_ID, terminalId: TERMINAL_ID, actorId: ACTOR_ID, clientRequestId: "fixture-count-001", location: "tablet-floor", lines: [{ productId: PRODUCT_A, countedQty: 11 }, { productId: PRODUCT_B, countedQty: 4 }], reason: "Conteo físico de cierre" };
  const counted = await inventoryRepository.execute(countInput);
  const countedReplay = await inventoryRepository.execute(countInput);
  assert(!counted.deduplicated && countedReplay.deduplicated, "count replay must deduplicate");

  const receiveInput = { action: "receive" as const, businessId: BUSINESS_ID, terminalId: TERMINAL_ID, actorId: ACTOR_ID, clientRequestId: "fixture-receive-001", location: "tablet-floor", purchaseOrderId: PURCHASE_ORDER_ID, lines: [{ purchaseOrderLineId: PURCHASE_ORDER_LINE_ID, qtyReceived: 3 }], reference: "REM-FIX-001" };
  const received = await inventoryRepository.execute(receiveInput);
  const receivedReplay = await inventoryRepository.execute(receiveInput);
  assert(!received.deduplicated && receivedReplay.deduplicated, "receipt replay must deduplicate");

  const productA = await tabletDb.product.findUniqueOrThrow({ where: { id: PRODUCT_A } });
  const tabletCounts = {
    cashMovements: await tabletDb.cashMovement.count(),
    cashAdjustments: await tabletDb.cashAdjustment.count(),
    stockMovements: await tabletDb.stockMovement.count(),
    auditCounts: await tabletDb.auditCount.count(),
    goodsReceipts: await tabletDb.goodsReceipt.count(),
    auditEvents: await tabletDb.auditEvent.count(),
    outboxEvents: await tabletDb.outboxEvent.count()
  };
  assert(productA.stockOnHand === 14, `Tablet stock must end at 14, got ${productA.stockOnHand}`);
  assert(tabletCounts.cashMovements === 3 && tabletCounts.cashAdjustments === 2, "cash rows must be exact");
  assert(tabletCounts.stockMovements === 3 && tabletCounts.auditCounts === 1 && tabletCounts.goodsReceipts === 1, "inventory rows must be exact");
  assert(tabletCounts.auditEvents === 5 && tabletCounts.outboxEvents === 9, "audit and outbox rows must be exact");

  const outboxRows = await tabletDb.outboxEvent.findMany({ orderBy: { createdAt: "asc" } });
  const envelopes = outboxRows.map((row) => JSON.parse(row.payloadJson)).sort((left, right) => left.sequence - right.sequence);
  fs.mkdirSync(path.dirname(envelopesPath), { recursive: true });
  fs.writeFileSync(envelopesPath, `${JSON.stringify({ schemaVersion: "tabux.triapp-fixture-envelopes.v1", envelopes }, null, 2)}\n`, "utf8");

  await tabletDb.role.update({ where: { id: "fixture-role" }, data: { permissions: { set: [] } } });
  const cashReplayDenied = await expectPermissionDenied(() => cashRepository.recordMovement(cashInInput));
  const inventoryReplayDenied = await expectPermissionDenied(() => inventoryRepository.execute(adjustInput));
  assert(await tabletDb.cashMovement.count() === 3 && await tabletDb.stockMovement.count() === 3, "denied replay must not mutate data");

  const tabletIntegrity = await tabletDb.$queryRawUnsafe<Array<Record<string, unknown>>>("PRAGMA integrity_check");
  const tabletForeignKeys = await tabletDb.$queryRawUnsafe<Array<Record<string, unknown>>>("PRAGMA foreign_key_check");
  assert(String(Object.values(tabletIntegrity[0] ?? {})[0]).toLowerCase() === "ok", "Tablet fixture integrity_check must be ok");
  assert(tabletForeignKeys.length === 0, "Tablet fixture foreign_key_check must be empty");

  const report = {
    schemaVersion: "tabux.authorized-contract-fixture.v1",
    generatedAt: new Date().toISOString(),
    status: "PASS",
    liveDataTouched: false,
    tablet: {
      databaseUrl: "isolated-fixture-redacted",
      productAStockOnHand: productA.stockOnHand,
      counts: tabletCounts,
      idempotency: { cash: cashInReplay.movement.deduplicated, adjust: adjustedReplay.deduplicated, count: countedReplay.deduplicated, receive: receivedReplay.deduplicated },
      permissionReplayDenied: { cash: cashReplayDenied, inventory: inventoryReplayDenied },
      outboxTopics: envelopes.map((envelope) => envelope.topic),
      integrityCheck: tabletIntegrity,
      foreignKeyViolations: tabletForeignKeys
    }
  };
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(`TABUX_AUTHORIZED_CONTRACT_FIXTURE_PASS events=${envelopes.length} tabletStock=${productA.stockOnHand}`);
}

run()
  .finally(async () => {
    await tabletDb.$disconnect();
  })
  .catch((error) => {
    console.error(error);
    throw error;
  });

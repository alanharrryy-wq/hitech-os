import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const tabletAppRoot = process.cwd();
const output = process.env.SYNC_SENTINEL_OUTPUT;
const token = process.env.SYNC_SENTINEL_TOKEN;
const origin = process.env.PRISMA_TABLET_PC_ORIGIN;
if (!output || !token || !origin) throw new Error("SYNC_SENTINEL_TABLET_ENV_MISSING");

const importFile = async (rel: string) => import(pathToFileURL(path.join(tabletAppRoot, rel)).href);
const [{ prisma }, { dispatchTabletOutboxOnce }, { pullCatalogDeltaFromPc }] = await Promise.all([
  importFile("src/server/prisma/client.ts"),
  importFile("src/server/sync/dispatcher.ts"),
  importFile("src/server/sync/catalog-pull.ts"),
]);

const ids = {
  tenantId: "tenant_sync_sentinel", customerId: "customer_sync_sentinel", businessId: "biz_sync_sentinel", storeId: "store_sync_sentinel", terminalId: "terminal_sync_sentinel", deviceId: "device_sync_sentinel", taxRateId: "tax_sync_sentinel", brandId: "brand_sync_sentinel", productId: "product_sync_sentinel", eventId: "event_sync_sentinel_sale_completed", saleId: "sale_sync_sentinel",
};
function assert(condition: unknown, message: string): asserts condition { if (!condition) throw new Error(`ASSERT:${message}`); }
function iso(value: unknown) { if (!value) return null; const date = value instanceof Date ? value : new Date(String(value)); return Number.isNaN(date.getTime()) ? null : date.toISOString(); }

async function seedTabletForJourneyA() {
  await prisma.business.upsert({ where: { id: ids.businessId }, update: { name: "Sync Sentinel Tablet" }, create: { id: ids.businessId, name: "Sync Sentinel Tablet", currency: "MXN" } });
  await prisma.store.upsert({ where: { businessId_code: { businessId: ids.businessId, code: "SENT" } }, update: { name: "Sentinel Store" }, create: { id: ids.storeId, businessId: ids.businessId, code: "SENT", name: "Sentinel Store" } });
  await prisma.terminal.upsert({ where: { businessId_code: { businessId: ids.businessId, code: "SENT-TAB" } }, update: { storeId: ids.storeId, name: "Sentinel Tablet", isActive: true }, create: { id: ids.terminalId, businessId: ids.businessId, storeId: ids.storeId, code: "SENT-TAB", name: "Sentinel Tablet", isActive: true } });
  await prisma.taxRate.upsert({ where: { id: ids.taxRateId }, update: { name: "IVA Sentinel", rateBps: 1600, isDefault: true, isActive: true }, create: { id: ids.taxRateId, businessId: ids.businessId, name: "IVA Sentinel", rateBps: 1600, isDefault: true, isActive: true } });
  await prisma.brand.upsert({ where: { id: ids.brandId }, update: { name: "Sentinel Brand", status: "ACTIVE" }, create: { id: ids.brandId, businessId: ids.businessId, name: "Sentinel Brand", description: "Synthetic certification brand", status: "ACTIVE" } });
  await prisma.product.upsert({ where: { id: ids.productId }, update: { sku: "SYNC-SENTINEL-001", name: "Sentinel Product local", category: "SENTINEL", brandId: ids.brandId, taxRateId: ids.taxRateId, priceCents: 1234, costCents: 700, stockOnHand: 80, isActive: true }, create: { id: ids.productId, businessId: ids.businessId, sku: "SYNC-SENTINEL-001", name: "Sentinel Product local", category: "SENTINEL", brandId: ids.brandId, taxRateId: ids.taxRateId, priceCents: 1234, costCents: 700, stockOnHand: 80, isActive: true } });
}

function saleEvent(occurredAt: string) {
  return {
    eventId: ids.eventId, eventType: "sale.completed", topic: "sale.completed", schemaVersion: "1.1.0", eventVersion: "1.0.0", tenantId: ids.tenantId, customerId: ids.customerId, businessId: ids.businessId, storeId: ids.storeId, terminalId: ids.terminalId, deviceId: ids.deviceId, actorId: "sync-sentinel-operator", aggregateId: ids.saleId, originRecordId: ids.saleId, idempotencyKey: "idem_sync_sentinel_sale_completed", correlationId: "corr_sync_sentinel_sale", causationId: "cause_sync_sentinel_sale", traceId: "trace_sync_sentinel_sale", source: "tablet-pos", occurredAt,
    payload: { saleId: ids.saleId, folio: "SYNC-SENTINEL-SALE", cashier: "Sync Sentinel", totalCents: 1234, subtotalCents: 1234, discountCents: 0, paymentMethod: "cash", cashReceivedCents: 1234, changeCents: 0, status: "COMPLETED", createdAt: occurredAt, completedAt: occurredAt, syntheticTestData: true, lines: [{ id: "line_sync_sentinel", productId: ids.productId, sku: "SYNC-SENTINEL-001", productName: "Sentinel Product", qty: 1, priceCents: 1234, unitPriceCents: 1234, totalCents: 1234 }], tenders: [{ id: "tender_sync_sentinel", tenderType: "cash", amountCents: 1234, reference: "SYNC-SENTINEL-SALE" }] },
  };
}

const config = { enabled: true, origin, ingestPath: "/api/backoffice/sync/ingest", healthPath: "/api/health", timeoutMs: 5000, automaticDispatch: false, ackStrict: true, batchSize: 10, maxAttempts: 3 };

async function journeyA() {
  await seedTabletForJourneyA();
  const occurredAt = new Date().toISOString();
  const event = saleEvent(occurredAt);
  await prisma.outboxEvent.deleteMany({ where: { businessId: ids.businessId, id: ids.eventId } });
  await prisma.outboxEvent.create({ data: { id: ids.eventId, businessId: ids.businessId, terminalId: ids.terminalId, topic: "sale.completed", aggregateId: ids.saleId, idempotencyKey: event.idempotencyKey, payloadJson: JSON.stringify(event), source: "tablet-pos", schemaVersion: "1.1.0", status: "pending", createdAt: new Date(occurredAt) } });
  const dispatch = await dispatchTabletOutboxOnce(config, { force: true });
  const outbox = await prisma.outboxEvent.findUnique({ where: { id: ids.eventId } });
  assert(dispatch.ok === true, `Journey A dispatcher did not return ok: ${JSON.stringify(dispatch)}`);
  assert(outbox?.status === "acked", `Journey A Tablet outbox not acked: ${JSON.stringify(outbox)}`);
  assert(["projected", "reconciled", "recognized_not_projected", "duplicate"].includes(String(outbox.remoteLifecycleStatus)), `Journey A remote lifecycle unexpected: ${outbox?.remoteLifecycleStatus}`);
  const stateResp = await fetch(`${origin}/__sentinel/state?eventId=${encodeURIComponent(ids.eventId)}`, { headers: { "x-sync-sentinel-token": token } });
  const state = await stateResp.json();
  assert(stateResp.ok && state?.sale?.id === ids.saleId, `Journey A PC sale projection missing: ${JSON.stringify(state)}`);
  assert(Array.isArray(state.sale.lines) && state.sale.lines.length === 1, "Journey A PC SaleLine projection missing");
  assert(Array.isArray(state.sale.paymentTenders) && state.sale.paymentTenders.length >= 1, "Journey A PC payment tender projection missing");
  assert(state?.event?.payloadJson, "Journey A PC canonical ledger payload missing");
  const canonical = JSON.parse(state.event.payloadJson);
  assert(canonical.eventId === ids.eventId && canonical.idempotencyKey === event.idempotencyKey, "Journey A canonical identity mismatch");
  assert(canonical.tenantId === ids.tenantId && canonical.businessId === ids.businessId && canonical.storeId === ids.storeId && canonical.terminalId === ids.terminalId && canonical.deviceId === ids.deviceId, "Journey A canonical scope mismatch");
  assert(typeof canonical.payloadHash === "string" && canonical.payloadHash.length === 64 && typeof canonical.batchChecksum === "string" && canonical.batchChecksum.length === 64, "Journey A integrity hashes missing");
  assert(state.sale.totalCents === event.payload.totalCents && state.sale.lines.length === event.payload.lines.length, "Journey A persisted canonical equality failed");
  return {
    dispatch,
    identity: { eventId: canonical.eventId, idempotencyKey: canonical.idempotencyKey, sequence: canonical.sequence, payloadHash: canonical.payloadHash, batchId: canonical.batchId, batchChecksum: canonical.batchChecksum },
    scope: { tenantId: canonical.tenantId, customerId: canonical.customerId ?? null, businessId: canonical.businessId, storeId: canonical.storeId, terminalId: canonical.terminalId, deviceId: canonical.deviceId },
    tabletOutbox: { status: outbox.status, attempts: outbox.attempts, lastAttemptAt: iso(outbox.lastAttemptAt), syncedAt: iso(outbox.syncedAt), ackedAt: iso(outbox.ackedAt), remoteLifecycleStatus: outbox.remoteLifecycleStatus, remoteEventId: outbox.remoteEventId },
    pcLedger: { lifecycleStatus: state.event.lifecycleStatus, receivedAt: iso(state.event.receivedAt), validatedAt: iso(state.event.validatedAt), acceptedAt: iso(state.event.acceptedAt), projectedAt: iso(state.event.projectedAt), reconciledAt: iso(state.event.reconciledAt) },
    pcSale: { id: state.sale.id, totalCents: state.sale.totalCents, lines: state.sale.lines.length, tenders: state.sale.paymentTenders.length },
    persistedCanonicalEquality: true,
  };
}

async function journeyB() {
  const bootstrap = await pullCatalogDeltaFromPc({ mode: "bootstrap", resetCheckpoint: true, pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, requestedBy: "sync-sentinel", config });
  assert(bootstrap.ok === true, `Journey B bootstrap failed: ${JSON.stringify(bootstrap)}`);
  const afterBootstrap = await prisma.product.findUnique({ where: { id: ids.productId } });
  assert(afterBootstrap?.name === "Sentinel Product v1", `Journey B bootstrap product name mismatch: ${afterBootstrap?.name}`);
  const cursor1 = bootstrap.cursorAfter;
  assert(Boolean(cursor1), "Journey B bootstrap checkpoint/cursor did not advance");
  await prisma.product.update({ where: { id: ids.productId }, data: { stockOnHand: 17 } });
  await new Promise((resolve) => setTimeout(resolve, 30));
  const mutateResp = await fetch(`${origin}/__sentinel/catalog-mutation`, { method: "POST", headers: { "content-type": "application/json", "x-sync-sentinel-token": token }, body: JSON.stringify({ name: "Sentinel Product v2", priceCents: 1777, stockOnHand: 999 }) });
  const mutated = await mutateResp.json();
  assert(mutateResp.ok && mutated?.product?.stockOnHand === 999, `Journey B PC synthetic mutation failed: ${JSON.stringify(mutated)}`);
  await new Promise((resolve) => setTimeout(resolve, 30));
  const delta = await pullCatalogDeltaFromPc({ mode: "delta", pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, requestedBy: "sync-sentinel", config });
  assert(delta.ok === true, `Journey B delta failed: ${JSON.stringify(delta)}`);
  const finalProduct = await prisma.product.findUnique({ where: { id: ids.productId } });
  assert(finalProduct?.name === "Sentinel Product v2", `Journey B non-stock field did not advance: ${finalProduct?.name}`);
  assert(finalProduct?.priceCents === 1777, `Journey B price did not advance: ${finalProduct?.priceCents}`);
  assert(finalProduct?.stockOnHand === 17, `Journey B local stock was overwritten: ${finalProduct?.stockOnHand}`);
  assert(Boolean(delta.cursorAfter) && delta.cursorAfter !== cursor1, `Journey B delta checkpoint did not advance: ${cursor1} -> ${delta.cursorAfter}`);
  return {
    scope: { sourceBusinessId: ids.businessId, targetBusinessId: ids.businessId, storeId: ids.storeId, terminalId: ids.terminalId },
    bootstrap: { reason: bootstrap.reason, counts: bootstrap.counts, cursorBefore: bootstrap.cursorBefore, cursorAfter: cursor1, checkpointStatus: bootstrap.checkpoint?.status, checkpointLifecycle: bootstrap.checkpoint?.lifecycleStatus },
    delta: { reason: delta.reason, counts: delta.counts, cursorBefore: delta.cursorBefore, cursorAfter: delta.cursorAfter, checkpointStatus: delta.checkpoint?.status, checkpointLifecycle: delta.checkpoint?.lifecycleStatus },
    finalProduct: { id: finalProduct.id, name: finalProduct.name, priceCents: finalProduct.priceCents, stockOnHand: finalProduct.stockOnHand },
    stockInvariant: { pcAdvertisedStock: 999, tabletLocalStockBeforeDelta: 17, tabletLocalStockAfterDelta: finalProduct.stockOnHand },
  };
}

const result: any = { schemaVersion: "prisma.sync-sentinel.journeys.v2", startedAt: new Date().toISOString(), productionCertified: false };
try {
  result.journeyA = await journeyA(); console.log("PASS_SYNC_JOURNEY_A");
  result.journeyB = await journeyB(); console.log("PASS_SYNC_JOURNEY_B");
  const negativeOutput = path.join(path.dirname(output), "negative-fixtures.json");
  process.env.SYNC_SENTINEL_NEGATIVE_OUTPUT = negativeOutput;
  const negativeRunner = path.join(tabletAppRoot, "../../../../../tools/prisma-sentinels/sync-sentinel/sync_sentinel/adapters/negative_runner.mts");
  await import(pathToFileURL(negativeRunner).href);
  const negative = JSON.parse(fs.readFileSync(negativeOutput, "utf8"));
  result.negativeFixtures = negative;
  assert(negative.ok === true, `negative fixture suite failed: ${JSON.stringify(negative.failures ?? [])}`);
  for (const letter of "ABCDEFGHIJKL") assert(negative.fixtures?.[letter]?.status === "PASS", `negative fixture ${letter} did not PASS`);
  result.ok = true;
} catch (error) {
  result.ok = false; result.error = error instanceof Error ? error.message : String(error); console.error(result.error); process.exitCode = 1;
} finally {
  result.finishedAt = new Date().toISOString();
  result.durationMs = Date.parse(result.finishedAt) - Date.parse(result.startedAt);
  fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, JSON.stringify(result, null, 2), "utf8"); await prisma.$disconnect();
}

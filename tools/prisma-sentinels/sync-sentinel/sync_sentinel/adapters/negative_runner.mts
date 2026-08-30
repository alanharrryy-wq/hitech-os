import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const tabletAppRoot = process.cwd();
const output = process.env.SYNC_SENTINEL_NEGATIVE_OUTPUT;
const token = process.env.SYNC_SENTINEL_TOKEN;
const origin = process.env.PRISMA_TABLET_PC_ORIGIN;
if (!output || !token || !origin) throw new Error("SYNC_SENTINEL_NEGATIVE_ENV_MISSING");

const importFile = async (rel: string) => import(pathToFileURL(path.join(tabletAppRoot, rel)).href);
const [
  { prisma },
  { dispatchTabletOutboxOnce },
  { applyCatalogDeltaEnvelope, getTabletCatalogPullStatus },
  { syncPayloadFingerprint },
  catalogContract,
] = await Promise.all([
  importFile("src/server/prisma/client.ts"),
  importFile("src/server/sync/dispatcher.ts"),
  importFile("src/server/sync/catalog-pull.ts"),
  importFile("../../pc/app/src/server/validators/sync-event-contract.ts"),
  importFile("../../../shared/twin-kernel/src/sync/catalog-delta.ts"),
]);

const { CATALOG_DELTA_CONTRACT_ID, CATALOG_DELTA_SCHEMA_VERSION, CATALOG_DELTA_STREAM } = catalogContract as any;
const ids = {
  tenantId: "tenant_sync_sentinel", customerId: "customer_sync_sentinel", businessId: "biz_sync_sentinel", storeId: "store_sync_sentinel", terminalId: "terminal_sync_sentinel", deviceId: "device_sync_sentinel", taxRateId: "tax_sync_sentinel", productId: "product_sync_sentinel", eventId: "event_sync_sentinel_sale_completed",
};
const config = { enabled: true, origin, ingestPath: "/api/backoffice/sync/ingest", healthPath: "/api/health", timeoutMs: 5000, automaticDispatch: false, ackStrict: true, batchSize: 10, maxAttempts: 3 };
function assert(condition: unknown, message: string): asserts condition { if (!condition) throw new Error(`ASSERT:${message}`); }
function iso(value: unknown) { if (!value) return null; const date = value instanceof Date ? value : new Date(String(value)); return Number.isNaN(date.getTime()) ? null : date.toISOString(); }

async function jsonRequest(url: string, init: RequestInit = {}) {
  const response = await fetch(url, init);
  const payload = await response.json().catch(() => null);
  return { response, payload };
}
async function controlPost(pathname: string, body: unknown) {
  const { response, payload } = await jsonRequest(`${origin}${pathname}`, { method: "POST", headers: { "content-type": "application/json", "x-sync-sentinel-token": token }, body: JSON.stringify(body) });
  assert(response.ok, `control POST ${pathname} failed HTTP ${response.status}: ${JSON.stringify(payload)}`);
  return payload as any;
}
async function pcState(eventId?: string) {
  const suffix = eventId ? `?eventId=${encodeURIComponent(eventId)}` : "";
  const { response, payload } = await jsonRequest(`${origin}/__sentinel/state${suffix}`, { headers: { "x-sync-sentinel-token": token } });
  assert(response.ok, `PC state failed HTTP ${response.status}: ${JSON.stringify(payload)}`);
  return payload as any;
}
async function postIngest(batch: any) {
  const { response, payload } = await jsonRequest(`${origin}/api/backoffice/sync/ingest`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(batch) });
  assert(response.status >= 200 && response.status < 300, `ingest HTTP ${response.status}: ${JSON.stringify(payload)}`);
  return { httpStatus: response.status, body: payload as any, classification: (payload as any)?.data ?? payload };
}
function refreshBatch(event: any) {
  const batchId = String(event.batchId || `batch_sync_sentinel_${event.eventId}`);
  event.batchId = batchId;
  const batchChecksum = syncPayloadFingerprint([{ eventId: event.eventId, payloadHash: event.payloadHash, sequence: event.sequence }]);
  event.batchChecksum = batchChecksum;
  return { batchId, batchChecksum, source: { app: "sync-sentinel", role: "fixture", capability: "sync-negative-certification" }, createdAt: new Date().toISOString(), events: [event] };
}
function saleFixtureEvent(base: any, suffix: string, idempotencyKey: string, sequenceOffset: number) {
  const event = structuredClone(base);
  const now = new Date().toISOString();
  const saleId = `sale_sync_sentinel_${suffix}`;
  event.eventId = `event_sync_sentinel_${suffix}`;
  event.idempotencyKey = idempotencyKey;
  event.aggregateId = saleId;
  event.originRecordId = saleId;
  event.correlationId = `corr_sync_sentinel_${suffix}`;
  event.causationId = `cause_sync_sentinel_${suffix}`;
  event.traceId = `trace_sync_sentinel_${suffix}`;
  event.occurredAt = now;
  event.capturedAt = now;
  event.sequence = Number(base.sequence) + sequenceOffset;
  event.subject = `prisma://sync/${ids.tenantId}/${ids.businessId}/${ids.storeId}/${ids.terminalId}/${ids.deviceId}/sale.completed/${saleId}`;
  event.payload = { ...structuredClone(base.payload), saleId, folio: `SYNC-SENTINEL-${suffix.toUpperCase()}`, createdAt: now, completedAt: now, syntheticTestData: true };
  event.payloadHash = syncPayloadFingerprint(event.payload);
  event.batchId = `batch_sync_sentinel_${suffix}`;
  return { event, batch: refreshBatch(event), saleId };
}
function classificationResult(input: any) { return input?.classification?.results?.[0] ?? null; }

const result: any = { schemaVersion: "prisma.sync-sentinel.negative-fixtures.v1", startedAt: new Date().toISOString(), productionCertified: false, fixtures: {} };
const failures: string[] = [];
async function runFixture(letter: string, fixtureId: string, faultZone: string, causal: { after: string; before: string }, fn: () => Promise<any>) {
  const startedAt = Date.now();
  try {
    const evidence = await fn();
    result.fixtures[letter] = { fixtureId, status: "PASS", faultZone, causal, durationMs: Date.now() - startedAt, evidence };
    console.log(`PASS_SYNC_NEG_${letter}`);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    failures.push(`${letter}:${detail}`);
    result.fixtures[letter] = { fixtureId, status: "FAIL", faultZone, causal, durationMs: Date.now() - startedAt, error: detail };
    console.error(`FAIL_SYNC_NEG_${letter} ${detail}`);
  }
}

async function main() {
  const baseState = await pcState(ids.eventId);
  assert(baseState?.event?.payloadJson, "Journey A PC ledger is required before negative fixtures");
  const baseEvent = JSON.parse(baseState.event.payloadJson);
  assert(baseEvent.eventId === ids.eventId, "Journey A canonical event identity mismatch");
  const baseSaleCount = Number(baseState.saleCount ?? 0);

  await runFixture("A", "SYNC.NEG.A.DUPLICATE_EVENT.V1", "IDEMPOTENCY", { after: "Journey A canonical projection and PC ledger persistence", before: "any second canonical projection" }, async () => {
    const replay = await postIngest({ batchId: baseEvent.batchId, batchChecksum: baseEvent.batchChecksum, events: [baseEvent] });
    const item = classificationResult(replay);
    const after = await pcState(ids.eventId);
    assert(item?.status === "duplicate", `expected duplicate, got ${JSON.stringify(item)}`);
    assert(Number(after.saleCount ?? -1) === baseSaleCount, "duplicate replay changed canonical sale count");
    const tablet = await prisma.outboxEvent.findUnique({ where: { id: ids.eventId } });
    assert(tablet?.status === "acked", "duplicate replay regressed Tablet final ACK");
    return { assertions: { duplicateExplicit: true, sameEventNotReprojected: true, tabletFinalAcked: true }, eventId: baseEvent.eventId, idempotencyKey: baseEvent.idempotencyKey, pcStatus: item.status, saleCountBefore: baseSaleCount, saleCountAfter: Number(after.saleCount) };
  });

  await runFixture("B", "SYNC.NEG.B.IDEMPOTENCY_PAYLOAD_CONFLICT.V1", "IDEMPOTENCY", { after: "existing businessId + idempotencyKey ledger resolution", before: "projection of a different payload" }, async () => {
    const fixture = saleFixtureEvent(baseEvent, "idem_conflict", baseEvent.idempotencyKey, 10);
    const before = Number((await pcState()).saleCount ?? 0);
    const ingest = await postIngest(fixture.batch);
    const item = classificationResult(ingest);
    const after = Number((await pcState()).saleCount ?? 0);
    assert(item?.status === "conflict", `expected conflict, got ${JSON.stringify(item)}`);
    assert(item?.conflicts?.some((x: any) => x?.code === "idempotency_payload_mismatch"), "missing idempotency_payload_mismatch");
    assert(after === before, "idempotency conflict projected a second sale");
    return { assertions: { sameIdempotencyKeyDetected: true, differentPayloadDetected: true, conflictEvidencePreserved: true, noAutoRetry: true }, status: item.status, conflictCode: item.conflicts?.[0]?.code, saleCountBefore: before, saleCountAfter: after };
  });

  await runFixture("C", "SYNC.NEG.C.BAD_PAYLOAD_HASH.V1", "CONTRACT_VALIDATION", { after: "PC ingest received the event", before: "canonical projector execution" }, async () => {
    const fixture = saleFixtureEvent(baseEvent, "bad_payload_hash", "idem_sync_sentinel_bad_payload_hash", 20);
    fixture.event.payloadHash = "0".repeat(64);
    fixture.batch = refreshBatch(fixture.event);
    const before = Number((await pcState()).saleCount ?? 0);
    const ingest = await postIngest(fixture.batch);
    const item = classificationResult(ingest);
    const after = Number((await pcState()).saleCount ?? 0);
    assert(item?.status === "rejected", `expected rejected payload hash, got ${JSON.stringify(item)}`);
    assert(item?.conflicts?.some((x: any) => x?.code === "payload_hash_mismatch"), "payload_hash_mismatch not explicit");
    assert(after === before, "bad payload hash reached sale projection");
    return { assertions: { payloadHashRejected: true, noProjection: true, rejectionEvidencePreserved: true }, status: item.status, conflictCode: item.conflicts?.[0]?.code };
  });

  await runFixture("D", "SYNC.NEG.D.BAD_BATCH_CHECKSUM.V1", "CONTRACT_VALIDATION", { after: "PC ingest extracted the batch", before: "per-event contract/projector processing" }, async () => {
    const fixture = saleFixtureEvent(baseEvent, "bad_batch_checksum", "idem_sync_sentinel_bad_batch_checksum", 30);
    const bad = "f".repeat(64);
    fixture.event.batchChecksum = bad;
    fixture.batch.batchChecksum = bad;
    fixture.batch.events = [fixture.event];
    const before = Number((await pcState()).saleCount ?? 0);
    const ingest = await postIngest(fixture.batch);
    const item = classificationResult(ingest);
    const after = Number((await pcState()).saleCount ?? 0);
    assert(item?.status === "rejected", `expected batch rejection, got ${JSON.stringify(item)}`);
    assert(item?.conflicts?.some((x: any) => x?.code === "batch_checksum_mismatch"), "batch_checksum_mismatch not explicit");
    assert(after === before, "bad batch checksum reached projection");
    return { assertions: { batchChecksumRejected: true, noProjection: true }, status: item.status, conflictCode: item.conflicts?.[0]?.code };
  });

  await runFixture("E", "SYNC.NEG.E.WRONG_SCOPE.V1", "SCOPE", { after: "canonical envelope parsing", before: "cross-scope persistence or projection" }, async () => {
    await controlPost("/__sentinel/expected-scope", { tenantId: ids.tenantId, customerId: ids.customerId });
    const fixture = saleFixtureEvent(baseEvent, "wrong_scope", "idem_sync_sentinel_wrong_scope", 40);
    fixture.event.tenantId = "tenant_sync_sentinel_wrong";
    const before = Number((await pcState()).saleCount ?? 0);
    const ingest = await postIngest(fixture.batch);
    const item = classificationResult(ingest);
    const after = Number((await pcState()).saleCount ?? 0);
    assert(item?.status === "rejected" || item?.status === "conflict", `expected scope rejection/conflict, got ${JSON.stringify(item)}`);
    assert(item?.conflicts?.some((x: any) => x?.code === "wrong_scope"), "wrong_scope not explicit");
    assert(after === before, "wrong-scope event changed canonical sale count");
    return { assertions: { scopeMismatchExplicit: true, noCrossScopeProjection: true }, status: item.status, conflictCode: item.conflicts?.[0]?.code };
  });

  const recovery = saleFixtureEvent(baseEvent, "recovery", "idem_sync_sentinel_recovery", 100);
  await prisma.outboxEvent.deleteMany({ where: { id: recovery.event.eventId } });
  await prisma.outboxEvent.create({ data: { id: recovery.event.eventId, businessId: ids.businessId, terminalId: ids.terminalId, topic: "sale.completed", aggregateId: recovery.saleId, idempotencyKey: recovery.event.idempotencyKey, payloadJson: JSON.stringify(recovery.event), source: "tablet-pos", schemaVersion: "1.1.0", status: "pending", createdAt: new Date() } });

  await runFixture("F", "SYNC.NEG.F.PC_UNAVAILABLE.V1", "NETWORK", { after: "Tablet local operation and Outbox persistence", before: "remote ACK" }, async () => {
    await controlPost("/__sentinel/fault", { mode: "ingest_unavailable" });
    await prisma.product.update({ where: { id: ids.productId }, data: { stockOnHand: 16 } });
    const dispatch = await dispatchTabletOutboxOnce(config, { force: true });
    const row = await prisma.outboxEvent.findUnique({ where: { id: recovery.event.eventId } });
    const product = await prisma.product.findUnique({ where: { id: ids.productId } });
    assert(dispatch.ok === false && dispatch.reason === "dispatch_failed", `expected network dispatch failure: ${JSON.stringify(dispatch)}`);
    assert(row?.status === "pending", `outbox must remain pending/retryable: ${JSON.stringify(row)}`);
    assert(Number(row?.attempts) === 1 && Boolean(row?.nextRetryAt), "retryable attempt provenance missing");
    assert(!row?.ackedAt, "fake ACK was persisted while PC ingest unavailable");
    assert(product?.stockOnHand === 16, "Tablet local operation did not survive PC outage");
    return { assertions: { tabletContinues: true, noFakeAck: true, retryableStatePersisted: true }, dispatch, outbox: { status: row.status, attempts: row.attempts, nextRetryAt: iso(row.nextRetryAt), ackedAt: iso(row.ackedAt) }, localStock: product.stockOnHand };
  });

  let retrySnapshot: any = null;
  await runFixture("G", "SYNC.NEG.G.RETRY_PROVENANCE.V1", "TABLET_DISPATCHER", { after: "first retryable network failure", before: "remote recovery" }, async () => {
    const before = await prisma.outboxEvent.findUnique({ where: { id: recovery.event.eventId } });
    await new Promise((resolve) => setTimeout(resolve, 20));
    const dispatch = await dispatchTabletOutboxOnce(config, { force: true });
    const after = await prisma.outboxEvent.findUnique({ where: { id: recovery.event.eventId } });
    assert(dispatch.ok === false && dispatch.reason === "dispatch_failed", "second retry should still fail while fault is active");
    assert(Number(after?.attempts) === Number(before?.attempts) + 1, "attempt counter did not increment exactly once");
    assert(String(after?.id) === String(before?.id) && String(after?.idempotencyKey) === String(before?.idempotencyKey), "retry changed event identity");
    assert(Boolean(after?.lastAttemptAt) && iso(after?.lastAttemptAt) !== iso(before?.lastAttemptAt), "lastAttemptAt did not advance");
    retrySnapshot = { attempts: after?.attempts, lastAttemptAt: iso(after?.lastAttemptAt), nextRetryAt: iso(after?.nextRetryAt) };
    return { assertions: { attemptCountIncrements: true, lastAttemptChanges: true, provenancePreserved: true }, eventId: after?.id, idempotencyKey: after?.idempotencyKey, beforeAttempts: before?.attempts, afterAttempts: after?.attempts, lastAttemptBefore: iso(before?.lastAttemptAt), lastAttemptAfter: iso(after?.lastAttemptAt) };
  });

  await runFixture("I", "SYNC.NEG.I.PC_RECOVERY_EVENTUAL_ACK.V1", "NETWORK", { after: "persisted retryable failures with unchanged identity", before: "final Tablet ACK reconciliation" }, async () => {
    await controlPost("/__sentinel/fault", { mode: "online" });
    const before = await prisma.outboxEvent.findUnique({ where: { id: recovery.event.eventId } });
    const dispatch = await dispatchTabletOutboxOnce(config, { force: true });
    const after = await prisma.outboxEvent.findUnique({ where: { id: recovery.event.eventId } });
    const remote = await pcState(recovery.event.eventId);
    assert(dispatch.ok === true, `recovery dispatch did not succeed: ${JSON.stringify(dispatch)}`);
    assert(after?.status === "acked" && Boolean(after?.ackedAt), `eventual ACK missing: ${JSON.stringify(after)}`);
    assert(String(after?.id) === recovery.event.eventId && String(after?.idempotencyKey) === recovery.event.idempotencyKey, "recovery changed identity");
    assert(remote?.event?.id === recovery.event.eventId, "PC ledger missing recovered event");
    return { assertions: { initialFailureNoAck: true, pcRecovers: true, retrySucceeds: true, finalOutboxAcked: true }, retrySnapshot, attemptsBeforeRecovery: before?.attempts, dispatch, tablet: { status: after.status, ackedAt: iso(after.ackedAt), remoteLifecycleStatus: after.remoteLifecycleStatus }, pc: { lifecycleStatus: remote.event.lifecycleStatus, receivedAt: iso(remote.event.receivedAt), reconciledAt: iso(remote.event.reconciledAt) } };
  });

  await runFixture("H", "SYNC.NEG.H.CONFLICT_NO_RETRY.V1", "IDEMPOTENCY", { after: "PC returns terminal idempotency conflict", before: "dispatcher schedules or performs another automatic retry" }, async () => {
    const seed = saleFixtureEvent(baseEvent, "conflict_seed", "idem_sync_sentinel_terminal_conflict", 1000);
    const seedIngest = await postIngest(seed.batch);
    assert(classificationResult(seedIngest)?.status === "accepted", `conflict seed was not accepted: ${JSON.stringify(seedIngest)}`);
    const candidate = saleFixtureEvent(baseEvent, "conflict_tablet", seed.event.idempotencyKey, 1001);
    await prisma.outboxEvent.deleteMany({ where: { id: candidate.event.eventId } });
    await prisma.outboxEvent.create({ data: { id: candidate.event.eventId, businessId: ids.businessId, terminalId: ids.terminalId, topic: "sale.completed", aggregateId: candidate.saleId, idempotencyKey: candidate.event.idempotencyKey, payloadJson: JSON.stringify(candidate.event), source: "tablet-pos", schemaVersion: "1.1.0", status: "pending", createdAt: new Date() } });
    const firstDispatch = await dispatchTabletOutboxOnce(config, { force: true });
    const conflicted = await prisma.outboxEvent.findUnique({ where: { id: candidate.event.eventId } });
    assert(conflicted?.status === "conflict", `Tablet did not preserve terminal conflict: ${JSON.stringify(conflicted)}`);
    assert(conflicted?.remoteConflictCode === "idempotency_payload_mismatch", `unexpected conflict code: ${conflicted?.remoteConflictCode}`);
    assert(conflicted?.nextRetryAt === null, "conflict incorrectly scheduled an automatic retry");
    const snapshot = { attempts: conflicted.attempts, lastAttemptAt: iso(conflicted.lastAttemptAt), status: conflicted.status };
    const secondDispatch = await dispatchTabletOutboxOnce(config, { force: true });
    const after = await prisma.outboxEvent.findUnique({ where: { id: candidate.event.eventId } });
    assert(after?.status === "conflict" && Number(after?.attempts) === Number(snapshot.attempts) && iso(after?.lastAttemptAt) === snapshot.lastAttemptAt, "conflict row was retried or mutated");
    return { assertions: { conflictNotAutoRetried: true, conflictEvidencePreserved: true }, firstDispatch, secondDispatch, conflictCode: after?.remoteConflictCode, before: snapshot, after: { attempts: after?.attempts, lastAttemptAt: iso(after?.lastAttemptAt), status: after?.status } };
  });

  await runFixture("J", "SYNC.NEG.J.DUPLICATE_CATALOG_DELTA.V1", "CHECKPOINT", { after: "first real catalog envelope apply and checkpoint advance", before: "duplicate replay could mutate local state again" }, async () => {
    const beforeStatus = await getTabletCatalogPullStatus({ pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, config });
    const cursorBefore = beforeStatus.checkpoint?.cursorValue ?? null;
    await new Promise((resolve) => setTimeout(resolve, 30));
    await controlPost("/__sentinel/catalog-mutation", { name: "Sentinel Product v3", priceCents: 1888, stockOnHand: 777 });
    await new Promise((resolve) => setTimeout(resolve, 30));
    const exported = await controlPost("/__sentinel/catalog-envelope", { mode: "delta", cursor: cursorBefore, businessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, target: "tablet", targetBusinessId: ids.businessId, limit: 500, requestedBy: "sync-sentinel-negative-j" });
    const envelope = exported?.data;
    assert(envelope && Array.isArray(envelope.changes) && envelope.changes.length > 0, `expected non-empty real PC delta: ${JSON.stringify(exported)}`);
    const first = await applyCatalogDeltaEnvelope(envelope, { mode: "delta", pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, cursor: cursorBefore, config });
    assert(first.ok === true && first.counts.applied > 0, `first real delta apply failed: ${JSON.stringify(first)}`);
    const stockAfterFirst = (await prisma.product.findUnique({ where: { id: ids.productId } }))?.stockOnHand;
    const replay = await applyCatalogDeltaEnvelope(envelope, { mode: "delta", pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, cursor: first.cursorAfter, config });
    const finalProduct = await prisma.product.findUnique({ where: { id: ids.productId } });
    assert(replay.ok === true && replay.counts.applied === 0 && replay.counts.duplicate > 0, `duplicate delta not recognized: ${JSON.stringify(replay)}`);
    assert(replay.cursorAfter === first.cursorAfter, `duplicate replay advanced checkpoint: ${first.cursorAfter} -> ${replay.cursorAfter}`);
    assert(finalProduct?.stockOnHand === stockAfterFirst && finalProduct?.stockOnHand === 16, "duplicate replay changed Tablet local stock");
    return { assertions: { duplicateExplicit: true, checkpointStable: true, localStockPreserved: true }, first: { cursorBefore: first.cursorBefore, cursorAfter: first.cursorAfter, counts: first.counts }, replay: { cursorBefore: replay.cursorBefore, cursorAfter: replay.cursorAfter, counts: replay.counts }, localStock: finalProduct.stockOnHand };
  });

  await runFixture("K", "SYNC.NEG.K.MISSING_CATALOG_DEPENDENCY.V1", "TABLET_CATALOG_PULL", { after: "shared catalog envelope validation", before: "Product upsert with a missing Brand dependency" }, async () => {
    const beforeStatus = await getTabletCatalogPullStatus({ pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, config });
    const cursorBefore = beforeStatus.checkpoint?.cursorValue ?? null;
    const cursor = "9999-12-31T23:59:59.998Z|003|product_sync_sentinel_missing_dependency";
    const occurredAt = new Date().toISOString();
    const entityId = "product_sync_sentinel_missing_dependency";
    const envelope = { contractId: CATALOG_DELTA_CONTRACT_ID, schemaVersion: CATALOG_DELTA_SCHEMA_VERSION, stream: CATALOG_DELTA_STREAM, mode: "delta", businessId: ids.businessId, generatedAt: occurredAt, scope: { businessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, target: "tablet" }, cursor: { requested: cursorBefore, from: cursorBefore, to: cursor, hasMore: false, checkpointStrategy: "updatedAt_entityRank_id" }, changes: [{ changeId: "chg_sync_sentinel_missing_dependency", entityType: "Product", entityId, businessId: ids.businessId, operation: "upsert", occurredAt, cursor, payload: { id: entityId, businessId: ids.businessId, sku: "SYNC-MISSING-DEP", name: "Missing dependency fixture", category: "SENTINEL", brandId: "brand_sync_sentinel_missing", taxRateId: ids.taxRateId, priceCents: 999, costCents: 500, stockOnHand: 1, isActive: true } }], counts: { total: 1, byEntity: { Product: 1 } }, diagnostics: { source: "pc-canonical-db", validator: CATALOG_DELTA_CONTRACT_ID, ordering: "updatedAt_entityRank_id", notes: ["synthetic missing dependency fixture"] } };
    const applied = await applyCatalogDeltaEnvelope(envelope, { mode: "delta", pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, cursor: cursorBefore, config });
    const product = await prisma.product.findUnique({ where: { id: entityId } });
    assert(applied.ok === false && applied.counts.conflict > 0, `missing dependency did not conflict: ${JSON.stringify(applied)}`);
    assert(applied.findings.some((x: any) => x?.code === "missing_dependency"), "missing_dependency finding not explicit");
    assert(applied.cursorAfter === cursorBefore, `conflicted dependency advanced checkpoint: ${cursorBefore} -> ${applied.cursorAfter}`);
    assert(product === null, "missing dependency fixture partially created Product");
    return { assertions: { missingDependencyExplicit: true, noPartialCorruptApply: true }, finding: applied.findings.find((x: any) => x?.code === "missing_dependency"), cursorBefore, cursorAfter: applied.cursorAfter, productCreated: false };
  });

  await runFixture("L", "SYNC.NEG.L.INVALID_CATALOG_PAYLOAD.V1", "CONTRACT_VALIDATION", { after: "Tablet catalog apply invocation", before: "successful checkpoint advancement" }, async () => {
    const beforeStatus = await getTabletCatalogPullStatus({ pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, config });
    const beforeCheckpoint = beforeStatus.checkpoint;
    const cursorBefore = beforeCheckpoint?.cursorValue ?? null;
    const invalid = { contractId: CATALOG_DELTA_CONTRACT_ID, schemaVersion: "9.9.9", stream: CATALOG_DELTA_STREAM, mode: "delta", businessId: ids.businessId, generatedAt: new Date().toISOString(), scope: { businessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, target: "tablet" }, cursor: { requested: cursorBefore, from: cursorBefore, to: "9999-12-31T23:59:59.999Z|003|invalid", hasMore: false, checkpointStrategy: "updatedAt_entityRank_id" }, changes: [], counts: { total: 0, byEntity: {} }, diagnostics: { source: "pc-canonical-db", validator: CATALOG_DELTA_CONTRACT_ID, ordering: "updatedAt_entityRank_id", notes: ["synthetic invalid payload fixture"] } };
    const applied = await applyCatalogDeltaEnvelope(invalid, { mode: "delta", pcBusinessId: ids.businessId, targetBusinessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, cursor: cursorBefore, config });
    assert(applied.ok === false && applied.reason === "invalid_payload", `invalid payload was not rejected: ${JSON.stringify(applied)}`);
    assert(applied.findings.some((x: any) => x?.code === "invalid_schema" && x?.severity === "rejected"), "invalid_schema rejection not explicit");
    assert(applied.cursorAfter === cursorBefore, `invalid payload advanced cursor: ${cursorBefore} -> ${applied.cursorAfter}`);
    assert(applied.checkpoint?.status === "rejected" && applied.checkpoint?.lifecycleStatus === "dead_letter", "invalid payload produced a fake successful checkpoint");
    assert((applied.checkpoint?.lastSuccessfulAt ?? null) === (beforeCheckpoint?.lastSuccessfulAt ?? null), "invalid payload changed lastSuccessfulAt");
    return { assertions: { invalidPayloadRejected: true, checkpointNotAdvanced: true }, reason: applied.reason, findings: applied.findings, cursorBefore, cursorAfter: applied.cursorAfter, checkpoint: { status: applied.checkpoint?.status, lifecycleStatus: applied.checkpoint?.lifecycleStatus, lastSuccessfulAt: applied.checkpoint?.lastSuccessfulAt } };
  });
}

try { await main(); }
catch (error) { const detail = error instanceof Error ? error.message : String(error); result.fatalError = detail; failures.push(`FATAL:${detail}`); console.error(detail); }
finally {
  await controlPost("/__sentinel/fault", { mode: "online" }).catch(() => null);
  result.finishedAt = new Date().toISOString();
  result.failureCount = failures.length;
  result.failures = failures;
  result.ok = failures.length === 0 && "ABCDEFGHIJKL".split("").every((letter) => result.fixtures?.[letter]?.status === "PASS");
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(result, null, 2), "utf8");
  await prisma.$disconnect();
  if (!result.ok) process.exitCode = 1;
}

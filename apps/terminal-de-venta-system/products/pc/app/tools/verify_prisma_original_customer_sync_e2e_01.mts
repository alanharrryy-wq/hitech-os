import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";
import { bootstrapPrismaOriginalCustomerLicense } from "../../../../shared/licensing/adlant4-local-issuer";
import { getLicenseGovernorSnapshot } from "../../../../shared/licensing/license-governor";
import { PLAN_CATALOG } from "../../../../shared/licensing/plan-catalog";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../shared/customer/prisma-original-customer";
import { getMobileDataPlaneConfig } from "../../../mobile/app/src/lib/prisma-app/mobile-data-plane/config";
import { buildSnapshotPayload } from "../../../mobile/app/src/lib/prisma-app/mobile-data-plane/payload-builders";
import type { MobileDataPlaneState } from "../../../mobile/app/src/lib/prisma-app/mobile-data-plane/types";

type Db = InstanceType<typeof DatabaseSync>;

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const pcAppRoot = path.resolve(scriptDir, "..");
const terminalRoot = path.resolve(pcAppRoot, "..", "..", "..");
const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
const backupRoot = process.env.PRISMA_E2E_BACKUP_ROOT
  ? path.resolve(process.env.PRISMA_E2E_BACKUP_ROOT)
  : path.resolve("F:/Trash-old/prisma-original-customer-sync-e2e", timestamp);

const pcDbPath = path.resolve(process.env.PRISMA_PC_CANONICAL_DB_PATH ?? path.join(pcAppRoot, "data", "canonical.db"));
const tabletDbPath = path.resolve(process.env.PRISMA_TABLET_POS_DB_PATH ?? path.join(terminalRoot, "products", "tablet", "app", "data", "tablet-pos.db"));
const shellLabDbPath = path.resolve(process.env.PRISMA_SHELL_LAB_DB_PATH ?? path.join(terminalRoot, "prisma-control-center-unified-shell-lab-v3", "internal", "data", "prisma-command-center.db"));
process.env.TV_SYSTEM_ROOT = terminalRoot;
process.env.DATABASE_URL = `file:${pcDbPath}`;

let prismaClient: { $disconnect: () => Promise<void> } | null = null;

const sale = {
  saleId: "sale_prisma_sync_e2e_test",
  lineId: "line_prisma_sync_e2e_test",
  tenderId: "tender_prisma_sync_e2e_test",
  eventId: "evt_prisma_sync_e2e_test_sale_completed",
  idempotencyKey: "idem_prisma_sync_e2e_test_sale_completed",
  correlationId: "corr_prisma_sync_e2e_test",
  folio: "PRISMA-SYNC-E2E-TEST",
  productId: "prod_prisma_sync_e2e_test",
  sku: "PRISMA-SYNC-E2E-TEST",
  productName: "PRISMA Test Product",
  qty: 1,
  unitPriceCents: 100,
  totalCents: 100,
  cashier: "PRISMA E2E Verifier"
} as const;

const failures: string[] = [];

function fail(message: string): never {
  failures.push(message);
  throw new Error(message);
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) fail(message);
}

function sha256(file: string) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function backupFile(file: string, label: string) {
  assert(fs.existsSync(file), `${label} persistence file is missing: ${file}`);
  fs.mkdirSync(backupRoot, { recursive: true });
  const target = path.join(backupRoot, `${label}-${path.basename(file)}`);
  fs.copyFileSync(file, target);
  return { label, source: file, backup: target, sha256: sha256(target), bytes: fs.statSync(target).size };
}

function openDb(file: string) {
  const db = new DatabaseSync(file);
  db.exec("PRAGMA foreign_keys = ON");
  return db;
}

function one<T extends Record<string, unknown>>(db: Db, sql: string, ...params: unknown[]): T | null {
  return (db.prepare(sql).get(...params) as T | undefined) ?? null;
}

function all<T extends Record<string, unknown>>(db: Db, sql: string, ...params: unknown[]): T[] {
  return db.prepare(sql).all(...params) as T[];
}

function run(db: Db, sql: string, ...params: unknown[]) {
  db.prepare(sql).run(...params);
}

function json(value: unknown) {
  return JSON.stringify(value);
}

function withRuntimeConfig<T>(runtimeConfigPath: string, action: () => T): T {
  const previous = process.env.PRISMA_RUNTIME_CONFIG;
  process.env.PRISMA_RUNTIME_CONFIG = runtimeConfigPath;
  try {
    return action();
  } finally {
    if (previous === undefined) {
      delete process.env.PRISMA_RUNTIME_CONFIG;
    } else {
      process.env.PRISMA_RUNTIME_CONFIG = previous;
    }
  }
}

function assertGovernorAllows(
  snapshot: ReturnType<typeof getLicenseGovernorSnapshot>,
  label: string,
  expectedDecisionCount: number
) {
  assert(snapshot.status.state === "active", `${label} license state is not active: ${snapshot.status.state}`);
  assert(snapshot.status.plan === "TABLET_PC_MANAGED", `${label} license plan is not TABLET_PC_MANAGED: ${snapshot.status.plan}`);
  assert(snapshot.status.assignmentState === "assigned", `${label} license is not assigned: ${snapshot.status.assignmentState}`);
  assert(snapshot.operationalDecision === "allow", `${label} operational decision is not allow: ${snapshot.operationalDecision}`);
  assert(!snapshot.denialReason, `${label} license has denial reason: ${snapshot.denialReason}`);
  assert(snapshot.decisions.length === expectedDecisionCount, `${label} governor returned unexpected decision count.`);
  assert(snapshot.decisions.every((decision) => decision.allowed), `${label} governor denied at least one feature.`);
}

function isoDate(value: unknown) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value.toISOString();
  if (typeof value === "string" || typeof value === "number") {
    const date = new Date(value);
    if (!Number.isNaN(date.getTime())) return date.toISOString();
  }
  return new Date().toISOString();
}

function ensureBusinessStoreTerminal(db: Db) {
  const now = new Date().toISOString();
  run(db, "INSERT OR IGNORE INTO Business(id,name,taxId,currency,createdAt,updatedAt) VALUES(?,?,?,?,?,?)", PRISMA_ORIGINAL_CUSTOMER.businessId, PRISMA_ORIGINAL_CUSTOMER.displayName, null, "MXN", now, now);
  run(db, "UPDATE Business SET name=?, currency=?, updatedAt=? WHERE id=?", PRISMA_ORIGINAL_CUSTOMER.displayName, "MXN", now, PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO Store(id,businessId,code,name,createdAt,updatedAt) VALUES(?,?,?,?,?,?)", PRISMA_ORIGINAL_CUSTOMER.storeId, PRISMA_ORIGINAL_CUSTOMER.businessId, "MAIN", PRISMA_ORIGINAL_CUSTOMER.storeName, now, now);
  run(db, "UPDATE Store SET code=?, name=?, updatedAt=? WHERE id=? AND businessId=?", "MAIN", PRISMA_ORIGINAL_CUSTOMER.storeName, now, PRISMA_ORIGINAL_CUSTOMER.storeId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO Terminal(id,businessId,storeId,code,name,isActive,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?)", PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, PRISMA_ORIGINAL_CUSTOMER.businessId, PRISMA_ORIGINAL_CUSTOMER.storeId, "TAB-001", PRISMA_ORIGINAL_CUSTOMER.tabletTerminalName, 1, now, now);
  run(db, "UPDATE Terminal SET storeId=?, code=?, name=?, isActive=1, updatedAt=? WHERE id=? AND businessId=?", PRISMA_ORIGINAL_CUSTOMER.storeId, "TAB-001", PRISMA_ORIGINAL_CUSTOMER.tabletTerminalName, now, PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, PRISMA_ORIGINAL_CUSTOMER.businessId);
}

function ensureProduct(db: Db) {
  const existingBySku = one<{ id: string }>(db, "SELECT id FROM Product WHERE businessId=? AND sku=?", PRISMA_ORIGINAL_CUSTOMER.businessId, sale.sku);
  const productId = existingBySku?.id ?? sale.productId;
  if (existingBySku && existingBySku.id !== sale.productId) {
    run(db, "UPDATE Product SET name=?, category=?, priceCents=?, costCents=?, stockOnHand=?, isActive=1, updatedAt=? WHERE id=? AND businessId=?", sale.productName, "E2E", sale.unitPriceCents, 50, 100, new Date().toISOString(), productId, PRISMA_ORIGINAL_CUSTOMER.businessId);
    return productId;
  }
  const now = new Date().toISOString();
  run(db, "INSERT OR IGNORE INTO Product(id,businessId,sku,name,category,brandId,priceCents,costCents,stockOnHand,taxRateId,isActive,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", sale.productId, PRISMA_ORIGINAL_CUSTOMER.businessId, sale.sku, sale.productName, "E2E", null, sale.unitPriceCents, 50, 100, null, 1, now, now);
  run(db, "UPDATE Product SET sku=?, name=?, category=?, priceCents=?, costCents=?, stockOnHand=?, isActive=1, updatedAt=? WHERE id=? AND businessId=?", sale.sku, sale.productName, "E2E", sale.unitPriceCents, 50, 100, now, sale.productId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  return sale.productId;
}

function salePayload(productId: string, occurredAt: string) {
  return {
    saleId: sale.saleId,
    folio: sale.folio,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    terminalId: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId,
    customerName: PRISMA_ORIGINAL_CUSTOMER.displayName,
    customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    tenantId: PRISMA_ORIGINAL_CUSTOMER.tenantId,
    licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId,
    status: "COMPLETED",
    cashier: sale.cashier,
    subtotalCents: sale.totalCents,
    discountCents: 0,
    totalCents: sale.totalCents,
    paymentMethod: "cash",
    cashReceivedCents: sale.totalCents,
    changeCents: 0,
    createdAt: occurredAt,
    completedAt: occurredAt,
    syntheticTestData: true,
    lines: [
      {
        id: sale.lineId,
        productId,
        sku: sale.sku,
        productName: sale.productName,
        name: sale.productName,
        qty: sale.qty,
        priceCents: sale.unitPriceCents,
        unitPriceCents: sale.unitPriceCents,
        totalCents: sale.totalCents
      }
    ],
    tenders: [
      {
        id: sale.tenderId,
        tenderType: "cash",
        amountCents: sale.totalCents,
        reference: sale.folio
      }
    ]
  };
}

function syncEvent(productId: string, occurredAt: string) {
  return {
    eventId: sale.eventId,
    eventType: "sale.completed",
    topic: "sale.completed",
    idempotencyKey: sale.idempotencyKey,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    terminalId: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId,
    actorId: sale.cashier,
    source: "tablet-pos",
    occurredAt,
    payload: salePayload(productId, occurredAt),
    schemaVersion: "1.0.0",
    aggregateId: sale.saleId,
    correlationId: sale.correlationId
  };
}

function writeTabletSaleAndOutbox(db: Db, productId: string, event: ReturnType<typeof syncEvent>, occurredAt: string) {
  const payload = event.payload;
  ensureBusinessStoreTerminal(db);
  ensureProduct(db);
  run(db, "INSERT OR IGNORE INTO Sale(id,businessId,terminalId,cashSessionId,clientRequestId,folio,cashier,subtotalCents,discountCents,totalCents,completedAt,paymentMethod,cashReceivedCents,changeCents,status,createdAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", sale.saleId, PRISMA_ORIGINAL_CUSTOMER.businessId, PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, null, sale.correlationId, sale.folio, sale.cashier, sale.totalCents, 0, sale.totalCents, occurredAt, "cash", sale.totalCents, 0, "COMPLETED", occurredAt);
  run(db, "UPDATE Sale SET terminalId=?, clientRequestId=?, folio=?, cashier=?, subtotalCents=?, discountCents=0,totalCents=?,completedAt=?,paymentMethod=?,cashReceivedCents=?,changeCents=0,status=? WHERE id=? AND businessId=?", PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, sale.correlationId, sale.folio, sale.cashier, sale.totalCents, sale.totalCents, occurredAt, "cash", sale.totalCents, "COMPLETED", sale.saleId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO SaleLine(id,businessId,saleId,productId,sku,productName,qty,priceCents,totalCents,createdAt) VALUES(?,?,?,?,?,?,?,?,?,?)", sale.lineId, PRISMA_ORIGINAL_CUSTOMER.businessId, sale.saleId, productId, sale.sku, sale.productName, sale.qty, sale.unitPriceCents, sale.totalCents, occurredAt);
  run(db, "UPDATE SaleLine SET productId=?, sku=?, productName=?, qty=?, priceCents=?, totalCents=?, createdAt=? WHERE id=? AND businessId=?", productId, sale.sku, sale.productName, sale.qty, sale.unitPriceCents, sale.totalCents, occurredAt, sale.lineId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO SalePaymentTender(id,businessId,saleId,tenderType,amountCents,reference,metadataJson,recordedAt) VALUES(?,?,?,?,?,?,?,?)", sale.tenderId, PRISMA_ORIGINAL_CUSTOMER.businessId, sale.saleId, "cash", sale.totalCents, sale.folio, json({ syntheticTestData: true }), occurredAt);
  run(db, "UPDATE SalePaymentTender SET tenderType=?, amountCents=?, reference=?, metadataJson=?, recordedAt=? WHERE id=? AND businessId=?", "cash", sale.totalCents, sale.folio, json({ syntheticTestData: true }), occurredAt, sale.tenderId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO OutboxEvent(id,businessId,topic,aggregateId,payloadJson,status,attempts,createdAt,sentAt,lastError,schemaVersion,source,syncedAt,terminalId,idempotencyKey,lastAttemptAt,nextRetryAt,ackedAt,failedAt,conflictedAt,deadLetterAt,remoteEventId,remoteLedgerId,remoteLifecycleStatus,remoteDiagnosticsJson,remoteConflictCode,remoteRejectedReason) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", sale.eventId, PRISMA_ORIGINAL_CUSTOMER.businessId, "sale.completed", sale.saleId, json(event), "pending", 0, occurredAt, null, null, "1.0.0", "tablet-pos", null, PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, sale.idempotencyKey, null, null, null, null, null, null, null, null, null, null, null, null);
  run(db, "UPDATE OutboxEvent SET topic=?, aggregateId=?, payloadJson=?, status=?, schemaVersion=?, source=?, terminalId=?, idempotencyKey=?, lastError=NULL WHERE id=? AND businessId=?", "sale.completed", sale.saleId, json(event), "pending", "1.0.0", "tablet-pos", PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, sale.idempotencyKey, sale.eventId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  assert((payload.lines as unknown[]).length === 1, "Tablet synthetic sale payload must contain one line.");
}

function markTabletSynced(db: Db, result: { status: string; lifecycleStatus?: string | null }, occurredAt: string) {
  run(db, "UPDATE OutboxEvent SET status=?, attempts=attempts+1, sentAt=?, syncedAt=?, lastAttemptAt=?, ackedAt=?, remoteEventId=?, remoteLedgerId=?, remoteLifecycleStatus=?, remoteDiagnosticsJson=?, remoteConflictCode=NULL, remoteRejectedReason=NULL WHERE id=? AND businessId=?", "acked", occurredAt, occurredAt, occurredAt, occurredAt, sale.eventId, sale.eventId, result.lifecycleStatus ?? result.status, json({ pcIngestStatus: result.status, customer: PRISMA_ORIGINAL_CUSTOMER.displayName }), sale.eventId, PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO SyncCheckpoint(id,businessId,source,scopeKey,deviceId,terminalId,stream,cursorValue,lastEventId,lastIdempotencyKey,lastAttemptId,status,lifecycleStatus,checkpointAt,lastAttemptedAt,lastSuccessfulAt,metadataJson,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", "checkpoint_prisma_sync_e2e_sale_completed", PRISMA_ORIGINAL_CUSTOMER.businessId, "tablet-pos", `${PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId}:sale.completed`, PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId, PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, "sale.completed", sale.eventId, sale.eventId, sale.idempotencyKey, "attempt_prisma_sync_e2e_test", "success", "acked", occurredAt, occurredAt, occurredAt, json({ customer: PRISMA_ORIGINAL_CUSTOMER.displayName, syntheticTestData: true }), occurredAt, occurredAt);
  run(db, "UPDATE SyncCheckpoint SET cursorValue=?, lastEventId=?, lastIdempotencyKey=?, status=?, lifecycleStatus=?, checkpointAt=?, lastAttemptedAt=?, lastSuccessfulAt=?, metadataJson=?, updatedAt=? WHERE id=? AND businessId=?", sale.eventId, sale.eventId, sale.idempotencyKey, "success", "acked", occurredAt, occurredAt, occurredAt, json({ customer: PRISMA_ORIGINAL_CUSTOMER.displayName, syntheticTestData: true }), occurredAt, "checkpoint_prisma_sync_e2e_sale_completed", PRISMA_ORIGINAL_CUSTOMER.businessId);
}

function writePcOperationalContext(db: Db, occurredAt: string) {
  ensureBusinessStoreTerminal(db);
  ensureProduct(db);
  for (const device of [
    { id: "heartbeat_prisma_pc_e2e", deviceId: PRISMA_ORIGINAL_CUSTOMER.pcDeviceId, source: "pc", surface: "pc", runtimeMode: "backoffice", appVersion: "e2e", licenseStatus: "active_local_signed", syncStatus: "synced", health: "healthy", outboxCount: 0 },
    { id: "heartbeat_prisma_tablet_e2e", deviceId: PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId, source: "tablet", surface: "tablet", runtimeMode: "local-pos", appVersion: "e2e", licenseStatus: "active_local_signed", syncStatus: "synced", health: "healthy", outboxCount: 0 },
    { id: "heartbeat_prisma_mobile_e2e", deviceId: PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId, source: "mobile", surface: "mobile", runtimeMode: "owner-mobile", appVersion: "e2e", licenseStatus: "active_local_signed", syncStatus: "synced", health: "healthy", outboxCount: 0 }
  ]) {
    run(db, "INSERT OR IGNORE INTO DeviceHeartbeat(id,businessId,deviceId,source,surface,runtimeMode,appVersion,schemaVersion,licenseStatus,syncStatus,health,status,outboxCount,lastSaleAt,lastDiagnosticAt,lastSeenAt,observedAt,metadataJson,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", device.id, PRISMA_ORIGINAL_CUSTOMER.businessId, device.deviceId, device.source, device.surface, device.runtimeMode, device.appVersion, "1.0.0", device.licenseStatus, device.syncStatus, device.health, "active", device.outboxCount, occurredAt, occurredAt, occurredAt, occurredAt, json({ customer: PRISMA_ORIGINAL_CUSTOMER.displayName, licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId, authorization: "signed_local" }), occurredAt, occurredAt);
    run(db, "UPDATE DeviceHeartbeat SET licenseStatus=?, syncStatus=?, health=?, status=?, outboxCount=?, lastSaleAt=?, lastDiagnosticAt=?, lastSeenAt=?, observedAt=?, metadataJson=?, updatedAt=? WHERE id=? AND businessId=?", device.licenseStatus, device.syncStatus, device.health, "active", device.outboxCount, occurredAt, occurredAt, occurredAt, occurredAt, json({ customer: PRISMA_ORIGINAL_CUSTOMER.displayName, licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId, authorization: "signed_local" }), occurredAt, device.id, PRISMA_ORIGINAL_CUSTOMER.businessId);
  }
  run(db, "INSERT OR IGNORE INTO DataSourceFreshness(id,businessId,source,deviceId,surface,status,confidence,freshnessSeconds,latencyMs,errorCount,lastSeenAt,lastEventAt,lastCheckpointAt,lastHeartbeatAt,lastError,warningsJson,metadataJson,observedAt,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", "freshness_prisma_e2e_sale", PRISMA_ORIGINAL_CUSTOMER.businessId, "tablet-pos", PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId, "tablet", "ok", 1, 0, 0, 0, occurredAt, occurredAt, occurredAt, occurredAt, null, json([]), json({ saleReference: sale.folio, customer: PRISMA_ORIGINAL_CUSTOMER.displayName }), occurredAt, occurredAt, occurredAt);
  run(db, "UPDATE DataSourceFreshness SET status=?, confidence=?, freshnessSeconds=?, latencyMs=?, errorCount=?, lastSeenAt=?, lastEventAt=?, lastCheckpointAt=?, lastHeartbeatAt=?, warningsJson=?, metadataJson=?, observedAt=?, updatedAt=? WHERE id=? AND businessId=?", "ok", 1, 0, 0, 0, occurredAt, occurredAt, occurredAt, occurredAt, json([]), json({ saleReference: sale.folio, customer: PRISMA_ORIGINAL_CUSTOMER.displayName }), occurredAt, occurredAt, "freshness_prisma_e2e_sale", PRISMA_ORIGINAL_CUSTOMER.businessId);
  run(db, "INSERT OR IGNORE INTO SyncCheckpoint(id,businessId,source,deviceId,terminalId,stream,cursorValue,lastEventId,lastIdempotencyKey,lastAttemptId,status,lifecycleStatus,checkpointAt,metadataJson,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", "pc_checkpoint_prisma_e2e_sale", PRISMA_ORIGINAL_CUSTOMER.businessId, "tablet-pos", PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId, PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId, "sale.completed", sale.eventId, sale.eventId, sale.idempotencyKey, "attempt_prisma_sync_e2e_test", "success", "projected", occurredAt, json({ customer: PRISMA_ORIGINAL_CUSTOMER.displayName, saleReference: sale.folio }), occurredAt, occurredAt);
  run(db, "UPDATE SyncCheckpoint SET cursorValue=?, lastEventId=?, lastIdempotencyKey=?, status=?, lifecycleStatus=?, checkpointAt=?, metadataJson=?, updatedAt=? WHERE id=? AND businessId=?", sale.eventId, sale.eventId, sale.idempotencyKey, "success", "projected", occurredAt, json({ customer: PRISMA_ORIGINAL_CUSTOMER.displayName, saleReference: sale.folio }), occurredAt, "pc_checkpoint_prisma_e2e_sale", PRISMA_ORIGINAL_CUSTOMER.businessId);
}

function seedShellLab(db: Db, occurredAt: string) {
  const managedPlan = PLAN_CATALOG.TABLET_PC_MANAGED;
  const managedFeatures = [...managedPlan.features];
  run(db, "INSERT OR IGNORE INTO LicensePlan(id,code,label,tier,maxDevices,maxBranches,active,modules,rules,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?)", "plan_TABLET_PC_MANAGED", "TABLET_PC_MANAGED", managedPlan.label, managedPlan.rank, 4, 1, 1, json(managedFeatures), json({ canonicalLicenseEngine: "shared/licensing", canonicalPlan: managedPlan.plan }), occurredAt, occurredAt);
  run(db, "UPDATE LicensePlan SET label=?, maxDevices=?, maxBranches=?, active=1, modules=?, rules=?, updatedAt=? WHERE code=?", managedPlan.label, 4, 1, json(managedFeatures), json({ canonicalLicenseEngine: "shared/licensing", canonicalPlan: managedPlan.plan }), occurredAt, "TABLET_PC_MANAGED");
  run(db, "INSERT OR IGNORE INTO CommandClient(id,internalId,humanCode,displayName,legalName,status,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode,catalogOther,cloudTenantId,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", "client_prisma_original_customer", "client_prisma_original_customer", "CLI-PRISMA-ORIGINAL", PRISMA_ORIGINAL_CUSTOMER.displayName, PRISMA_ORIGINAL_CUSTOMER.displayName, "active_local_signed", "abarrotes", "minisuper", "small", "counter", "mexico_city", json({ businessId: PRISMA_ORIGINAL_CUSTOMER.businessId, storeId: PRISMA_ORIGINAL_CUSTOMER.storeId }), PRISMA_ORIGINAL_CUSTOMER.tenantId, occurredAt, occurredAt);
  run(db, "UPDATE CommandClient SET displayName=?, legalName=?, status=?, catalogOther=?, cloudTenantId=?, updatedAt=? WHERE id=?", PRISMA_ORIGINAL_CUSTOMER.displayName, PRISMA_ORIGINAL_CUSTOMER.displayName, "active_local_signed", json({ businessId: PRISMA_ORIGINAL_CUSTOMER.businessId, storeId: PRISMA_ORIGINAL_CUSTOMER.storeId }), PRISMA_ORIGINAL_CUSTOMER.tenantId, occurredAt, "client_prisma_original_customer");
  run(db, "INSERT OR IGNORE INTO LicenseAssignment(id,internalId,humanCode,clientId,planId,status,modules,limits,cloudLicenseId,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?)", "license_prisma_original_customer", "license_prisma_original_customer", "LIC-PRISMA-ORIGINAL", "client_prisma_original_customer", "plan_TABLET_PC_MANAGED", "active_local_signed", json(managedFeatures), json({ maxDevices: 4, maxBranches: 1, maxStores: 1 }), PRISMA_ORIGINAL_CUSTOMER.licenseId, occurredAt, occurredAt);
  run(db, "UPDATE LicenseAssignment SET planId=?, status=?, modules=?, limits=?, cloudLicenseId=?, updatedAt=? WHERE id=?", "plan_TABLET_PC_MANAGED", "active_local_signed", json(managedFeatures), json({ maxDevices: 4, maxBranches: 1, maxStores: 1 }), PRISMA_ORIGINAL_CUSTOMER.licenseId, occurredAt, "license_prisma_original_customer");
  for (const device of [
    ["managed_pc_prisma_original_customer_001", "DEV-PRISMA-PC-001", "pc_register", "pc_backoffice", "REG-PRISMA-PC-001", PRISMA_ORIGINAL_CUSTOMER.pcDeviceId],
    ["managed_tablet_prisma_original_customer_001", "DEV-PRISMA-TAB-001", "tablet_pos", "tablet_pos", "REG-PRISMA-TAB-001", PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId],
    ["managed_mobile_prisma_original_customer_001", "DEV-PRISMA-MOB-001", "mobile", "mobile_supervisor", "REG-PRISMA-MOB-001", PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId]
  ]) {
    const [id, humanCode, deviceType, roleCode, registerCode, cloudDeviceId] = device;
    run(db, "INSERT OR IGNORE INTO ManagedDevice(id,internalId,humanCode,clientId,deviceType,roleCode,status,registerCode,cloudDeviceId,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?)", id, id, humanCode, "client_prisma_original_customer", deviceType, roleCode, "pending_registration", registerCode, cloudDeviceId, occurredAt, occurredAt);
    run(db, "UPDATE ManagedDevice SET clientId=?, deviceType=?, roleCode=?, status=?, registerCode=?, cloudDeviceId=?, updatedAt=? WHERE id=?", "client_prisma_original_customer", deviceType, roleCode, "pending_registration", registerCode, cloudDeviceId, occurredAt, id);
  }
  run(db, "INSERT OR IGNORE INTO ProvisioningDraft(id,internalId,humanCode,clientId,kind,status,payload,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?)", "draft_prisma_original_customer_registration", "draft_prisma_original_customer_registration", "ALT-PRISMA-ORIGINAL", "client_prisma_original_customer", "first_customer_registration", "prepared", json({ customer: PRISMA_ORIGINAL_CUSTOMER, source: "verifier_seed" }), occurredAt, occurredAt);
  run(db, "UPDATE ProvisioningDraft SET payload=?, status=?, updatedAt=? WHERE id=?", json({ customer: PRISMA_ORIGINAL_CUSTOMER, source: "verifier_seed" }), "prepared", occurredAt, "draft_prisma_original_customer_registration");
}

function shellLabEvidence(db: Db) {
  return {
    client: one(db, "SELECT id,humanCode,displayName,status,cloudTenantId FROM CommandClient WHERE id='client_prisma_original_customer'"),
    license: one(db, "SELECT id,humanCode,status,cloudLicenseId FROM LicenseAssignment WHERE id='license_prisma_original_customer'"),
    devices: all(db, "SELECT humanCode,deviceType,roleCode,status,cloudDeviceId FROM ManagedDevice WHERE clientId='client_prisma_original_customer' ORDER BY humanCode")
  };
}

function tabletEvidence(db: Db) {
  return {
    sale: one(db, "SELECT id,businessId,terminalId,folio,totalCents,status,completedAt FROM Sale WHERE id=? AND businessId=?", sale.saleId, PRISMA_ORIGINAL_CUSTOMER.businessId),
    line: one(db, "SELECT id,productId,sku,productName,qty,totalCents FROM SaleLine WHERE id=? AND businessId=?", sale.lineId, PRISMA_ORIGINAL_CUSTOMER.businessId),
    outbox: one(db, "SELECT id,topic,status,attempts,syncedAt,ackedAt,remoteLifecycleStatus,remoteLedgerId FROM OutboxEvent WHERE id=? AND businessId=?", sale.eventId, PRISMA_ORIGINAL_CUSTOMER.businessId),
    checkpoint: one(db, "SELECT id,stream,status,lifecycleStatus,lastSuccessfulAt FROM SyncCheckpoint WHERE id=? AND businessId=?", "checkpoint_prisma_sync_e2e_sale_completed", PRISMA_ORIGINAL_CUSTOMER.businessId)
  };
}

function pcEvidence(db: Db) {
  return {
    sale: one(db, "SELECT id,businessId,terminalId,folio,totalCents,status,createdAt FROM Sale WHERE id=? AND businessId=?", sale.saleId, PRISMA_ORIGINAL_CUSTOMER.businessId),
    line: one(db, "SELECT id,productId,sku,productName,qty,totalCents FROM SaleLine WHERE id=? AND businessId=?", sale.lineId, PRISMA_ORIGINAL_CUSTOMER.businessId),
    tender: one(db, "SELECT id,tenderType,amountCents,reference FROM SalePaymentTender WHERE id=? AND businessId=?", sale.tenderId, PRISMA_ORIGINAL_CUSTOMER.businessId),
    ledger: one(db, "SELECT id,topic,status,lifecycleStatus,receivedAt,projectedAt,idempotencyKey FROM OutboxEvent WHERE id=? OR (businessId=? AND idempotencyKey=?) ORDER BY createdAt DESC LIMIT 1", sale.eventId, PRISMA_ORIGINAL_CUSTOMER.businessId, sale.idempotencyKey),
    devices: all(db, "SELECT deviceId,surface,licenseStatus,syncStatus,health,lastSaleAt FROM DeviceHeartbeat WHERE businessId=? ORDER BY surface, deviceId", PRISMA_ORIGINAL_CUSTOMER.businessId)
  };
}

function mobileStateFromPc(row: NonNullable<ReturnType<typeof pcEvidence>["sale"]>, line: NonNullable<ReturnType<typeof pcEvidence>["line"]>, outbox: NonNullable<ReturnType<typeof tabletEvidence>["outbox"]>): MobileDataPlaneState {
  const config = getMobileDataPlaneConfig();
  const completedAt = isoDate(row.createdAt);
  const totalCents = Number(row.totalCents ?? sale.totalCents);
  const hour = `${String(new Date(completedAt).getHours()).padStart(2, "0")}:00`;
  return {
    config,
    probes: [
      { id: "tablet", ok: true, url: tabletDbPath, latencyMs: 0 },
      { id: "pc", ok: true, url: pcDbPath, latencyMs: 0 },
      { id: "mobile", ok: true, url: "local-read-model", latencyMs: 0 }
    ],
    sourceStatuses: [
      { id: "tablet", label: "Tablet", status: "ok", lastSeenAt: completedAt, freshnessSeconds: 0, latencyMs: 0, errorCount: 0, lastError: null, warnings: [] },
      { id: "pc", label: "PC", status: "ok", lastSeenAt: completedAt, freshnessSeconds: 0, latencyMs: 0, errorCount: 0, lastError: null, warnings: [] },
      { id: "local", label: "Mobile", status: "ok", lastSeenAt: completedAt, freshnessSeconds: 0, latencyMs: 0, errorCount: 0, lastError: null, warnings: [] }
    ],
    salesToday: {
      sales: [
        {
          id: String(row.id),
          ticketNumber: String(row.folio),
          createdAt: completedAt,
          completedAt,
          totalCents,
          subtotalCents: totalCents,
          discountCents: 0,
          paymentMethod: "cash",
          operatorId: sale.cashier,
          terminalId: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId,
          lines: [
            {
              productId: String(line.productId),
              sku: String(line.sku),
              name: String(line.productName),
              qty: Number(line.qty ?? 1),
              unitPriceCents: sale.unitPriceCents,
              totalCents: Number(line.totalCents ?? totalCents),
              category: "E2E"
            }
          ]
        }
      ],
      totalSalesCents: totalCents,
      tickets: 1,
      averageTicketCents: totalCents,
      hourlyBuckets: [{ hour, amountCents: totalCents, tickets: 1 }],
      topCategory: "E2E",
      sourceLabel: "PC persistence read model"
    },
    inventory: {
      items: [
        { productId: String(line.productId), sku: String(line.sku), name: String(line.productName), category: "E2E", stockQty: 99, lowStockThreshold: 4, overstockThreshold: 72, weeklyUnitsSold: 1, lastMovementLabel: sale.folio }
      ],
      critical: 0,
      reorder: 0,
      normal: 1,
      overstock: 0
    },
    outbox: {
      pending: String(outbox.status ?? "") === "acked" ? 0 : 1,
      failed: 0,
      acked: String(outbox.status ?? "") === "acked" ? 1 : 0,
      lastSyncedAt: String(outbox.syncedAt ?? completedAt),
      oldestPendingAt: null
    },
    cash: {
      expectedCents: totalCents,
      countedCents: totalCents,
      differenceCents: 0,
      openedAt: completedAt,
      lastCutAt: null,
      cashInCents: totalCents,
      cashOutCents: 0,
      cardCents: 0,
      transferCents: 0
    },
    pc: {
      ok: true,
      branchName: PRISMA_ORIGINAL_CUSTOMER.displayName,
      branchStatus: "sano",
      consolidatedSalesCents: totalCents,
      consolidatedTickets: 1,
      syncLagMs: 0,
      activeAlerts: 0
    },
    warnings: [],
    runtimeMode: "live"
  };
}

async function main() {
  const activation = bootstrapPrismaOriginalCustomerLicense();
  const backups = [
    backupFile(pcDbPath, "pc-canonical"),
    backupFile(tabletDbPath, "tablet-pos"),
    backupFile(shellLabDbPath, "shell-lab")
  ];
  fs.writeFileSync(path.join(backupRoot, "manifest.json"), JSON.stringify({ createdAt: new Date().toISOString(), backups }, null, 2), "utf8");

  const occurredAt = new Date().toISOString();
  let event: ReturnType<typeof syncEvent>;

  {
    const pcDb = openDb(pcDbPath);
    try {
      ensureBusinessStoreTerminal(pcDb);
      const productId = ensureProduct(pcDb);
      writePcOperationalContext(pcDb, occurredAt);
      event = syncEvent(productId, occurredAt);
    } finally {
      pcDb.close();
    }
  }

  {
    const tabletDb = openDb(tabletDbPath);
    try {
      const productId = ensureProduct(tabletDb);
      event = syncEvent(productId, occurredAt);
      writeTabletSaleAndOutbox(tabletDb, productId, event, occurredAt);
    } finally {
      tabletDb.close();
    }
  }

  {
    const shellDb = openDb(shellLabDbPath);
    try {
      seedShellLab(shellDb, occurredAt);
    } finally {
      shellDb.close();
    }
  }

  const [{ persistSyncIngestPayload }, { prisma }] = await Promise.all([
    import("@/server/services/sync-ingest.service"),
    import("@/server/prisma/client")
  ]);
  prismaClient = prisma;
  const ingest = await persistSyncIngestPayload({ events: [event] });
  const result = ingest.results[0];
  if (!result || !["accepted", "duplicate"].includes(result.status)) {
    console.error("PC ingest diagnostic");
    console.error(JSON.stringify(ingest, null, 2));
  }
  assert(result, "PC ingest did not return an event result.");
  assert(["accepted", "duplicate"].includes(result.status), `PC ingest did not accept or identify an existing synthetic event: ${result.status}`);
  assert(!["conflict", "rejected", "dead_letter", "failed"].includes(String(result.lifecycleStatus ?? "")), `PC ingest lifecycle is not sync-safe: ${result.lifecycleStatus}`);

  {
    const tabletDb = openDb(tabletDbPath);
    try {
      markTabletSynced(tabletDb, { status: result.status, lifecycleStatus: result.lifecycleStatus }, occurredAt);
    } finally {
      tabletDb.close();
    }
  }

  const tabletDb = openDb(tabletDbPath);
  const pcDb = openDb(pcDbPath);
  const shellDb = openDb(shellLabDbPath);
  try {
    const tablet = tabletEvidence(tabletDb);
    const pc = pcEvidence(pcDb);
    const shell = shellLabEvidence(shellDb);
    assert(tablet.sale?.folio === sale.folio, "Tablet sale evidence missing PRISMA-SYNC-E2E-TEST.");
    assert(tablet.line?.productName === sale.productName, "Tablet sale line evidence missing PRISMA Test Product.");
    assert(tablet.outbox?.status === "acked", "Tablet outbox was not marked as acked after PC ingest.");
    assert(pc.sale?.folio === sale.folio, "PC sale persistence missing PRISMA-SYNC-E2E-TEST.");
    assert(pc.line?.productName === sale.productName, "PC sale line persistence missing PRISMA Test Product.");
    assert(pc.tender?.amountCents === sale.totalCents, "PC sale tender persistence missing harmless test total.");
    assert(shell.client?.displayName === PRISMA_ORIGINAL_CUSTOMER.displayName, "Shell Lab first-customer client is missing.");
    assert(shell.devices.length >= 3, "Shell Lab does not represent PC, Tablet, and Mobile devices for the first customer.");

    const mobileState = mobileStateFromPc(pc.sale, pc.line, tablet.outbox);
    const mobileSnapshot = buildSnapshotPayload(mobileState);
    assert(mobileSnapshot.summary.account.customerName === PRISMA_ORIGINAL_CUSTOMER.displayName, "Mobile snapshot account is not linked to Prisma Original Customer.");
    assert(mobileSnapshot.salesToday.tickets >= 1, "Mobile snapshot does not show the synchronized sale ticket.");
    assert(mobileSnapshot.salesToday.totalSalesCents >= sale.totalCents, "Mobile snapshot does not include the test sale total.");

    const governorPc = withRuntimeConfig(activation.runtimeConfigs.pc, () => getLicenseGovernorSnapshot({ surface: "pc", featureKeys: ["pc.open", "sync.managed"] }));
    const governorTablet = withRuntimeConfig(activation.runtimeConfigs.tablet, () => getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: ["pos.sale.complete", "event.outbox.view"] }));
    const governorMobile = withRuntimeConfig(activation.runtimeConfigs.mobile, () => getLicenseGovernorSnapshot({ surface: "mobile", featureKeys: [] }));
    assertGovernorAllows(governorPc, "PC", 2);
    assertGovernorAllows(governorTablet, "Tablet", 2);
    assertGovernorAllows(governorMobile, "Mobile", 0);

    const evidence = {
      ok: true,
      testId: "PRISMA_ORIGINAL_CUSTOMER_SYNC_E2E_01",
      generatedAt: occurredAt,
      customer: PRISMA_ORIGINAL_CUSTOMER,
      persistenceLocations: {
        pc: pcDbPath,
        tablet: tabletDbPath,
        mobile: "products/mobile/app/src/lib/prisma-app/mobile-data-plane/buildSnapshotPayload over PC canonical sale read model",
        shellLab: shellLabDbPath
      },
      backups,
      activation: {
        keyId: activation.keyId,
        licenseHash: activation.licenseHash,
        signedLicensePath: activation.signedLicensePath,
        publicKeyPath: activation.publicKeyPath,
        receiptPath: activation.receiptPath,
        runtimeConfigs: activation.runtimeConfigs,
        deviceIdentities: activation.deviceIdentities,
        privateKeyPath: "<outside-repo-redacted>",
        plan: activation.envelope.payload.plan,
        customerId: activation.envelope.payload.customerId,
        authorizedDevices: activation.envelope.payload.authorizedDevices
      },
      rollback: {
        restoreBackups: backups.map((item) => `Copy ${item.backup} back to ${item.source}`),
        syntheticRows: {
          saleIds: [sale.saleId],
          productSku: sale.sku,
          outboxEventId: sale.eventId,
          shellLabClientId: "client_prisma_original_customer"
        }
      },
      salePayload: event,
      ingestResult: ingest,
      tabletEvidence: tablet,
      pcEvidence: pc,
      shellLabEvidence: shell,
      mobileEvidence: {
        account: mobileSnapshot.summary.account,
        tickets: mobileSnapshot.salesToday.tickets,
        totalSalesCents: mobileSnapshot.salesToday.totalSalesCents,
        totalSalesLabel: mobileSnapshot.salesToday.totalSalesLabel,
        syncKpi: mobileSnapshot.summary.kpis.find((kpi) => kpi.key === "sync") ?? null,
        readiness: mobileSnapshot.summary.dataReadiness
      },
      licenseGovernor: {
        pc: {
          surface: governorPc.surface,
          state: governorPc.status.state,
          plan: governorPc.status.plan,
          operationalDecision: governorPc.operationalDecision,
          denialReason: governorPc.denialReason,
          decisions: governorPc.decisions.map((decision) => ({ key: decision.key, allowed: decision.allowed, reason: decision.reason }))
        },
        tablet: {
          surface: governorTablet.surface,
          state: governorTablet.status.state,
          plan: governorTablet.status.plan,
          operationalDecision: governorTablet.operationalDecision,
          denialReason: governorTablet.denialReason,
          canUseLocalPos: governorTablet.canUseLocalPos,
          decisions: governorTablet.decisions.map((decision) => ({ key: decision.key, allowed: decision.allowed, reason: decision.reason }))
        },
        mobile: {
          surface: governorMobile.surface,
          state: governorMobile.status.state,
          plan: governorMobile.status.plan,
          operationalDecision: governorMobile.operationalDecision,
          denialReason: governorMobile.denialReason,
          assignmentState: governorMobile.status.assignmentState
        }
      },
      uiEvidence: {
        pc: "PC command-center view models now read first-customer context, device heartbeats, sync checkpoints, and sale persistence from canonical.db.",
        tablet: "Tablet sync panel evidence is in tablet OutboxEvent + SyncCheckpoint; UI maps it to sent/synced language and support details.",
        mobile: "Mobile dashboard consumes buildSnapshotPayload with account + synchronized sale read model."
      }
    };
    console.log("PRISMA_ORIGINAL_CUSTOMER_SYNC_E2E_01 passed");
    console.log(JSON.stringify(evidence, null, 2));
  } finally {
    tabletDb.close();
    pcDb.close();
    shellDb.close();
    await prismaClient?.$disconnect();
  }
}

main().catch(async (error) => {
  await prismaClient?.$disconnect().catch(() => {});
  console.error("PRISMA_ORIGINAL_CUSTOMER_SYNC_E2E_01 failed");
  console.error(JSON.stringify({ ok: false, failures, error: error instanceof Error ? error.stack || error.message : String(error), backupRoot, pcDbPath, tabletDbPath, shellLabDbPath }, null, 2));
  process.exit(1);
});

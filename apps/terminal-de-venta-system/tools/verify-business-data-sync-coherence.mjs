#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";

const terminalRoot = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const checkedAt = new Date().toISOString();

const dbFiles = {
  pc: "products/pc/app/data/canonical.db",
  tablet: "products/tablet/app/data/tablet-pos.db"
};

const tableComparisons = [
  { table: "Business", key: ["id"], fields: ["id", "name", "taxId", "currency"] },
  { table: "Store", key: ["id"], fields: ["id", "businessId", "code", "name"] },
  { table: "Terminal", key: ["id"], fields: ["id", "businessId", "storeId", "code", "name", "isActive"] },
  { table: "Product", key: ["id"], fields: ["id", "businessId", "sku", "name", "category", "priceCents", "costCents", "stockOnHand", "isActive"] },
  { table: "Supplier", key: ["id"], fields: ["id", "businessId", "name", "status"] },
  { table: "ProductSupplier", key: ["id"], fields: ["id", "businessId", "productId", "supplierId", "isPrimary", "status", "leadTimeDays"] },
  { table: "Sale", key: ["id"], fields: ["id", "businessId", "terminalId", "cashSessionId", "folio", "cashier", "totalCents", "status", "createdAt"] },
  { table: "SaleLine", key: ["id"], fields: ["id", "businessId", "saleId", "productId", "sku", "productName", "qty", "priceCents", "totalCents"] },
  { table: "SalePaymentTender", key: ["id"], fields: ["id", "businessId", "saleId", "tenderType", "amountCents", "reference"] },
  { table: "SyncCheckpoint", key: ["id"], fields: ["id", "businessId", "source", "deviceId", "terminalId", "stream", "cursorValue", "lastEventId", "lastIdempotencyKey", "status"] }
];

function rel(file) {
  return path.join(terminalRoot, file);
}

function read(file) {
  return fs.readFileSync(rel(file), "utf8");
}

function fileExists(file) {
  return fs.existsSync(rel(file));
}

function openDb(label) {
  const file = rel(dbFiles[label]);
  if (!fs.existsSync(file)) throw new Error(`${label} DB not found at ${dbFiles[label]}`);
  return new DatabaseSync(file, { readOnly: true });
}

function columns(db, table) {
  return db.prepare(`PRAGMA table_info("${table}")`).all().map((row) => String(row.name));
}

function tableExists(db, table) {
  return Boolean(db.prepare("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?").get(table));
}

function quote(name) {
  return `"${String(name).replace(/"/g, '""')}"`;
}

function normalizeValue(value) {
  if (value == null) return null;
  if (typeof value === "number") return Number.isFinite(value) ? value : String(value);
  if (typeof value === "bigint") return Number(value);
  if (typeof value === "boolean") return value;
  return String(value);
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  }
  return normalizeValue(value);
}

function digest(value) {
  return crypto.createHash("sha256").update(JSON.stringify(stable(value))).digest("hex");
}

function selectComparableRows(db, spec) {
  if (!tableExists(db, spec.table)) return { exists: false, columns: [], rows: [] };
  const availableColumns = columns(db, spec.table);
  const selectedFields = spec.fields.filter((field) => availableColumns.includes(field));
  const orderFields = spec.key.filter((field) => availableColumns.includes(field));
  const orderBy = orderFields.length ? ` ORDER BY ${orderFields.map(quote).join(", ")}` : "";
  const sql = `SELECT ${selectedFields.map(quote).join(", ")} FROM ${quote(spec.table)}${orderBy}`;
  const rows = db.prepare(sql).all().map((row) => {
    const normalized = {};
    for (const field of selectedFields) normalized[field] = normalizeValue(row[field]);
    return normalized;
  });
  return { exists: true, columns: selectedFields, rows };
}

function compareTables(pcDb, tabletDb) {
  const checks = [];
  const comparisons = [];
  for (const spec of tableComparisons) {
    const pc = selectComparableRows(pcDb, spec);
    const tablet = selectComparableRows(tabletDb, spec);
    const samePresence = pc.exists === tablet.exists;
    const sameColumns = JSON.stringify(pc.columns) === JSON.stringify(tablet.columns);
    const sameRows = digest(pc.rows) === digest(tablet.rows);
    const status = samePresence && sameColumns && sameRows ? "PASS" : "FAIL";
    const comparison = {
      table: spec.table,
      status,
      pcRows: pc.rows.length,
      tabletRows: tablet.rows.length,
      comparedColumns: pc.columns,
      pcDigest: digest(pc.rows),
      tabletDigest: digest(tablet.rows)
    };
    comparisons.push(comparison);
    checks.push({
      name: `${spec.table} operational equivalence`,
      status,
      evidence: comparison
    });
  }
  return { checks, comparisons };
}

function selectRows(db, sql, params = []) {
  return db.prepare(sql).all(...params);
}

function saleIds(db) {
  return new Set(selectRows(db, "SELECT id FROM Sale ORDER BY id").map((row) => String(row.id)));
}

function setDiff(left, right) {
  return Array.from(left).filter((item) => !right.has(item)).sort();
}

function parseJson(value) {
  try {
    return JSON.parse(String(value ?? ""));
  } catch {
    return null;
  }
}

function outboxSaleLinks(db, label) {
  const sales = saleIds(db);
  const rows = selectRows(db, "SELECT id, businessId, terminalId, topic, aggregateId, idempotencyKey, payloadJson, status, source, schemaVersion FROM OutboxEvent ORDER BY id");
  const saleEvents = rows.filter((row) => sales.has(String(row.aggregateId)));
  const missingPayloadIdentity = [];
  const duplicateIdempotencyKeys = [];
  const seenKeys = new Set();
  for (const row of saleEvents) {
    const payload = parseJson(row.payloadJson);
    const payloadSaleId = payload?.saleId ?? payload?.originSaleId ?? payload?.payload?.saleId ?? payload?.payload?.originSaleId;
    const idempotencyKey = String(row.idempotencyKey ?? "");
    if (payloadSaleId && String(payloadSaleId) !== String(row.aggregateId)) {
      missingPayloadIdentity.push({ id: row.id, aggregateId: row.aggregateId, payloadSaleId });
    }
    if (!payloadSaleId && !String(row.payloadJson ?? "").includes(String(row.aggregateId))) {
      missingPayloadIdentity.push({ id: row.id, aggregateId: row.aggregateId, payloadSaleId: null });
    }
    if (idempotencyKey) {
      if (seenKeys.has(idempotencyKey)) duplicateIdempotencyKeys.push(idempotencyKey);
      seenKeys.add(idempotencyKey);
    }
  }
  return {
    label,
    saleCount: sales.size,
    outboxRows: rows.length,
    saleLinkedEvents: saleEvents.length,
    missingSaleOutbox: setDiff(sales, new Set(saleEvents.map((row) => String(row.aggregateId)))),
    missingPayloadIdentity,
    duplicateIdempotencyKeys: Array.from(new Set(duplicateIdempotencyKeys)).sort()
  };
}

function compareOutboxIdentity(pcDb, tabletDb) {
  const pc = selectRows(pcDb, "SELECT id, businessId, terminalId, topic, aggregateId, idempotencyKey, schemaVersion FROM OutboxEvent ORDER BY id");
  const tablet = selectRows(tabletDb, "SELECT id, businessId, terminalId, topic, aggregateId, idempotencyKey, schemaVersion FROM OutboxEvent ORDER BY id");
  const comparable = (rows) => rows.map((row) => stable(row));
  const pcDigest = digest(comparable(pc));
  const tabletDigest = digest(comparable(tablet));
  return {
    status: pcDigest === tabletDigest ? "PASS" : "FAIL",
    pcRows: pc.length,
    tabletRows: tablet.length,
    pcDigest,
    tabletDigest
  };
}

function checkOutboxSourceLineage(pcDb, tabletDb) {
  const pcSources = selectRows(pcDb, "SELECT DISTINCT source FROM OutboxEvent ORDER BY source").map((row) => String(row.source ?? ""));
  const tabletSources = selectRows(tabletDb, "SELECT DISTINCT source FROM OutboxEvent ORDER BY source").map((row) => String(row.source ?? ""));
  return {
    status: pcSources.every((source) => /canonical|projection|pc/i.test(source)) && tabletSources.every((source) => /tablet|pos/i.test(source)) ? "PASS" : "FAIL",
    pcSources,
    tabletSources
  };
}

function checkOutboxAndProvenance(pcDb, tabletDb) {
  const pc = outboxSaleLinks(pcDb, "pc");
  const tablet = outboxSaleLinks(tabletDb, "tablet");
  const identity = compareOutboxIdentity(pcDb, tabletDb);
  const sourceLineage = checkOutboxSourceLineage(pcDb, tabletDb);
  return [
    {
      name: "Tablet sale rows have sale-linked outbox events",
      status: tablet.missingSaleOutbox.length === 0 && tablet.missingPayloadIdentity.length === 0 ? "PASS" : "FAIL",
      evidence: tablet
    },
    {
      name: "PC canonical sale rows have projected sale-linked outbox events",
      status: pc.missingSaleOutbox.length === 0 && pc.missingPayloadIdentity.length === 0 ? "PASS" : "FAIL",
      evidence: pc
    },
    {
      name: "Outbox idempotency keys are unique per local DB",
      status: pc.duplicateIdempotencyKeys.length === 0 && tablet.duplicateIdempotencyKeys.length === 0 ? "PASS" : "FAIL",
      evidence: { pc: pc.duplicateIdempotencyKeys, tablet: tablet.duplicateIdempotencyKeys }
    },
    {
      name: "Outbox business identity matches across PC and Tablet",
      status: identity.status,
      evidence: identity
    },
    {
      name: "Outbox source lineage distinguishes Tablet origin from PC projection",
      status: sourceLineage.status,
      evidence: sourceLineage
    }
  ];
}

function readSourceChecks() {
  const checks = [];
  const add = (name, file, predicate) => {
    const text = fileExists(file) ? read(file) : "";
    const status = text && predicate(text) ? "PASS" : "FAIL";
    checks.push({ name, status, evidence: { file } });
  };

  add(
    "Tablet sale mutation is license-gated before completeLocalSale",
    "products/tablet/app/app/api/pos/sales/complete/route.ts",
    (text) => text.includes('guardTabletFeatureForApi("pos.sale.complete")') && text.indexOf("guardTabletFeatureForApi") < text.indexOf("completeLocalSale")
  );
  add(
    "PC ingest persists through sync-ingest service with idempotency/conflict contract",
    "products/pc/app/app/api/backoffice/sync/ingest/route.ts",
    (text) => text.includes("persistSyncIngestPayload") && text.includes("duplicate") && text.includes("conflict")
  );
  add(
    "PC catalog export endpoint uses canonical delta service",
    "products/pc/app/app/api/sync/export/catalog-delta/route.ts",
    (text) => text.includes("buildPcCatalogDelta") && text.includes("exportPcCatalogDelta")
  );
  add(
    "Tablet catalog pull endpoint uses PC catalog pull service",
    "products/tablet/app/app/api/pos/sync/pull/route.ts",
    (text) => text.includes("pullCatalogDeltaFromPc") && text.includes("getTabletCatalogPullStatus")
  );
  add(
    "Mobile data plane reads local DBs read-only and does not mutate",
    "products/mobile/app/src/lib/prisma-app/mobile-data-plane/local-db-snapshot.ts",
    (text) => text.includes("readOnly: true") && !/\b(INSERT|UPDATE|DELETE|CREATE|DROP)\b/i.test(text)
  );
  add(
    "Cloud Center customer setup provisions plan, license, setup bundle, slots and claims",
    "infra/cloudflare/licflow3-worker/src/worker.js",
    (text) => text.includes("createCustomerSetup") && text.includes("upsertSetupBundle") && text.includes("buildDeviceClaimSlotsForPlan") && text.includes("claimCustomerDevice")
  );
  add(
    "License feature resolver hard-denies sale origin without valid scope",
    "shared/licensing/feature-resolver.ts",
    (text) => text.includes("SALE_ORIGIN_FEATURES") && text.includes("hard_deny") && text.includes("pos.sale.complete")
  );

  return checks;
}

function statusFromChecks(checks) {
  return checks.some((check) => check.status === "FAIL") ? "FAIL" : "PASS";
}

function main() {
  const pcDb = openDb("pc");
  const tabletDb = openDb("tablet");
  try {
    const tableResult = compareTables(pcDb, tabletDb);
    const checks = [
      ...tableResult.checks,
      ...checkOutboxAndProvenance(pcDb, tabletDb),
      ...readSourceChecks()
    ];
    const payload = {
      ok: statusFromChecks(checks) === "PASS",
      status: statusFromChecks(checks),
      checkedAt,
      scope: "Cloud Center + Apps + Data Sync/DB/Projections, excluding Code Atlas",
      dbs: dbFiles,
      tableComparisons: tableResult.comparisons,
      checks,
      failures: checks.filter((check) => check.status === "FAIL")
    };
    console.log(JSON.stringify(payload, null, 2));
    if (!payload.ok) process.exit(1);
  } finally {
    pcDb.close();
    tabletDb.close();
  }
}

main();

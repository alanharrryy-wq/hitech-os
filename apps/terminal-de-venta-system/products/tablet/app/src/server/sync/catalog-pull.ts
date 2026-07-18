import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID } from "@/server/pos-api/validators";
import { loadPrismaTabletPcOriginConfig, pcUrl, type PrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";
import {
  CATALOG_DELTA_STREAM,
  validateCatalogDeltaEnvelope,
  type CatalogDeltaEnvelope,
  type CatalogDeltaEntityType,
  type CatalogDeltaFinding,
  type CatalogDeltaMode,
  type CatalogDeltaRecord
} from "@shared-kernel/sync/catalog-delta";

const CATALOG_PULL_SOURCE = "pc.catalog.pull";
const DEFAULT_TIMEOUT_MS = 2500;
const ENTITY_APPLY_ORDER: CatalogDeltaEntityType[] = [
  "TaxRate",
  "Brand",
  "Supplier",
  "Product",
  "ModifierGroup",
  "ModifierOption",
  "ProductModifierGroup",
  "ProductSupplier",
  "PriceList",
  "PriceListItem",
  "DropdownCatalog",
  "DropdownOption"
];
const ENTITY_RANK = new Map(ENTITY_APPLY_ORDER.map((entity, index) => [entity, index]));

export type TabletCatalogPullInput = {
  mode?: CatalogDeltaMode | string | null;
  resetCheckpoint?: boolean;
  pcBusinessId?: string | null;
  targetBusinessId?: string | null;
  terminalId?: string | null;
  storeId?: string | null;
  cursor?: string | null;
  limit?: number | string | null;
  requestedBy?: string | null;
  config?: PrismaTabletPcOriginConfig;
};

export type TabletCatalogPullCounts = {
  received: number;
  applied: number;
  rejected: number;
  conflict: number;
  duplicate: number;
  byEntity: Record<string, number>;
};

export type TabletCatalogPullResult = {
  ok: boolean;
  reason: string;
  mode: CatalogDeltaMode;
  stream: typeof CATALOG_DELTA_STREAM;
  sourceBusinessId: string | null;
  targetBusinessId: string;
  terminalId: string;
  cursorBefore: string | null;
  cursorAfter: string | null;
  checkpoint: TabletCatalogCheckpointView | null;
  counts: TabletCatalogPullCounts;
  findings: CatalogDeltaFinding[];
  errors: string[];
  health: {
    enabled: boolean;
    origin: string | null;
    url: string | null;
    status: "disabled" | "missing_origin" | "online" | "offline" | "invalid_payload" | "applied" | "partial";
    httpStatus?: number;
  };
};

export type TabletCatalogCheckpointView = {
  id: string;
  businessId: string;
  source: string;
  scopeKey: string;
  deviceId: string | null;
  terminalId: string | null;
  stream: string;
  cursorValue: string | null;
  lastEventId: string | null;
  lastAttemptId: string | null;
  status: string;
  lifecycleStatus: string | null;
  checkpointAt: string;
  lastAttemptedAt: string | null;
  lastSuccessfulAt: string | null;
  metadata: Record<string, unknown>;
};

export type TabletCatalogPullStatus = {
  stream: typeof CATALOG_DELTA_STREAM;
  targetBusinessId: string;
  terminalId: string;
  pc: {
    enabled: boolean;
    origin: string | null;
    exportPath: string;
  };
  checkpoint: TabletCatalogCheckpointView | null;
  tableCounts: Record<string, number>;
};

function asString(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function normalizeMode(value: unknown): CatalogDeltaMode {
  const mode = asString(value).toLowerCase();
  if (mode === "bootstrap" || mode === "resync") return mode;
  return "delta";
}

function normalizeLimit(value: unknown) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 500;
  return Math.max(1, Math.min(Math.trunc(parsed), 2000));
}

function iso(value: unknown) {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(String(value));
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function date(value: unknown, fallback = new Date()) {
  const parsed = value instanceof Date ? value : new Date(String(value || ""));
  return Number.isNaN(parsed.getTime()) ? fallback : parsed;
}

function asInt(value: unknown, fallback = 0) {
  const parsed = Number(value);
  return Number.isInteger(parsed) ? parsed : fallback;
}

function asBool(value: unknown, fallback = false) {
  if (typeof value === "boolean") return value;
  if (typeof value === "string") return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
  return fallback;
}

function maybeString(value: unknown) {
  const text = asString(value);
  return text || null;
}

function scopeKey(input: { sourceBusinessId?: string | null; targetBusinessId: string; terminalId?: string | null; storeId?: string | null }) {
  return [
    CATALOG_PULL_SOURCE,
    `source:${input.sourceBusinessId || "pc"}`,
    `target:${input.targetBusinessId}`,
    `terminal:${input.terminalId || "all"}`,
    `store:${input.storeId || "all"}`
  ].join("|");
}

function sanitizedFinding(input: CatalogDeltaFinding): CatalogDeltaFinding {
  return {
    code: input.code,
    severity: input.severity,
    entityType: input.entityType ?? null,
    entityId: input.entityId ?? null,
    changeId: input.changeId ?? null,
    detail: input.detail.slice(0, 500)
  };
}

function conflict(code: CatalogDeltaFinding["code"], detail: string, item?: CatalogDeltaRecord, severity: CatalogDeltaFinding["severity"] = "conflict"): CatalogDeltaFinding {
  return {
    code,
    severity,
    entityType: item?.entityType ?? null,
    entityId: item?.entityId ?? null,
    changeId: item?.changeId ?? null,
    detail
  };
}

function parseMetadata(value: string | null | undefined) {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value);
    return typeof parsed === "object" && parsed !== null ? parsed : {};
  } catch {
    return {};
  }
}

function checkpointView(row: any): TabletCatalogCheckpointView | null {
  if (!row) return null;
  return {
    id: row.id,
    businessId: row.businessId,
    source: row.source,
    scopeKey: row.scopeKey,
    deviceId: row.deviceId ?? null,
    terminalId: row.terminalId ?? null,
    stream: row.stream,
    cursorValue: row.cursorValue ?? null,
    lastEventId: row.lastEventId ?? null,
    lastAttemptId: row.lastAttemptId ?? null,
    status: row.status,
    lifecycleStatus: row.lifecycleStatus ?? null,
    checkpointAt: iso(row.checkpointAt) ?? new Date(0).toISOString(),
    lastAttemptedAt: iso(row.lastAttemptedAt),
    lastSuccessfulAt: iso(row.lastSuccessfulAt),
    metadata: parseMetadata(row.metadataJson)
  };
}

async function readCheckpoint(targetBusinessId: string, key: string) {
  const db = prisma as any;
  return db.syncCheckpoint.findUnique({
    where: { businessId_scopeKey_stream: { businessId: targetBusinessId, scopeKey: key, stream: CATALOG_DELTA_STREAM } }
  }).catch(() => null);
}

async function ensureTargetBusiness(tx: any, businessId: string) {
  await tx.business.upsert({
    where: { id: businessId },
    update: { currency: "MXN" },
    create: { id: businessId, name: "PRISMA Tablet Local", taxId: null, currency: "MXN" }
  });
}

async function ensureSameBusinessById(tx: any, delegateName: string, id: string, targetBusinessId: string, item: CatalogDeltaRecord) {
  const existing = await tx[delegateName].findUnique({ where: { id } }).catch(() => null);
  if (existing && existing.businessId !== targetBusinessId) {
    return conflict("invalid_schema", `${item.entityType} ${id} exists in a different Tablet business scope.`, item, "rejected");
  }
  return null;
}

async function applyTaxRate(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await ensureSameBusinessById(tx, "taxRate", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const name = asString(payload.name);
  const byName = await tx.taxRate.findUnique({ where: { businessId_name: { businessId: targetBusinessId, name } } }).catch(() => null);
  if (byName && byName.id !== id) return conflict("duplicate_change", `TaxRate name ${name} already belongs to ${byName.id}.`, item);
  await tx.taxRate.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      name,
      rateBps: asInt(payload.rateBps),
      isDefault: asBool(payload.isDefault),
      isActive: asBool(payload.isActive, true),
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      name,
      rateBps: asInt(payload.rateBps),
      isDefault: asBool(payload.isDefault),
      isActive: asBool(payload.isActive, true),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applyBrand(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await ensureSameBusinessById(tx, "brand", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const name = asString(payload.name);
  const byName = await tx.brand.findUnique({ where: { businessId_name: { businessId: targetBusinessId, name } } }).catch(() => null);
  if (byName && byName.id !== id) return conflict("duplicate_change", `Brand name ${name} already belongs to ${byName.id}.`, item);
  await tx.brand.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      name,
      description: maybeString(payload.description),
      status: asString(payload.status) || "ACTIVE",
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      name,
      description: maybeString(payload.description),
      status: asString(payload.status) || "ACTIVE",
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applySupplier(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await ensureSameBusinessById(tx, "supplier", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const name = asString(payload.name);
  const byName = await tx.supplier.findUnique({ where: { businessId_name: { businessId: targetBusinessId, name } } }).catch(() => null);
  if (byName && byName.id !== id) return conflict("duplicate_change", `Supplier name ${name} already belongs to ${byName.id}.`, item);
  await tx.supplier.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      name,
      status: asString(payload.status) || "ACTIVE",
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      name,
      status: asString(payload.status) || "ACTIVE",
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function replaceProductBarcodes(tx: any, item: CatalogDeltaRecord, targetBusinessId: string, productId: string, rawBarcodes: unknown) {
  if (!Array.isArray(rawBarcodes)) return null;
  const barcodes = Array.from(new Set(rawBarcodes.map(String).map((code) => code.trim()).filter(Boolean))).sort();
  for (const code of barcodes) {
    const existing = await tx.barcode.findUnique({ where: { businessId_code: { businessId: targetBusinessId, code } } }).catch(() => null);
    if (existing && existing.productId !== productId) {
      return conflict("duplicate_change", `Barcode ${code} already belongs to product ${existing.productId}.`, item);
    }
  }
  await tx.barcode.deleteMany({ where: { businessId: targetBusinessId, productId } });
  for (const code of barcodes) {
    await tx.barcode.create({
      data: {
        id: `${productId}_barcode_${code}`.slice(0, 120),
        businessId: targetBusinessId,
        productId,
        code
      }
    });
  }
  return null;
}

async function applyProduct(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await ensureSameBusinessById(tx, "product", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const brandId = maybeString(payload.brandId);
  const taxRateId = maybeString(payload.taxRateId);
  const hasMediaRef = Object.prototype.hasOwnProperty.call(payload, "mediaRef");
  const mediaRef = maybeString(payload.mediaRef);
  if (brandId) {
    const brand = await tx.brand.findFirst({ where: { id: brandId, businessId: targetBusinessId }, select: { id: true } });
    if (!brand) return conflict("missing_dependency", `Brand ${brandId} is missing for Product ${id}.`, item);
  }
  if (taxRateId) {
    const taxRate = await tx.taxRate.findFirst({ where: { id: taxRateId, businessId: targetBusinessId }, select: { id: true } });
    if (!taxRate) return conflict("missing_dependency", `TaxRate ${taxRateId} is missing for Product ${id}.`, item);
  }
  const sku = asString(payload.sku);
  const bySku = await tx.product.findUnique({ where: { businessId_sku: { businessId: targetBusinessId, sku } } }).catch(() => null);
  if (bySku && bySku.id !== id) return conflict("duplicate_change", `SKU ${sku} already belongs to product ${bySku.id}.`, item);
  const existing = await tx.product.findFirst({ where: { id, businessId: targetBusinessId } });
  await tx.product.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      sku,
      name: asString(payload.name),
      category: asString(payload.category) || "General",
      brandId,
      taxRateId,
      priceCents: asInt(payload.priceCents),
      costCents: asInt(payload.costCents),
      stockOnHand: asInt(payload.stockOnHand),
      isActive: asBool(payload.isActive, true),
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      sku,
      name: asString(payload.name),
      category: asString(payload.category) || "General",
      brandId,
      taxRateId,
      priceCents: asInt(payload.priceCents),
      costCents: asInt(payload.costCents),
      isActive: asBool(payload.isActive, true),
      stockOnHand: existing?.stockOnHand ?? asInt(payload.stockOnHand),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  if (hasMediaRef) {
    await tx.$executeRaw`
      UPDATE "Product" SET "mediaRef" = ${mediaRef} WHERE "businessId" = ${targetBusinessId} AND "id" = ${id}
    `;
  }
  return replaceProductBarcodes(tx, item, targetBusinessId, id, payload.barcodes);
}

async function rawBusinessConflict(tx: any, table: "ModifierGroup" | "ModifierOption" | "ProductModifierGroup", id: string, targetBusinessId: string, item: CatalogDeltaRecord) {
  const rows = await tx.$queryRawUnsafe(`SELECT "businessId" FROM "${table}" WHERE "id" = ? LIMIT 1`, id) as Array<{ businessId: string }>;
  if (rows[0] && rows[0].businessId !== targetBusinessId) return conflict("invalid_schema", `${table} ${id} belongs to another business.`, item);
  return null;
}

async function applyModifierGroup(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await rawBusinessConflict(tx, "ModifierGroup", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const name = asString(payload.name);
  const now = date(item.occurredAt);
  await tx.$executeRaw`
    INSERT INTO "ModifierGroup" ("id", "businessId", "name", "minSelections", "maxSelections", "status", "sortOrder", "version", "createdAt", "updatedAt")
    VALUES (${id}, ${targetBusinessId}, ${name}, ${Math.max(0, asInt(payload.minSelections))}, ${Math.max(1, asInt(payload.maxSelections, 1))}, ${asString(payload.status) || "ACTIVE"}, ${asInt(payload.sortOrder)}, ${Math.max(1, asInt(payload.version, 1))}, ${date(payload.createdAt, now)}, ${date(payload.updatedAt, now)})
    ON CONFLICT("id") DO UPDATE SET "name" = excluded."name", "minSelections" = excluded."minSelections", "maxSelections" = excluded."maxSelections", "status" = excluded."status", "sortOrder" = excluded."sortOrder", "version" = excluded."version", "updatedAt" = excluded."updatedAt"
  `;
  return null;
}

async function applyModifierOption(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const modifierGroupId = asString(payload.modifierGroupId);
  const idConflict = await rawBusinessConflict(tx, "ModifierOption", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const groups = await tx.$queryRaw`SELECT "id" FROM "ModifierGroup" WHERE "id" = ${modifierGroupId} AND "businessId" = ${targetBusinessId} LIMIT 1` as Array<{ id: string }>;
  if (!groups[0]) return conflict("missing_dependency", `ModifierGroup ${modifierGroupId} is missing for ModifierOption ${id}.`, item);
  const now = date(item.occurredAt);
  await tx.$executeRaw`
    INSERT INTO "ModifierOption" ("id", "businessId", "modifierGroupId", "name", "priceDeltaCents", "isDefault", "status", "sortOrder", "version", "createdAt", "updatedAt")
    VALUES (${id}, ${targetBusinessId}, ${modifierGroupId}, ${asString(payload.name)}, ${asInt(payload.priceDeltaCents)}, ${asBool(payload.isDefault)}, ${asString(payload.status) || "ACTIVE"}, ${asInt(payload.sortOrder)}, ${Math.max(1, asInt(payload.version, 1))}, ${date(payload.createdAt, now)}, ${date(payload.updatedAt, now)})
    ON CONFLICT("id") DO UPDATE SET "name" = excluded."name", "priceDeltaCents" = excluded."priceDeltaCents", "isDefault" = excluded."isDefault", "status" = excluded."status", "sortOrder" = excluded."sortOrder", "version" = excluded."version", "updatedAt" = excluded."updatedAt"
  `;
  return null;
}

async function applyProductModifierGroup(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const productId = asString(payload.productId);
  const modifierGroupId = asString(payload.modifierGroupId);
  const idConflict = await rawBusinessConflict(tx, "ProductModifierGroup", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const [products, groups] = await Promise.all([
    tx.product.findFirst({ where: { id: productId, businessId: targetBusinessId }, select: { id: true } }),
    tx.$queryRaw`SELECT "id" FROM "ModifierGroup" WHERE "id" = ${modifierGroupId} AND "businessId" = ${targetBusinessId} LIMIT 1` as Promise<Array<{ id: string }>>
  ]);
  if (!products) return conflict("missing_dependency", `Product ${productId} is missing for ProductModifierGroup ${id}.`, item);
  if (!groups[0]) return conflict("missing_dependency", `ModifierGroup ${modifierGroupId} is missing for ProductModifierGroup ${id}.`, item);
  const now = date(item.occurredAt);
  await tx.$executeRaw`
    INSERT INTO "ProductModifierGroup" ("id", "businessId", "productId", "modifierGroupId", "required", "sortOrder", "status", "version", "createdAt", "updatedAt")
    VALUES (${id}, ${targetBusinessId}, ${productId}, ${modifierGroupId}, ${asBool(payload.required)}, ${asInt(payload.sortOrder)}, ${asString(payload.status) || "ACTIVE"}, ${Math.max(1, asInt(payload.version, 1))}, ${date(payload.createdAt, now)}, ${date(payload.updatedAt, now)})
    ON CONFLICT("id") DO UPDATE SET "required" = excluded."required", "sortOrder" = excluded."sortOrder", "status" = excluded."status", "version" = excluded."version", "updatedAt" = excluded."updatedAt"
  `;
  return null;
}

async function applyProductSupplier(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const productId = asString(payload.productId);
  const supplierId = asString(payload.supplierId);
  const idConflict = await ensureSameBusinessById(tx, "productSupplier", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const [product, supplier] = await Promise.all([
    tx.product.findFirst({ where: { id: productId, businessId: targetBusinessId }, select: { id: true } }),
    tx.supplier.findFirst({ where: { id: supplierId, businessId: targetBusinessId }, select: { id: true } })
  ]);
  if (!product) return conflict("missing_dependency", `Product ${productId} is missing for ProductSupplier ${id}.`, item);
  if (!supplier) return conflict("missing_dependency", `Supplier ${supplierId} is missing for ProductSupplier ${id}.`, item);
  if (asBool(payload.isPrimary)) {
    await tx.productSupplier.updateMany({ where: { businessId: targetBusinessId, productId, NOT: { id } }, data: { isPrimary: false } });
  }
  await tx.productSupplier.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      productId,
      supplierId,
      isPrimary: asBool(payload.isPrimary),
      status: asString(payload.status) || "ACTIVE",
      leadTimeDays: payload.leadTimeDays === null || payload.leadTimeDays === undefined ? null : asInt(payload.leadTimeDays),
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      isPrimary: asBool(payload.isPrimary),
      status: asString(payload.status) || "ACTIVE",
      leadTimeDays: payload.leadTimeDays === null || payload.leadTimeDays === undefined ? null : asInt(payload.leadTimeDays),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applyPriceList(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await ensureSameBusinessById(tx, "priceList", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const name = asString(payload.name);
  const byName = await tx.priceList.findUnique({ where: { businessId_name: { businessId: targetBusinessId, name } } }).catch(() => null);
  if (byName && byName.id !== id) return conflict("duplicate_change", `PriceList name ${name} already belongs to ${byName.id}.`, item);
  await tx.priceList.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      name,
      currency: asString(payload.currency) || "MXN",
      isDefault: asBool(payload.isDefault),
      isActive: asBool(payload.isActive, true),
      startsAt: date(payload.startsAt, date(item.occurredAt)),
      endsAt: payload.endsAt ? date(payload.endsAt) : null,
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      name,
      currency: asString(payload.currency) || "MXN",
      isDefault: asBool(payload.isDefault),
      isActive: asBool(payload.isActive, true),
      startsAt: date(payload.startsAt, date(item.occurredAt)),
      endsAt: payload.endsAt ? date(payload.endsAt) : null,
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applyPriceListItem(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const priceListId = asString(payload.priceListId);
  const productId = asString(payload.productId);
  const idConflict = await ensureSameBusinessById(tx, "priceListItem", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const [priceList, product] = await Promise.all([
    tx.priceList.findFirst({ where: { id: priceListId, businessId: targetBusinessId }, select: { id: true } }),
    tx.product.findFirst({ where: { id: productId, businessId: targetBusinessId }, select: { id: true } })
  ]);
  if (!priceList) return conflict("missing_dependency", `PriceList ${priceListId} is missing for PriceListItem ${id}.`, item);
  if (!product) return conflict("missing_dependency", `Product ${productId} is missing for PriceListItem ${id}.`, item);
  await tx.priceListItem.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      priceListId,
      productId,
      priceCents: asInt(payload.priceCents),
      startsAt: date(payload.startsAt, date(item.occurredAt)),
      endsAt: payload.endsAt ? date(payload.endsAt) : null,
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      priceCents: asInt(payload.priceCents),
      startsAt: date(payload.startsAt, date(item.occurredAt)),
      endsAt: payload.endsAt ? date(payload.endsAt) : null,
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applyDropdownCatalog(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const idConflict = await ensureSameBusinessById(tx, "dropdownCatalog", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const code = asString(payload.code);
  const byCode = await tx.dropdownCatalog.findUnique({ where: { businessId_code: { businessId: targetBusinessId, code } } }).catch(() => null);
  if (byCode && byCode.id !== id) return conflict("duplicate_change", `DropdownCatalog code ${code} already belongs to ${byCode.id}.`, item);
  await tx.dropdownCatalog.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      code,
      label: asString(payload.label),
      description: maybeString(payload.description),
      status: asString(payload.status) || "ACTIVE",
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      code,
      label: asString(payload.label),
      description: maybeString(payload.description),
      status: asString(payload.status) || "ACTIVE",
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applyDropdownOption(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  const payload = item.payload;
  const id = asString(payload.id) || item.entityId;
  const catalogId = asString(payload.catalogId);
  const idConflict = await ensureSameBusinessById(tx, "dropdownOption", id, targetBusinessId, item);
  if (idConflict) return idConflict;
  const catalog = await tx.dropdownCatalog.findFirst({ where: { id: catalogId, businessId: targetBusinessId }, select: { id: true } });
  if (!catalog) return conflict("missing_dependency", `DropdownCatalog ${catalogId} is missing for DropdownOption ${id}.`, item);
  await tx.dropdownOption.upsert({
    where: { id },
    create: {
      id,
      businessId: targetBusinessId,
      catalogId,
      code: asString(payload.code),
      label: asString(payload.label),
      sortOrder: asInt(payload.sortOrder),
      isDefault: asBool(payload.isDefault),
      status: asString(payload.status) || "ACTIVE",
      metadataJson: maybeString(payload.metadataJson),
      createdAt: date(payload.createdAt, date(item.occurredAt)),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    },
    update: {
      code: asString(payload.code),
      label: asString(payload.label),
      sortOrder: asInt(payload.sortOrder),
      isDefault: asBool(payload.isDefault),
      status: asString(payload.status) || "ACTIVE",
      metadataJson: maybeString(payload.metadataJson),
      updatedAt: date(payload.updatedAt, date(item.occurredAt))
    }
  });
  return null;
}

async function applyOne(tx: any, item: CatalogDeltaRecord, targetBusinessId: string) {
  if (item.entityType === "TaxRate") return applyTaxRate(tx, item, targetBusinessId);
  if (item.entityType === "Brand") return applyBrand(tx, item, targetBusinessId);
  if (item.entityType === "Supplier") return applySupplier(tx, item, targetBusinessId);
  if (item.entityType === "Product") return applyProduct(tx, item, targetBusinessId);
  if (item.entityType === "ModifierGroup") return applyModifierGroup(tx, item, targetBusinessId);
  if (item.entityType === "ModifierOption") return applyModifierOption(tx, item, targetBusinessId);
  if (item.entityType === "ProductModifierGroup") return applyProductModifierGroup(tx, item, targetBusinessId);
  if (item.entityType === "ProductSupplier") return applyProductSupplier(tx, item, targetBusinessId);
  if (item.entityType === "PriceList") return applyPriceList(tx, item, targetBusinessId);
  if (item.entityType === "PriceListItem") return applyPriceListItem(tx, item, targetBusinessId);
  if (item.entityType === "DropdownCatalog") return applyDropdownCatalog(tx, item, targetBusinessId);
  if (item.entityType === "DropdownOption") return applyDropdownOption(tx, item, targetBusinessId);
  return conflict("unknown_entity", `Unsupported entity ${item.entityType}.`, item, "rejected");
}

function orderedChanges(envelope: CatalogDeltaEnvelope) {
  return [...envelope.changes].sort((a, b) => {
    const rank = (ENTITY_RANK.get(a.entityType) ?? 999) - (ENTITY_RANK.get(b.entityType) ?? 999);
    if (rank !== 0) return rank;
    return a.cursor.localeCompare(b.cursor);
  });
}

export async function applyCatalogDeltaEnvelope(envelopeInput: unknown, input: TabletCatalogPullInput = {}): Promise<TabletCatalogPullResult> {
  const validation = validateCatalogDeltaEnvelope(envelopeInput);
  const targetBusinessId = asString(input.targetBusinessId) || DEFAULT_POS_API_BUSINESS_ID;
  const terminalId = asString(input.terminalId) || DEFAULT_POS_API_TERMINAL_ID;
  const mode = normalizeMode(input.mode || validation.envelope?.mode);
  const key = scopeKey({ sourceBusinessId: validation.envelope?.businessId ?? input.pcBusinessId, targetBusinessId, terminalId, storeId: input.storeId });
  const checkpointBefore = await readCheckpoint(targetBusinessId, key);
  const cursorBefore = input.resetCheckpoint ? null : asString(input.cursor) || checkpointBefore?.cursorValue || null;

  if (!validation.envelope) {
    const attemptId = randomUUID();
    const now = new Date();
    const findings = validation.findings.map(sanitizedFinding);
    const checkpoint = await upsertCheckpoint({
      targetBusinessId,
      key,
      terminalId,
      sourceBusinessId: input.pcBusinessId ?? null,
      cursor: cursorBefore,
      lastEventId: null,
      attemptId,
      status: "rejected",
      lifecycleStatus: "dead_letter",
      lastAttemptedAt: now,
      lastSuccessfulAt: checkpointBefore?.lastSuccessfulAt ?? null,
      metadata: { mode, findings, error: "invalid_payload" }
    });
    return baseResult({
      ok: false,
      reason: "invalid_payload",
      mode,
      sourceBusinessId: input.pcBusinessId ?? null,
      targetBusinessId,
      terminalId,
      cursorBefore,
      cursorAfter: cursorBefore,
      checkpoint,
      counts: emptyCounts(),
      findings,
      errors: ["Payload PC -> Tablet catalog delta rejected by shared validator."],
      healthStatus: "invalid_payload"
    });
  }

  const envelope = validation.envelope;
  const findings: CatalogDeltaFinding[] = validation.findings.map(sanitizedFinding);
  const seen = new Set<string>();
  const counts = emptyCounts();
  counts.received = envelope.changes.length;
  let lastAppliedCursor = cursorBefore;
  let lastEventId: string | null = null;

  await (prisma as any).$transaction(async (tx: any) => {
    await ensureTargetBusiness(tx, targetBusinessId);
    for (const item of orderedChanges(envelope)) {
      counts.byEntity[item.entityType] = (counts.byEntity[item.entityType] ?? 0) + 1;
      if (seen.has(item.changeId) || (cursorBefore && item.cursor <= cursorBefore)) {
        counts.duplicate += 1;
        seen.add(item.changeId);
        continue;
      }
      seen.add(item.changeId);
      const itemConflict = await applyOne(tx, item, targetBusinessId);
      if (itemConflict) {
        const sanitized = sanitizedFinding(itemConflict);
        findings.push(sanitized);
        if (sanitized.severity === "rejected") counts.rejected += 1;
        else counts.conflict += 1;
        continue;
      }
      counts.applied += 1;
      if (!lastAppliedCursor || item.cursor > lastAppliedCursor) lastAppliedCursor = item.cursor;
      lastEventId = item.changeId;
    }
  });

  const failed = counts.rejected + counts.conflict;
  const ok = failed === 0;
  const cursorAfter = ok ? envelope.cursor.to ?? lastAppliedCursor : cursorBefore;
  const now = new Date();
  const attemptId = randomUUID();
  const status = ok ? (counts.applied > 0 ? "applied" : "empty") : "partial";
  const checkpoint = await upsertCheckpoint({
    targetBusinessId,
    key,
    terminalId,
    sourceBusinessId: envelope.businessId,
    cursor: cursorAfter,
    lastEventId,
    attemptId,
    status,
    lifecycleStatus: ok ? "reconciled" : "conflict",
    lastAttemptedAt: now,
    lastSuccessfulAt: ok ? now : checkpointBefore?.lastSuccessfulAt ?? null,
    metadata: {
      mode: envelope.mode,
      sourceBusinessId: envelope.businessId,
      counts,
      cursorBefore,
      attemptedCursor: envelope.cursor.to,
      findings: findings.map(sanitizedFinding),
      safeToContinueSelling: true,
      stockPolicy: "Product.stockOnHand set on create only; local Tablet sale stock is not reset on catalog update."
    }
  });

  return baseResult({
    ok,
    reason: ok ? status : "partial",
    mode: envelope.mode,
    sourceBusinessId: envelope.businessId,
    targetBusinessId,
    terminalId,
    cursorBefore,
    cursorAfter,
    checkpoint,
    counts,
    findings,
    errors: ok ? [] : findings.map((item) => item.detail),
    healthStatus: ok ? "applied" : "partial"
  });
}

function emptyCounts(): TabletCatalogPullCounts {
  return { received: 0, applied: 0, rejected: 0, conflict: 0, duplicate: 0, byEntity: {} };
}

async function upsertCheckpoint(input: {
  targetBusinessId: string;
  key: string;
  terminalId: string;
  sourceBusinessId: string | null;
  cursor: string | null;
  lastEventId: string | null;
  attemptId: string;
  status: string;
  lifecycleStatus: string;
  lastAttemptedAt: Date;
  lastSuccessfulAt: Date | string | null;
  metadata: Record<string, unknown>;
}) {
  const db = prisma as any;
  await db.business.upsert({
    where: { id: input.targetBusinessId },
    update: {},
    create: { id: input.targetBusinessId, name: "PRISMA Tablet Local", taxId: null, currency: "MXN" }
  });
  const row = await db.syncCheckpoint.upsert({
    where: { businessId_scopeKey_stream: { businessId: input.targetBusinessId, scopeKey: input.key, stream: CATALOG_DELTA_STREAM } },
    create: {
      id: `sync_checkpoint_${randomUUID()}`,
      businessId: input.targetBusinessId,
      source: CATALOG_PULL_SOURCE,
      scopeKey: input.key,
      deviceId: input.terminalId,
      terminalId: input.terminalId,
      stream: CATALOG_DELTA_STREAM,
      cursorValue: input.cursor,
      lastEventId: input.lastEventId,
      lastIdempotencyKey: input.lastEventId,
      lastAttemptId: input.attemptId,
      status: input.status,
      lifecycleStatus: input.lifecycleStatus,
      checkpointAt: new Date(),
      lastAttemptedAt: input.lastAttemptedAt,
      lastSuccessfulAt: input.lastSuccessfulAt ? date(input.lastSuccessfulAt) : null,
      metadataJson: JSON.stringify(input.metadata)
    },
    update: {
      cursorValue: input.cursor,
      lastEventId: input.lastEventId,
      lastIdempotencyKey: input.lastEventId,
      lastAttemptId: input.attemptId,
      status: input.status,
      lifecycleStatus: input.lifecycleStatus,
      checkpointAt: new Date(),
      lastAttemptedAt: input.lastAttemptedAt,
      lastSuccessfulAt: input.lastSuccessfulAt ? date(input.lastSuccessfulAt) : null,
      metadataJson: JSON.stringify(input.metadata)
    }
  });
  return checkpointView(row);
}

function baseResult(input: Omit<TabletCatalogPullResult, "stream" | "health"> & { healthStatus: TabletCatalogPullResult["health"]["status"]; httpStatus?: number; url?: string | null; config?: PrismaTabletPcOriginConfig }): TabletCatalogPullResult {
  return {
    ok: input.ok,
    reason: input.reason,
    mode: input.mode,
    stream: CATALOG_DELTA_STREAM,
    sourceBusinessId: input.sourceBusinessId,
    targetBusinessId: input.targetBusinessId,
    terminalId: input.terminalId,
    cursorBefore: input.cursorBefore,
    cursorAfter: input.cursorAfter,
    checkpoint: input.checkpoint,
    counts: input.counts,
    findings: input.findings.map(sanitizedFinding),
    errors: input.errors.map((error) => error.slice(0, 500)),
    health: {
      enabled: input.config?.enabled ?? false,
      origin: input.config?.origin ?? null,
      url: input.url ?? null,
      status: input.healthStatus,
      ...(input.httpStatus ? { httpStatus: input.httpStatus } : {})
    }
  };
}

async function fetchCatalogDelta(config: PrismaTabletPcOriginConfig, input: TabletCatalogPullInput, cursor: string | null, mode: CatalogDeltaMode) {
  const sourceBusinessId = asString(input.pcBusinessId) || undefined;
  const targetBusinessId = asString(input.targetBusinessId) || DEFAULT_POS_API_BUSINESS_ID;
  const url = pcUrl(config, "/api/sync/export/catalog-delta");
  if (!url) return { ok: false as const, reason: "missing_pc_origin", url: null, status: 0, payload: null };
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.timeoutMs || DEFAULT_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      method: "POST",
      cache: "no-store",
      signal: controller.signal,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        mode,
        cursor,
        businessId: sourceBusinessId,
        terminalId: asString(input.terminalId) || DEFAULT_POS_API_TERMINAL_ID,
        storeId: asString(input.storeId) || undefined,
        target: "tablet",
        targetBusinessId,
        limit: normalizeLimit(input.limit),
        requestedBy: asString(input.requestedBy) || "tablet-operator"
      })
    });
    const payload = await response.json().catch(() => null);
    return { ok: response.ok, reason: response.ok ? "ok" : "pc_http_error", url, status: response.status, payload };
  } catch (error) {
    return { ok: false as const, reason: error instanceof Error ? error.message : "pc_unavailable", url, status: 0, payload: null };
  } finally {
    clearTimeout(timeout);
  }
}

export async function pullCatalogDeltaFromPc(input: TabletCatalogPullInput = {}): Promise<TabletCatalogPullResult> {
  const config = input.config ?? loadPrismaTabletPcOriginConfig();
  const mode = normalizeMode(input.mode);
  const targetBusinessId = asString(input.targetBusinessId) || DEFAULT_POS_API_BUSINESS_ID;
  const terminalId = asString(input.terminalId) || DEFAULT_POS_API_TERMINAL_ID;
  const key = scopeKey({ sourceBusinessId: input.pcBusinessId, targetBusinessId, terminalId, storeId: input.storeId });
  const checkpoint = await readCheckpoint(targetBusinessId, key);
  const cursor = input.resetCheckpoint || mode !== "delta" ? null : asString(input.cursor) || checkpoint?.cursorValue || null;

  if (!config.enabled) {
    return baseResult({
      ok: false,
      reason: "pc_sync_disabled",
      mode,
      sourceBusinessId: input.pcBusinessId ?? null,
      targetBusinessId,
      terminalId,
      cursorBefore: cursor,
      cursorAfter: cursor,
      checkpoint: checkpointView(checkpoint),
      counts: emptyCounts(),
      findings: [],
      errors: ["PC sync is disabled in Tablet runtime config; local POS remains available."],
      healthStatus: "disabled",
      config
    });
  }

  const fetched = await fetchCatalogDelta(config, input, cursor, mode);
  if (!fetched.ok || !fetched.payload) {
    return baseResult({
      ok: false,
      reason: fetched.reason === "missing_pc_origin" ? "missing_pc_origin" : "pc_unavailable",
      mode,
      sourceBusinessId: input.pcBusinessId ?? null,
      targetBusinessId,
      terminalId,
      cursorBefore: cursor,
      cursorAfter: cursor,
      checkpoint: checkpointView(checkpoint),
      counts: emptyCounts(),
      findings: [],
      errors: [`PC catalog export unavailable: ${fetched.reason}.`],
      healthStatus: fetched.reason === "missing_pc_origin" ? "missing_origin" : "offline",
      httpStatus: fetched.status || undefined,
      url: fetched.url,
      config
    });
  }

  const envelope = fetched.payload?.ok === true && fetched.payload?.data ? fetched.payload.data : fetched.payload;
  const applied = await applyCatalogDeltaEnvelope(envelope, {
    ...input,
    mode,
    targetBusinessId,
    terminalId,
    cursor,
    config
  });
  return {
    ...applied,
    health: {
      ...applied.health,
      enabled: config.enabled,
      origin: config.origin,
      url: fetched.url,
      httpStatus: fetched.status,
      status: applied.ok ? "applied" : applied.health.status
    }
  };
}

export async function getTabletCatalogPullStatus(input: TabletCatalogPullInput = {}): Promise<TabletCatalogPullStatus> {
  const config = input.config ?? loadPrismaTabletPcOriginConfig();
  const targetBusinessId = asString(input.targetBusinessId) || DEFAULT_POS_API_BUSINESS_ID;
  const terminalId = asString(input.terminalId) || DEFAULT_POS_API_TERMINAL_ID;
  const key = scopeKey({ sourceBusinessId: input.pcBusinessId, targetBusinessId, terminalId, storeId: input.storeId });
  const db = prisma as any;
  const [
    checkpoint,
    taxRates,
    brands,
    suppliers,
    products,
    productSuppliers,
    priceLists,
    priceListItems,
    dropdownCatalogs,
    dropdownOptions
  ] = await Promise.all([
    readCheckpoint(targetBusinessId, key),
    db.taxRate.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.brand.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.supplier.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.product.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.productSupplier.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.priceList.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.priceListItem.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.dropdownCatalog.count({ where: { businessId: targetBusinessId } }).catch(() => 0),
    db.dropdownOption.count({ where: { businessId: targetBusinessId } }).catch(() => 0)
  ]);
  return {
    stream: CATALOG_DELTA_STREAM,
    targetBusinessId,
    terminalId,
    pc: {
      enabled: config.enabled,
      origin: config.origin,
      exportPath: "/api/sync/export/catalog-delta"
    },
    checkpoint: checkpointView(checkpoint),
    tableCounts: {
      TaxRate: taxRates,
      Brand: brands,
      Supplier: suppliers,
      Product: products,
      ProductSupplier: productSuppliers,
      PriceList: priceLists,
      PriceListItem: priceListItems,
      DropdownCatalog: dropdownCatalogs,
      DropdownOption: dropdownOptions
    }
  };
}

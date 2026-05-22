import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import {
  CATALOG_DELTA_CONTRACT_ID,
  CATALOG_DELTA_SCHEMA_VERSION,
  CATALOG_DELTA_STREAM,
  catalogDeltaCountByEntity,
  validateCatalogDeltaEnvelope,
  type CatalogDeltaEnvelope,
  type CatalogDeltaEntityType,
  type CatalogDeltaMode,
  type CatalogDeltaRecord
} from "@shared-kernel/sync/catalog-delta";

const DEFAULT_BUSINESS_ID = "biz_hitech_default";
const DEFAULT_LIMIT = 500;
const ENTITY_ORDER: CatalogDeltaEntityType[] = [
  "TaxRate",
  "Brand",
  "Supplier",
  "Product",
  "ProductSupplier",
  "PriceList",
  "PriceListItem",
  "DropdownCatalog",
  "DropdownOption"
];
const ENTITY_RANK = new Map(ENTITY_ORDER.map((entity, index) => [entity, index + 1]));
const EXPORT_AUDIT_TOPIC = "pc.catalog.delta.exported";

export type PcCatalogDeltaExportInput = {
  businessId?: string | null;
  terminalId?: string | null;
  storeId?: string | null;
  target?: string | null;
  cursor?: string | null;
  mode?: CatalogDeltaMode | string | null;
  limit?: number | string | null;
  requestedBy?: string | null;
};

export type PcCatalogDeltaStatus = {
  stream: typeof CATALOG_DELTA_STREAM;
  businessId: string;
  supportedEntities: CatalogDeltaEntityType[];
  latestExport: null | {
    id: string;
    mode: string | null;
    target: string | null;
    cursor: string | null;
    total: number;
    byEntity: Record<string, number>;
    createdAt: string;
    status: string;
  };
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
  if (!Number.isFinite(parsed)) return DEFAULT_LIMIT;
  return Math.max(1, Math.min(Math.trunc(parsed), 2000));
}

function iso(value: unknown) {
  if (value instanceof Date) return value.toISOString();
  const date = new Date(String(value || ""));
  return Number.isNaN(date.getTime()) ? new Date(0).toISOString() : date.toISOString();
}

function cleanObject<T extends Record<string, unknown>>(value: T): T {
  return Object.fromEntries(Object.entries(value).filter(([, field]) => field !== undefined)) as T;
}

function cursorFor(entityType: CatalogDeltaEntityType, entityId: string, updatedAt: unknown) {
  const rank = String(ENTITY_RANK.get(entityType) ?? 99).padStart(2, "0");
  return `${iso(updatedAt)}~${rank}~${entityId}`;
}

function changeIdFor(entityType: CatalogDeltaEntityType, entityId: string, updatedAt: unknown) {
  return `${CATALOG_DELTA_STREAM}:${entityType}:${entityId}:${iso(updatedAt)}`;
}

function dateOrNull(value: unknown) {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(String(value));
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function mapRecord(entityType: CatalogDeltaEntityType, row: any, payload: Record<string, unknown>): CatalogDeltaRecord {
  const cursor = cursorFor(entityType, row.id, row.updatedAt ?? row.createdAt);
  return {
    changeId: changeIdFor(entityType, row.id, row.updatedAt ?? row.createdAt),
    entityType,
    entityId: row.id,
    businessId: row.businessId,
    operation: "upsert",
    occurredAt: iso(row.updatedAt ?? row.createdAt),
    cursor,
    payload
  };
}

function mapTaxRate(row: any) {
  return mapRecord("TaxRate", row, {
    id: row.id,
    businessId: row.businessId,
    name: row.name,
    rateBps: row.rateBps,
    isDefault: row.isDefault,
    isActive: row.isActive,
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  });
}

function mapBrand(row: any) {
  return mapRecord("Brand", row, cleanObject({
    id: row.id,
    businessId: row.businessId,
    name: row.name,
    description: row.description,
    status: row.status,
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  }));
}

function mapSupplier(row: any) {
  return mapRecord("Supplier", row, {
    id: row.id,
    businessId: row.businessId,
    name: row.name,
    status: row.status,
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  });
}

function mapProduct(row: any) {
  return mapRecord("Product", row, cleanObject({
    id: row.id,
    businessId: row.businessId,
    sku: row.sku,
    name: row.name,
    category: row.category,
    brandId: row.brandId,
    taxRateId: row.taxRateId,
    priceCents: row.priceCents,
    costCents: row.costCents,
    stockOnHand: row.stockOnHand,
    isActive: row.isActive,
    barcodes: Array.isArray(row.barcodes) ? row.barcodes.map((item: any) => String(item.code)).filter(Boolean).sort() : [],
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  }));
}

function mapProductSupplier(row: any) {
  return mapRecord("ProductSupplier", row, {
    id: row.id,
    businessId: row.businessId,
    productId: row.productId,
    supplierId: row.supplierId,
    isPrimary: row.isPrimary,
    status: row.status,
    leadTimeDays: row.leadTimeDays,
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  });
}

function mapPriceList(row: any) {
  return mapRecord("PriceList", row, cleanObject({
    id: row.id,
    businessId: row.businessId,
    name: row.name,
    currency: row.currency,
    isDefault: row.isDefault,
    isActive: row.isActive,
    startsAt: iso(row.startsAt),
    endsAt: dateOrNull(row.endsAt),
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  }));
}

function mapPriceListItem(row: any) {
  return mapRecord("PriceListItem", row, cleanObject({
    id: row.id,
    businessId: row.businessId,
    priceListId: row.priceListId,
    productId: row.productId,
    priceCents: row.priceCents,
    startsAt: iso(row.startsAt),
    endsAt: dateOrNull(row.endsAt),
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  }));
}

function mapDropdownCatalog(row: any) {
  return mapRecord("DropdownCatalog", row, cleanObject({
    id: row.id,
    businessId: row.businessId,
    code: row.code,
    label: row.label,
    description: row.description,
    status: row.status,
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  }));
}

function mapDropdownOption(row: any) {
  return mapRecord("DropdownOption", row, cleanObject({
    id: row.id,
    businessId: row.businessId,
    catalogId: row.catalogId,
    code: row.code,
    label: row.label,
    sortOrder: row.sortOrder,
    isDefault: row.isDefault,
    status: row.status,
    metadataJson: row.metadataJson,
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  }));
}

async function resolveBusinessId(input?: string | null) {
  const explicit = asString(input);
  if (explicit) return explicit;
  const db = prisma as any;
  const business = await db.business.findFirst({ select: { id: true }, orderBy: { createdAt: "asc" } }).catch(() => null);
  return business?.id ?? DEFAULT_BUSINESS_ID;
}

async function collectCatalogRecords(businessId: string): Promise<CatalogDeltaRecord[]> {
  const db = prisma as any;
  const [
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
    db.taxRate.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.brand.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.supplier.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.product.findMany({ where: { businessId }, include: { barcodes: true }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.productSupplier.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.priceList.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.priceListItem.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.dropdownCatalog.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] }),
    db.dropdownOption.findMany({ where: { businessId }, orderBy: [{ updatedAt: "asc" }, { id: "asc" }] })
  ]);

  return [
    ...taxRates.map(mapTaxRate),
    ...brands.map(mapBrand),
    ...suppliers.map(mapSupplier),
    ...products.map(mapProduct),
    ...productSuppliers.map(mapProductSupplier),
    ...priceLists.map(mapPriceList),
    ...priceListItems.map(mapPriceListItem),
    ...dropdownCatalogs.map(mapDropdownCatalog),
    ...dropdownOptions.map(mapDropdownOption)
  ].sort((a, b) => a.cursor.localeCompare(b.cursor));
}

function validateCursor(value: string | null) {
  if (!value) return;
  if (!/^\d{4}-\d{2}-\d{2}T/.test(value) || !value.includes("~")) {
    throw new Error("CATALOG_DELTA_INVALID_CURSOR");
  }
}

export async function buildPcCatalogDelta(input: PcCatalogDeltaExportInput = {}): Promise<CatalogDeltaEnvelope> {
  const businessId = await resolveBusinessId(input.businessId);
  const mode = normalizeMode(input.mode);
  const limit = normalizeLimit(input.limit);
  const requestedCursor = mode === "delta" ? asString(input.cursor) || null : null;
  validateCursor(requestedCursor);

  const allRecords = await collectCatalogRecords(businessId);
  const filtered = requestedCursor ? allRecords.filter((record) => record.cursor > requestedCursor) : allRecords;
  const changes = filtered.slice(0, limit);
  const lastCursor = changes.at(-1)?.cursor ?? requestedCursor;
  const envelope: CatalogDeltaEnvelope = {
    contractId: CATALOG_DELTA_CONTRACT_ID,
    schemaVersion: CATALOG_DELTA_SCHEMA_VERSION,
    stream: CATALOG_DELTA_STREAM,
    mode,
    businessId,
    generatedAt: new Date().toISOString(),
    scope: {
      businessId,
      terminalId: asString(input.terminalId) || null,
      storeId: asString(input.storeId) || null,
      target: asString(input.target) || "tablet"
    },
    cursor: {
      requested: requestedCursor,
      from: requestedCursor,
      to: lastCursor,
      hasMore: filtered.length > changes.length,
      checkpointStrategy: "updatedAt_entityRank_id"
    },
    changes,
    counts: {
      total: changes.length,
      byEntity: catalogDeltaCountByEntity(changes)
    },
    diagnostics: {
      source: "pc-canonical-db",
      validator: CATALOG_DELTA_CONTRACT_ID,
      ordering: "updatedAt_entityRank_id",
      notes: [
        mode === "delta" ? "Incremental export uses cursor > requested cursor." : "Full export ignores prior cursor by mode.",
        "PC export is read-only against catalog/master-data tables."
      ]
    }
  };

  const validation = validateCatalogDeltaEnvelope(envelope);
  if (!validation.envelope || validation.findings.some((finding) => finding.severity === "rejected")) {
    const detail = validation.findings.map((finding) => finding.detail).join(" | ");
    throw new Error(`CATALOG_DELTA_CONTRACT_INVALID: ${detail}`);
  }
  return validation.envelope;
}

export async function recordPcCatalogDeltaExport(envelope: CatalogDeltaEnvelope, input: PcCatalogDeltaExportInput = {}) {
  const db = prisma as any;
  const auditEvent = await db.auditEvent.create({
    data: {
      id: `audit_${randomUUID()}`,
      businessId: envelope.businessId,
      actorId: null,
      topic: EXPORT_AUDIT_TOPIC,
      entityType: "CatalogDelta",
      entityId: envelope.cursor.to ?? `${CATALOG_DELTA_STREAM}:empty`,
      summary: `Catalog delta ${envelope.mode} generado para ${envelope.scope.target ?? "tablet"} con ${envelope.counts.total} cambio(s).`,
      beforeJson: null,
      afterJson: JSON.stringify({
        contractId: envelope.contractId,
        stream: envelope.stream,
        mode: envelope.mode,
        cursor: envelope.cursor,
        counts: envelope.counts,
        target: envelope.scope.target,
        terminalId: envelope.scope.terminalId,
        storeId: envelope.scope.storeId,
        requestedBy: input.requestedBy ?? "pc-operator"
      }),
      metadataJson: JSON.stringify({
        status: "generated",
        noFakeAck: true,
        safeToContinueSelling: true,
        generatedAt: envelope.generatedAt
      })
    }
  });
  return auditEvent;
}

export async function exportPcCatalogDelta(input: PcCatalogDeltaExportInput = {}, options: { recordAudit?: boolean } = {}) {
  const envelope = await buildPcCatalogDelta(input);
  const auditEvent = options.recordAudit ? await recordPcCatalogDeltaExport(envelope, input) : null;
  return { envelope, auditEventId: auditEvent?.id ?? null };
}

export async function getPcCatalogDeltaStatus(input: { businessId?: string | null } = {}): Promise<PcCatalogDeltaStatus> {
  const db = prisma as any;
  const businessId = await resolveBusinessId(input.businessId);
  const [
    latestExport,
    taxRateCount,
    brandCount,
    supplierCount,
    productCount,
    productSupplierCount,
    priceListCount,
    priceListItemCount,
    dropdownCatalogCount,
    dropdownOptionCount
  ] = await Promise.all([
    db.auditEvent.findFirst({ where: { businessId, topic: EXPORT_AUDIT_TOPIC }, orderBy: { createdAt: "desc" } }).catch(() => null),
    db.taxRate.count({ where: { businessId } }).catch(() => 0),
    db.brand.count({ where: { businessId } }).catch(() => 0),
    db.supplier.count({ where: { businessId } }).catch(() => 0),
    db.product.count({ where: { businessId } }).catch(() => 0),
    db.productSupplier.count({ where: { businessId } }).catch(() => 0),
    db.priceList.count({ where: { businessId } }).catch(() => 0),
    db.priceListItem.count({ where: { businessId } }).catch(() => 0),
    db.dropdownCatalog.count({ where: { businessId } }).catch(() => 0),
    db.dropdownOption.count({ where: { businessId } }).catch(() => 0)
  ]);
  const after = latestExport?.afterJson ? JSON.parse(latestExport.afterJson) : null;
  const meta = latestExport?.metadataJson ? JSON.parse(latestExport.metadataJson) : null;
  return {
    stream: CATALOG_DELTA_STREAM,
    businessId,
    supportedEntities: ENTITY_ORDER,
    latestExport: latestExport ? {
      id: latestExport.id,
      mode: after?.mode ?? null,
      target: after?.target ?? null,
      cursor: after?.cursor?.to ?? null,
      total: Number(after?.counts?.total ?? 0),
      byEntity: after?.counts?.byEntity ?? {},
      createdAt: iso(latestExport.createdAt),
      status: meta?.status ?? "generated"
    } : null,
    tableCounts: {
      TaxRate: taxRateCount,
      Brand: brandCount,
      Supplier: supplierCount,
      Product: productCount,
      ProductSupplier: productSupplierCount,
      PriceList: priceListCount,
      PriceListItem: priceListItemCount,
      DropdownCatalog: dropdownCatalogCount,
      DropdownOption: dropdownOptionCount
    }
  };
}

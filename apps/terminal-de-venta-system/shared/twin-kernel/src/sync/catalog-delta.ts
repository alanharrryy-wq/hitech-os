export const CATALOG_DELTA_CONTRACT_ID = "PRISMA_PC_TO_TABLET_CATALOG_DELTA_V1" as const;
export const CATALOG_DELTA_SCHEMA_VERSION = "1.0.0" as const;
export const CATALOG_DELTA_STREAM = "pc.catalog.delta.v1" as const;

export const CATALOG_DELTA_ENTITY_TYPES = [
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
] as const;

export const CATALOG_DELTA_MODES = ["delta", "bootstrap", "resync"] as const;
export const CATALOG_DELTA_OPERATIONS = ["upsert"] as const;

export type CatalogDeltaEntityType = (typeof CATALOG_DELTA_ENTITY_TYPES)[number];
export type CatalogDeltaMode = (typeof CATALOG_DELTA_MODES)[number];
export type CatalogDeltaOperation = (typeof CATALOG_DELTA_OPERATIONS)[number];

export type CatalogDeltaFindingSeverity = "warning" | "conflict" | "rejected";
export type CatalogDeltaFindingCode =
  | "duplicate_change"
  | "invalid_schema"
  | "missing_dependency"
  | "stale_cursor"
  | "unknown_entity";

export type CatalogDeltaFinding = {
  code: CatalogDeltaFindingCode;
  severity: CatalogDeltaFindingSeverity;
  entityType?: string | null;
  entityId?: string | null;
  changeId?: string | null;
  detail: string;
};

export type CatalogDeltaRecord = {
  changeId: string;
  entityType: CatalogDeltaEntityType;
  entityId: string;
  businessId: string;
  operation: CatalogDeltaOperation;
  occurredAt: string;
  cursor: string;
  payload: Record<string, unknown>;
};

export type CatalogDeltaCursor = {
  requested: string | null;
  from: string | null;
  to: string | null;
  hasMore: boolean;
  checkpointStrategy: "updatedAt_entityRank_id";
};

export type CatalogDeltaEnvelope = {
  contractId: typeof CATALOG_DELTA_CONTRACT_ID;
  schemaVersion: typeof CATALOG_DELTA_SCHEMA_VERSION;
  stream: typeof CATALOG_DELTA_STREAM;
  mode: CatalogDeltaMode;
  businessId: string;
  generatedAt: string;
  scope: {
    businessId: string;
    terminalId?: string | null;
    storeId?: string | null;
    target?: string | null;
  };
  cursor: CatalogDeltaCursor;
  changes: CatalogDeltaRecord[];
  counts: {
    total: number;
    byEntity: Record<string, number>;
  };
  diagnostics: {
    source: "pc-canonical-db";
    validator: typeof CATALOG_DELTA_CONTRACT_ID;
    ordering: CatalogDeltaCursor["checkpointStrategy"];
    notes: string[];
  };
};

const ENTITY_REQUIRED_FIELDS: Record<CatalogDeltaEntityType, string[]> = {
  TaxRate: ["id", "businessId", "name", "rateBps", "isDefault", "isActive"],
  Brand: ["id", "businessId", "name", "status"],
  Supplier: ["id", "businessId", "name", "status"],
  Product: ["id", "businessId", "sku", "name", "category", "priceCents", "costCents", "isActive"],
  ModifierGroup: ["id", "businessId", "name", "minSelections", "maxSelections", "status", "sortOrder", "version"],
  ModifierOption: ["id", "businessId", "modifierGroupId", "name", "priceDeltaCents", "isDefault", "status", "sortOrder", "version"],
  ProductModifierGroup: ["id", "businessId", "productId", "modifierGroupId", "required", "status", "sortOrder", "version"],
  ProductSupplier: ["id", "businessId", "productId", "supplierId", "isPrimary", "status"],
  PriceList: ["id", "businessId", "name", "currency", "isDefault", "isActive", "startsAt"],
  PriceListItem: ["id", "businessId", "priceListId", "productId", "priceCents", "startsAt"],
  DropdownCatalog: ["id", "businessId", "code", "label", "status"],
  DropdownOption: ["id", "businessId", "catalogId", "code", "label", "sortOrder", "isDefault", "status"]
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function isIsoDate(value: unknown) {
  return typeof value === "string" && value.trim() !== "" && !Number.isNaN(Date.parse(value));
}

function isKnownEntity(value: string): value is CatalogDeltaEntityType {
  return CATALOG_DELTA_ENTITY_TYPES.includes(value as CatalogDeltaEntityType);
}

function isKnownMode(value: string): value is CatalogDeltaMode {
  return CATALOG_DELTA_MODES.includes(value as CatalogDeltaMode);
}

function finding(input: CatalogDeltaFinding): CatalogDeltaFinding {
  return input;
}

export function catalogDeltaItemKey(item: Pick<CatalogDeltaRecord, "entityType" | "entityId">) {
  return `${item.entityType}:${item.entityId}`;
}

export function catalogDeltaCountByEntity(changes: Array<Pick<CatalogDeltaRecord, "entityType">>) {
  return changes.reduce<Record<string, number>>((acc, item) => {
    acc[item.entityType] = (acc[item.entityType] ?? 0) + 1;
    return acc;
  }, {});
}

export function validateCatalogDeltaRecord(input: unknown, envelopeBusinessId?: string): { record: CatalogDeltaRecord | null; findings: CatalogDeltaFinding[] } {
  const findings: CatalogDeltaFinding[] = [];
  if (!isRecord(input)) {
    return { record: null, findings: [finding({ code: "invalid_schema", severity: "rejected", detail: "Catalog delta item must be an object." })] };
  }

  const changeId = asString(input.changeId);
  const entityType = asString(input.entityType);
  const entityId = asString(input.entityId);
  const businessId = asString(input.businessId);
  const operation = asString(input.operation);
  const occurredAt = asString(input.occurredAt);
  const cursor = asString(input.cursor);
  const payload = isRecord(input.payload) ? input.payload : null;

  if (!changeId) findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, detail: "changeId is required." }));
  if (!isKnownEntity(entityType)) findings.push(finding({ code: "unknown_entity", severity: "rejected", entityType, entityId, changeId, detail: `Unsupported entityType: ${entityType || "(empty)"}.` }));
  if (!entityId) findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, changeId, detail: "entityId is required." }));
  if (!businessId) findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: "businessId is required." }));
  if (envelopeBusinessId && businessId && businessId !== envelopeBusinessId) {
    findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: "Item businessId does not match envelope businessId." }));
  }
  if (operation !== "upsert") findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: "Only upsert operation is supported in V1." }));
  if (!isIsoDate(occurredAt)) findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: "occurredAt must be ISO date." }));
  if (!cursor) findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: "cursor is required." }));
  if (!payload) findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: "payload object is required." }));

  if (payload && isKnownEntity(entityType)) {
    for (const field of ENTITY_REQUIRED_FIELDS[entityType]) {
      if (!(field in payload) || payload[field] === null || payload[field] === undefined || payload[field] === "") {
        findings.push(finding({ code: "invalid_schema", severity: "rejected", entityType, entityId, changeId, detail: `${entityType}.${field} is required.` }));
      }
    }
  }

  if (findings.some((item) => item.severity === "rejected")) return { record: null, findings };

  return {
    record: {
      changeId,
      entityType: entityType as CatalogDeltaEntityType,
      entityId,
      businessId,
      operation: "upsert",
      occurredAt,
      cursor,
      payload: payload ?? {}
    },
    findings
  };
}

export function validateCatalogDeltaEnvelope(input: unknown): { envelope: CatalogDeltaEnvelope | null; findings: CatalogDeltaFinding[] } {
  const findings: CatalogDeltaFinding[] = [];
  if (!isRecord(input)) {
    return { envelope: null, findings: [finding({ code: "invalid_schema", severity: "rejected", detail: "Catalog delta envelope must be an object." })] };
  }

  const contractId = asString(input.contractId);
  const schemaVersion = asString(input.schemaVersion);
  const stream = asString(input.stream);
  const mode = asString(input.mode);
  const businessId = asString(input.businessId);
  const generatedAt = asString(input.generatedAt);
  const scope = isRecord(input.scope) ? input.scope : {};
  const cursor = isRecord(input.cursor) ? input.cursor : null;
  const changes = Array.isArray(input.changes) ? input.changes : null;

  if (contractId !== CATALOG_DELTA_CONTRACT_ID) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: `contractId must be ${CATALOG_DELTA_CONTRACT_ID}.` }));
  if (schemaVersion !== CATALOG_DELTA_SCHEMA_VERSION) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: `schemaVersion must be ${CATALOG_DELTA_SCHEMA_VERSION}.` }));
  if (stream !== CATALOG_DELTA_STREAM) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: `stream must be ${CATALOG_DELTA_STREAM}.` }));
  if (!isKnownMode(mode)) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: `mode must be one of ${CATALOG_DELTA_MODES.join(", ")}.` }));
  if (!businessId) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: "businessId is required." }));
  if (!isIsoDate(generatedAt)) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: "generatedAt must be ISO date." }));
  if (!cursor) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: "cursor object is required." }));
  if (!changes) findings.push(finding({ code: "invalid_schema", severity: "rejected", detail: "changes array is required." }));

  const seen = new Set<string>();
  const records: CatalogDeltaRecord[] = [];
  if (changes) {
    for (const candidate of changes) {
      const validation = validateCatalogDeltaRecord(candidate, businessId);
      findings.push(...validation.findings);
      if (!validation.record) continue;
      if (seen.has(validation.record.changeId)) {
        findings.push(finding({
          code: "duplicate_change",
          severity: "warning",
          entityType: validation.record.entityType,
          entityId: validation.record.entityId,
          changeId: validation.record.changeId,
          detail: "Duplicate changeId appears in the same envelope."
        }));
      }
      seen.add(validation.record.changeId);
      records.push(validation.record);
    }
  }

  if (findings.some((item) => item.severity === "rejected")) return { envelope: null, findings };
  const diagnostics = isRecord(input.diagnostics) ? input.diagnostics : {};

  return {
    envelope: {
      contractId: CATALOG_DELTA_CONTRACT_ID,
      schemaVersion: CATALOG_DELTA_SCHEMA_VERSION,
      stream: CATALOG_DELTA_STREAM,
      mode: mode as CatalogDeltaMode,
      businessId,
      generatedAt,
      scope: {
        businessId: asString(scope.businessId) || businessId,
        terminalId: asString(scope.terminalId) || null,
        storeId: asString(scope.storeId) || null,
        target: asString(scope.target) || null
      },
      cursor: {
        requested: cursor ? asString(cursor.requested) || null : null,
        from: cursor ? asString(cursor.from) || null : null,
        to: cursor ? asString(cursor.to) || null : null,
        hasMore: Boolean(cursor?.hasMore),
        checkpointStrategy: "updatedAt_entityRank_id"
      },
      changes: records,
      counts: {
        total: records.length,
        byEntity: catalogDeltaCountByEntity(records)
      },
      diagnostics: {
        source: "pc-canonical-db",
        validator: CATALOG_DELTA_CONTRACT_ID,
        ordering: "updatedAt_entityRank_id",
        notes: Array.isArray(diagnostics.notes) ? diagnostics.notes.map(String) : []
      }
    },
    findings
  };
}

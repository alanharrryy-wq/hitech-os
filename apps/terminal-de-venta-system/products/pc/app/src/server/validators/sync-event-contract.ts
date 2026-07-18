import crypto from "node:crypto";
import { SHARED_SYNC_LIFECYCLE_STATES } from "@shared-kernel/sync/events";

export const REQUIRED_SYNC_EVENT_FIELDS = [
  "eventId",
  "source",
  "subject",
  "eventType",
  "topic",
  "eventVersion",
  "schemaVersion",
  "tenantId",
  "businessId",
  "storeId",
  "terminalId",
  "deviceId",
  "actorId",
  "aggregateId",
  "originRecordId",
  "idempotencyKey",
  "sequence",
  "correlationId",
  "causationId",
  "traceId",
  "occurredAt",
  "capturedAt",
  "payloadHash",
  "batchId",
  "batchChecksum",
  "payload"
] as const;

export const RECOGNIZED_SYNC_TOPICS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected",
  "sale.cancelled",
  "sale.refunded",
  "cash.session.opened",
  "cash.movement.recorded",
  "shift.opened",
  "shift.closed",
  "stock.adjusted",
  "inventory.operation.recorded",
  "catalog.product.created",
  "catalog.product.updated",
  "customer.created",
  "sync.event.sent",
  "sync.event.failed",
  "sync.conflict.detected",
  "sync.conflict.resolved",
  "supplier.created",
  "supplier.updated",
  "supplier.disabled",
  "product.supplier.linked",
  "product.supplier.unlinked",
  "product.supplier.updated"
] as const;

export const SUPPORTED_SYNC_EVENT_VERSIONS = ["1.0.0"] as const;
export const SUPPORTED_SYNC_SCHEMA_VERSIONS = ["1.0.0", "1.1.0"] as const;
export const SYNC_LIFECYCLE_STATES = SHARED_SYNC_LIFECYCLE_STATES;
export type SyncLifecycleState = (typeof SYNC_LIFECYCLE_STATES)[number];

export type SyncEventStatus = "accepted" | "duplicate" | "conflict" | "rejected";
export type SyncConflictSeverity = "warning" | "conflict" | "rejected";

export type SyncConflictFinding = {
  code: string;
  label: string;
  severity: SyncConflictSeverity;
  detail: string;
};

export type SyncEventEnvelope = {
  eventId: string;
  source: string;
  subject: string;
  eventType: string;
  topic: string;
  eventVersion: string;
  schemaVersion: string;
  tenantId: string;
  customerId?: string;
  businessId: string;
  storeId: string;
  terminalId: string;
  deviceId: string;
  actorId: string;
  aggregateId: string;
  originRecordId: string;
  idempotencyKey: string;
  sequence: number;
  correlationId: string;
  causationId: string;
  traceId: string;
  occurredAt: string;
  capturedAt: string;
  payloadHash: string;
  batchId: string;
  batchChecksum: string;
  payload: Record<string, unknown>;
};

export type SyncIngestResult = {
  eventId: string | null;
  topic: string | null;
  status: SyncEventStatus;
  lifecycleStatus?: SyncLifecycleState;
  conflicts: SyncConflictFinding[];
  errors: string[];
  diagnostics?: string[];
  projectedModels?: string[];
};

export type SyncIngestClassification = {
  status: SyncEventStatus;
  eventsReceived: number;
  results: SyncIngestResult[];
  summary: Record<SyncEventStatus, number>;
  meta: {
    persistence: "dry_run" | "outbox_event";
    durable?: boolean;
    storageModel?: string;
    idempotencyKey: "eventId" | "idempotencyKey";
    recognizedTopics: readonly string[];
    supportedEventVersions?: readonly string[];
    supportedSchemaVersions: readonly string[];
    note: string;
  };
};

export const SYNC_CONFLICT_CATALOG: Record<string, Omit<SyncConflictFinding, "detail">> = {
  product_discontinued: { code: "product_discontinued", label: "Producto descontinuado", severity: "conflict" },
  old_local_price: { code: "old_local_price", label: "Precio local viejo", severity: "conflict" },
  negative_stock: { code: "negative_stock", label: "Stock negativo", severity: "conflict" },
  duplicate_event: { code: "duplicate_event", label: "Evento duplicado", severity: "warning" },
  terminal_not_registered: { code: "terminal_not_registered", label: "Terminal no registrada", severity: "conflict" },
  sale_outside_shift: { code: "sale_outside_shift", label: "Venta fuera de turno", severity: "conflict" },
  inconsistent_sequence: { code: "inconsistent_sequence", label: "Secuencia inconsistente", severity: "conflict" },
  stale_sequence: { code: "stale_sequence", label: "Secuencia vencida", severity: "conflict" },
  wrong_scope: { code: "wrong_scope", label: "Scope no autorizado", severity: "rejected" },
  payload_hash_mismatch: { code: "payload_hash_mismatch", label: "Hash de payload inválido", severity: "rejected" },
  idempotency_payload_mismatch: { code: "idempotency_payload_mismatch", label: "Idempotencia con payload distinto", severity: "conflict" },
  unsupported_event_version: { code: "unsupported_event_version", label: "Versión de evento no soportada", severity: "rejected" },
  unsupported_schema_version: { code: "unsupported_schema_version", label: "Versión de schema no soportada", severity: "rejected" },
  batch_checksum_mismatch: { code: "batch_checksum_mismatch", label: "Checksum de lote inválido", severity: "rejected" },
  invalid_schema: { code: "invalid_schema", label: "Schema inválido", severity: "rejected" },
  unknown_topic: { code: "unknown_topic", label: "Topic desconocido", severity: "rejected" }
};

function conflict(code: keyof typeof SYNC_CONFLICT_CATALOG, detail: string): SyncConflictFinding {
  return { ...SYNC_CONFLICT_CATALOG[code], detail };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function asSequence(value: unknown): number | null {
  if (typeof value === "number" && Number.isSafeInteger(value) && value >= 0) return value;
  if (typeof value === "string" && /^\d+$/.test(value.trim())) {
    const parsed = Number(value);
    if (Number.isSafeInteger(parsed) && parsed >= 0) return parsed;
  }
  return null;
}

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (!isRecord(value)) return value;
  return Object.keys(value).sort().reduce<Record<string, unknown>>((acc, key) => {
    acc[key] = stable(value[key]);
    return acc;
  }, {});
}

export function syncPayloadFingerprint(value: unknown) {
  return crypto.createHash("sha256").update(JSON.stringify(stable(value))).digest("hex");
}

export function normalizeSyncTimestamp(value: unknown): string {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value.toISOString();
  if (typeof value === "number" && Number.isFinite(value)) {
    const milliseconds = Math.abs(value) >= 100_000_000_000 ? value : value * 1000;
    const date = new Date(milliseconds);
    return Number.isNaN(date.getTime()) ? "" : date.toISOString();
  }
  if (typeof value === "string" && value.trim()) {
    const text = value.trim();
    if (/^-?\d{10,}$/.test(text)) return normalizeSyncTimestamp(Number(text));
    const date = new Date(text);
    return Number.isNaN(date.getTime()) ? "" : date.toISOString();
  }
  return "";
}

export function extractSyncEvents(input: unknown): unknown[] {
  if (Array.isArray(input)) return input;
  if (!isRecord(input)) return [];
  if (Array.isArray(input.events)) return input.events;
  if (isRecord(input.data) && Array.isArray(input.data.events)) return input.data.events;
  if (typeof input.eventId === "string") return [input];
  return [];
}

function payloadConflicts(event: SyncEventEnvelope): SyncConflictFinding[] {
  const payload = event.payload;
  const conflicts: SyncConflictFinding[] = [];
  if (payload.productIsActive === false || payload.isDiscontinued === true) {
    conflicts.push(conflict("product_discontinued", "El payload marca producto inactivo o descontinuado."));
  }
  if (payload.terminalRegistered === false) {
    conflicts.push(conflict("terminal_not_registered", "La terminal no está registrada para consolidación PC."));
  }
  const stockAfter = typeof payload.stockAfter === "number" ? payload.stockAfter : null;
  if (stockAfter !== null && stockAfter < 0) {
    conflicts.push(conflict("negative_stock", "El evento deja inventario debajo de cero."));
  }
  if (typeof payload.localPriceCents === "number" && typeof payload.currentPriceCents === "number" && payload.localPriceCents !== payload.currentPriceCents) {
    conflicts.push(conflict("old_local_price", "El precio local de Tablet no coincide con el precio actual informado."));
  }
  if (event.topic === "sale.completed" && payload.cashSessionRequired === true && !asString(payload.cashSessionId)) {
    conflicts.push(conflict("sale_outside_shift", "Venta completada sin turno/corte requerido."));
  }
  if (payload.previousEventId === event.eventId || payload.sequenceError === true) {
    conflicts.push(conflict("inconsistent_sequence", "El payload reporta secuencia inconsistente."));
  }
  if ((event.topic === "supplier.created" || event.topic === "supplier.updated" || event.topic === "supplier.disabled") && !asString(payload.supplierId ?? payload.id)) {
    conflicts.push(conflict("invalid_schema", "supplier.* requires supplierId."));
  }
  if ((event.topic === "supplier.created" || event.topic === "supplier.updated") && !asString(payload.name ?? payload.tradeName)) {
    conflicts.push(conflict("invalid_schema", "supplier.created/updated require name."));
  }
  if ((event.topic === "product.supplier.linked" || event.topic === "product.supplier.unlinked" || event.topic === "product.supplier.updated") && (!asString(payload.productId) || !asString(payload.supplierId))) {
    conflicts.push(conflict("invalid_schema", "product.supplier.* requires productId and supplierId."));
  }
  return conflicts;
}

export function canonicalEventType(input: Record<string, unknown>) {
  return asString(input.eventType) || asString(input.topic);
}

export function getSyncConflictCatalog(): SyncConflictFinding[] {
  return Object.values(SYNC_CONFLICT_CATALOG).map((item) => ({
    ...item,
    detail: "Clasificación canónica usada por PC para ingest, proyección, conflicto y replay."
  }));
}

function expectedScopeValue(name: "tenantId" | "customerId", eventValue: string) {
  const envName = name === "tenantId" ? "PRISMA_SYNC_TENANT_ID" : "PRISMA_SYNC_CUSTOMER_ID";
  const expected = process.env[envName]?.trim() ?? "";
  return expected && eventValue && expected !== eventValue
    ? conflict("wrong_scope", `${name} ${eventValue} no coincide con ${envName}.`)
    : null;
}

export function validateSyncEventEnvelope(input: unknown): { event: SyncEventEnvelope | null; errors: string[]; conflicts: SyncConflictFinding[] } {
  const errors: string[] = [];
  const conflicts: SyncConflictFinding[] = [];
  if (!isRecord(input)) {
    return { event: null, errors: ["El evento debe ser objeto JSON."], conflicts: [conflict("invalid_schema", "La entrada no es objeto JSON.")] };
  }

  const eventId = asString(input.eventId);
  const topic = canonicalEventType(input);
  const eventType = topic;
  const source = asString(input.source);
  const subject = asString(input.subject);
  const eventVersion = asString(input.eventVersion);
  const schemaVersion = asString(input.schemaVersion);
  const tenantId = asString(input.tenantId);
  const customerId = asString(input.customerId);
  const businessId = asString(input.businessId);
  const storeId = asString(input.storeId);
  const terminalId = asString(input.terminalId);
  const deviceId = asString(input.deviceId);
  const actorId = asString(input.actorId);
  const aggregateId = asString(input.aggregateId);
  const originRecordId = asString(input.originRecordId);
  const idempotencyKey = asString(input.idempotencyKey) || eventId;
  const sequence = asSequence(input.sequence);
  const correlationId = asString(input.correlationId);
  const causationId = asString(input.causationId);
  const traceId = asString(input.traceId);
  const occurredAt = normalizeSyncTimestamp(input.occurredAt);
  const capturedAt = normalizeSyncTimestamp(input.capturedAt);
  const payloadHash = asString(input.payloadHash).toLowerCase();
  const batchId = asString(input.batchId);
  const batchChecksum = asString(input.batchChecksum).toLowerCase();
  const payload = isRecord(input.payload) ? input.payload : null;

  for (const [name, value] of Object.entries({
    eventId, source, subject, eventType, topic, eventVersion, schemaVersion,
    tenantId, businessId, storeId, terminalId, deviceId, actorId, aggregateId,
    originRecordId, idempotencyKey, correlationId, causationId, traceId,
    occurredAt, capturedAt, payloadHash, batchId, batchChecksum
  })) {
    if (!value) errors.push(`${name} debe ser texto no vacío.`);
  }
  if (sequence === null) errors.push("sequence debe ser entero seguro no negativo.");
  if (!payload) errors.push("payload debe ser objeto JSON.");

  if (topic && !RECOGNIZED_SYNC_TOPICS.includes(topic as (typeof RECOGNIZED_SYNC_TOPICS)[number])) {
    conflicts.push(conflict("unknown_topic", `Topic recibido: ${topic}.`));
    errors.push(`topic no reconocido: ${topic}.`);
  }
  if (eventVersion && !SUPPORTED_SYNC_EVENT_VERSIONS.includes(eventVersion as (typeof SUPPORTED_SYNC_EVENT_VERSIONS)[number])) {
    conflicts.push(conflict("unsupported_event_version", `eventVersion recibido: ${eventVersion}.`));
  }
  if (schemaVersion && !SUPPORTED_SYNC_SCHEMA_VERSIONS.includes(schemaVersion as (typeof SUPPORTED_SYNC_SCHEMA_VERSIONS)[number])) {
    conflicts.push(conflict("unsupported_schema_version", `schemaVersion recibido: ${schemaVersion}.`));
  }
  if (payload && payloadHash && syncPayloadFingerprint(payload) !== payloadHash) {
    conflicts.push(conflict("payload_hash_mismatch", "payloadHash no coincide con sha256(stable-json(payload))."));
  }
  if (payloadHash && !/^[a-f0-9]{64}$/.test(payloadHash)) {
    errors.push("payloadHash debe ser SHA-256 hexadecimal.");
  }
  if (batchChecksum && !/^[a-f0-9]{64}$/.test(batchChecksum)) {
    errors.push("batchChecksum debe ser SHA-256 hexadecimal.");
  }

  const tenantConflict = expectedScopeValue("tenantId", tenantId);
  if (tenantConflict) conflicts.push(tenantConflict);
  const customerConflict = expectedScopeValue("customerId", customerId);
  if (customerConflict) conflicts.push(customerConflict);

  if (errors.length > 0 || conflicts.some((item) => item.severity === "rejected")) {
    return {
      event: null,
      errors,
      conflicts: conflicts.length ? conflicts : [conflict("invalid_schema", "Evento inválido por contrato canónico.")]
    };
  }

  const event: SyncEventEnvelope = {
    eventId,
    source,
    subject,
    eventType,
    topic,
    eventVersion,
    schemaVersion,
    tenantId,
    ...(customerId ? { customerId } : {}),
    businessId,
    storeId,
    terminalId,
    deviceId,
    actorId,
    aggregateId,
    originRecordId,
    idempotencyKey,
    sequence: sequence ?? 0,
    correlationId,
    causationId,
    traceId,
    occurredAt,
    capturedAt,
    payloadHash,
    batchId,
    batchChecksum,
    payload: payload ?? {}
  };
  return { event, errors, conflicts: [...conflicts, ...payloadConflicts(event)] };
}

function summary(results: SyncIngestResult[]): Record<SyncEventStatus, number> {
  const base: Record<SyncEventStatus, number> = { accepted: 0, duplicate: 0, conflict: 0, rejected: 0 };
  for (const result of results) base[result.status] += 1;
  return base;
}

function topStatus(sum: Record<SyncEventStatus, number>): SyncEventStatus {
  if (sum.rejected > 0) return "rejected";
  if (sum.conflict > 0) return "conflict";
  if (sum.duplicate > 0) return "duplicate";
  return "accepted";
}

export function classifySyncIngestPayload(input: unknown): SyncIngestClassification {
  const candidates = extractSyncEvents(input);
  const seen = new Map<string, string>();
  const results: SyncIngestResult[] = [];
  for (const candidate of candidates) {
    const validation = validateSyncEventEnvelope(candidate);
    const eventId = isRecord(candidate) ? asString(candidate.eventId) || null : null;
    const topic = isRecord(candidate) ? canonicalEventType(candidate) || null : null;
    if (!validation.event) {
      results.push({ eventId, topic, status: "rejected", conflicts: validation.conflicts, errors: validation.errors });
      continue;
    }
    const priorHash = seen.get(validation.event.idempotencyKey);
    if (priorHash) {
      const samePayload = priorHash === validation.event.payloadHash;
      results.push({
        eventId: validation.event.eventId,
        topic: validation.event.topic,
        status: samePayload ? "duplicate" : "conflict",
        lifecycleStatus: samePayload ? "received" : "conflict",
        conflicts: [conflict(
          samePayload ? "duplicate_event" : "idempotency_payload_mismatch",
          samePayload
            ? "El idempotencyKey aparece repetido dentro del mismo lote con payload idéntico."
            : "El idempotencyKey aparece repetido dentro del mismo lote con payload distinto."
        )],
        errors: []
      });
      continue;
    }
    seen.set(validation.event.idempotencyKey, validation.event.payloadHash);
    results.push({
      eventId: validation.event.eventId,
      topic: validation.event.topic,
      status: validation.conflicts.length ? "conflict" : "accepted",
      lifecycleStatus: validation.conflicts.length ? "conflict" : "validated",
      conflicts: validation.conflicts,
      errors: []
    });
  }
  const sum = summary(results);
  return {
    status: topStatus(sum),
    eventsReceived: candidates.length,
    results,
    summary: sum,
    meta: {
      persistence: "dry_run",
      idempotencyKey: "idempotencyKey",
      recognizedTopics: RECOGNIZED_SYNC_TOPICS,
      supportedEventVersions: SUPPORTED_SYNC_EVENT_VERSIONS,
      supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
      note: "Clasificación sin persistencia. Usa POST para persistir en OutboxEvent y observabilidad canónica."
    }
  };
}

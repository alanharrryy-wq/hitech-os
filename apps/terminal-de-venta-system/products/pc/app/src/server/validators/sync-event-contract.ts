import crypto from "node:crypto";
import { SHARED_SYNC_LIFECYCLE_STATES } from "@shared-kernel/sync/events";

export const REQUIRED_SYNC_EVENT_FIELDS = [
  "eventId",
  "eventType",
  "topic",
  "idempotencyKey",
  "businessId",
  "terminalId",
  "actorId",
  "source",
  "occurredAt",
  "payload",
  "schemaVersion",
  "correlationId"
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
  "catalog.product.created",
  "catalog.product.updated",
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

export const SUPPORTED_SYNC_SCHEMA_VERSIONS = ["1.0.0"] as const;
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
  eventType: string;
  topic: string;
  idempotencyKey: string;
  businessId: string;
  terminalId: string;
  actorId: string;
  source: string;
  occurredAt: string;
  payload: Record<string, unknown>;
  schemaVersion: string;
  aggregateId?: string;
  correlationId?: string;
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
    detail: "Clasificación canónica usada por PC I05 para exponer conflictos de ingest."
  }));
}

export function validateSyncEventEnvelope(input: unknown): { event: SyncEventEnvelope | null; errors: string[]; conflicts: SyncConflictFinding[] } {
  const errors: string[] = [];
  const conflicts: SyncConflictFinding[] = [];
  if (!isRecord(input)) {
    return { event: null, errors: ["El evento debe ser objeto JSON."], conflicts: [conflict("invalid_schema", "La entrada no es objeto JSON.")] };
  }
  for (const field of REQUIRED_SYNC_EVENT_FIELDS) {
    if (field === "eventType" || field === "topic" || field === "idempotencyKey" || field === "correlationId") continue;
    if (!(field in input)) errors.push(`Falta campo requerido: ${field}.`);
  }
  const eventId = asString(input.eventId);
  const topic = canonicalEventType(input);
  const eventType = topic;
  const idempotencyKey = asString(input.idempotencyKey) || eventId;
  const businessId = asString(input.businessId);
  const terminalId = asString(input.terminalId);
  const actorId = asString(input.actorId);
  const source = asString(input.source);
  const occurredAt = asString(input.occurredAt);
  const schemaVersion = asString(input.schemaVersion);
  const payload = isRecord(input.payload) ? input.payload : null;
  const aggregateId = asString(input.aggregateId);
  const correlationId = asString(input.correlationId);

  if (!eventId) errors.push("eventId debe ser texto no vacío.");
  if (!topic) errors.push("eventType/topic debe ser texto no vacío.");
  if (!idempotencyKey) errors.push("idempotencyKey debe ser texto no vacío o resolverse desde eventId.");
  if (!businessId) errors.push("businessId debe ser texto no vacío.");
  if (!terminalId) errors.push("terminalId debe ser texto no vacío.");
  if (!actorId) errors.push("actorId debe ser texto no vacío.");
  if (!source) errors.push("source debe ser texto no vacío.");
  if (!occurredAt || Number.isNaN(Date.parse(occurredAt))) errors.push("occurredAt debe ser fecha ISO válida.");
  if (!payload) errors.push("payload debe ser objeto JSON.");

  if (topic && !RECOGNIZED_SYNC_TOPICS.includes(topic as (typeof RECOGNIZED_SYNC_TOPICS)[number])) {
    conflicts.push(conflict("unknown_topic", `Topic recibido: ${topic}.`));
    errors.push(`topic no reconocido: ${topic}.`);
  }
  if (!SUPPORTED_SYNC_SCHEMA_VERSIONS.includes(schemaVersion as (typeof SUPPORTED_SYNC_SCHEMA_VERSIONS)[number])) {
    conflicts.push(conflict("invalid_schema", `schemaVersion recibido: ${schemaVersion || "(vacío)"}.`));
  }
  if (errors.length > 0 || conflicts.some((item) => item.severity === "rejected")) {
    return { event: null, errors, conflicts: conflicts.length ? conflicts : [conflict("invalid_schema", "Evento inválido por contrato mínimo.")] };
  }
  const event: SyncEventEnvelope = {
    eventId,
    eventType,
    topic,
    idempotencyKey,
    businessId,
    terminalId,
    actorId,
    source,
    occurredAt,
    payload: payload ?? {},
    schemaVersion,
    ...(aggregateId ? { aggregateId } : {}),
    ...(correlationId ? { correlationId } : {})
  };
  return { event, errors, conflicts: payloadConflicts(event) };
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
  const seen = new Set<string>();
  const results: SyncIngestResult[] = [];
  for (const candidate of candidates) {
    const validation = validateSyncEventEnvelope(candidate);
    const eventId = isRecord(candidate) ? asString(candidate.eventId) || null : null;
    const topic = isRecord(candidate) ? canonicalEventType(candidate) || null : null;
    if (validation.event && seen.has(validation.event.idempotencyKey)) {
      results.push({ eventId: validation.event.eventId, topic: validation.event.topic, status: "duplicate", lifecycleStatus: "received", conflicts: [conflict("duplicate_event", "El idempotencyKey aparece repetido dentro del mismo lote.")], errors: [] });
      continue;
    }
    if (!validation.event) {
      results.push({ eventId, topic, status: "rejected", conflicts: validation.conflicts, errors: validation.errors });
      continue;
    }
    seen.add(validation.event.idempotencyKey);
    results.push({ eventId: validation.event.eventId, topic: validation.event.topic, status: validation.conflicts.length ? "conflict" : "accepted", lifecycleStatus: validation.conflicts.length ? "conflict" : "validated", conflicts: validation.conflicts, errors: [] });
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
      supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
      note: "Clasificación sin persistencia. Usa POST sin dryRun para persistir en OutboxEvent."
    }
  };
}

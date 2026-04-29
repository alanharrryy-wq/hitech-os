import { conflictFinding, type ConflictFinding } from "./conflicts";

export const REQUIRED_EVENT_FIELDS = [
  "eventId",
  "topic",
  "businessId",
  "terminalId",
  "actorId",
  "source",
  "occurredAt",
  "payload",
  "schemaVersion"
] as const;

export const RECOGNIZED_EVENT_TOPICS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected",
  "sale.cancelled",
  "sale.refunded",
  "shift.opened",
  "shift.closed",
  "stock.adjusted",
  "catalog.product.created",
  "catalog.product.updated",
  "sync.event.sent",
  "sync.event.failed",
  "sync.conflict.detected",
  "sync.conflict.resolved"
] as const;

export const SUPPORTED_SCHEMA_VERSIONS = ["1.0.0"] as const;

export type RecognizedEventTopic = (typeof RECOGNIZED_EVENT_TOPICS)[number];
export type IngestResultStatus = "accepted" | "rejected" | "duplicate" | "conflict";

export type BackofficeEventEnvelope = {
  eventId: string;
  topic: RecognizedEventTopic;
  businessId: string;
  terminalId: string;
  actorId: string;
  source: string;
  occurredAt: string;
  payload: Record<string, unknown>;
  schemaVersion: string;
  aggregateId?: string;
};

export type IngestEventResult = {
  eventId: string | null;
  topic: string | null;
  status: IngestResultStatus;
  conflicts: ConflictFinding[];
  errors: string[];
};

export type IngestClassification = {
  status: IngestResultStatus;
  eventsReceived: number;
  results: IngestEventResult[];
  summary: Record<IngestResultStatus, number>;
  meta: {
    persistence: "validation_only" | "outbox_event";
    supportedSchemaVersions: readonly string[];
    recognizedTopics: readonly string[];
    note: string;
    durable?: boolean;
    storageModel?: string;
    idempotencyKey?: string;
  };
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function isRecognizedTopic(topic: string): topic is RecognizedEventTopic {
  return RECOGNIZED_EVENT_TOPICS.includes(topic as RecognizedEventTopic);
}

export function extractIngestEvents(input: unknown): unknown[] {
  if (Array.isArray(input)) return input;
  if (!isRecord(input)) return [];
  if (Array.isArray(input.events)) return input.events;
  if (isRecord(input.data) && Array.isArray(input.data.events)) return input.data.events;
  if (isRecord(input.data) && isRecord(input.data.data) && Array.isArray(input.data.data.events)) return input.data.data.events;
  if (typeof input.eventId === "string") return [input];
  return [];
}

function classifyPayloadConflicts(event: BackofficeEventEnvelope) {
  const conflicts: ConflictFinding[] = [];
  const payload = event.payload;

  if (payload.productIsActive === false || payload.isDiscontinued === true) {
    conflicts.push(conflictFinding("product_discontinued", "El payload marca el producto como inactivo o descontinuado."));
  }

  const stockAfter = typeof payload.stockAfter === "number" ? payload.stockAfter : null;
  if (stockAfter !== null && stockAfter < 0) {
    conflicts.push(conflictFinding("negative_stock", "El evento deja inventario local debajo de cero."));
  }

  if (typeof payload.localPriceCents === "number" && typeof payload.currentPriceCents === "number" && payload.localPriceCents !== payload.currentPriceCents) {
    conflicts.push(conflictFinding("old_local_price", "El precio usado por Tablet no coincide con el precio vigente informado."));
  }

  if (event.topic === "sale.completed" && payload.cashSessionRequired === true && !asString(payload.cashSessionId)) {
    conflicts.push(conflictFinding("sale_outside_shift", "La política exige cashSessionId y la venta completada no lo trae."));
  }

  if (payload.previousEventId === event.eventId || payload.sequenceError === true) {
    conflicts.push(conflictFinding("inconsistent_sequence", "El payload reporta una secuencia inconsistente."));
  }

  return conflicts;
}

export function validateBackofficeEvent(input: unknown): { event: BackofficeEventEnvelope | null; errors: string[]; conflicts: ConflictFinding[] } {
  const errors: string[] = [];
  const conflicts: ConflictFinding[] = [];

  if (!isRecord(input)) {
    return {
      event: null,
      errors: ["El evento debe ser un objeto JSON."],
      conflicts: [conflictFinding("invalid_schema", "La entrada no es un objeto JSON.")]
    };
  }

  for (const field of REQUIRED_EVENT_FIELDS) {
    if (!(field in input)) errors.push(`Falta campo requerido: ${field}.`);
  }

  const eventId = asString(input.eventId);
  const topic = asString(input.topic);
  const businessId = asString(input.businessId);
  const terminalId = asString(input.terminalId);
  const actorId = asString(input.actorId);
  const source = asString(input.source);
  const occurredAt = asString(input.occurredAt);
  const schemaVersion = asString(input.schemaVersion);
  const payload = isRecord(input.payload) ? input.payload : null;
  const aggregateId = asString(input.aggregateId);

  if (!eventId) errors.push("eventId debe ser texto no vacío.");
  if (!topic) errors.push("topic debe ser texto no vacío.");
  if (!businessId || !terminalId) {
    conflicts.push(conflictFinding("invalid_schema", "businessId y terminalId son obligatorios para consolidar."));
  }
  if (!actorId) errors.push("actorId debe ser texto no vacío.");
  if (!source) errors.push("source debe ser texto no vacío.");
  if (!occurredAt || Number.isNaN(Date.parse(occurredAt))) errors.push("occurredAt debe ser una fecha ISO válida.");
  if (!payload) errors.push("payload debe ser un objeto JSON.");

  if (topic && !isRecognizedTopic(topic)) {
    errors.push(`topic no reconocido: ${topic}.`);
    conflicts.push(conflictFinding("unknown_topic", `topic recibido: ${topic}.`));
  }

  if (!SUPPORTED_SCHEMA_VERSIONS.includes(schemaVersion as (typeof SUPPORTED_SCHEMA_VERSIONS)[number])) {
    conflicts.push(conflictFinding("invalid_schema", `schemaVersion recibido: ${schemaVersion || "(vacío)"}.`));
  }

  if (errors.length > 0 || conflicts.some((item) => item.severity === "rejected")) {
    return { event: null, errors, conflicts: conflicts.length ? conflicts : [conflictFinding("invalid_schema", "El evento no cumple el contrato mínimo.")] };
  }

  const event: BackofficeEventEnvelope = {
    eventId,
    topic: topic as RecognizedEventTopic,
    businessId,
    terminalId,
    actorId,
    source,
    occurredAt,
    payload: payload ?? {},
    schemaVersion,
    ...(aggregateId ? { aggregateId } : {})
  };

  return { event, errors, conflicts: classifyPayloadConflicts(event) };
}

export function classifyIngestPayload(input: unknown): IngestClassification {
  const events = extractIngestEvents(input);
  const seen = new Set<string>();
  const results: IngestEventResult[] = [];

  for (const candidate of events) {
    const validation = validateBackofficeEvent(candidate);
    const eventId = isRecord(candidate) ? asString(candidate.eventId) || null : null;
    const topic = isRecord(candidate) ? asString(candidate.topic) || null : null;

    if (validation.event && seen.has(validation.event.eventId)) {
      results.push({
        eventId: validation.event.eventId,
        topic: validation.event.topic,
        status: "duplicate",
        conflicts: [conflictFinding("duplicate_event", "El mismo eventId aparece más de una vez en el lote recibido.")],
        errors: []
      });
      continue;
    }

    if (!validation.event) {
      results.push({
        eventId,
        topic,
        status: "rejected",
        conflicts: validation.conflicts,
        errors: validation.errors
      });
      continue;
    }

    seen.add(validation.event.eventId);
    results.push({
      eventId: validation.event.eventId,
      topic: validation.event.topic,
      status: validation.conflicts.length ? "conflict" : "accepted",
      conflicts: validation.conflicts,
      errors: []
    });
  }

  const summary: Record<IngestResultStatus, number> = {
    accepted: 0,
    rejected: 0,
    duplicate: 0,
    conflict: 0
  };
  for (const result of results) summary[result.status] += 1;

  return {
    status: summary.rejected > 0 ? "rejected" : summary.conflict > 0 ? "conflict" : summary.duplicate > 0 ? "duplicate" : "accepted",
    eventsReceived: events.length,
    results,
    summary,
    meta: {
      persistence: "validation_only",
      supportedSchemaVersions: SUPPORTED_SCHEMA_VERSIONS,
      recognizedTopics: RECOGNIZED_EVENT_TOPICS,
      note: "PC valida y clasifica eventos Tablet; persistencia de ingest consolidado queda explícitamente pendiente."
    }
  };
}

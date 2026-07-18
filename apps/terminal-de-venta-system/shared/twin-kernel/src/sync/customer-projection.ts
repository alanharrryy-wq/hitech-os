export const CUSTOMER_PROJECTION_CONTRACT_ID = "PRISMA_PC_TO_TABLET_CUSTOMER_PROJECTION_V1" as const;
export const CUSTOMER_PROJECTION_STREAM = "pc.customer.projection.v1" as const;
export const CUSTOMER_PROJECTION_SCHEMA_VERSION = "1.0.0" as const;

export type CustomerProjectionOperation = "upsert" | "tombstone";

export type CustomerProjectionRecord = {
  changeId: string;
  customerId: string;
  businessId: string;
  operation: CustomerProjectionOperation;
  version: number;
  occurredAt: string;
  cursor: string;
  payload: {
    id: string;
    businessId: string;
    displayName: string;
    isActive: boolean;
    version: number;
    sourceSurface: "pc" | "tablet";
    updatedAt: string;
    tombstoneAt: string | null;
  };
};

export type CustomerProjectionEnvelope = {
  contractId: typeof CUSTOMER_PROJECTION_CONTRACT_ID;
  schemaVersion: typeof CUSTOMER_PROJECTION_SCHEMA_VERSION;
  stream: typeof CUSTOMER_PROJECTION_STREAM;
  businessId: string;
  generatedAt: string;
  cursor: { requested: string | null; next: string | null; hasMore: boolean };
  changes: CustomerProjectionRecord[];
};

function text(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function isIso(value: unknown) {
  return typeof value === "string" && !Number.isNaN(Date.parse(value));
}

export function validateCustomerProjectionEnvelope(input: unknown): { envelope: CustomerProjectionEnvelope | null; errors: string[] } {
  if (!input || typeof input !== "object" || Array.isArray(input)) return { envelope: null, errors: ["Envelope de cliente inválido."] };
  const raw = input as Record<string, unknown>;
  const errors: string[] = [];
  if (raw.contractId !== CUSTOMER_PROJECTION_CONTRACT_ID) errors.push("contractId inválido.");
  if (raw.schemaVersion !== CUSTOMER_PROJECTION_SCHEMA_VERSION) errors.push("schemaVersion inválido.");
  if (raw.stream !== CUSTOMER_PROJECTION_STREAM) errors.push("stream inválido.");
  const businessId = text(raw.businessId);
  if (!businessId) errors.push("businessId requerido.");
  if (!isIso(raw.generatedAt)) errors.push("generatedAt inválido.");
  if (!Array.isArray(raw.changes)) errors.push("changes debe ser arreglo.");
  if (errors.length) return { envelope: null, errors };

  const changes: CustomerProjectionRecord[] = [];
  for (const candidate of raw.changes as unknown[]) {
    const record = candidate && typeof candidate === "object" && !Array.isArray(candidate) ? candidate as Record<string, unknown> : {};
    const payload = record.payload && typeof record.payload === "object" && !Array.isArray(record.payload) ? record.payload as Record<string, unknown> : {};
    const customerId = text(record.customerId);
    const recordBusinessId = text(record.businessId);
    const operation = text(record.operation);
    const version = Number(record.version);
    if (!customerId || !recordBusinessId || recordBusinessId !== businessId || (operation !== "upsert" && operation !== "tombstone") || !Number.isInteger(version) || version < 1 || !isIso(record.occurredAt) || !text(record.cursor) || text(payload.id) !== customerId || text(payload.businessId) !== businessId || !text(payload.displayName) || Number(payload.version) !== version || !isIso(payload.updatedAt)) {
      errors.push(`Cambio de cliente inválido: ${customerId || "sin id"}.`);
      continue;
    }
    changes.push(record as CustomerProjectionRecord);
  }
  if (errors.length) return { envelope: null, errors };
  return { envelope: raw as unknown as CustomerProjectionEnvelope, errors: [] };
}

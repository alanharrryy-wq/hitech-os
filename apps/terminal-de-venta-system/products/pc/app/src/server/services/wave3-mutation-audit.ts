import { randomUUID } from "node:crypto";

export async function appendWave3Audit(tx: any, input: {
  businessId: string;
  topic: string;
  entityType: string;
  entityId?: string | null;
  summary: string;
  before?: unknown;
  after?: unknown;
  metadata?: Record<string, unknown>;
}) {
  return tx.auditEvent.create({
    data: {
      id: randomUUID(),
      businessId: input.businessId,
      actorId: null,
      topic: input.topic,
      entityType: input.entityType,
      entityId: input.entityId ?? null,
      summary: input.summary,
      beforeJson: input.before === undefined ? null : JSON.stringify(input.before),
      afterJson: input.after === undefined ? null : JSON.stringify(input.after),
      metadataJson: JSON.stringify({ wave: 3, surface: "pc", ...(input.metadata ?? {}) })
    }
  });
}

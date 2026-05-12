import { prisma } from "../prisma/client";
import {
  OUTBOX_STATUS_ACKED,
  OUTBOX_STATUS_CONFLICT,
  OUTBOX_STATUS_FAILED,
  OUTBOX_STATUS_PENDING,
  OUTBOX_STATUS_SENT
} from "../pos-engine/constants";
import type { PosListInput } from "../pos-api/validators";

export const OUTBOX_STATUSES = [
  OUTBOX_STATUS_PENDING,
  OUTBOX_STATUS_SENT,
  OUTBOX_STATUS_FAILED,
  OUTBOX_STATUS_ACKED,
  OUTBOX_STATUS_CONFLICT
] as const;

export type OutboxStatus = (typeof OUTBOX_STATUSES)[number];

type OutboxRow = {
  id: string;
  businessId: string;
  topic: string;
  aggregateId: string;
  idempotencyKey?: string | null;
  payloadJson: string;
  status: string;
  attempts: number;
  createdAt: Date;
  sentAt: Date | null;
  lastError: string | null;
};

function parsePayload(payloadJson: string) {
  try {
    return JSON.parse(payloadJson) as Record<string, unknown>;
  } catch {
    return { raw: payloadJson, parseWarning: "INVALID_OUTBOX_PAYLOAD_JSON" };
  }
}

export function normalizeOutboxStatus(status: string): string {
  const normalized = status.toLowerCase();
  if (OUTBOX_STATUSES.includes(normalized as OutboxStatus)) return normalized;
  return status;
}

export function toOutboxEvent(row: OutboxRow) {
  const payload = parsePayload(row.payloadJson);
  return {
    id: row.id,
    eventId: typeof payload.eventId === "string" ? payload.eventId : row.id,
    businessId: row.businessId,
    topic: row.topic,
    aggregateId: row.aggregateId,
    idempotencyKey: row.idempotencyKey ?? (typeof payload.idempotencyKey === "string" ? payload.idempotencyKey : null),
    payload,
    status: normalizeOutboxStatus(row.status),
    attempts: row.attempts,
    createdAt: row.createdAt.toISOString(),
    sentAt: row.sentAt ? row.sentAt.toISOString() : null,
    lastError: row.lastError
  };
}

function statusFilter(status?: string) {
  if (!status) return {};
  return { status: { in: [status, status.toLowerCase(), status.toUpperCase()] } };
}

export async function listOutboxEvents(input: Pick<PosListInput, "businessId" | "limit" | "status">) {
  const rows = await prisma.outboxEvent.findMany({
    where: {
      businessId: input.businessId,
      ...statusFilter(input.status)
    },
    orderBy: { createdAt: "desc" },
    take: input.limit
  });
  return rows.map((row: any) => toOutboxEvent(row));
}

export async function listRecentEvents(input: Pick<PosListInput, "businessId" | "limit">) {
  const rows = await prisma.outboxEvent.findMany({
    where: { businessId: input.businessId },
    orderBy: { createdAt: "desc" },
    take: input.limit
  });
  return rows.map((row: any) => toOutboxEvent(row));
}

export async function countOutboxByState(businessId: string) {
  const [pending, failed, sent, acked, conflict] = await Promise.all([
    prisma.outboxEvent.count({ where: { businessId, status: { in: ["pending", "PENDING"] } } }),
    prisma.outboxEvent.count({ where: { businessId, status: { in: ["failed", "FAILED"] } } }),
    prisma.outboxEvent.count({ where: { businessId, status: { in: ["sent", "SENT"] } } }),
    prisma.outboxEvent.count({ where: { businessId, status: { in: ["acked", "ACKED"] } } }),
    prisma.outboxEvent.count({ where: { businessId, status: { in: ["conflict", "CONFLICT"] } } })
  ]);

  return {
    pending,
    failed,
    sent,
    acked,
    conflict
  };
}

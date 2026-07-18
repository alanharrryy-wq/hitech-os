import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID } from "@/server/pos-api/validators";
import { loadPrismaTabletPcOriginConfig, pcUrl, type PrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";
import { CUSTOMER_PROJECTION_STREAM, validateCustomerProjectionEnvelope, type CustomerProjectionEnvelope, type CustomerProjectionRecord } from "@shared-kernel/sync/customer-projection";

const CUSTOMER_PULL_SOURCE = "pc.customer.projection.pull";

type ApplyCounts = { applied: number; duplicate: number; stale: number; conflict: number; rejected: number };

function checkpointKey(input: { businessId: string; terminalId: string }) {
  return `${CUSTOMER_PULL_SOURCE}|source:pc|target:${input.businessId}|terminal:${input.terminalId}`;
}

function iso(value: unknown) {
  const date = value instanceof Date ? value : new Date(String(value || ""));
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

async function applyRecord(tx: any, businessId: string, record: CustomerProjectionRecord): Promise<keyof ApplyCounts> {
  if (record.businessId !== businessId || record.payload.businessId !== businessId) return "rejected";
  const existing = await tx.$queryRaw<Array<{ id: string; businessId: string; displayName: string; isActive: boolean | number; version: number; tombstoneAt: Date | string | null }>>`
    SELECT "id", "businessId", "displayName", "isActive", "version", "tombstoneAt" FROM "Customer" WHERE "id" = ${record.customerId} LIMIT 1
  `;
  const prior = existing[0];
  if (prior && prior.businessId !== businessId) return "conflict";
  if (prior && Number(prior.version) > record.version) return "stale";
  const same = prior && Number(prior.version) === record.version && prior.displayName === record.payload.displayName && (prior.isActive === true || prior.isActive === 1) === record.payload.isActive && iso(prior.tombstoneAt) === record.payload.tombstoneAt;
  if (same) return "duplicate";
  if (prior && Number(prior.version) === record.version) return "conflict";

  await tx.$executeRaw`
    INSERT INTO "Customer" ("id", "businessId", "displayName", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt")
    VALUES (${record.customerId}, ${businessId}, ${record.payload.displayName}, ${record.payload.isActive}, ${record.version}, ${record.payload.sourceSurface}, ${record.payload.tombstoneAt ? new Date(record.payload.tombstoneAt) : null}, ${new Date(record.occurredAt)}, ${new Date(record.payload.updatedAt)})
    ON CONFLICT("id") DO UPDATE SET
      "displayName" = excluded."displayName", "isActive" = excluded."isActive", "version" = excluded."version", "sourceSurface" = excluded."sourceSurface", "tombstoneAt" = excluded."tombstoneAt", "updatedAt" = excluded."updatedAt"
    WHERE "Customer"."businessId" = excluded."businessId" AND "Customer"."version" < excluded."version"
  `;
  return "applied";
}

export async function applyCustomerProjectionEnvelope(input: { businessId: string; terminalId?: string; envelope: unknown }) {
  const validation = validateCustomerProjectionEnvelope(input.envelope);
  const counts: ApplyCounts = { applied: 0, duplicate: 0, stale: 0, conflict: 0, rejected: 0 };
  if (!validation.envelope) return { ok: false, counts, errors: validation.errors, cursor: null };
  const envelope = validation.envelope;
  if (envelope.businessId !== input.businessId) return { ok: false, counts, errors: ["El businessId de la proyección no coincide con Tablet."], cursor: null };
  const terminalId = input.terminalId || DEFAULT_POS_API_TERMINAL_ID;
  const db = prisma as any;
  await db.$transaction(async (tx: any) => {
    await tx.business.upsert({ where: { id: input.businessId }, update: { currency: "MXN" }, create: { id: input.businessId, name: "PRISMA Tablet Local", currency: "MXN" } });
    for (const record of envelope.changes) counts[await applyRecord(tx, input.businessId, record)] += 1;
    const now = new Date();
    await tx.syncCheckpoint.upsert({
      where: { businessId_scopeKey_stream: { businessId: input.businessId, scopeKey: checkpointKey({ businessId: input.businessId, terminalId }), stream: CUSTOMER_PROJECTION_STREAM } },
      create: { id: `customer_checkpoint_${randomUUID()}`, businessId: input.businessId, source: CUSTOMER_PULL_SOURCE, scopeKey: checkpointKey({ businessId: input.businessId, terminalId }), terminalId, stream: CUSTOMER_PROJECTION_STREAM, cursorValue: envelope.cursor.next, lastEventId: envelope.changes.at(-1)?.changeId ?? null, status: counts.conflict || counts.rejected ? "conflict" : "acked", lifecycleStatus: counts.conflict || counts.rejected ? "conflict" : "reconciled", checkpointAt: now, lastAttemptedAt: now, lastSuccessfulAt: counts.conflict || counts.rejected ? null : now, metadataJson: JSON.stringify({ counts, contractId: envelope.contractId }) },
      update: { cursorValue: envelope.cursor.next, lastEventId: envelope.changes.at(-1)?.changeId ?? null, status: counts.conflict || counts.rejected ? "conflict" : "acked", lifecycleStatus: counts.conflict || counts.rejected ? "conflict" : "reconciled", checkpointAt: now, lastAttemptedAt: now, lastSuccessfulAt: counts.conflict || counts.rejected ? undefined : now, metadataJson: JSON.stringify({ counts, contractId: envelope.contractId }) }
    });
  });
  return { ok: counts.conflict === 0 && counts.rejected === 0, counts, errors: [], cursor: envelope.cursor.next };
}

export async function pullCustomerProjectionFromPc(input: { businessId?: string; terminalId?: string; cursor?: string | null; config?: PrismaTabletPcOriginConfig } = {}) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  const terminalId = input.terminalId || DEFAULT_POS_API_TERMINAL_ID;
  const config = input.config ?? loadPrismaTabletPcOriginConfig();
  if (!config.enabled || !config.origin) return { ok: false, reason: "PC_ORIGIN_UNAVAILABLE", counts: null, errors: ["La conexión PC no está configurada."], cursor: input.cursor ?? null };
  const checkpoint = await (prisma as any).syncCheckpoint.findUnique({ where: { businessId_scopeKey_stream: { businessId, scopeKey: checkpointKey({ businessId, terminalId }), stream: CUSTOMER_PROJECTION_STREAM } } }).catch(() => null);
  const cursor = input.cursor ?? checkpoint?.cursorValue ?? null;
  const url = pcUrl(config, `/api/sync/export/customer-projection?businessId=${encodeURIComponent(businessId)}${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`);
  if (!url) return { ok: false, reason: "PC_ORIGIN_UNAVAILABLE", counts: null, errors: ["La conexión PC no está configurada."], cursor };
  const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(config.timeoutMs) }).catch(() => null);
  if (!response?.ok) return { ok: false, reason: "PC_CUSTOMER_PROJECTION_UNAVAILABLE", counts: null, errors: [`PC respondió ${response?.status ?? "sin conexión"}.`], cursor };
  const body = await response.json().catch(() => null) as { data?: CustomerProjectionEnvelope } | null;
  return { reason: "PC_CUSTOMER_PROJECTION_APPLIED", ...(await applyCustomerProjectionEnvelope({ businessId, terminalId, envelope: body?.data ?? body })) };
}

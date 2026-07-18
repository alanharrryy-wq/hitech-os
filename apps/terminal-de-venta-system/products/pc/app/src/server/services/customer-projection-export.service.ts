import { prisma } from "@/server/prisma/client";
import {
  CUSTOMER_PROJECTION_CONTRACT_ID,
  CUSTOMER_PROJECTION_SCHEMA_VERSION,
  CUSTOMER_PROJECTION_STREAM,
  type CustomerProjectionEnvelope,
  type CustomerProjectionRecord
} from "@shared-kernel/sync/customer-projection";

type CustomerProjectionRow = { id: string; businessId: string; displayName: string; isActive: boolean | number; version: number; sourceSurface: string; tombstoneAt: Date | string | null; updatedAt: Date | string };

function iso(value: Date | string | null) {
  const date = value instanceof Date ? value : new Date(String(value ?? ""));
  return Number.isNaN(date.getTime()) ? new Date(0).toISOString() : date.toISOString();
}

function cursorFor(row: CustomerProjectionRow) {
  return `${iso(row.updatedAt)}~${row.id}`;
}

function parseCursor(value: string | null | undefined) {
  const raw = value?.trim() ?? "";
  if (!raw) return null;
  const split = raw.lastIndexOf("~");
  if (split <= 0 || !raw.slice(split + 1)) throw new Error("CUSTOMER_PROJECTION_INVALID_CURSOR");
  const at = new Date(raw.slice(0, split));
  if (Number.isNaN(at.getTime())) throw new Error("CUSTOMER_PROJECTION_INVALID_CURSOR");
  return { at, id: raw.slice(split + 1) };
}

export async function buildCustomerProjectionDelta(input: { businessId: string; cursor?: string | null; limit?: number | null }): Promise<CustomerProjectionEnvelope> {
  const businessId = input.businessId.trim();
  if (!businessId) throw new Error("CUSTOMER_PROJECTION_BUSINESS_REQUIRED");
  const cursor = parseCursor(input.cursor);
  const limit = Math.max(1, Math.min(Math.trunc(input.limit ?? 200), 1000));
  const rows = cursor
    ? await prisma.$queryRaw<CustomerProjectionRow[]>`
        SELECT "id", "businessId", "displayName", "isActive", "version", "sourceSurface", "tombstoneAt", "updatedAt"
        FROM "Customer" WHERE "businessId" = ${businessId} AND ("updatedAt" > ${cursor.at} OR ("updatedAt" = ${cursor.at} AND "id" > ${cursor.id}))
        ORDER BY "updatedAt" ASC, "id" ASC LIMIT ${limit + 1}
      `
    : await prisma.$queryRaw<CustomerProjectionRow[]>`
        SELECT "id", "businessId", "displayName", "isActive", "version", "sourceSurface", "tombstoneAt", "updatedAt"
        FROM "Customer" WHERE "businessId" = ${businessId}
        ORDER BY "updatedAt" ASC, "id" ASC LIMIT ${limit + 1}
      `;
  const page = rows.slice(0, limit);
  const changes: CustomerProjectionRecord[] = page.map((row) => {
    const updatedAt = iso(row.updatedAt);
    const tombstoneAt = row.tombstoneAt ? iso(row.tombstoneAt) : null;
    const isActive = row.isActive === true || row.isActive === 1;
    const operation = !isActive || tombstoneAt ? "tombstone" as const : "upsert" as const;
    return {
      changeId: `${CUSTOMER_PROJECTION_STREAM}:${row.id}:${row.version}`,
      customerId: row.id,
      businessId,
      operation,
      version: Number(row.version),
      occurredAt: updatedAt,
      cursor: cursorFor(row),
      payload: { id: row.id, businessId, displayName: row.displayName, isActive, version: Number(row.version), sourceSurface: row.sourceSurface === "tablet" ? "tablet" : "pc", updatedAt, tombstoneAt }
    };
  });
  return {
    contractId: CUSTOMER_PROJECTION_CONTRACT_ID,
    schemaVersion: CUSTOMER_PROJECTION_SCHEMA_VERSION,
    stream: CUSTOMER_PROJECTION_STREAM,
    businessId,
    generatedAt: new Date().toISOString(),
    cursor: { requested: input.cursor?.trim() || null, next: changes.at(-1)?.cursor ?? (input.cursor?.trim() || null), hasMore: rows.length > limit },
    changes
  };
}

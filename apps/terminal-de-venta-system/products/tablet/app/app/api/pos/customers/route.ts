import { randomUUID } from "node:crypto";
import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID } from "@/server/pos-api/validators";
import { prisma } from "@/server/prisma/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type CustomerRow = { id: string; displayName: string; isActive: boolean | number; version: number; sourceSurface: string; tombstoneAt: Date | string | null; updatedAt: Date | string };

function text(value: unknown, max = 140) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function isConfiguredScope(value: string, configured: string) {
  return !value || value === configured;
}

export async function GET(request: Request) {
  try {
    const params = new URL(request.url).searchParams;
    const requestedBusinessId = text(params.get("businessId"), 120);
    if (!isConfiguredScope(requestedBusinessId, DEFAULT_POS_API_BUSINESS_ID)) return fail("CUSTOMER_SCOPE_DENIED", "La consulta de clientes no pertenece al negocio configurado en esta Tablet.", 403);
    const businessId = DEFAULT_POS_API_BUSINESS_ID;
    const query = text(params.get("q"), 100);
    const rows = query
      ? await prisma.$queryRaw<CustomerRow[]>`SELECT "id", "displayName", "isActive", "version", "sourceSurface", "tombstoneAt", "updatedAt" FROM "Customer" WHERE "businessId" = ${businessId} AND "isActive" = true AND "tombstoneAt" IS NULL AND "displayName" LIKE ${`%${query}%`} ORDER BY "displayName" ASC LIMIT 40`
      : await prisma.$queryRaw<CustomerRow[]>`SELECT "id", "displayName", "isActive", "version", "sourceSurface", "tombstoneAt", "updatedAt" FROM "Customer" WHERE "businessId" = ${businessId} AND "isActive" = true AND "tombstoneAt" IS NULL ORDER BY "displayName" ASC LIMIT 40`;
    return ok({ customers: rows.map((row) => ({ id: row.id, displayName: row.displayName, version: Number(row.version), sourceSurface: row.sourceSurface, updatedAt: new Date(row.updatedAt).toISOString() })) }, undefined, { endpoint: "GET /api/pos/customers", privacy: "minimal_pos_projection" });
  } catch (error) {
    return toPosApiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const requestedBusinessId = text(body?.businessId, 120);
    const requestedTerminalId = text(body?.terminalId, 120);
    if (!isConfiguredScope(requestedBusinessId, DEFAULT_POS_API_BUSINESS_ID) || !isConfiguredScope(requestedTerminalId, DEFAULT_POS_API_TERMINAL_ID)) {
      return fail("CUSTOMER_SCOPE_DENIED", "El alta de cliente no pertenece al negocio o terminal configurados en esta Tablet.", 403);
    }
    const businessId = DEFAULT_POS_API_BUSINESS_ID;
    const terminalId = DEFAULT_POS_API_TERMINAL_ID;
    const displayName = text(body?.displayName, 140);
    const actorId = text(body?.cashier ?? body?.operatorId, 120) || "tablet-cashier";
    if (displayName.length < 2) return fail("CUSTOMER_NAME_REQUIRED", "Captura el nombre del cliente.", 400);
    const duplicate = await prisma.$queryRaw<Array<{ id: string }>>`SELECT "id" FROM "Customer" WHERE "businessId" = ${businessId} AND "isActive" = true AND LOWER("displayName") = LOWER(${displayName}) LIMIT 1`;
    if (duplicate[0]) return fail("CUSTOMER_DUPLICATE", "Ya existe un cliente activo con ese nombre.", 409, { customerId: duplicate[0].id });
    const customerId = randomUUID();
    const eventId = `customer_created_${randomUUID()}`;
    const now = new Date();
    const payload = { retailCustomerId: customerId, businessId, displayName, version: 1, isActive: true, sourceSurface: "tablet", updatedAt: now.toISOString() };
    await (prisma as any).$transaction(async (tx: any) => {
      await tx.business.upsert({ where: { id: businessId }, update: { currency: "MXN" }, create: { id: businessId, name: "PRISMA Tablet Local", currency: "MXN" } });
      await tx.$executeRaw`INSERT INTO "Customer" ("id", "businessId", "displayName", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt") VALUES (${customerId}, ${businessId}, ${displayName}, true, 1, 'tablet', null, ${now}, ${now})`;
      await tx.outboxEvent.create({ data: { id: eventId, businessId, terminalId, topic: "customer.created", aggregateId: customerId, idempotencyKey: `customer.created:${businessId}:${customerId}:1`, payloadJson: JSON.stringify({ eventId, topic: "customer.created", eventType: "customer.created", businessId, terminalId, actorId, aggregateId: customerId, idempotencyKey: `customer.created:${businessId}:${customerId}:1`, occurredAt: now.toISOString(), payload }), source: "tablet-pos", schemaVersion: "1.0.0", status: "pending", createdAt: now } });
      await tx.auditEvent.create({ data: { id: `audit_${randomUUID()}`, businessId, actorId: null, topic: "customer.created", entityType: "Customer", entityId: customerId, summary: "Cliente mínimo creado desde POS Tablet.", afterJson: JSON.stringify({ id: customerId, displayName, version: 1 }), metadataJson: JSON.stringify({ actorId, privacy: "minimal_pos_projection", outboxEventId: eventId }), createdAt: now } });
    });
    return ok({ customer: { id: customerId, displayName, version: 1, sourceSurface: "tablet", updatedAt: now.toISOString() }, outboxEventId: eventId }, { status: 201 }, { endpoint: "POST /api/pos/customers", sync: "pending" });
  } catch (error) {
    return toPosApiError(error);
  }
}

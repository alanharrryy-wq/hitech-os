import { prisma } from "../prisma/client";
import { makePosId } from "../pos-engine/ids";

export async function createSaleReturn(input: any) {
  const now = new Date();
  const topic = "sale.return.created";
  const saleReturn = await prisma.saleReturn.create({
    data: {
      id: makePosId("return"),
      businessId: input.businessId,
      saleFolio: input.saleFolio,
      reason: input.reasonLabel || input.reason,
      amountCents: input.amountCents,
      status: "CREATED",
      cashier: input.cashier,
      createdAt: now
    }
  });

  const eventId = makePosId("event");
  const idempotencyKey = `${topic}:${input.businessId}:${saleReturn.id}`;
  await prisma.outboxEvent.create({
    data: {
      id: eventId,
      businessId: input.businessId,
      topic,
      aggregateId: saleReturn.id,
      idempotencyKey,
      status: "pending",
      createdAt: now,
      payloadJson: JSON.stringify({
        eventId: saleReturn.id,
        topic,
        idempotencyKey,
        businessId: input.businessId,
        actorId: input.cashier,
        source: "tablet-pos-contextual-return",
        occurredAt: now.toISOString(),
        schemaVersion: "1.0",
        payload: { saleFolio: input.saleFolio, amountCents: input.amountCents, lines: input.lines }
      })
    }
  });

  return {
    returnId: saleReturn.id,
    saleFolio: saleReturn.saleFolio,
    reason: saleReturn.reason,
    amountCents: saleReturn.amountCents,
    status: saleReturn.status,
    cashier: saleReturn.cashier,
    createdAt: saleReturn.createdAt
  };
}

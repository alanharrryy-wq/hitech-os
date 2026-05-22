import { prisma } from "../prisma/client";
import { DEFAULT_CASHIER, DEFAULT_TERMINAL_ID, POS_EVENT_SCHEMA_VERSION } from "../pos-engine/constants";
import { makePosId } from "../pos-engine/ids";

function asString(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function asInt(value: unknown) {
  if (Number.isInteger(value)) return value as number;
  if (typeof value === "number" && Number.isFinite(value)) return Math.trunc(value);
  if (typeof value === "string" && value.trim() && Number.isInteger(Number(value))) return Number(value);
  return null;
}

function restoreStockFor(input: any, line: any) {
  if (line?.restoreStock === true || line?.restoreStock === "true" || line?.restoreStock === "1") return true;
  if (line?.restoreStock === false || line?.restoreStock === "false" || line?.restoreStock === "0") return false;
  const reason = `${input?.reason ?? ""} ${input?.reasonLabel ?? ""}`.toLowerCase();
  return !(reason.includes("damaged") || reason.includes("damage") || reason.includes("defect") || reason.includes("merma"));
}

function normalizeReturnLines(input: any) {
  return (Array.isArray(input.lines) ? input.lines : [])
    .filter((line: any) => line && typeof line === "object")
    .map((line: any, index: number) => {
      const qty = asInt(line.qty) ?? 0;
      const unitPriceCents = asInt(line.unitPriceCents ?? line.priceCents) ?? 0;
      const amountCents = asInt(line.amountCents ?? line.totalCents) ?? qty * unitPriceCents;
      return {
        id: asString(line.id) || makePosId("return_line"),
        saleLineId: asString(line.saleLineId) || null,
        productId: asString(line.productId),
        sku: asString(line.sku),
        productName: asString(line.productName ?? line.name) || asString(line.sku) || `Producto devuelto ${index + 1}`,
        qty,
        unitPriceCents,
        amountCents,
        restoreStock: restoreStockFor(input, line)
      };
    })
    .filter((line: any) => line.productId && line.qty > 0 && line.amountCents > 0);
}

export async function createSaleReturn(input: any) {
  const now = new Date();
  const topic = "sale.refunded";
  const terminalId = asString(input.terminalId) || DEFAULT_TERMINAL_ID;
  const actorId = asString(input.actorId ?? input.cashier) || DEFAULT_CASHIER;
  const normalizedLines = normalizeReturnLines(input);
  const db = prisma as any;

  return db.$transaction(async (tx: any) => {
    const saleReturn = await tx.saleReturn.create({
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

    for (const [index, line] of normalizedLines.entries()) {
      const product = await tx.product.findFirst({ where: { id: line.productId, businessId: input.businessId } });
      const stockMovementId = line.restoreStock ? makePosId("stock_return") : null;
      if (line.restoreStock && product) {
        await tx.stockMovement.create({
          data: {
            id: stockMovementId,
            businessId: input.businessId,
            productId: line.productId,
            movement: "return",
            qty: line.qty,
            reason: topic,
            location: "tablet-floor",
            beforeQty: product.stockOnHand,
            afterQty: product.stockOnHand + line.qty,
            sourceType: topic,
            sourceId: saleReturn.id,
            createdAt: now
          }
        });
        await tx.product.update({ where: { id: line.productId }, data: { stockOnHand: { increment: line.qty } } });
      }

      await tx.saleReturnLine.create({
        data: {
          id: line.id || `${saleReturn.id}_line_${index + 1}`,
          businessId: input.businessId,
          saleReturnId: saleReturn.id,
          saleId: asString(input.saleId) || null,
          saleLineId: line.saleLineId,
          productId: line.productId,
          sku: line.sku || product?.sku || line.productId,
          productName: line.productName || product?.name || line.productId,
          qty: line.qty,
          amountCents: line.amountCents,
          restoreStock: line.restoreStock,
          stockMovementId,
          createdAt: now
        }
      });
    }

    const eventId = makePosId("event");
    const idempotencyKey = `${topic}:${input.businessId}:${terminalId}:${saleReturn.id}`;
    const envelope = {
      eventId,
      eventType: topic,
      topic,
      idempotencyKey,
      businessId: input.businessId,
      terminalId,
      actorId,
      aggregateId: saleReturn.id,
      correlationId: asString(input.saleId) || input.saleFolio || saleReturn.id,
      source: "tablet-pos-contextual-return",
      occurredAt: now.toISOString(),
      schemaVersion: POS_EVENT_SCHEMA_VERSION,
      payload: {
        returnId: saleReturn.id,
        saleId: asString(input.saleId) || null,
        saleFolio: input.saleFolio,
        reason: input.reason || "other",
        reasonLabel: input.reasonLabel || saleReturn.reason,
        notes: input.notes || null,
        amountCents: input.amountCents,
        cashier: input.cashier || actorId,
        terminalId,
        actorId,
        lines: normalizedLines
      }
    };

    await tx.outboxEvent.create({
      data: {
        id: eventId,
        businessId: input.businessId,
        terminalId,
        topic,
        aggregateId: saleReturn.id,
        idempotencyKey,
        status: "pending",
        createdAt: now,
        source: envelope.source,
        schemaVersion: POS_EVENT_SCHEMA_VERSION,
        payloadJson: JSON.stringify(envelope)
      }
    });

    return {
      returnId: saleReturn.id,
      saleFolio: saleReturn.saleFolio,
      reason: saleReturn.reason,
      amountCents: saleReturn.amountCents,
      status: saleReturn.status,
      cashier: saleReturn.cashier,
      createdAt: saleReturn.createdAt,
      lineCount: normalizedLines.length,
      topic
    };
  });
}

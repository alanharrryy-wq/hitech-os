/* PRISMA_DARK_PACKSHOTS_197 */
import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";

export type ProductMediaRecord = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  mediaRef: string | null;
  updatedAt: string;
};

type ProductRow = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  mediaRef: string | null;
  updatedAt: Date | string;
};

function iso(value: Date | string) {
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? new Date(0).toISOString() : date.toISOString();
}

function toRecord(row: ProductRow): ProductMediaRecord {
  return { id: row.id, businessId: row.businessId, sku: row.sku, name: row.name, mediaRef: row.mediaRef, updatedAt: iso(row.updatedAt) };
}

export class ProductMediaRepository {
  private async readOne(businessId: string, productId: string) {
    const rows = await prisma.$queryRaw<ProductRow[]>`
      SELECT "id", "businessId", "sku", "name", "mediaRef", "updatedAt" FROM "Product"
      WHERE "businessId" = ${businessId} AND "id" = ${productId} LIMIT 1
    `;
    return rows[0] ? toRecord(rows[0]) : null;
  }

  async list(businessId: string) {
    const rows = await prisma.$queryRaw<ProductRow[]>`
      SELECT "id", "businessId", "sku", "name", "mediaRef", "updatedAt" FROM "Product"
      WHERE "businessId" = ${businessId} AND "isActive" = true ORDER BY "name" ASC, "sku" ASC LIMIT 5000
    `;
    return rows.map(toRecord);
  }

  async update(input: { businessId: string; productId: string; mediaRef: string | null; expectedUpdatedAt: string }) {
    const current = await this.readOne(input.businessId, input.productId);
    if (!current) return null;
    if (current.updatedAt !== input.expectedUpdatedAt) throw new Error("PRODUCT_MEDIA_VERSION_CONFLICT");
    const now = new Date();
    const next: ProductMediaRecord = { ...current, mediaRef: input.mediaRef, updatedAt: now.toISOString() };
    const changed = await prisma.$transaction(async (tx: any) => {
      const count = await tx.$executeRaw`
        UPDATE "Product" SET "mediaRef" = ${input.mediaRef}, "updatedAt" = ${now}
        WHERE "businessId" = ${input.businessId} AND "id" = ${input.productId} AND "updatedAt" = ${new Date(input.expectedUpdatedAt)}
      `;
      if (Number(count) <= 0) return false;
      await tx.auditEvent.create({
        data: {
          id: randomUUID(), businessId: input.businessId, actorId: null, topic: input.mediaRef ? "product.media_ref_set" : "product.media_ref_cleared",
          entityType: "Product", entityId: input.productId, summary: `Product media reference ${input.mediaRef ? "set" : "cleared"} for ${current.sku}.`,
          beforeJson: JSON.stringify({ mediaRef: current.mediaRef, updatedAt: current.updatedAt }), afterJson: JSON.stringify({ mediaRef: input.mediaRef, updatedAt: next.updatedAt }),
          metadataJson: JSON.stringify({ source: "pc", portableReferenceOnly: true })
        }
      });
      await tx.outboxEvent.create({
        data: {
          id: randomUUID(), businessId: input.businessId, topic: "product.media_ref.changed", eventType: input.mediaRef ? "product.media_ref.set" : "product.media_ref.cleared",
          aggregateId: input.productId, idempotencyKey: `product_media:${input.productId}:${now.getTime()}`, payloadJson: JSON.stringify({ productId: input.productId, businessId: input.businessId, occurredAt: now.toISOString() }),
          source: "pc", schemaVersion: "product-media.v1", status: "pending", lifecycleStatus: "pending", attempts: 0, createdAt: now
        }
      });
      return true;
    });
    if (!changed) throw new Error("PRODUCT_MEDIA_VERSION_CONFLICT");
    const updated = await this.readOne(input.businessId, input.productId);
    if (!updated) throw new Error("PRODUCT_MEDIA_UPDATE_NOT_VISIBLE");
    return updated;
  }
}

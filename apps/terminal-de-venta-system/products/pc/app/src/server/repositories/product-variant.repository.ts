import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";

export type ProductVariantStatus = "ACTIVE" | "INACTIVE";

export type ProductVariantProduct = {
  id: string;
  sku: string;
  name: string;
  isActive: boolean;
};

export type ProductVariantRecord = {
  id: string;
  businessId: string;
  productId: string;
  productSku: string;
  productName: string;
  variantProductId: string;
  variantSku: string;
  variantName: string;
  label: string;
  attributes: Record<string, string>;
  sortOrder: number;
  status: ProductVariantStatus;
  version: number;
  createdAt: string;
  updatedAt: string;
};

export type CreateProductVariantInput = {
  productId: string;
  variantProductId: string;
  label: string;
  attributes: Record<string, string>;
  sortOrder: number;
  idempotencyKey: string;
};

export type UpdateProductVariantInput = {
  expectedVersion: number;
  label?: string;
  attributes?: Record<string, string>;
  sortOrder?: number;
  status?: ProductVariantStatus;
};

type ProductRow = { id: string; sku: string; name: string; isActive: boolean | number };
type VariantRow = {
  id: string;
  businessId: string;
  productId: string;
  productSku: string;
  productName: string;
  variantProductId: string;
  variantSku: string;
  variantName: string;
  label: string;
  attributesJson: string | null;
  sortOrder: number;
  status: string;
  version: number;
  createdAt: Date | string;
  updatedAt: Date | string;
};

function iso(value: Date | string) {
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? new Date(0).toISOString() : date.toISOString();
}

function parseAttributes(value: string | null): Record<string, string> {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).flatMap(([key, raw]) => typeof raw === "string" && key ? [[key, raw]] : []));
  } catch {
    return {};
  }
}

function status(value: string): ProductVariantStatus {
  return value === "INACTIVE" ? "INACTIVE" : "ACTIVE";
}

function toRecord(row: VariantRow): ProductVariantRecord {
  return {
    id: row.id,
    businessId: row.businessId,
    productId: row.productId,
    productSku: row.productSku,
    productName: row.productName,
    variantProductId: row.variantProductId,
    variantSku: row.variantSku,
    variantName: row.variantName,
    label: row.label,
    attributes: parseAttributes(row.attributesJson),
    sortOrder: Number(row.sortOrder),
    status: status(row.status),
    version: Number(row.version),
    createdAt: iso(row.createdAt),
    updatedAt: iso(row.updatedAt)
  };
}

export class ProductVariantRepository {
  private async readOne(businessId: string, variantId: string): Promise<ProductVariantRecord | null> {
    const rows = await prisma.$queryRaw<VariantRow[]>`
      SELECT "ProductVariant"."id", "ProductVariant"."businessId", "ProductVariant"."productId", "Parent"."sku" AS "productSku", "Parent"."name" AS "productName",
        "ProductVariant"."variantProductId", "Child"."sku" AS "variantSku", "Child"."name" AS "variantName", "ProductVariant"."label", "ProductVariant"."attributesJson",
        "ProductVariant"."sortOrder", "ProductVariant"."status", "ProductVariant"."version", "ProductVariant"."createdAt", "ProductVariant"."updatedAt"
      FROM "ProductVariant"
      INNER JOIN "Product" AS "Parent" ON "Parent"."id" = "ProductVariant"."productId" AND "Parent"."businessId" = "ProductVariant"."businessId"
      INNER JOIN "Product" AS "Child" ON "Child"."id" = "ProductVariant"."variantProductId" AND "Child"."businessId" = "ProductVariant"."businessId"
      WHERE "ProductVariant"."businessId" = ${businessId} AND "ProductVariant"."id" = ${variantId}
      LIMIT 1
    `;
    return rows[0] ? toRecord(rows[0]) : null;
  }

  private async readProduct(businessId: string, productId: string) {
    const rows = await prisma.$queryRaw<ProductRow[]>`
      SELECT "id", "sku", "name", "isActive" FROM "Product" WHERE "businessId" = ${businessId} AND "id" = ${productId} LIMIT 1
    `;
    return rows[0] ? { ...rows[0], isActive: rows[0].isActive === true || rows[0].isActive === 1 } : null;
  }

  private async validatePair(businessId: string, productId: string, variantProductId: string) {
    if (productId === variantProductId) throw new Error("PRODUCT_VARIANT_SELF_REFERENCE");
    const [parent, child] = await Promise.all([this.readProduct(businessId, productId), this.readProduct(businessId, variantProductId)]);
    if (!parent || !child || !parent.isActive || !child.isActive) throw new Error("PRODUCT_VARIANT_PRODUCT_NOT_AVAILABLE");
    const nested = await prisma.$queryRaw<Array<{ id: string }>>`
      SELECT "id" FROM "ProductVariant" WHERE "businessId" = ${businessId} AND "variantProductId" = ${productId} AND "status" = 'ACTIVE' LIMIT 1
    `;
    if (nested[0]) throw new Error("PRODUCT_VARIANT_NESTED_PARENT");
  }

  private async recordAudit(tx: any, input: { businessId: string; topic: string; variant: ProductVariantRecord; before?: Pick<ProductVariantRecord, "status" | "label" | "version"> }) {
    await tx.auditEvent.create({
      data: {
        id: randomUUID(),
        businessId: input.businessId,
        actorId: null,
        topic: input.topic,
        entityType: "ProductVariant",
        entityId: input.variant.id,
        summary: `Product variant ${input.variant.label} ${input.topic}.`,
        beforeJson: input.before ? JSON.stringify(input.before) : null,
        afterJson: JSON.stringify({ id: input.variant.id, productId: input.variant.productId, variantProductId: input.variant.variantProductId, label: input.variant.label, status: input.variant.status, version: input.variant.version }),
        metadataJson: JSON.stringify({ source: "pc", preservesSellableProductOwner: true })
      }
    });
  }

  private async recordOutbox(tx: any, input: { businessId: string; eventType: "created" | "updated" | "deactivated"; variant: ProductVariantRecord; at: Date }) {
    await tx.outboxEvent.create({
      data: {
        id: randomUUID(),
        businessId: input.businessId,
        topic: "product_variant.changed",
        eventType: `product_variant.${input.eventType}`,
        aggregateId: input.variant.id,
        idempotencyKey: `product_variant:${input.variant.id}:v${input.variant.version}`,
        payloadJson: JSON.stringify({ id: input.variant.id, businessId: input.businessId, productId: input.variant.productId, variantProductId: input.variant.variantProductId, status: input.variant.status, version: input.variant.version, occurredAt: input.at.toISOString() }),
        source: "pc",
        schemaVersion: "product-variant.v1",
        status: "pending",
        lifecycleStatus: "pending",
        attempts: 0,
        createdAt: input.at
      }
    });
  }

  async listProducts(businessId: string): Promise<ProductVariantProduct[]> {
    const rows = await prisma.$queryRaw<ProductRow[]>`
      SELECT "id", "sku", "name", "isActive" FROM "Product" WHERE "businessId" = ${businessId} AND "isActive" = true
      ORDER BY "name" ASC, "sku" ASC LIMIT 300
    `;
    return rows.map((row) => ({ id: row.id, sku: row.sku, name: row.name, isActive: row.isActive === true || row.isActive === 1 }));
  }

  async list(businessId: string): Promise<ProductVariantRecord[]> {
    const rows = await prisma.$queryRaw<VariantRow[]>`
      SELECT "ProductVariant"."id", "ProductVariant"."businessId", "ProductVariant"."productId", "Parent"."sku" AS "productSku", "Parent"."name" AS "productName",
        "ProductVariant"."variantProductId", "Child"."sku" AS "variantSku", "Child"."name" AS "variantName", "ProductVariant"."label", "ProductVariant"."attributesJson",
        "ProductVariant"."sortOrder", "ProductVariant"."status", "ProductVariant"."version", "ProductVariant"."createdAt", "ProductVariant"."updatedAt"
      FROM "ProductVariant"
      INNER JOIN "Product" AS "Parent" ON "Parent"."id" = "ProductVariant"."productId" AND "Parent"."businessId" = "ProductVariant"."businessId"
      INNER JOIN "Product" AS "Child" ON "Child"."id" = "ProductVariant"."variantProductId" AND "Child"."businessId" = "ProductVariant"."businessId"
      WHERE "ProductVariant"."businessId" = ${businessId}
      ORDER BY "Parent"."name" ASC, "ProductVariant"."sortOrder" ASC, "Child"."name" ASC LIMIT 300
    `;
    return rows.map(toRecord);
  }

  async create(businessId: string, input: CreateProductVariantInput) {
    const existing = await prisma.$queryRaw<Array<{ id: string }>>`
      SELECT "id" FROM "ProductVariant" WHERE "businessId" = ${businessId} AND "idempotencyKey" = ${input.idempotencyKey} LIMIT 1
    `;
    if (existing[0]) {
      const variant = await this.readOne(businessId, existing[0].id);
      if (variant) return { variant, replayed: true };
    }
    await this.validatePair(businessId, input.productId, input.variantProductId);
    const duplicate = await prisma.$queryRaw<Array<{ id: string }>>`
      SELECT "id" FROM "ProductVariant" WHERE "businessId" = ${businessId} AND "variantProductId" = ${input.variantProductId} LIMIT 1
    `;
    if (duplicate[0]) throw new Error("PRODUCT_VARIANT_SELLABLE_ALREADY_LINKED");
    const id = randomUUID();
    const now = new Date();
    const variant: ProductVariantRecord = {
      id, businessId, productId: input.productId, productSku: "", productName: "", variantProductId: input.variantProductId, variantSku: "", variantName: "",
      label: input.label, attributes: input.attributes, sortOrder: input.sortOrder, status: "ACTIVE", version: 1, createdAt: now.toISOString(), updatedAt: now.toISOString()
    };
    await prisma.$transaction(async (tx: any) => {
      await tx.$executeRaw`
        INSERT INTO "ProductVariant" ("id", "businessId", "productId", "variantProductId", "label", "attributesJson", "sortOrder", "status", "idempotencyKey", "version", "createdAt", "updatedAt")
        VALUES (${id}, ${businessId}, ${input.productId}, ${input.variantProductId}, ${input.label}, ${JSON.stringify(input.attributes)}, ${input.sortOrder}, 'ACTIVE', ${input.idempotencyKey}, 1, ${now}, ${now})
      `;
      await this.recordAudit(tx, { businessId, topic: "product_variant.created", variant });
      await this.recordOutbox(tx, { businessId, eventType: "created", variant, at: now });
    });
    const created = await this.readOne(businessId, id);
    if (!created) throw new Error("PRODUCT_VARIANT_CREATE_NOT_VISIBLE");
    return { variant: created, replayed: false };
  }

  async update(businessId: string, variantId: string, input: UpdateProductVariantInput) {
    const current = await this.readOne(businessId, variantId);
    if (!current) return null;
    if (current.version !== input.expectedVersion) throw new Error("PRODUCT_VARIANT_VERSION_CONFLICT");
    const now = new Date();
    const next: ProductVariantRecord = {
      ...current,
      label: input.label ?? current.label,
      attributes: input.attributes ?? current.attributes,
      sortOrder: input.sortOrder ?? current.sortOrder,
      status: input.status ?? current.status,
      version: current.version + 1,
      updatedAt: now.toISOString()
    };
    const changed = await prisma.$transaction(async (tx: any) => {
      const count = await tx.$executeRaw`
        UPDATE "ProductVariant" SET "label" = ${next.label}, "attributesJson" = ${JSON.stringify(next.attributes)}, "sortOrder" = ${next.sortOrder}, "status" = ${next.status}, "version" = "version" + 1, "updatedAt" = ${now}
        WHERE "businessId" = ${businessId} AND "id" = ${variantId} AND "version" = ${input.expectedVersion}
      `;
      if (Number(count) <= 0) return false;
      const eventType = next.status === "INACTIVE" ? "deactivated" : "updated";
      await this.recordAudit(tx, { businessId, topic: `product_variant.${eventType}`, variant: next, before: { status: current.status, label: current.label, version: current.version } });
      await this.recordOutbox(tx, { businessId, eventType, variant: next, at: now });
      return true;
    });
    if (!changed) throw new Error("PRODUCT_VARIANT_VERSION_CONFLICT");
    const updated = await this.readOne(businessId, variantId);
    if (!updated) throw new Error("PRODUCT_VARIANT_UPDATE_NOT_VISIBLE");
    return updated;
  }
}

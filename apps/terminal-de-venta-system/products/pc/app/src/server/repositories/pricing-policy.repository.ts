// PRISMA_PRICING_OWNER_V1
import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";

export const PRICING_ENTITIES = [
  "price-lists",
  "price-list-items",
  "tax-rates",
  "promotions",
  "discounts",
  "authorization-rules",
  "authorization-requests"
] as const;

export type PricingEntity = (typeof PRICING_ENTITIES)[number];

export type PricingWorkspace = {
  businessId: string;
  mutationReady: boolean;
  warnings: string[];
  products: Array<{ id: string; sku: string; name: string; priceCents: number; isActive: boolean }>;
  priceLists: Array<Record<string, unknown>>;
  priceListItems: Array<Record<string, unknown>>;
  taxRates: Array<Record<string, unknown>>;
  promotions: Array<Record<string, unknown>>;
  discounts: Array<Record<string, unknown>>;
  authorizationRules: Array<Record<string, unknown>>;
  authorizationRequests: Array<Record<string, unknown>>;
  generatedAt: string;
};

const TABLES: Record<PricingEntity, string> = {
  "price-lists": "PriceList",
  "price-list-items": "PriceListItem",
  "tax-rates": "TaxRate",
  promotions: "PromotionRule",
  discounts: "DiscountPolicy",
  "authorization-rules": "PricingAuthorizationRule",
  "authorization-requests": "PricingAuthorizationRequest"
};

const TOPICS: Record<PricingEntity, string> = {
  "price-lists": "pricing.price_list.changed",
  "price-list-items": "pricing.price_list_item.changed",
  "tax-rates": "pricing.tax_rate.changed",
  promotions: "pricing.promotion.changed",
  discounts: "pricing.discount_policy.changed",
  "authorization-rules": "pricing.authorization_rule.changed",
  "authorization-requests": "pricing.authorization.requested"
};

const ALLOWED_UPDATE_COLUMNS: Record<PricingEntity, string[]> = {
  "price-lists": ["name", "currency", "isDefault", "isActive", "startsAt", "endsAt"],
  "price-list-items": ["priceListId", "productId", "priceCents", "startsAt", "endsAt"],
  "tax-rates": ["name", "rateBps", "isDefault", "isActive"],
  promotions: ["name", "description", "ruleType", "priority", "stackingPolicy", "eligibilityJson", "benefitJson", "startsAt", "endsAt", "status"],
  discounts: ["name", "discountType", "valueBps", "valueCents", "minimumSubtotalCents", "maximumDiscountCents", "scopeJson", "authorizationRuleId", "startsAt", "endsAt", "status"],
  "authorization-rules": ["name", "actionType", "thresholdType", "thresholdValue", "requiredPermission", "status"],
  "authorization-requests": ["status", "decidedById", "decisionReason", "decidedAt"]
};

function quoteIdentifier(value: string) {
  if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(value)) throw new Error("PRICING_IDENTIFIER_INVALID");
  return `"${value}"`;
}

function serializable(value: unknown): unknown {
  if (value instanceof Date) return value.toISOString();
  if (Array.isArray(value)) return value.map(serializable);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([key, item]) => [key, serializable(item)]));
  }
  return value;
}

function statusForCreate(entity: PricingEntity, input: Record<string, unknown>) {
  if (entity === "authorization-requests") return "PENDING";
  return String(input.status || "ACTIVE").toUpperCase();
}

async function safeRows<T = Record<string, unknown>>(sql: string, ...params: unknown[]): Promise<T[]> {
  try {
    return await (prisma as any).$queryRawUnsafe(sql, ...params) as T[];
  } catch {
    return [];
  }
}

async function migrationReady() {
  const tables = await safeRows<{ name: string }>(
    "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('PromotionRule','DiscountPolicy','PricingAuthorizationRule','PricingAuthorizationRequest')"
  );
  if (new Set(tables.map((row) => row.name)).size !== 4) return false;
  const columns = await safeRows<{ name: string }>('PRAGMA table_info("PriceList")');
  return columns.some((column) => column.name === "version") && columns.some((column) => column.name === "idempotencyKey");
}

async function readOne(tx: any, entity: PricingEntity, businessId: string, id: string) {
  const table = quoteIdentifier(TABLES[entity]);
  const rows = await tx.$queryRawUnsafe(`SELECT * FROM ${table} WHERE "businessId" = ? AND "id" = ? LIMIT 1`, businessId, id);
  return rows[0] ? serializable(rows[0]) as Record<string, unknown> : null;
}

async function recordEvidence(
  tx: any,
  input: {
    entity: PricingEntity;
    businessId: string;
    record: Record<string, unknown>;
    eventType: "created" | "updated" | "deactivated" | "requested" | "approved" | "denied";
    before?: Record<string, unknown> | null;
    actorId?: string | null;
  }
) {
  const recordId = String(input.record.id);
  const version = Number(input.record.version ?? 1);
  const topic = input.entity === "authorization-requests" && (input.eventType === "approved" || input.eventType === "denied")
    ? "pricing.authorization.decided"
    : TOPICS[input.entity];
  const now = new Date();
  await tx.auditEvent.create({
    data: {
      id: randomUUID(),
      businessId: input.businessId,
      actorId: input.actorId ?? null,
      topic,
      entityType: TABLES[input.entity],
      entityId: recordId,
      summary: `${TABLES[input.entity]} ${input.eventType}.`,
      beforeJson: input.before ? JSON.stringify(input.before) : null,
      afterJson: JSON.stringify(input.record),
      metadataJson: JSON.stringify({
        source: "pc",
        durable: true,
        pricingOwnerVersion: "v1",
        eventType: input.eventType
      }),
      createdAt: now
    }
  });
  await tx.outboxEvent.create({
    data: {
      id: randomUUID(),
      businessId: input.businessId,
      terminalId: null,
      topic,
      eventType: `${topic}.${input.eventType}`,
      aggregateId: recordId,
      idempotencyKey: `${topic}:${recordId}:v${version}`,
      correlationId: null,
      payloadJson: JSON.stringify({
        businessId: input.businessId,
        aggregateId: recordId,
        version,
        actorId: input.actorId ?? null,
        occurredAt: now.toISOString(),
        record: input.record
      }),
      source: "pc",
      schemaVersion: "pricing-owner.v1",
      status: "pending",
      lifecycleStatus: "pending",
      attempts: 0,
      createdAt: now
    }
  });
}

function createData(entity: PricingEntity, input: Record<string, unknown>) {
  const now = new Date();
  const common = {
    id: randomUUID(),
    businessId: String(input.businessId),
    idempotencyKey: String(input.idempotencyKey),
    version: 1,
    createdAt: now,
    updatedAt: now
  };
  if (entity === "price-lists") {
    return {
      ...common,
      name: input.name,
      currency: input.currency ?? "MXN",
      isDefault: Boolean(input.isDefault),
      isActive: input.isActive !== false,
      startsAt: input.startsAt,
      endsAt: input.endsAt ?? null
    };
  }
  if (entity === "price-list-items") {
    return {
      ...common,
      priceListId: input.priceListId,
      productId: input.productId,
      priceCents: input.priceCents,
      startsAt: input.startsAt,
      endsAt: input.endsAt ?? null
    };
  }
  if (entity === "tax-rates") {
    return {
      ...common,
      name: input.name,
      rateBps: input.rateBps,
      isDefault: Boolean(input.isDefault),
      isActive: input.isActive !== false
    };
  }
  if (entity === "promotions") {
    return {
      ...common,
      name: input.name,
      description: input.description ?? null,
      ruleType: input.ruleType,
      priority: input.priority ?? 100,
      stackingPolicy: input.stackingPolicy ?? "EXCLUSIVE",
      eligibilityJson: input.eligibilityJson ?? "{}",
      benefitJson: input.benefitJson ?? "{}",
      startsAt: input.startsAt,
      endsAt: input.endsAt ?? null,
      status: statusForCreate(entity, input),
      createdById: input.actorId ?? null,
      updatedById: input.actorId ?? null
    };
  }
  if (entity === "discounts") {
    return {
      ...common,
      name: input.name,
      discountType: input.discountType,
      valueBps: input.valueBps ?? null,
      valueCents: input.valueCents ?? null,
      minimumSubtotalCents: input.minimumSubtotalCents ?? 0,
      maximumDiscountCents: input.maximumDiscountCents ?? null,
      scopeJson: input.scopeJson ?? "{}",
      authorizationRuleId: input.authorizationRuleId ?? null,
      startsAt: input.startsAt,
      endsAt: input.endsAt ?? null,
      status: statusForCreate(entity, input),
      createdById: input.actorId ?? null,
      updatedById: input.actorId ?? null
    };
  }
  if (entity === "authorization-rules") {
    return {
      ...common,
      name: input.name,
      actionType: input.actionType,
      thresholdType: input.thresholdType,
      thresholdValue: input.thresholdValue,
      requiredPermission: input.requiredPermission,
      status: statusForCreate(entity, input)
    };
  }
  return {
    ...common,
    ruleId: input.ruleId,
    requestedById: input.requestedById ?? null,
    requestedActionJson: input.requestedActionJson ?? "{}",
    reason: input.reason,
    status: "PENDING",
    decidedById: null,
    decisionReason: null,
    decidedAt: null
  };
}

export class PricingPolicyRepository {
  async workspace(businessId: string): Promise<PricingWorkspace> {
    const ready = await migrationReady();
    const warnings: string[] = [];
    if (!ready) warnings.push("La migración canónica de Pricing aún no está aplicada; las mutaciones permanecen bloqueadas.");

    const [products, fallbackPriceLists, fallbackTaxRates] = await Promise.all([
      prisma.product.findMany({
        where: { businessId, isActive: true },
        select: { id: true, sku: true, name: true, priceCents: true, isActive: true },
        orderBy: [{ name: "asc" }, { sku: "asc" }],
        take: 500
      }).catch(() => []),
      prisma.priceList.findMany({
        where: { businessId },
        select: { id: true, name: true, currency: true, isDefault: true, isActive: true, startsAt: true, endsAt: true, createdAt: true, updatedAt: true, _count: { select: { items: true } } },
        orderBy: [{ isDefault: "desc" }, { name: "asc" }]
      }).catch(() => []),
      prisma.taxRate.findMany({
        where: { businessId },
        select: { id: true, name: true, rateBps: true, isDefault: true, isActive: true, createdAt: true, updatedAt: true },
        orderBy: [{ isDefault: "desc" }, { name: "asc" }]
      }).catch(() => [])
    ]);

    const [priceListsRaw, itemsRaw, taxesRaw, promotions, discounts, rules, requests] = ready
      ? await Promise.all([
          safeRows('SELECT p.*, (SELECT COUNT(*) FROM "PriceListItem" i WHERE i."businessId" = p."businessId" AND i."priceListId" = p."id") AS "itemCount" FROM "PriceList" p WHERE p."businessId" = ? ORDER BY p."isDefault" DESC, p."name" ASC', businessId),
          safeRows('SELECT i.*, p."name" AS "priceListName", pr."sku" AS "productSku", pr."name" AS "productName" FROM "PriceListItem" i LEFT JOIN "PriceList" p ON p."id" = i."priceListId" AND p."businessId" = i."businessId" LEFT JOIN "Product" pr ON pr."id" = i."productId" AND pr."businessId" = i."businessId" WHERE i."businessId" = ? ORDER BY i."updatedAt" DESC LIMIT 500', businessId),
          safeRows('SELECT * FROM "TaxRate" WHERE "businessId" = ? ORDER BY "isDefault" DESC, "name" ASC', businessId),
          safeRows('SELECT * FROM "PromotionRule" WHERE "businessId" = ? ORDER BY "priority" ASC, "updatedAt" DESC', businessId),
          safeRows('SELECT * FROM "DiscountPolicy" WHERE "businessId" = ? ORDER BY "updatedAt" DESC', businessId),
          safeRows('SELECT * FROM "PricingAuthorizationRule" WHERE "businessId" = ? ORDER BY "updatedAt" DESC', businessId),
          safeRows('SELECT r.*, a."name" AS "ruleName" FROM "PricingAuthorizationRequest" r LEFT JOIN "PricingAuthorizationRule" a ON a."id" = r."ruleId" AND a."businessId" = r."businessId" WHERE r."businessId" = ? ORDER BY r."createdAt" DESC LIMIT 200', businessId)
        ])
      : [[], [], [], [], [], [], []];

    return {
      businessId,
      mutationReady: ready,
      warnings,
      products: serializable(products) as PricingWorkspace["products"],
      priceLists: ready ? serializable(priceListsRaw) as Array<Record<string, unknown>> : serializable(fallbackPriceLists.map((row) => ({ ...row, version: 1, itemCount: row._count.items }))) as Array<Record<string, unknown>>,
      priceListItems: serializable(itemsRaw) as Array<Record<string, unknown>>,
      taxRates: ready ? serializable(taxesRaw) as Array<Record<string, unknown>> : serializable(fallbackTaxRates.map((row) => ({ ...row, version: 1 }))) as Array<Record<string, unknown>>,
      promotions: serializable(promotions) as Array<Record<string, unknown>>,
      discounts: serializable(discounts) as Array<Record<string, unknown>>,
      authorizationRules: serializable(rules) as Array<Record<string, unknown>>,
      authorizationRequests: serializable(requests) as Array<Record<string, unknown>>,
      generatedAt: new Date().toISOString()
    };
  }

  async list(businessId: string, entity: PricingEntity) {
    if (!(await migrationReady())) throw new Error("PRICING_MIGRATION_REQUIRED");
    const table = quoteIdentifier(TABLES[entity]);
    return serializable(await safeRows(`SELECT * FROM ${table} WHERE "businessId" = ? ORDER BY "updatedAt" DESC LIMIT 500`, businessId));
  }

  async create(businessId: string, entity: PricingEntity, input: Record<string, unknown>) {
    if (!(await migrationReady())) throw new Error("PRICING_MIGRATION_REQUIRED");
    const table = quoteIdentifier(TABLES[entity]);
    const idempotencyKey = String(input.idempotencyKey || "");
    const existing = await safeRows<Record<string, unknown>>(
      `SELECT * FROM ${table} WHERE "businessId" = ? AND "idempotencyKey" = ? LIMIT 1`,
      businessId,
      idempotencyKey
    );
    if (existing[0]) return { record: serializable(existing[0]) as Record<string, unknown>, replayed: true };

    const data: Record<string, unknown> = createData(entity, { ...input, businessId });
    return prisma.$transaction(async (tx: any) => {
      if (entity === "price-list-items") {
        const dependencies = await Promise.all([
          tx.$queryRawUnsafe('SELECT "id" FROM "PriceList" WHERE "businessId" = ? AND "id" = ? LIMIT 1', businessId, data.priceListId),
          tx.$queryRawUnsafe('SELECT "id" FROM "Product" WHERE "businessId" = ? AND "id" = ? LIMIT 1', businessId, data.productId)
        ]);
        if (!dependencies[0][0]) throw new Error("PRICING_PRICE_LIST_NOT_FOUND");
        if (!dependencies[1][0]) throw new Error("PRICING_PRODUCT_NOT_FOUND");
      }
      if (entity === "discounts" && data.authorizationRuleId) {
        const rule = await tx.$queryRawUnsafe('SELECT "id" FROM "PricingAuthorizationRule" WHERE "businessId" = ? AND "id" = ? LIMIT 1', businessId, data.authorizationRuleId);
        if (!rule[0]) throw new Error("PRICING_AUTH_RULE_NOT_FOUND");
      }
      if (entity === "authorization-requests") {
        const rule = await tx.$queryRawUnsafe('SELECT "id" FROM "PricingAuthorizationRule" WHERE "businessId" = ? AND "id" = ? AND "status" = ? LIMIT 1', businessId, data.ruleId, "ACTIVE");
        if (!rule[0]) throw new Error("PRICING_AUTH_RULE_NOT_FOUND");
      }
      if (entity === "price-lists" && data.isDefault) {
        await tx.$executeRawUnsafe('UPDATE "PriceList" SET "isDefault" = 0, "version" = "version" + 1, "updatedAt" = ? WHERE "businessId" = ?', new Date(), businessId);
      }
      if (entity === "tax-rates" && data.isDefault) {
        await tx.$executeRawUnsafe('UPDATE "TaxRate" SET "isDefault" = 0, "version" = "version" + 1, "updatedAt" = ? WHERE "businessId" = ?', new Date(), businessId);
      }
      const columns = Object.keys(data);
      const sql = `INSERT INTO ${table} (${columns.map(quoteIdentifier).join(", ")}) VALUES (${columns.map(() => "?").join(", ")})`;
      await tx.$executeRawUnsafe(sql, ...columns.map((column) => data[column as keyof typeof data]));
      const record = await readOne(tx, entity, businessId, String(data.id));
      if (!record) throw new Error("PRICING_CREATE_NOT_VISIBLE");
      await recordEvidence(tx, {
        entity,
        businessId,
        record,
        eventType: entity === "authorization-requests" ? "requested" : "created",
        actorId: typeof input.actorId === "string" ? input.actorId : null
      });
      return { record, replayed: false };
    });
  }

  async update(businessId: string, entity: PricingEntity, id: string, input: Record<string, unknown>) {
    if (!(await migrationReady())) throw new Error("PRICING_MIGRATION_REQUIRED");
    const expectedVersion = Number(input.expectedVersion);
    if (!Number.isInteger(expectedVersion) || expectedVersion < 1) throw new Error("PRICING_VERSION_REQUIRED");
    const table = quoteIdentifier(TABLES[entity]);

    return prisma.$transaction(async (tx: any) => {
      const current = await readOne(tx, entity, businessId, id);
      if (!current) return null;
      if (Number(current.version) !== expectedVersion) throw new Error("PRICING_VERSION_CONFLICT");

      const update: Record<string, unknown> = {};
      for (const column of ALLOWED_UPDATE_COLUMNS[entity]) {
        if (input[column] !== undefined) update[column] = input[column];
      }
      if (entity === "authorization-requests") {
        const status = String(update.status || "").toUpperCase();
        if (status !== "APPROVED" && status !== "DENIED") throw new Error("PRICING_AUTH_DECISION_INVALID");
        if (String(current.status).toUpperCase() !== "PENDING") throw new Error("PRICING_AUTH_REQUEST_TERMINAL");
        update.status = status;
        update.decidedAt = new Date();
      }
      if (entity === "price-lists" && update.isDefault === true) {
        await tx.$executeRawUnsafe('UPDATE "PriceList" SET "isDefault" = 0, "version" = "version" + 1, "updatedAt" = ? WHERE "businessId" = ? AND "id" <> ?', new Date(), businessId, id);
      }
      if (entity === "tax-rates" && update.isDefault === true) {
        await tx.$executeRawUnsafe('UPDATE "TaxRate" SET "isDefault" = 0, "version" = "version" + 1, "updatedAt" = ? WHERE "businessId" = ? AND "id" <> ?', new Date(), businessId, id);
      }
      if (!Object.keys(update).length) throw new Error("PRICING_UPDATE_EMPTY");

      const columns = Object.keys(update);
      const now = new Date();
      const sql = `UPDATE ${table} SET ${columns.map((column) => `${quoteIdentifier(column)} = ?`).join(", ")}, "version" = "version" + 1, "updatedAt" = ? WHERE "businessId" = ? AND "id" = ? AND "version" = ?`;
      const changed = await tx.$executeRawUnsafe(sql, ...columns.map((column) => update[column]), now, businessId, id, expectedVersion);
      if (Number(changed) <= 0) throw new Error("PRICING_VERSION_CONFLICT");
      const record = await readOne(tx, entity, businessId, id);
      if (!record) throw new Error("PRICING_UPDATE_NOT_VISIBLE");
      const eventType = entity === "authorization-requests"
        ? String(record.status).toUpperCase() === "APPROVED" ? "approved" : "denied"
        : update.status === "INACTIVE" || update.isActive === false ? "deactivated" : "updated";
      await recordEvidence(tx, {
        entity,
        businessId,
        record,
        before: current,
        eventType,
        actorId: typeof input.actorId === "string" ? input.actorId : null
      });
      return record;
    });
  }
}

export const pricingPolicyRepository = new PricingPolicyRepository();

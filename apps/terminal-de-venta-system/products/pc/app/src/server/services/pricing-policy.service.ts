// PRISMA_PRICING_OWNER_V1
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import {
  PRICING_ENTITIES,
  pricingPolicyRepository,
  type PricingEntity,
  type PricingWorkspace
} from "@/server/repositories/pricing-policy.repository";

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function text(value: unknown, max: number, required = false) {
  const normalized = typeof value === "string" ? value.trim().slice(0, max) : "";
  if (required && !normalized) throw new Error("PRICING_REQUIRED_FIELD");
  return normalized;
}

function optionalText(value: unknown, max: number) {
  const normalized = text(value, max);
  return normalized || null;
}

function integer(value: unknown, options: { min?: number; max?: number; nullable?: boolean } = {}) {
  if ((value === null || value === undefined || value === "") && options.nullable) return null;
  const parsed = Number(value);
  if (!Number.isInteger(parsed)) throw new Error("PRICING_INTEGER_REQUIRED");
  if (options.min !== undefined && parsed < options.min) throw new Error("PRICING_VALUE_OUT_OF_RANGE");
  if (options.max !== undefined && parsed > options.max) throw new Error("PRICING_VALUE_OUT_OF_RANGE");
  return parsed;
}

function bool(value: unknown, fallback = false) {
  if (value === undefined) return fallback;
  return value === true || value === 1 || value === "1" || value === "true" || value === "on";
}

function date(value: unknown, required = false) {
  if (value === null || value === undefined || value === "") {
    if (required) throw new Error("PRICING_DATE_REQUIRED");
    return null;
  }
  const parsed = new Date(String(value));
  if (Number.isNaN(parsed.getTime())) throw new Error("PRICING_DATE_INVALID");
  return parsed;
}

function json(value: unknown, fallback: Record<string, unknown> = {}) {
  if (value === undefined || value === null || value === "") return JSON.stringify(fallback);
  if (typeof value === "object") return JSON.stringify(value);
  try {
    const parsed = JSON.parse(String(value));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error();
    return JSON.stringify(parsed);
  } catch {
    throw new Error("PRICING_JSON_INVALID");
  }
}

function idempotency(value: unknown) {
  const key = text(value, 160, true);
  if (key.length < 12) throw new Error("PRICING_IDEMPOTENCY_REQUIRED");
  return key;
}

export function isPricingEntity(value: string): value is PricingEntity {
  return PRICING_ENTITIES.includes(value as PricingEntity);
}

export function pricingFeatureKey(entity: PricingEntity, action: "read" | "create" | "update") {
  if (action === "read") return "pricing.read";
  if (entity === "price-lists" || entity === "price-list-items") return "pricing.price-lists.write";
  if (entity === "tax-rates") return "pricing.taxes.write";
  if (entity === "promotions") return "pricing.promotions.write";
  if (entity === "discounts") return "pricing.discounts.write";
  if (entity === "authorization-rules") return "pricing.authorization.decide";
  return action === "create" ? "pricing.authorization.request" : "pricing.authorization.decide";
}

export async function getPricingPolicySnapshot(): Promise<PricingWorkspace> {
  const businessId = await resolvePcBusinessScope();
  return pricingPolicyRepository.workspace(businessId);
}

export async function listPricingEntity(entity: PricingEntity) {
  const businessId = await resolvePcBusinessScope();
  return pricingPolicyRepository.list(businessId, entity);
}

export function readPricingCreate(entity: PricingEntity, body: unknown) {
  const raw = record(body);
  const common = { idempotencyKey: idempotency(raw.idempotencyKey), actorId: optionalText(raw.actorId, 120) };
  if (entity === "price-lists") {
    return {
      ...common,
      name: text(raw.name, 140, true),
      currency: text(raw.currency, 3) || "MXN",
      isDefault: bool(raw.isDefault),
      isActive: raw.isActive === undefined ? true : bool(raw.isActive),
      startsAt: date(raw.startsAt, true),
      endsAt: date(raw.endsAt)
    };
  }
  if (entity === "price-list-items") {
    return {
      ...common,
      priceListId: text(raw.priceListId, 120, true),
      productId: text(raw.productId, 120, true),
      priceCents: integer(raw.priceCents, { min: 0, max: 2_000_000_000 }),
      startsAt: date(raw.startsAt, true),
      endsAt: date(raw.endsAt)
    };
  }
  if (entity === "tax-rates") {
    return {
      ...common,
      name: text(raw.name, 140, true),
      rateBps: integer(raw.rateBps, { min: 0, max: 10000 }),
      isDefault: bool(raw.isDefault),
      isActive: raw.isActive === undefined ? true : bool(raw.isActive)
    };
  }
  if (entity === "promotions") {
    return {
      ...common,
      name: text(raw.name, 160, true),
      description: optionalText(raw.description, 800),
      ruleType: text(raw.ruleType, 80, true),
      priority: integer(raw.priority ?? 100, { min: 0, max: 100000 }),
      stackingPolicy: text(raw.stackingPolicy, 40) || "EXCLUSIVE",
      eligibilityJson: json(raw.eligibilityJson),
      benefitJson: json(raw.benefitJson),
      startsAt: date(raw.startsAt, true),
      endsAt: date(raw.endsAt),
      status: text(raw.status, 24) || "ACTIVE"
    };
  }
  if (entity === "discounts") {
    const discountType = text(raw.discountType, 40, true).toUpperCase();
    const valueBps = integer(raw.valueBps, { min: 0, max: 10000, nullable: true });
    const valueCents = integer(raw.valueCents, { min: 0, max: 2_000_000_000, nullable: true });
    if ((discountType === "PERCENT" && valueBps === null) || (discountType === "FIXED" && valueCents === null)) {
      throw new Error("PRICING_DISCOUNT_VALUE_REQUIRED");
    }
    return {
      ...common,
      name: text(raw.name, 160, true),
      discountType,
      valueBps,
      valueCents,
      minimumSubtotalCents: integer(raw.minimumSubtotalCents ?? 0, { min: 0 }),
      maximumDiscountCents: integer(raw.maximumDiscountCents, { min: 0, nullable: true }),
      scopeJson: json(raw.scopeJson),
      authorizationRuleId: optionalText(raw.authorizationRuleId, 120),
      startsAt: date(raw.startsAt, true),
      endsAt: date(raw.endsAt),
      status: text(raw.status, 24) || "ACTIVE"
    };
  }
  if (entity === "authorization-rules") {
    return {
      ...common,
      name: text(raw.name, 160, true),
      actionType: text(raw.actionType, 80, true),
      thresholdType: text(raw.thresholdType, 80, true),
      thresholdValue: integer(raw.thresholdValue, { min: 0 }),
      requiredPermission: text(raw.requiredPermission, 160, true),
      status: text(raw.status, 24) || "ACTIVE"
    };
  }
  return {
    ...common,
    ruleId: text(raw.ruleId, 120, true),
    requestedById: optionalText(raw.requestedById, 120),
    requestedActionJson: json(raw.requestedActionJson),
    reason: text(raw.reason, 800, true)
  };
}

export function readPricingUpdate(entity: PricingEntity, body: unknown) {
  const raw = record(body);
  const output: Record<string, unknown> = {
    expectedVersion: integer(raw.expectedVersion, { min: 1 }),
    actorId: optionalText(raw.actorId, 120)
  };
  const copyText = (key: string, max: number) => {
    if (raw[key] !== undefined) output[key] = optionalText(raw[key], max);
  };
  const copyBool = (key: string) => {
    if (raw[key] !== undefined) output[key] = bool(raw[key]);
  };
  const copyDate = (key: string) => {
    if (raw[key] !== undefined) output[key] = date(raw[key]);
  };
  const copyInt = (key: string, options: { min?: number; max?: number; nullable?: boolean } = {}) => {
    if (raw[key] !== undefined) output[key] = integer(raw[key], options);
  };

  if (entity === "price-lists") {
    copyText("name", 140); copyText("currency", 3); copyBool("isDefault"); copyBool("isActive"); copyDate("startsAt"); copyDate("endsAt");
  } else if (entity === "price-list-items") {
    copyText("priceListId", 120); copyText("productId", 120); copyInt("priceCents", { min: 0 }); copyDate("startsAt"); copyDate("endsAt");
  } else if (entity === "tax-rates") {
    copyText("name", 140); copyInt("rateBps", { min: 0, max: 10000 }); copyBool("isDefault"); copyBool("isActive");
  } else if (entity === "promotions") {
    copyText("name", 160); copyText("description", 800); copyText("ruleType", 80); copyInt("priority", { min: 0 }); copyText("stackingPolicy", 40);
    if (raw.eligibilityJson !== undefined) output.eligibilityJson = json(raw.eligibilityJson);
    if (raw.benefitJson !== undefined) output.benefitJson = json(raw.benefitJson);
    copyDate("startsAt"); copyDate("endsAt"); copyText("status", 24);
  } else if (entity === "discounts") {
    copyText("name", 160); copyText("discountType", 40); copyInt("valueBps", { min: 0, max: 10000, nullable: true }); copyInt("valueCents", { min: 0, nullable: true });
    copyInt("minimumSubtotalCents", { min: 0 }); copyInt("maximumDiscountCents", { min: 0, nullable: true });
    if (raw.scopeJson !== undefined) output.scopeJson = json(raw.scopeJson);
    copyText("authorizationRuleId", 120); copyDate("startsAt"); copyDate("endsAt"); copyText("status", 24);
  } else if (entity === "authorization-rules") {
    copyText("name", 160); copyText("actionType", 80); copyText("thresholdType", 80); copyInt("thresholdValue", { min: 0 }); copyText("requiredPermission", 160); copyText("status", 24);
  } else {
    copyText("status", 24); copyText("decidedById", 120); copyText("decisionReason", 800);
  }
  return output;
}

export async function createPricingEntity(entity: PricingEntity, body: unknown) {
  const businessId = await resolvePcBusinessScope();
  return pricingPolicyRepository.create(businessId, entity, readPricingCreate(entity, body));
}

export async function updatePricingEntity(entity: PricingEntity, id: string, body: unknown) {
  const businessId = await resolvePcBusinessScope();
  return pricingPolicyRepository.update(businessId, entity, id, readPricingUpdate(entity, body));
}

import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import {
  ProductVariantRepository,
  type CreateProductVariantInput,
  type ProductVariantStatus,
  type UpdateProductVariantInput
} from "@/server/repositories/product-variant.repository";

const repository = new ProductVariantRepository();

function text(value: unknown, max: number) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function attributes(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return Object.fromEntries(Object.entries(value as Record<string, unknown>).flatMap(([key, raw]) => {
    const normalizedKey = key.trim().toLocaleLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 32);
    const normalizedValue = text(raw, 80);
    return normalizedKey && normalizedValue ? [[normalizedKey, normalizedValue]] : [];
  }).slice(0, 8));
}

function sortOrder(value: unknown) {
  const parsed = Number(value);
  return Number.isInteger(parsed) ? Math.max(0, Math.min(parsed, 9_999)) : 0;
}

export function readProductVariantCreate(body: unknown): CreateProductVariantInput {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const productId = text(raw.productId, 120);
  const variantProductId = text(raw.variantProductId, 120);
  const label = text(raw.label, 140);
  const idempotencyKey = text(raw.idempotencyKey, 120);
  if (!productId || !variantProductId) throw new Error("PRODUCT_VARIANT_PRODUCTS_REQUIRED");
  if (label.length < 2) throw new Error("PRODUCT_VARIANT_LABEL_REQUIRED");
  if (idempotencyKey.length < 12) throw new Error("PRODUCT_VARIANT_IDEMPOTENCY_REQUIRED");
  return { productId, variantProductId, label, attributes: attributes(raw.attributes), sortOrder: sortOrder(raw.sortOrder), idempotencyKey };
}

export function readProductVariantUpdate(body: unknown): UpdateProductVariantInput {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const expectedVersion = Number(raw.expectedVersion);
  if (!Number.isInteger(expectedVersion) || expectedVersion < 1) throw new Error("PRODUCT_VARIANT_VERSION_REQUIRED");
  const status = raw.status === undefined ? undefined : raw.status === "ACTIVE" || raw.status === "INACTIVE" ? raw.status as ProductVariantStatus : null;
  if (status === null) throw new Error("PRODUCT_VARIANT_STATUS_INVALID");
  const label = raw.label === undefined ? undefined : text(raw.label, 140);
  if (label !== undefined && label.length < 2) throw new Error("PRODUCT_VARIANT_LABEL_REQUIRED");
  return { expectedVersion, status, label, attributes: raw.attributes === undefined ? undefined : attributes(raw.attributes), sortOrder: raw.sortOrder === undefined ? undefined : sortOrder(raw.sortOrder) };
}

export async function getProductVariantWorkspace() {
  try {
    const businessId = await resolvePcBusinessScope();
    const [variants, products] = await Promise.all([repository.list(businessId), repository.listProducts(businessId)]);
    return { variants, products, meta: { source: "canonical_prisma" as const, warning: null as string | null, generatedAt: new Date().toISOString() } };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "lectura no disponible";
    return { variants: [], products: [], meta: { source: "unavailable" as const, warning: `No fue posible leer variantes: ${reason}. Verifica la migración canónica.`, generatedAt: new Date().toISOString() } };
  }
}

export async function createProductVariant(input: CreateProductVariantInput) {
  return repository.create(await resolvePcBusinessScope(), input);
}

export async function updateProductVariant(variantId: string, input: UpdateProductVariantInput) {
  return repository.update(await resolvePcBusinessScope(), variantId, input);
}

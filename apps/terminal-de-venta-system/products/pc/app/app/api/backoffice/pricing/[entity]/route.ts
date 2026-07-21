// PRISMA_PRICING_OWNER_V1
import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import {
  createPricingEntity,
  isPricingEntity,
  listPricingEntity,
  pricingFeatureKey
} from "@/server/services/pricing-policy.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function pricingFailure(error: unknown) {
  const code = error instanceof Error ? error.message : "";
  const map: Record<string, [string, number]> = {
    INVALID_JSON_BODY: ["El cuerpo JSON no es válido.", 400],
    PRICING_REQUIRED_FIELD: ["Falta un campo obligatorio.", 400],
    PRICING_INTEGER_REQUIRED: ["Se esperaba un número entero.", 400],
    PRICING_VALUE_OUT_OF_RANGE: ["Un valor está fuera del rango permitido.", 400],
    PRICING_DATE_REQUIRED: ["Falta una fecha obligatoria.", 400],
    PRICING_DATE_INVALID: ["La fecha no es válida.", 400],
    PRICING_JSON_INVALID: ["La configuración JSON no es válida.", 400],
    PRICING_IDEMPOTENCY_REQUIRED: ["La solicitud no incluye una llave de idempotencia válida.", 400],
    PRICING_DISCOUNT_VALUE_REQUIRED: ["El descuento requiere porcentaje o importe fijo.", 400],
    PRICING_MIGRATION_REQUIRED: ["La migración canónica de Pricing todavía no está aplicada.", 503],
    PRICING_PRICE_LIST_NOT_FOUND: ["La lista de precios no existe.", 404],
    PRICING_PRODUCT_NOT_FOUND: ["El producto no existe.", 404],
    PRICING_AUTH_RULE_NOT_FOUND: ["La regla de autorización no existe o está inactiva.", 404],
    PRICING_CREATE_NOT_VISIBLE: ["El registro se escribió, pero no pudo releerse.", 500]
  };
  const match = map[code];
  return match ? fail(code, match[0], match[1]) : null;
}

export async function GET(_request: Request, context: { params: Promise<{ entity: string }> }) {
  try {
    const entity = (await context.params).entity;
    if (!isPricingEntity(entity)) return fail("PRICING_ENTITY_INVALID", "La entidad de Pricing no es válida.", 404);
    const licenseGate = await guardPcFeatureForApi(pricingFeatureKey(entity, "read"));
    if (licenseGate) return licenseGate;
    const records = await listPricingEntity(entity);
    return ok({ records }, { endpoint: `GET /api/backoffice/pricing/${entity}`, bounded: true });
  } catch (error) {
    return pricingFailure(error) ?? toBackofficeError(error);
  }
}

export async function POST(request: Request, context: { params: Promise<{ entity: string }> }) {
  try {
    const entity = (await context.params).entity;
    if (!isPricingEntity(entity)) return fail("PRICING_ENTITY_INVALID", "La entidad de Pricing no es válida.", 404);
    const licenseGate = await guardPcFeatureForApi(pricingFeatureKey(entity, "create"));
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => {
      throw new Error("INVALID_JSON_BODY");
    });
    const result = await createPricingEntity(entity, body);
    return ok(result, { endpoint: `POST /api/backoffice/pricing/${entity}`, idempotent: result.replayed }, { status: result.replayed ? 200 : 201 });
  } catch (error) {
    return pricingFailure(error) ?? toBackofficeError(error);
  }
}

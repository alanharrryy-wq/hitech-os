// PRISMA_PRICING_OWNER_V1
import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import {
  isPricingEntity,
  pricingFeatureKey,
  updatePricingEntity
} from "@/server/services/pricing-policy.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function pricingFailure(error: unknown) {
  const code = error instanceof Error ? error.message : "";
  const map: Record<string, [string, number]> = {
    INVALID_JSON_BODY: ["El cuerpo JSON no es válido.", 400],
    PRICING_VERSION_REQUIRED: ["La actualización requiere la versión leída.", 400],
    PRICING_VERSION_CONFLICT: ["El registro cambió en otra sesión. Vuelve a cargarlo.", 409],
    PRICING_UPDATE_EMPTY: ["No se enviaron cambios válidos.", 400],
    PRICING_AUTH_DECISION_INVALID: ["La decisión debe ser APPROVED o DENIED.", 400],
    PRICING_AUTH_REQUEST_TERMINAL: ["La solicitud ya fue decidida.", 409],
    PRICING_MIGRATION_REQUIRED: ["La migración canónica de Pricing todavía no está aplicada.", 503],
    PRICING_UPDATE_NOT_VISIBLE: ["El registro cambió, pero no pudo releerse.", 500]
  };
  const match = map[code];
  return match ? fail(code, match[0], match[1]) : null;
}

export async function PATCH(request: Request, context: { params: Promise<{ entity: string; entityId: string }> }) {
  try {
    const params = await context.params;
    if (!isPricingEntity(params.entity)) return fail("PRICING_ENTITY_INVALID", "La entidad de Pricing no es válida.", 404);
    const entityId = params.entityId.trim();
    if (!entityId) return fail("PRICING_ID_REQUIRED", "El registro no es válido.", 400);
    const licenseGate = await guardPcFeatureForApi(pricingFeatureKey(params.entity, "update"));
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => {
      throw new Error("INVALID_JSON_BODY");
    });
    const record = await updatePricingEntity(params.entity, entityId, body);
    if (!record) return fail("PRICING_NOT_FOUND", "El registro no existe en este negocio.", 404);
    return ok({ record }, { endpoint: `PATCH /api/backoffice/pricing/${params.entity}/:entityId`, readAfterWrite: true });
  } catch (error) {
    return pricingFailure(error) ?? toBackofficeError(error);
  }
}

import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { getInventoryCount, updateInventoryCount } from "@/server/services/inventory-mutations.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ countId: string }> };
const countIdFrom = (context: RouteContext) => context.params.then(({ countId }) => countId.trim());

export async function GET(_: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const countId = await countIdFrom(context);
    if (!countId) return fail("COUNT_ID_REQUIRED", "Falta el conteo solicitado.", 400);
    const count = await getInventoryCount(countId);
    if (!count) return fail("COUNT_NOT_FOUND", "No existe el conteo solicitado.", 404);
    return ok({ count }, { endpoint: "GET /api/backoffice/counts/records/:countId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) { return toBackofficeError(error); }
}

export async function PATCH(request: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("inventory.counts");
    if (licenseGate) return licenseGate;
    const countId = await countIdFrom(context);
    if (!countId) return fail("COUNT_ID_REQUIRED", "Falta el conteo solicitado.", 400);
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const count = await updateInventoryCount(countId, body);
    if (!count) return fail("COUNT_NOT_FOUND", "No existe el conteo solicitado.", 404);
    return ok({ count }, { endpoint: "PATCH /api/backoffice/counts/records/:countId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "COUNT_ALREADY_CLOSED") return fail("COUNT_ALREADY_CLOSED", "El conteo ya está cerrado y no admite cambios.", 409);
    if (error instanceof Error && error.message === "COUNT_TRANSITION_INVALID") return fail("COUNT_TRANSITION_INVALID", "La transición de estado del conteo no es válida.", 409);
    if (error instanceof Error && error.message.startsWith("COUNT_")) return fail(error.message, "Los datos del conteo no son válidos.", 400);
    return toBackofficeError(error);
  }
}

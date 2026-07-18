import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { executeModifierCatalogCommand, readModifierCatalogCommand } from "@/server/services/modifier-catalog.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const gate = await guardPcFeatureForApi("pc.open");
    if (gate) return gate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    return ok(await executeModifierCatalogCommand(readModifierCatalogCommand(body)), { endpoint: "POST /api/backoffice/product-modifiers", readAfterWrite: true });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "El cuerpo JSON no es válido.", 400);
    if (code === "MODIFIER_IDEMPOTENCY_REQUIRED") return fail(code, "La acción requiere una llave de idempotencia.", 400);
    if (code.endsWith("_INVALID") || code === "MODIFIER_ACTION_INVALID") return fail(code, "Revisa los datos del modificador.", 400);
    if (code.endsWith("_NOT_FOUND")) return fail(code, "El producto o grupo ya no está disponible para esta acción.", 404);
    return toBackofficeError(error);
  }
}

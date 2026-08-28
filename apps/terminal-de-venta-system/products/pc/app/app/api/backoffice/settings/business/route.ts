import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { getBusinessSettings, updateBusinessSettings } from "@/server/services/business-settings.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const settings = await getBusinessSettings();
    return ok({ settings }, { endpoint: "GET /api/backoffice/settings/business", persistence: "Business", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "SETTINGS_BUSINESS_NOT_FOUND") return fail("SETTINGS_BUSINESS_NOT_FOUND", "No existe el negocio configurado.", 404);
    return toBackofficeError(error);
  }
}

export async function PATCH(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const settings = await updateBusinessSettings(body);
    return ok({ settings }, { endpoint: "PATCH /api/backoffice/settings/business", persistence: "Business", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "SETTINGS_BUSINESS_NOT_FOUND") return fail("SETTINGS_BUSINESS_NOT_FOUND", "No existe el negocio configurado.", 404);
    if (error instanceof Error && error.message === "SETTINGS_UPDATE_EMPTY") return fail("SETTINGS_UPDATE_EMPTY", "No hay cambios de configuración para guardar.", 400);
    if (error instanceof Error && error.message === "SETTINGS_NAME_INVALID") return fail("SETTINGS_NAME_INVALID", "El nombre del negocio no es válido.", 400);
    if (error instanceof Error && error.message === "SETTINGS_CURRENCY_INVALID") return fail("SETTINGS_CURRENCY_INVALID", "La moneda debe usar un código de tres letras.", 400);
    return toBackofficeError(error);
  }
}

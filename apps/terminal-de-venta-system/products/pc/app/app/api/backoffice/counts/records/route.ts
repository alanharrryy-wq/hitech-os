import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { createInventoryCount } from "@/server/services/inventory-mutations.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("inventory.counts");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const count = await createInventoryCount(body);
    return ok({ count }, { endpoint: "POST /api/backoffice/counts/records", persistence: "canonical_prisma", wave: 3 }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message.startsWith("COUNT_")) return fail(error.message, "Los datos del conteo no son válidos.", 400);
    return toBackofficeError(error);
  }
}

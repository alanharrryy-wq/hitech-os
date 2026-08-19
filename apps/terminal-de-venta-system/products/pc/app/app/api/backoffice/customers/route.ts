import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { CustomerDuplicateError } from "@/server/repositories/customer.repository";
import { createCustomer, getCustomerWorkspace, readCustomerWriteInput } from "@/server/services/customer.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const params = new URL(request.url).searchParams;
    const limit = Number(params.get("limit"));
    const workspace = await getCustomerWorkspace({
      query: params.get("q") ?? "",
      includeInactive: params.get("includeInactive") === "true",
      limit: Number.isInteger(limit) ? limit : undefined
    });
    return ok(workspace, { endpoint: "GET /api/backoffice/customers", bounded: true });
  } catch (error) {
    return toBackofficeError(error, { customerSafe: true });
  }
}

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => {
      throw new Error("INVALID_JSON_BODY");
    });
    const customer = await createCustomer(readCustomerWriteInput(body));
    return ok({ customer }, { endpoint: "POST /api/backoffice/customers" }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "No pudimos leer la solicitud. Intenta de nuevo.", 400);
    if (error instanceof Error && error.message === "CUSTOMER_NAME_REQUIRED") return fail("CUSTOMER_NAME_REQUIRED", "Captura el nombre del cliente.", 400);
    if (error instanceof Error && error.message === "CUSTOMER_EMAIL_INVALID") return fail("CUSTOMER_EMAIL_INVALID", "El correo del cliente no tiene un formato válido.", 400);
    if (error instanceof CustomerDuplicateError) return fail("CUSTOMER_DUPLICATE", "Ya existe una ficha activa con datos coincidentes.", 409, { duplicates: error.duplicates.map((customer) => ({ id: customer.id, displayName: customer.displayName })) });
    return toBackofficeError(error, { customerSafe: true });
  }
}

import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { CustomerDuplicateError } from "@/server/repositories/customer.repository";
import { getCustomerDetail, readCustomerWriteInput, updateCustomer } from "@/server/services/customer.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ customerId: string }> };

function customerIdFrom(context: RouteContext) {
  return context.params.then(({ customerId }) => customerId.trim());
}

export async function GET(_: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const customerId = await customerIdFrom(context);
    if (!customerId) return fail("CUSTOMER_ID_REQUIRED", "No pudimos identificar el cliente solicitado.", 400);
    const customer = await getCustomerDetail(customerId);
    if (!customer) return fail("CUSTOMER_NOT_FOUND", "No encontramos ese cliente.", 404);
    return ok({ customer }, { endpoint: "GET /api/backoffice/customers/:customerId" });
  } catch (error) {
    return toBackofficeError(error, { customerSafe: true });
  }
}

export async function PATCH(request: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const customerId = await customerIdFrom(context);
    if (!customerId) return fail("CUSTOMER_ID_REQUIRED", "No pudimos identificar el cliente solicitado.", 400);
    const body = await request.json().catch(() => {
      throw new Error("INVALID_JSON_BODY");
    });
    const customer = await updateCustomer(customerId, readCustomerWriteInput(body, { partial: true }));
    if (!customer) return fail("CUSTOMER_NOT_FOUND", "No encontramos ese cliente.", 404);
    return ok({ customer }, { endpoint: "PATCH /api/backoffice/customers/:customerId" });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "No pudimos leer la solicitud. Intenta de nuevo.", 400);
    if (error instanceof Error && error.message === "CUSTOMER_NAME_REQUIRED") return fail("CUSTOMER_NAME_REQUIRED", "El nombre debe tener al menos dos caracteres.", 400);
    if (error instanceof Error && error.message === "CUSTOMER_EMAIL_INVALID") return fail("CUSTOMER_EMAIL_INVALID", "El correo del cliente no tiene un formato válido.", 400);
    if (error instanceof Error && error.message === "CUSTOMER_VERSION_CONFLICT") return fail("CUSTOMER_VERSION_CONFLICT", "El cliente cambió en otra sesión. Vuelve a cargarlo antes de guardar.", 409);
    if (error instanceof CustomerDuplicateError) return fail("CUSTOMER_DUPLICATE", "Ya existe una ficha activa con datos coincidentes.", 409, { duplicates: error.duplicates.map((customer) => ({ id: customer.id, displayName: customer.displayName })) });
    return toBackofficeError(error, { customerSafe: true });
  }
}

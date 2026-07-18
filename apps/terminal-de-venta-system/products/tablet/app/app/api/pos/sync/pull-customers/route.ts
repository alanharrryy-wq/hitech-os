import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { pullCustomerProjectionFromPc } from "@/server/sync/customer-projection-pull";
import { DEFAULT_POS_API_BUSINESS_ID, DEFAULT_POS_API_TERMINAL_ID } from "@/server/pos-api/validators";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const requestedBusinessId = typeof body?.businessId === "string" ? body.businessId.trim() : "";
    const requestedTerminalId = typeof body?.terminalId === "string" ? body.terminalId.trim() : "";
    if ((requestedBusinessId && requestedBusinessId !== DEFAULT_POS_API_BUSINESS_ID) || (requestedTerminalId && requestedTerminalId !== DEFAULT_POS_API_TERMINAL_ID)) {
      return fail("CUSTOMER_PROJECTION_SCOPE_DENIED", "La proyección solicitada no pertenece al negocio o terminal configurados en esta Tablet.", 403);
    }
    const result = await pullCustomerProjectionFromPc({ businessId: DEFAULT_POS_API_BUSINESS_ID, terminalId: DEFAULT_POS_API_TERMINAL_ID, cursor: typeof body?.cursor === "string" ? body.cursor : null });
    if (!result.ok) return fail(result.reason, result.errors.join(" "), 503, { cursor: result.cursor });
    return ok(result, undefined, { endpoint: "POST /api/pos/sync/pull-customers" });
  } catch (error) {
    return toPosApiError(error);
  }
}

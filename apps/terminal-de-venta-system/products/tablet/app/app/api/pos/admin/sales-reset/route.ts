import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { DEFAULT_POS_API_BUSINESS_ID } from "@/server/pos-api/validators";
import { performSalesReset, previewSalesReset, SALES_RESET_CONFIRMATION } from "@/server/pos-api/sales-reset.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function businessIdFromUrl(request: Request) {
  const value = new URL(request.url).searchParams.get("businessId")?.trim();
  return value || DEFAULT_POS_API_BUSINESS_ID;
}

export async function GET(request: Request) {
  try {
    const businessId = businessIdFromUrl(request);
    const preview = await previewSalesReset(businessId);
    return ok({ preview }, undefined, {
      endpoint: "GET /api/pos/admin/sales-reset",
      businessId,
      locked: true,
      destructiveAction: true
    });
  } catch (error) {
    return toPosApiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const confirmation = typeof body?.confirmation === "string" ? body.confirmation : "";
    if (confirmation !== SALES_RESET_CONFIRMATION) {
      return fail(
        "SALES_RESET_CONFIRMATION_REQUIRED",
        "Escribe la frase exacta para ejecutar el reset seguro de ventas.",
        423,
        { requiredPhrase: SALES_RESET_CONFIRMATION }
      );
    }

    const businessId = typeof body?.businessId === "string" && body.businessId.trim()
      ? body.businessId.trim()
      : DEFAULT_POS_API_BUSINESS_ID;
    const operatorNote = typeof body?.operatorNote === "string" ? body.operatorNote.slice(0, 600) : null;
    const result = await performSalesReset({ businessId, confirmation, operatorNote });
    return ok({ result }, { status: 200 }, {
      endpoint: "POST /api/pos/admin/sales-reset",
      businessId,
      destructiveAction: true,
      preservesLicenseConfig: true
    });
  } catch (error) {
    if (error instanceof Error && error.message === "SALES_RESET_CONFIRMATION_REQUIRED") {
      return fail("SALES_RESET_CONFIRMATION_REQUIRED", "Confirmación inválida para reset de ventas.", 423);
    }
    return toPosApiError(error);
  }
}

import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { getSaleDetail } from "@/server/pos-api/sales-detail.prisma";
import { DEFAULT_POS_API_BUSINESS_ID } from "@/server/pos-api/validators";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function readSaleIdOrFolio(searchParams: URLSearchParams) {
  return (
    searchParams.get("saleId") ||
    searchParams.get("folio") ||
    searchParams.get("code") ||
    searchParams.get("ticket") ||
    ""
  ).trim();
}

export async function GET(request: Request) {
  try {
    const searchParams = new URL(request.url).searchParams;
    const businessId = (searchParams.get("businessId") || DEFAULT_POS_API_BUSINESS_ID).trim();
    const saleIdOrFolio = readSaleIdOrFolio(searchParams);

    if (!saleIdOrFolio) {
      return fail(
        "SALE_DETAIL_ID_REQUIRED",
        "Falta saleId, folio, code o ticket para consultar el detalle.",
        400,
      );
    }

    const ticket = await getSaleDetail({ businessId, saleIdOrFolio });

    if (!ticket) {
      return fail(
        "SALE_NOT_FOUND",
        "No encontré ese ticket cerrado en la base local de Tablet.",
        404,
        { saleIdOrFolio, businessId },
      );
    }

    return ok({ ticket }, undefined, {
      endpoint: "GET /api/pos/sales/detail",
      businessId,
      saleIdOrFolio,
    });
  } catch (error) {
    return toPosApiError(error);
  }
}

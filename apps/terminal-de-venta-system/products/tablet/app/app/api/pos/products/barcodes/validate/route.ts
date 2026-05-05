import { barcodeAvailability, productMutationErrorToResponse } from "@/server/pos-api/product-mutations.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const params = new URL(request.url).searchParams;
    const result = await barcodeAvailability({
      code: params.get("code") ?? "",
      businessId: params.get("businessId") ?? undefined,
      productId: params.get("productId") ?? undefined
    });
    return Response.json({ ok: true, data: result, meta: { endpoint: "GET /api/pos/products/barcodes/validate" } }, { status: 200 });
  } catch (error) {
    const response = productMutationErrorToResponse(error);
    return Response.json({ ok: false, code: response.code, message: response.message, details: response.details }, { status: response.status });
  }
}

import { productMutationErrorToResponse, updateTabletProduct } from "@/server/pos-api/product-mutations.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const product = await updateTabletProduct(body);
    return Response.json({ ok: true, data: { product }, meta: { endpoint: "POST /api/pos/products/update" } }, { status: 200 });
  } catch (error) {
    const response = productMutationErrorToResponse(error);
    return Response.json({ ok: false, code: response.code, message: response.message, details: response.details }, { status: response.status });
  }
}

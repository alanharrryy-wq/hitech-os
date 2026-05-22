import { disableTabletSupplier, supplierMutationErrorToResponse } from "@/server/pos-api/supplier-mutations.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const value = await disableTabletSupplier(body);
    return Response.json({ ok: true, data: { supplier: value }, meta: { endpoint: "POST /api/pos/suppliers/disable" } }, { status: 200 });
  } catch (error) {
    const response = supplierMutationErrorToResponse(error);
    return Response.json({ ok: false, code: response.code, message: response.message, details: response.details }, { status: response.status });
  }
}

import { NextResponse } from "next/server";
import { resolveLocalCatalogProduct } from "../../../../../src/server/local-catalog";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code") || url.searchParams.get("sku") || url.searchParams.get("barcode") || "";
  const includeInactive = url.searchParams.get("includeInactive") === "1";
  const product = await resolveLocalCatalogProduct(code, { includeInactive });

  if (!product) {
    return NextResponse.json(
      {
        ok: false,
        code: "LOCAL_PRODUCT_NOT_FOUND",
        message: "No encontré ese producto en el catálogo local de Tablet.",
        details: { code },
      },
      { status: 404 },
    );
  }

  return NextResponse.json({
    ok: true,
    data: { product },
    meta: { source: "tablet-local-catalog", code, includeInactive },
  });
}

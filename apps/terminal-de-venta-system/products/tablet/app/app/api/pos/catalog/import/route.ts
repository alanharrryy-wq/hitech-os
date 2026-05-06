import { NextResponse } from "next/server";
import { importLocalCatalogProducts } from "../../../../../src/server/local-catalog";

export const runtime = "nodejs";

type ImportBody = {
  source?: string;
  products?: unknown[];
};

export async function POST(request: Request) {
  let body: ImportBody;
  try {
    body = (await request.json()) as ImportBody;
  } catch {
    return NextResponse.json(
      {
        ok: false,
        code: "LOCAL_CATALOG_INVALID_JSON",
        message: "El JSON de importación no es válido.",
      },
      { status: 400 },
    );
  }

  if (!Array.isArray(body.products)) {
    return NextResponse.json(
      {
        ok: false,
        code: "LOCAL_CATALOG_PRODUCTS_REQUIRED",
        message: "La importación necesita un arreglo products.",
      },
      { status: 400 },
    );
  }

  const result = await importLocalCatalogProducts({
    source: body.source || "tablet-local-catalog-api-import",
    products: body.products as any,
  });

  return NextResponse.json({
    ok: true,
    data: result,
    meta: { source: "tablet-local-catalog" },
  });
}

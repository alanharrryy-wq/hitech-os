import { NextResponse } from "next/server";
import { listLocalCatalogProducts } from "../../../../../src/server/local-catalog";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const q = url.searchParams.get("q") || "";
  const includeInactive = url.searchParams.get("includeInactive") === "1";
  const products = await listLocalCatalogProducts({ q, includeInactive });

  return NextResponse.json({
    ok: true,
    data: { products },
    meta: {
      source: "tablet-local-catalog",
      count: products.length,
      q,
      includeInactive,
    },
  });
}

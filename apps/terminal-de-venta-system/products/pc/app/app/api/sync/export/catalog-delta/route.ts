import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { buildPcCatalogDelta, exportPcCatalogDelta } from "@/server/services/catalog-delta-export.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function inputFromUrl(request: Request) {
  const url = new URL(request.url);
  return {
    businessId: url.searchParams.get("businessId"),
    terminalId: url.searchParams.get("terminalId"),
    storeId: url.searchParams.get("storeId"),
    target: url.searchParams.get("target"),
    cursor: url.searchParams.get("cursor"),
    mode: url.searchParams.get("mode"),
    limit: url.searchParams.get("limit")
  };
}

export async function GET(request: Request) {
  try {
    const envelope = await buildPcCatalogDelta(inputFromUrl(request));
    return ok(envelope, { endpoint: "GET /api/sync/export/catalog-delta" });
  } catch (error) {
    if (error instanceof Error && error.message === "CATALOG_DELTA_INVALID_CURSOR") {
      return fail("CATALOG_DELTA_INVALID_CURSOR", "Cursor de catalogo invalido.", 400);
    }
    return toBackofficeError(error);
  }
}

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("export.advanced");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => ({}));
    const result = await exportPcCatalogDelta({
      businessId: typeof body?.businessId === "string" ? body.businessId : null,
      terminalId: typeof body?.terminalId === "string" ? body.terminalId : null,
      storeId: typeof body?.storeId === "string" ? body.storeId : null,
      target: typeof body?.target === "string" ? body.target : "tablet",
      cursor: typeof body?.cursor === "string" ? body.cursor : null,
      mode: typeof body?.mode === "string" ? body.mode : "delta",
      limit: body?.limit,
      requestedBy: typeof body?.requestedBy === "string" ? body.requestedBy : "pc-operator"
    }, { recordAudit: true });
    return ok({ ...result.envelope, auditEventId: result.auditEventId }, { endpoint: "POST /api/sync/export/catalog-delta" });
  } catch (error) {
    if (error instanceof Error && error.message === "CATALOG_DELTA_INVALID_CURSOR") {
      return fail("CATALOG_DELTA_INVALID_CURSOR", "Cursor de catalogo invalido.", 400);
    }
    return toBackofficeError(error);
  }
}

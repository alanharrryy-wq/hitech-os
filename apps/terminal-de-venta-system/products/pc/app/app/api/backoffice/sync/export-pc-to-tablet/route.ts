import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { getSyncContract } from "@/server/services/pc-data-mode-contract.service";
import { exportPcCatalogDelta } from "@/server/services/catalog-delta-export.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return ok(getSyncContract("export-pc-to-tablet"), { endpoint: "GET /api/backoffice/sync/export-pc-to-tablet", mutation: false });
}

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("sync.managed");
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

    return ok(
      { ...result.envelope, auditEventId: result.auditEventId },
      {
        endpoint: "POST /api/backoffice/sync/export-pc-to-tablet",
        mutation: true,
        owner: "catalog-delta-export.service",
        delivery: "prepared_for_tablet",
        fakeAck: false,
        wave: 3
      }
    );
  } catch (error) {
    if (error instanceof Error && error.message === "CATALOG_DELTA_INVALID_CURSOR") {
      return fail("CATALOG_DELTA_INVALID_CURSOR", "Cursor de catálogo inválido.", 400);
    }
    return toBackofficeError(error);
  }
}

import { ok, fail } from "@/server/pos-api/responses";
import { getTabletRuntimeSnapshotFromRequest } from "@/server/tablet-runtime-snapshot";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const snapshot = await getTabletRuntimeSnapshotFromRequest(request);
    return ok({ snapshot }, undefined, {
      endpoint: "GET /api/tablet/runtime/snapshot",
      schemaVersion: snapshot.schemaVersion,
      localSalesAllowed: snapshot.localSalesAllowed,
      pcRequiredForBasicSale: snapshot.pcRequiredForBasicSale
    });
  } catch (error) {
    return fail(
      "TABLET_RUNTIME_SNAPSHOT_ERROR",
      "No se pudo leer el estado operativo de la Tablet.",
      500,
      { cause: error instanceof Error ? error.message : String(error) }
    );
  }
}

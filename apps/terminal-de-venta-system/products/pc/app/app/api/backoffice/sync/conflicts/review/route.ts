import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { markSyncConflictReviewed } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const conflictId = typeof body?.conflictId === "string" ? body.conflictId.trim() : "";
    if (!conflictId) return fail("SYNC_CONFLICT_ID_REQUIRED", "Falta conflictId para marcar revision.", 400);
    const resolutionNote = typeof body?.resolutionNote === "string" ? body.resolutionNote.slice(0, 600) : null;
    const result = await markSyncConflictReviewed({ conflictId, resolutionNote });
    return ok(result, { endpoint: "POST /api/backoffice/sync/conflicts/review" });
  } catch (error) {
    if (error instanceof Error && error.message === "SYNC_CONFLICT_NOT_FOUND") {
      return fail("SYNC_CONFLICT_NOT_FOUND", "No existe el conflicto solicitado.", 404);
    }
    return toBackofficeError(error);
  }
}

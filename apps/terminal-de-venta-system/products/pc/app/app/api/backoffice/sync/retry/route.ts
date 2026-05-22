import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { retryFailedSyncEvent } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const eventId = typeof body?.eventId === "string" ? body.eventId.trim() : "";
    if (!eventId) return fail("SYNC_EVENT_ID_REQUIRED", "Falta eventId para reintentar.", 400);
    const operatorNote = typeof body?.operatorNote === "string" ? body.operatorNote.slice(0, 600) : null;
    const result = await retryFailedSyncEvent({ eventId, operatorNote });
    return ok(result, { endpoint: "POST /api/backoffice/sync/retry" });
  } catch (error) {
    if (error instanceof Error && error.message === "SYNC_EVENT_NOT_FOUND") {
      return fail("SYNC_EVENT_NOT_FOUND", "No existe el evento solicitado.", 404);
    }
    if (error instanceof Error && error.message === "SYNC_EVENT_NOT_RETRYABLE") {
      return fail("SYNC_EVENT_NOT_RETRYABLE", "Solo se reintentan eventos fallidos o dead_letter.", 409);
    }
    return toBackofficeError(error);
  }
}

import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { recordTabletGovernanceCommand } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const ALLOWED_COMMANDS = new Set(["catalog.release", "price-policy.release", "license.refresh", "runtime.refresh"]);

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const commandType = typeof body?.commandType === "string" ? body.commandType.trim() : "";
    if (!ALLOWED_COMMANDS.has(commandType)) {
      return fail("INVALID_GOVERNANCE_COMMAND", "Comando de gobierno no permitido.", 400, {
        allowed: Array.from(ALLOWED_COMMANDS)
      });
    }
    const target = typeof body?.target === "string" && body.target.trim() ? body.target.trim() : "all";
    const operatorNote = typeof body?.operatorNote === "string" ? body.operatorNote.slice(0, 600) : null;
    const requestedBy = typeof body?.requestedBy === "string" ? body.requestedBy.slice(0, 120) : null;
    const result = await recordTabletGovernanceCommand({ commandType, target, operatorNote, requestedBy });
    return ok(result, { endpoint: "POST /api/backoffice/tablet-communication/governance-command" });
  } catch (error) {
    return toBackofficeError(error);
  }
}

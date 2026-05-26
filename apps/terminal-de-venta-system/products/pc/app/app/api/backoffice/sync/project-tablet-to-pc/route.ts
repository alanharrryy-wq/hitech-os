import { fail, ok } from "@/lib/backoffice/api-response";
import { getSyncContract } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return ok(getSyncContract("project-tablet-to-pc"), { endpoint: "GET /api/backoffice/sync/project-tablet-to-pc", mutation: false });
}

export async function POST() {
  const detail = getSyncContract("project-tablet-to-pc");
  return fail("PC_SYNC_PROJECTOR_NOT_WIRED", detail.message, 501, detail);
}

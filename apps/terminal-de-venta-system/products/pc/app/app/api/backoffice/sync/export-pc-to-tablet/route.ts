import { fail, ok } from "@/lib/backoffice/api-response";
import { getSyncContract } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return ok(getSyncContract("export-pc-to-tablet"), { endpoint: "GET /api/backoffice/sync/export-pc-to-tablet", mutation: false });
}

export async function POST() {
  const detail = getSyncContract("export-pc-to-tablet");
  return fail("PC_SYNC_EXPORT_NOT_WIRED", detail.message, 501, detail);
}

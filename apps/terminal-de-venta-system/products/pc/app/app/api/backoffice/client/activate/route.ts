import { fail } from "@/lib/backoffice/api-response";
import { guardedMutationResponse } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST() {
  const detail = guardedMutationResponse("client.activate");
  return fail(detail.code, detail.message, 501, detail);
}

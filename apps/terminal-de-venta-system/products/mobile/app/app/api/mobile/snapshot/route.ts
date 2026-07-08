import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane/state-loader";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { sourceFromRuntimeMode } from "@/lib/prisma-app/mobile-data-plane/runtime-mode";
import { okMobileSnapshotResponse } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

function readScopedOverrides(request: Request) {
  const params = new URL(request.url).searchParams;
  const overrides: { businessId?: string; terminalId?: string; salesDate?: string } = {};
  const businessId = params.get("businessId")?.trim();
  const terminalId = params.get("terminalId")?.trim();
  const salesDate = params.get("date")?.trim();
  if (businessId) overrides.businessId = businessId;
  if (terminalId) overrides.terminalId = terminalId;
  if (salesDate) overrides.salesDate = salesDate;
  return overrides;
}

export async function GET(request: Request) {
  const state = await loadMobileDataPlaneState(readScopedOverrides(request));
  const source = sourceFromRuntimeMode(state.runtimeMode);
  const snapshot = buildSnapshotPayload(state);

  return Response.json(
    okMobileSnapshotResponse(snapshot, source, state.runtimeMode, state.probes),
    noStoreJsonInit()
  );
}

import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { sourceFromRuntimeMode } from "@/lib/prisma-app/mobile-data-plane/runtime-mode";
import { buildPrismaMobilePulseTimeline, PRISMA_MOBILE_PULSE_TIMELINE_CONTRACT_ID } from "@/lib/prisma-app/prisma-mobile-pulse-timeline";
import { createClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { loadAuthorizedMobileState } from "@/lib/prisma-app/mobile-security";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(request: Request) {
  const guarded = await loadAuthorizedMobileState(request, "RM.ACTIVITY.TIMELINE");
  if (!guarded.ok) return guarded.response;
  const state = guarded.state;
  const source = sourceFromRuntimeMode(state.runtimeMode);
  const snapshot = buildSnapshotPayload(state);
  const clientSnapshot = createClientSnapshot(snapshot, source, guarded.safeWarnings);
  return Response.json({
    ok: true,
    data: buildPrismaMobilePulseTimeline(clientSnapshot),
    meta: {
      apiVersion: "2026-05-02.mobile.24",
      endpoint: "pulse_timeline",
      generatedAt: new Date().toISOString(),
      source,
      runtimeMode: state.runtimeMode,
      contractId: PRISMA_MOBILE_PULSE_TIMELINE_CONTRACT_ID,
      upstreams: state.probes
    }
  }, noStoreJsonInit());
}

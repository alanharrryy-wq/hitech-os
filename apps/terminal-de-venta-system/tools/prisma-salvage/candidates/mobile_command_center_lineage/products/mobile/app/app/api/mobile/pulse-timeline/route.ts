import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane/state-loader";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { buildPrismaMobilePulseTimeline, PRISMA_MOBILE_PULSE_TIMELINE_CONTRACT_ID } from "@/lib/prisma-app/prisma-mobile-pulse-timeline";
import { createClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";

export const dynamic = "force-dynamic";
export const revalidate = 0;

function sourceFromMode(mode: "connected" | "partial" | "offline") {
  return mode === "offline" ? "unavailable" : "connected-data-plane";
}

export async function GET() {
  const state = await loadMobileDataPlaneState();
  const source = sourceFromMode(state.runtimeMode);
  const snapshot = buildSnapshotPayload(state);
  const clientSnapshot = createClientSnapshot(snapshot, source, state.warnings);
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

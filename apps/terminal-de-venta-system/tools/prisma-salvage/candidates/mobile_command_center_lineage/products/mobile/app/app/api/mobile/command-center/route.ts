import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane/state-loader";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { buildPrismaMobileCommandCenter, PRISMA_MOBILE_COMMAND_CENTER_CONTRACT_ID } from "@/lib/prisma-app/prisma-mobile-command-center";
import { createClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";

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
    data: buildPrismaMobileCommandCenter(clientSnapshot),
    meta: {
      apiVersion: "2026-05-02.mobile.20",
      endpoint: "command_center",
      generatedAt: new Date().toISOString(),
      source,
      runtimeMode: state.runtimeMode,
      contractId: PRISMA_MOBILE_COMMAND_CENTER_CONTRACT_ID,
      upstreams: state.probes
    }
  }, noStoreJsonInit());
}

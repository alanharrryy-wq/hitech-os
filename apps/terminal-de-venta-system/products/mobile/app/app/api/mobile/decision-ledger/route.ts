import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane/state-loader";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { buildPrismaMobileDecisionLedger, PRISMA_MOBILE_DECISION_LEDGER_CONTRACT_ID } from "@/lib/prisma-app/prisma-mobile-decision-ledger";
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
    data: buildPrismaMobileDecisionLedger(clientSnapshot),
    meta: {
      apiVersion: "2026-05-02.mobile.23",
      endpoint: "decision_ledger",
      generatedAt: new Date().toISOString(),
      source,
      runtimeMode: state.runtimeMode,
      contractId: PRISMA_MOBILE_DECISION_LEDGER_CONTRACT_ID,
      upstreams: state.probes
    }
  }, noStoreJsonInit());
}

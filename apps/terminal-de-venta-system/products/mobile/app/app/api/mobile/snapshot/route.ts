import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane/state-loader";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { sourceFromRuntimeMode } from "@/lib/prisma-app/mobile-data-plane/runtime-mode";
import { okMobileSnapshotResponse } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  const state = await loadMobileDataPlaneState();
  const source = sourceFromRuntimeMode(state.runtimeMode);
  const snapshot = buildSnapshotPayload(state);

  return Response.json(
    okMobileSnapshotResponse(snapshot, source, state.runtimeMode, state.probes),
    noStoreJsonInit()
  );
}

import { buildSnapshotPayload } from "./mobile-data-plane/payload-builders";
import type { MobileDataPlaneState } from "./mobile-data-plane/types";

export function getPrismaMobileSnapshotPayloadFromState(state: MobileDataPlaneState) {
  return buildSnapshotPayload(state);
}

export function getPrismaMobileSnapshotPayload(): never {
  throw new Error("PRISMA App Mobile 18 no expone snapshot síncrono heredado. Usa /api/mobile/snapshot o loadMobileDataPlaneState().");
}

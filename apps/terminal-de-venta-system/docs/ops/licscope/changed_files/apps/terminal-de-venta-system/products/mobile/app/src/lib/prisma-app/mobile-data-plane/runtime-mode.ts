import type { PrismaMobileApiMeta } from "../prisma-app-api-contracts";
import type { DataPlaneRuntimeMode } from "./types";

export function sourceFromRuntimeMode(mode: DataPlaneRuntimeMode): PrismaMobileApiMeta["source"] {
  if (mode === "offline" || mode === "unknown" || mode === "reference-disabled") return "unavailable";
  if (mode === "stale") return "local-cache";
  return "connected-data-plane";
}

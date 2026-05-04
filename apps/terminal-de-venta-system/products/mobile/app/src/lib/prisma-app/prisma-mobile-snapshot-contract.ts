import { z } from "zod";
import {
  PrismaMobileAlertsPayloadSchema,
  PrismaMobileApiMetaSchema,
  PrismaMobileBranchesPayloadSchema,
  PrismaMobileCashCurrentPayloadSchema,
  PrismaMobileHealthPayloadSchema,
  PrismaMobileInventoryWatchlistPayloadSchema,
  PrismaMobileReportsDailyPayloadSchema,
  PrismaMobileSalesTodayPayloadSchema,
  PrismaMobileSummaryPayloadSchema,
  type PrismaMobileAlertsPayload,
  type PrismaMobileBranchesPayload,
  type PrismaMobileCashCurrentPayload,
  type PrismaMobileHealthPayload,
  type PrismaMobileInventoryWatchlistPayload,
  type PrismaMobileReportsDailyPayload,
  type PrismaMobileSalesTodayPayload,
  type PrismaMobileSummaryPayload
} from "./prisma-app-api-contracts";

export const PRISMA_MOBILE_UI_CONTRACT_ID = "PRISMA_APP_MOBILE_17_DATA_PLANE";
export const PRISMA_MOBILE_SNAPSHOT_API_VERSION = "2026-05-02.mobile.17";
export const PRISMA_MOBILE_SNAPSHOT_ENDPOINT = "/api/mobile/snapshot";

export const PrismaMobileSnapshotPayloadSchema = z.object({
  summary: PrismaMobileSummaryPayloadSchema,
  salesToday: PrismaMobileSalesTodayPayloadSchema,
  cashCurrent: PrismaMobileCashCurrentPayloadSchema,
  inventoryWatchlist: PrismaMobileInventoryWatchlistPayloadSchema,
  alerts: PrismaMobileAlertsPayloadSchema,
  reportsDaily: PrismaMobileReportsDailyPayloadSchema,
  branches: PrismaMobileBranchesPayloadSchema,
  health: PrismaMobileHealthPayloadSchema
});

export const PrismaMobileSnapshotMetaSchema = z.object({
  apiVersion: z.literal(PRISMA_MOBILE_SNAPSHOT_API_VERSION),
  endpoint: z.literal("snapshot"),
  generatedAt: z.string().datetime(),
  source: z.enum(["api-snapshot", "api-endpoints", "connected-data-plane", "tablet-pos", "pc-backoffice", "local-cache", "unavailable"]),
  runtimeMode: z.enum(["connected", "partial", "offline"]),
  contractId: z.literal(PRISMA_MOBILE_UI_CONTRACT_ID),
  upstreamContractId: PrismaMobileApiMetaSchema.shape.contractId,
  upstreams: PrismaMobileApiMetaSchema.shape.upstreams
});

export const PrismaMobileSnapshotEnvelopeSchema = z.object({ ok: z.literal(true), data: PrismaMobileSnapshotPayloadSchema, meta: PrismaMobileSnapshotMetaSchema });

export const PrismaMobileClientSnapshotSchema = z.object({
  snapshot: PrismaMobileSnapshotPayloadSchema,
  source: PrismaMobileSnapshotMetaSchema.shape.source,
  fetchedAt: z.string().datetime(),
  stale: z.boolean(),
  errors: z.array(z.string())
});

export type PrismaMobileSnapshotPayload = z.infer<typeof PrismaMobileSnapshotPayloadSchema>;
export type PrismaMobileSnapshotMeta = z.infer<typeof PrismaMobileSnapshotMetaSchema>;
export type PrismaMobileSnapshotEnvelope = z.infer<typeof PrismaMobileSnapshotEnvelopeSchema>;
export type PrismaMobileClientSnapshot = z.infer<typeof PrismaMobileClientSnapshotSchema>;
export type PrismaMobileSnapshotParts = {
  summary: PrismaMobileSummaryPayload;
  salesToday: PrismaMobileSalesTodayPayload;
  cashCurrent: PrismaMobileCashCurrentPayload;
  inventoryWatchlist: PrismaMobileInventoryWatchlistPayload;
  alerts: PrismaMobileAlertsPayload;
  reportsDaily: PrismaMobileReportsDailyPayload;
  branches: PrismaMobileBranchesPayload;
  health: PrismaMobileHealthPayload;
};

export function buildPrismaMobileSnapshotMeta(source: PrismaMobileSnapshotMeta["source"], runtimeMode: PrismaMobileSnapshotMeta["runtimeMode"] = "connected", upstreams: PrismaMobileSnapshotMeta["upstreams"] = []): PrismaMobileSnapshotMeta {
  return PrismaMobileSnapshotMetaSchema.parse({
    apiVersion: PRISMA_MOBILE_SNAPSHOT_API_VERSION,
    endpoint: "snapshot",
    generatedAt: new Date().toISOString(),
    source,
    runtimeMode,
    contractId: PRISMA_MOBILE_UI_CONTRACT_ID,
    upstreamContractId: "PRISMA_APP_MOBILE_17_DATA_PLANE",
    upstreams
  });
}

export function okMobileSnapshotResponse(data: PrismaMobileSnapshotPayload, source: PrismaMobileSnapshotMeta["source"] = "api-snapshot", runtimeMode: PrismaMobileSnapshotMeta["runtimeMode"] = "connected", upstreams: PrismaMobileSnapshotMeta["upstreams"] = []): PrismaMobileSnapshotEnvelope {
  return PrismaMobileSnapshotEnvelopeSchema.parse({ ok: true, data, meta: buildPrismaMobileSnapshotMeta(source, runtimeMode, upstreams) });
}

export function createClientSnapshot(snapshot: PrismaMobileSnapshotPayload, source: PrismaMobileClientSnapshot["source"], errors: string[] = []): PrismaMobileClientSnapshot {
  return PrismaMobileClientSnapshotSchema.parse({ snapshot, source, fetchedAt: new Date().toISOString(), stale: source === "local-cache" || errors.length > 0, errors });
}

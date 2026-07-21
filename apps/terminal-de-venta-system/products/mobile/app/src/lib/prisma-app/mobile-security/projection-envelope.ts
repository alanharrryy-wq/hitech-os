import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { MobileRequestContext } from "./context";
import { sanitizeMobileWarnings } from "./sanitize";

export const MOBILE_PROJECTION_CONTRACT_VERSION = "2026-07-20.mobile.projection.1";
export const MOBILE_PROJECTION_SCHEMA_VERSION = "prisma.mobile.projection.v1";

export const MOBILE_PHASE1_READ_MODELS = [
  "RM.SYSTEM.SUMMARY",
  "RM.DATA.READINESS",
  "RM.SYNC.SOURCE_HEALTH",
  "RM.BUSINESS.EXECUTIVE_SUMMARY",
  "RM.SALES.SUMMARY"
] as const;

export type MobilePhase1ReadModelId = (typeof MOBILE_PHASE1_READ_MODELS)[number];

type ProjectionSpec = {
  owner: string;
  sourceSystem: string;
  privacyClass: string;
  ttlSeconds: number;
};

const PROJECTION_SPECS: Record<MobilePhase1ReadModelId, ProjectionSpec> = {
  "RM.SYSTEM.SUMMARY": {
    owner: "PLATFORM|PC|TABLET",
    sourceSystem: "PRISMA_GOVERNED_PROJECTION",
    privacyClass: "PRIV.SECURITY_SENSITIVE",
    ttlSeconds: 60
  },
  "RM.DATA.READINESS": {
    owner: "TABLET|PC",
    sourceSystem: "PRISMA_GOVERNED_PROJECTION",
    privacyClass: "PRIV.INTERNAL_OPERATIONAL",
    ttlSeconds: 60
  },
  "RM.SYNC.SOURCE_HEALTH": {
    owner: "TABLET|PC",
    sourceSystem: "PRISMA_GOVERNED_PROJECTION",
    privacyClass: "PRIV.SECURITY_SENSITIVE",
    ttlSeconds: 60
  },
  "RM.BUSINESS.EXECUTIVE_SUMMARY": {
    owner: "TABLET|PC",
    sourceSystem: "PRISMA_GOVERNED_PROJECTION",
    privacyClass: "PRIV.INTERNAL_OPERATIONAL",
    ttlSeconds: 300
  },
  "RM.SALES.SUMMARY": {
    owner: "TABLET",
    sourceSystem: "PRISMA_GOVERNED_PROJECTION",
    privacyClass: "PRIV.FINANCIAL_RESTRICTED",
    ttlSeconds: 120
  }
};

function freshnessState(state: MobileDataPlaneState): string {
  if (state.runtimeMode === "live") return "STA.FRESH";
  if (state.runtimeMode === "stale") return "STA.STALE";
  if (state.runtimeMode === "partial") return "STA.PARTIAL";
  if (state.runtimeMode === "offline") return "STA.SOURCE_OFFLINE";
  return "STA.UNKNOWN";
}

function dataQuality(state: MobileDataPlaneState): string {
  if (state.runtimeMode === "live" && state.warnings.length === 0) return "COMPLETE";
  if (state.runtimeMode === "offline") return "UNAVAILABLE";
  if (state.runtimeMode === "stale") return "STALE";
  return "PARTIAL";
}

export function buildMobileProjectionEnvelope<TData>(
  readModelId: MobilePhase1ReadModelId,
  data: TData,
  state: MobileDataPlaneState,
  context: MobileRequestContext
) {
  const generatedAt = new Date();
  const spec = PROJECTION_SPECS[readModelId];

  return {
    ok: true as const,
    data,
    meta: {
      readModelId,
      contractVersion: MOBILE_PROJECTION_CONTRACT_VERSION,
      schemaVersion: MOBILE_PROJECTION_SCHEMA_VERSION,
      sourceSystem: spec.sourceSystem,
      sourceRuntime: "3140",
      sourceOwner: spec.owner,
      tenantId: context.tenantId,
      businessId: context.businessId,
      branchId: context.branchId ?? null,
      terminalId: context.terminalId ?? null,
      deviceId: context.deviceId,
      licenseId: context.licenseId,
      actorId: context.actorId,
      capturedAt: generatedAt.toISOString(),
      observedAt: generatedAt.toISOString(),
      generatedAt: generatedAt.toISOString(),
      expiresAt: new Date(generatedAt.getTime() + spec.ttlSeconds * 1_000).toISOString(),
      timezone: "America/Mexico_City",
      currency: "MXN",
      locale: "es-MX",
      freshnessState: freshnessState(state),
      dataQuality: dataQuality(state),
      privacyClass: spec.privacyClass,
      permissionScope: readModelId,
      authorizationMode: context.authorizationMode,
      traceId: context.traceId,
      sourceEventIds: [] as string[],
      nextCursor: null,
      warnings: sanitizeMobileWarnings(state.warnings),
      errors: [] as string[]
    }
  };
}

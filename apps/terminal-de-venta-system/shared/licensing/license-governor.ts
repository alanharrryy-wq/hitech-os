import { FEATURE_KEYS } from "./feature-keys";
import { resolveFeatures } from "./feature-resolver";
import { getLicenseRefreshStatus } from "./license-refresh-client";
import { loadLocalLicense } from "./license-loader";
import { resolveRuntimeContext, type RuntimeContext } from "../runtime";
import type { LicenseRefreshState } from "./license-refresh-state";
import type { FeatureResolution, LicenseSurface, NormalizedLicenseStatus } from "./license-types";

export type LicenseGovernorSnapshot = {
  surface: LicenseSurface;
  status: NormalizedLicenseStatus;
  runtimeContext: RuntimeContext;
  refreshState: LicenseRefreshState;
  decisions: FeatureResolution[];
  operationalDecision: NormalizedLicenseStatus["operationalDecision"];
  canUseLocalPos: boolean;
  denialReason: NormalizedLicenseStatus["denialReason"];
};

export function getLicenseGovernorSnapshot(options: { surface: LicenseSurface; featureKeys?: string[] }): LicenseGovernorSnapshot {
  const runtimeContext = resolveRuntimeContext({ role: options.surface });
  const refreshState = getLicenseRefreshStatus();
  const loaded = loadLocalLicense();
  const status: NormalizedLicenseStatus = {
    ...loaded,
    lastRefreshAt: loaded.lastRefreshAt ?? refreshState.lastSuccessAt ?? refreshState.lastRefreshAt,
    evidenceEvent: {
      ...loaded.evidenceEvent,
      source: refreshState.state === "refresh_disabled" ? "refresh_state" : loaded.evidenceEvent.source
    }
  };
  const featureKeys = options.featureKeys ?? [...FEATURE_KEYS];
  const decisions = resolveFeatures(status, featureKeys);
  const posDecision = decisions.find((decision) => decision.key === "pos.sale.complete");

  return {
    surface: options.surface,
    status,
    runtimeContext,
    refreshState,
    decisions,
    operationalDecision: status.operationalDecision,
    canUseLocalPos: Boolean(posDecision?.allowed),
    denialReason: posDecision?.denialReason ?? status.denialReason
  };
}

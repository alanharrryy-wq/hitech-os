import { loadLocalLicense } from "./license-loader";
import { resolveFeature } from "./feature-resolver";
import type { FeatureResolution, LicenseApiEnvelope, NormalizedLicenseStatus } from "./license-types";

export function getLicenseStatus(): NormalizedLicenseStatus {
  return loadLocalLicense();
}

export function getFeatureResolution(key: string): FeatureResolution {
  return resolveFeature(loadLocalLicense(), key);
}

export function licenseDeniedEnvelope(resolution: FeatureResolution): LicenseApiEnvelope<never> {
  return {
    ok: false,
    code: "LICENSE_FEATURE_DENIED",
    message: resolution.reason,
    details: {
      feature: resolution.key,
      plan: resolution.plan,
      state: resolution.state,
      requiredPlan: resolution.requiredPlan,
      assignmentState: resolution.assignmentState,
      denialReason: resolution.denialReason,
      enforcement: resolution.enforcement,
      operationalDecision: resolution.operationalDecision,
      evidenceEvent: resolution.evidenceEvent,
      saleBasicsStillAvailable: resolution.saleBasicsStillAvailable,
      warnings: resolution.warnings
    }
  };
}

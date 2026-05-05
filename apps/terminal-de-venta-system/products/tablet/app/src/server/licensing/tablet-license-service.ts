import { FEATURE_KEYS, getFeatureResolution, getLicenseStatus } from "../../../../../../shared/licensing";
import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../../shared/licensing";

export function getTabletLicenseStatus(): NormalizedLicenseStatus {
  return getLicenseStatus();
}

export function resolveTabletFeature(featureKey: string): FeatureResolution {
  return getFeatureResolution(featureKey);
}

export function getTabletFeatureList(): FeatureResolution[] {
  const keys = FEATURE_KEYS.filter((key) => key.startsWith("pos.") || key.startsWith("shift.") || key.startsWith("inventory.local") || key.startsWith("event.") || key.startsWith("export.") || key.startsWith("report."));
  return keys.map((key) => resolveTabletFeature(key));
}

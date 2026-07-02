import { FEATURE_KEYS, getLicenseGovernorSnapshot } from "../../../../../../shared/licensing";
import type { FeatureResolution, LicenseGovernorSnapshot, NormalizedLicenseStatus } from "../../../../../../shared/licensing";

export function getTabletLicenseStatus(): NormalizedLicenseStatus {
  return getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: getTabletFeatureKeys() }).status;
}

export function resolveTabletFeature(featureKey: string): FeatureResolution {
  return getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: [featureKey] }).decisions[0];
}

export function getTabletFeatureList(): FeatureResolution[] {
  return getTabletLicenseGovernor().decisions;
}

export function getTabletLicenseGovernor(): LicenseGovernorSnapshot {
  return getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: getTabletFeatureKeys() });
}

function getTabletFeatureKeys(): string[] {
  return FEATURE_KEYS.filter((key) => key.startsWith("pos.") || key.startsWith("shift.") || key.startsWith("inventory.local") || key.startsWith("event.") || key.startsWith("export.") || key.startsWith("report."));
}

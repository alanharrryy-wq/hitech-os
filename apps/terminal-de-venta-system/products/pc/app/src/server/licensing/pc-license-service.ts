import { FEATURE_KEYS, getLicenseGovernorSnapshot } from "../../../../../../shared/licensing";
import type { FeatureResolution, LicenseGovernorSnapshot, NormalizedLicenseStatus } from "../../../../../../shared/licensing";

function getPcFeatureKeys(): string[] {
  return FEATURE_KEYS.filter((key) => key.startsWith("pc.") || key.startsWith("sync.") || key.startsWith("catalog.") || key.startsWith("stock.") || key.startsWith("inventory.") || key.startsWith("purchase.") || key.startsWith("receiving.") || key.startsWith("replenishment.") || key.startsWith("audit.") || key.startsWith("multi.") || key.startsWith("forecast.") || key.startsWith("advanced."));
}

export function getPcLicenseGovernor(): LicenseGovernorSnapshot {
  return getLicenseGovernorSnapshot({ surface: "pc", featureKeys: getPcFeatureKeys() });
}

export function getPcLicenseStatus(): NormalizedLicenseStatus {
  return getPcLicenseGovernor().status;
}

export function resolvePcFeature(featureKey: string): FeatureResolution {
  return getLicenseGovernorSnapshot({ surface: "pc", featureKeys: [featureKey] }).decisions[0];
}

export function getPcFeatureList(): FeatureResolution[] {
  return getPcLicenseGovernor().decisions;
}

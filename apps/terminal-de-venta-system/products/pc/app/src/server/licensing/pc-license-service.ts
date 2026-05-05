import { FEATURE_KEYS, getFeatureResolution, getLicenseStatus } from "../../../../../../shared/licensing";
import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../../shared/licensing";

export function getPcLicenseStatus(): NormalizedLicenseStatus {
  return getLicenseStatus();
}

export function resolvePcFeature(featureKey: string): FeatureResolution {
  return getFeatureResolution(featureKey);
}

export function getPcFeatureList(): FeatureResolution[] {
  const keys = FEATURE_KEYS.filter((key) => key.startsWith("pc.") || key.startsWith("sync.") || key.startsWith("catalog.") || key.startsWith("stock.") || key.startsWith("inventory.") || key.startsWith("purchase.") || key.startsWith("receiving.") || key.startsWith("replenishment.") || key.startsWith("audit.") || key.startsWith("multi.") || key.startsWith("forecast.") || key.startsWith("advanced."));
  return keys.map((key) => resolvePcFeature(key));
}

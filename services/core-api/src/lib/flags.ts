import { FEATURE_FLAGS_DEFAULTS, type FeatureFlags } from "../contracts.ts";

export function getFeatureFlags(overrides?: Partial<FeatureFlags>): FeatureFlags {
  return {
    ...FEATURE_FLAGS_DEFAULTS,
    ...(overrides ?? {})
  };
}

export const DEFAULT_FLAGS: FeatureFlags = { ...FEATURE_FLAGS_DEFAULTS };

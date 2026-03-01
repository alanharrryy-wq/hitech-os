import {
  FEATURE_FLAG_KEYS,
  FeatureFlagKey,
  FeatureFlags,
  createFeatureFlags,
} from "../contracts/FactoryContracts";
import { deepFreeze } from "../shared/Immutability";

export interface FeatureFlagRegistration {
  readonly key: FeatureFlagKey;
  readonly description: string;
  readonly defaultValue: false;
}

function compareRegistrations(
  left: FeatureFlagRegistration,
  right: FeatureFlagRegistration,
): number {
  return left.key.localeCompare(right.key);
}

export class FeatureFlagRegistry {
  private readonly registrations: readonly FeatureFlagRegistration[];

  constructor() {
    const registrations = FEATURE_FLAG_KEYS.map((key) => ({
      key,
      description: `Feature flag ${key} is opt-in and defaults OFF.`,
      defaultValue: false as const,
    })).sort(compareRegistrations);
    this.registrations = deepFreeze(registrations);
  }

  list(): readonly FeatureFlagRegistration[] {
    return this.registrations;
  }

  resolve(
    overrides: Readonly<Partial<Record<FeatureFlagKey, boolean>>> = {},
  ): FeatureFlags {
    return createFeatureFlags(overrides);
  }

  assertAllOff(flags: FeatureFlags): void {
    for (const registration of this.registrations) {
      if (flags[registration.key] !== false) {
        throw new Error(`Feature flag ${registration.key} must remain OFF by default.`);
      }
    }
  }
}

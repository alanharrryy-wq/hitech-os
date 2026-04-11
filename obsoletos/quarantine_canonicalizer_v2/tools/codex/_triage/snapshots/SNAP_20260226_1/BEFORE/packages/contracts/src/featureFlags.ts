import { z } from "zod";

export const FeatureFlagsSchema = z
  .object({
    enableAiExecution: z.boolean().default(false),
    enableCapabilitiesProxy: z.boolean().default(false),
    enableExperimentalUi: z.boolean().default(false),
    enableHealthDashboard: z.boolean().default(false)
  })
  .strict();

export type FeatureFlags = z.infer<typeof FeatureFlagsSchema>;

export const FEATURE_FLAGS_KEYS = Object.freeze([
  "enableAiExecution",
  "enableCapabilitiesProxy",
  "enableExperimentalUi",
  "enableHealthDashboard"
]);

export const FEATURE_FLAGS_DEFAULTS: FeatureFlags = Object.freeze({
  enableAiExecution: false,
  enableCapabilitiesProxy: false,
  enableExperimentalUi: false,
  enableHealthDashboard: false
});

export function resolveFeatureFlags(input?: Partial<FeatureFlags>): FeatureFlags {
  return FeatureFlagsSchema.parse({
    ...FEATURE_FLAGS_DEFAULTS,
    ...(input ?? {})
  });
}

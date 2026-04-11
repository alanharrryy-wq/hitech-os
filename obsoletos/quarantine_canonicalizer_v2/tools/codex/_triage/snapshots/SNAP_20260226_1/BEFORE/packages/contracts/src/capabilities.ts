import { z } from "zod";
import { FEATURE_FLAGS_DEFAULTS, FeatureFlagsSchema } from "./featureFlags.js";
import { type JobKind, JobKindSchema } from "./job.js";

export const AgentCapabilitiesSchema = z
  .object({
    serviceName: z.literal("ai-agent"),
    version: z.string().min(1),
    protocolVersion: z.string().min(1),
    deterministic: z.literal(true),
    supportedJobKinds: z.array(JobKindSchema).min(1),
    maxInputChars: z.number().int().positive(),
    defaults: FeatureFlagsSchema.default(FEATURE_FLAGS_DEFAULTS),
    notes: z.array(z.string().min(1))
  })
  .strict();

export type AgentCapabilities = z.infer<typeof AgentCapabilitiesSchema>;

const DEFAULT_SUPPORTED_JOB_KINDS: readonly JobKind[] = ["echo", "extract_keywords", "summarize_text"];
const DEFAULT_NOTES: readonly string[] = ["deterministic-by-default", "no timer-driven control"];

export function createAgentCapabilities(input: {
  version: string;
  protocolVersion: string;
  maxInputChars: number;
  supportedJobKinds?: readonly JobKind[];
  notes?: readonly string[];
}): AgentCapabilities {
  return AgentCapabilitiesSchema.parse({
    serviceName: "ai-agent",
    version: input.version,
    protocolVersion: input.protocolVersion,
    deterministic: true,
    supportedJobKinds: [...(input.supportedJobKinds ?? DEFAULT_SUPPORTED_JOB_KINDS)].sort((left, right) =>
      left.localeCompare(right)
    ),
    maxInputChars: input.maxInputChars,
    defaults: FEATURE_FLAGS_DEFAULTS,
    notes: [...(input.notes ?? DEFAULT_NOTES)]
      .map((item) => item.trim())
      .filter((item) => item.length > 0)
      .sort((left, right) => left.localeCompare(right))
  });
}

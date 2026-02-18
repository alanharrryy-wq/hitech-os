import { z } from "zod";
import { FEATURE_FLAGS_DEFAULTS, FeatureFlagsSchema } from "./featureFlags.js";

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

export const JsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([z.string(), z.number(), z.boolean(), z.null(), z.array(JsonValueSchema), z.record(JsonValueSchema)])
);

export const JobKindSchema = z.enum(["echo", "summarize_text", "extract_keywords"]);

export const JobRequestSchema = z
  .object({
    jobId: z.string().min(1),
    kind: JobKindSchema,
    input: z.record(JsonValueSchema),
    requestedAtUtc: z.string().datetime({ offset: true }),
    flags: FeatureFlagsSchema.default(FEATURE_FLAGS_DEFAULTS)
  })
  .strict();

export const JobStatusSchema = z.enum(["queued", "running", "completed", "failed"]);

export const StructuredLogLevelSchema = z.enum(["info", "warn", "error"]);

export const StructuredLogSchema = z
  .object({
    seq: z.number().int().min(0),
    level: StructuredLogLevelSchema,
    event: z.string().min(1),
    message: z.string().min(1),
    atUtc: z.string().datetime({ offset: true }),
    details: z.record(JsonValueSchema).default({})
  })
  .strict();

export const JobResultSchema = z
  .object({
    jobId: z.string().min(1),
    kind: JobKindSchema,
    status: JobStatusSchema,
    output: z.record(JsonValueSchema),
    logs: z.array(StructuredLogSchema),
    finishedAtUtc: z.string().datetime({ offset: true }).nullable()
  })
  .strict();

export type JobRequest = z.infer<typeof JobRequestSchema>;
export type JobResult = z.infer<typeof JobResultSchema>;
export type JobKind = z.infer<typeof JobKindSchema>;
export type JobStatus = z.infer<typeof JobStatusSchema>;
export type StructuredLog = z.infer<typeof StructuredLogSchema>;

export function createQueuedJobResult(input: { jobId: string; kind: JobKind; atUtc: string }): JobResult {
  return {
    jobId: input.jobId,
    kind: input.kind,
    status: "queued",
    output: {},
    logs: [
      {
        seq: 0,
        level: "info",
        event: "job.accepted",
        message: "Job accepted into deterministic queue",
        atUtc: input.atUtc,
        details: {}
      }
    ],
    finishedAtUtc: null
  };
}

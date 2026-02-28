import { z } from "zod";
import { RunIdSchema, UserIdSchema, WidgetIdSchema } from "../brands.js";
import { IsoDateTimeSchema } from "./shared.js";

export const RunStatusSchema = z.enum([
  "queued",
  "scheduled",
  "running",
  "paused",
  "succeeded",
  "failed",
  "canceled"
]);

export const RunPrioritySchema = z.enum(["low", "normal", "high", "critical"]);

export const RunSourceSchema = z.enum(["manual", "schedule", "api", "automation"]);

export const RunHealthSchema = z.enum(["healthy", "degraded", "stalled", "unknown"]);

export const RunTimestampSchema = z
  .object({
    createdAt: IsoDateTimeSchema,
    scheduledAt: IsoDateTimeSchema.nullable().default(null),
    startedAt: IsoDateTimeSchema.nullable().default(null),
    updatedAt: IsoDateTimeSchema,
    finishedAt: IsoDateTimeSchema.nullable().default(null)
  })
  .strict();

export const RunProgressSchema = z
  .object({
    currentStep: z.number().int().min(0),
    totalSteps: z.number().int().min(1),
    percent: z.number().min(0).max(100),
    etaSeconds: z.number().int().min(0).nullable().default(null)
  })
  .strict();

export const RunTagSchema = z
  .string()
  .trim()
  .min(2)
  .max(48)
  .regex(/^[a-z0-9][a-z0-9:-]{1,47}$/i);

export const RunSummarySchema = z
  .object({
    id: RunIdSchema,
    name: z.string().min(3).max(120),
    status: RunStatusSchema,
    priority: RunPrioritySchema,
    source: RunSourceSchema,
    ownerId: UserIdSchema,
    assigneeId: UserIdSchema.nullable().default(null),
    widgetIds: z.array(WidgetIdSchema).min(1).max(24),
    health: RunHealthSchema,
    progress: RunProgressSchema,
    tags: z.array(RunTagSchema).max(20).default([]),
    timestamps: RunTimestampSchema,
    version: z.number().int().min(1).default(1)
  })
  .strict();

export const RunMetricSnapshotSchema = z
  .object({
    cpuPercent: z.number().min(0).max(100),
    memoryMb: z.number().min(0),
    ioReadKb: z.number().min(0),
    ioWriteKb: z.number().min(0),
    activeWorkers: z.number().int().min(0)
  })
  .strict();

export const RunStepSchema = z
  .object({
    stepId: z.string().min(1).max(64),
    label: z.string().min(1).max(120),
    status: z.enum(["pending", "running", "succeeded", "failed", "skipped"]),
    startedAt: IsoDateTimeSchema.nullable().default(null),
    endedAt: IsoDateTimeSchema.nullable().default(null),
    durationMs: z.number().int().min(0).nullable().default(null)
  })
  .strict();

export const RunDetailsSchema = RunSummarySchema.extend({
  description: z.string().max(800).default(""),
  metrics: RunMetricSnapshotSchema,
  steps: z.array(RunStepSchema).max(200),
  blockedReason: z.string().max(240).nullable().default(null),
  retryCount: z.number().int().min(0).default(0),
  maxRetries: z.number().int().min(0).max(20).default(3)
}).strict();

export const RunStatusTransitionSchema = z
  .object({
    from: RunStatusSchema,
    to: RunStatusSchema,
    at: IsoDateTimeSchema,
    reason: z.string().min(3).max(240).default("status-change")
  })
  .strict();

export type RunStatus = z.infer<typeof RunStatusSchema>;
export type RunPriority = z.infer<typeof RunPrioritySchema>;
export type RunSource = z.infer<typeof RunSourceSchema>;
export type RunHealth = z.infer<typeof RunHealthSchema>;
export type RunSummary = z.infer<typeof RunSummarySchema>;
export type RunDetails = z.infer<typeof RunDetailsSchema>;
export type RunStep = z.infer<typeof RunStepSchema>;
export type RunProgress = z.infer<typeof RunProgressSchema>;
export type RunStatusTransition = z.infer<typeof RunStatusTransitionSchema>;

const TERMINAL_STATUSES = new Set<RunStatus>(["succeeded", "failed", "canceled"]);

export function isRunTerminal(status: RunStatus): boolean {
  return TERMINAL_STATUSES.has(status);
}

export function computeRunDurationMs(timestamps: {
  startedAt: string | null;
  finishedAt: string | null;
  updatedAt: string;
}): number | null {
  if (!timestamps.startedAt) {
    return null;
  }

  const start = Date.parse(timestamps.startedAt);
  const end = Date.parse(timestamps.finishedAt ?? timestamps.updatedAt);

  if (Number.isNaN(start) || Number.isNaN(end)) {
    return null;
  }

  return Math.max(0, end - start);
}

export function canTransitionRunStatus(from: RunStatus, to: RunStatus): boolean {
  if (from === to) {
    return true;
  }

  const transitions: Record<RunStatus, readonly RunStatus[]> = {
    queued: ["scheduled", "running", "canceled"],
    scheduled: ["running", "canceled"],
    running: ["paused", "succeeded", "failed", "canceled"],
    paused: ["running", "canceled", "failed"],
    succeeded: [],
    failed: ["queued", "scheduled"],
    canceled: ["queued", "scheduled"]
  };

  return transitions[from].includes(to);
}

export function deriveRunHealth(input: {
  status: RunStatus;
  progressPercent: number;
  updatedAt: string;
  nowAt: string;
}): RunHealth {
  if (isRunTerminal(input.status)) {
    return input.status === "succeeded" ? "healthy" : "degraded";
  }

  const lagMs = Date.parse(input.nowAt) - Date.parse(input.updatedAt);
  const staleThresholdMs = 8 * 60 * 1000;

  if (Number.isNaN(lagMs)) {
    return "unknown";
  }

  if (lagMs > staleThresholdMs) {
    return "stalled";
  }

  if (input.status === "running" && input.progressPercent < 2) {
    return "degraded";
  }

  return "healthy";
}

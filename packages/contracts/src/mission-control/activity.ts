import { z } from "zod";
import { RunIdSchema, UserIdSchema } from "../brands.js";
import { IsoDateTimeSchema, SeveritySchema } from "./shared.js";

export const ActivityActorTypeSchema = z.enum(["user", "service", "system"]);

export const ActivityActorSchema = z
  .object({
    type: ActivityActorTypeSchema,
    id: z.string().min(1).max(120),
    userId: UserIdSchema.nullable().default(null),
    displayName: z.string().min(1).max(120),
    avatarUrl: z.string().url().nullable().default(null)
  })
  .strict();

export const ActivityEventTypeSchema = z.enum([
  "run.created",
  "run.queued",
  "run.started",
  "run.progress",
  "run.paused",
  "run.resumed",
  "run.completed",
  "run.failed",
  "run.canceled",
  "evidence.added",
  "widget.updated",
  "system.alert",
  "auth.login",
  "auth.logout"
]);

export const ActivityMetadataSchema = z
  .record(z.union([z.string(), z.number(), z.boolean(), z.null(), z.array(z.string())]))
  .default({});

export const ActivityEventSchema = z
  .object({
    id: z.string().regex(/^act_[a-z0-9][a-z0-9-_]{5,63}$/),
    type: ActivityEventTypeSchema,
    severity: SeveritySchema,
    title: z.string().min(3).max(200),
    message: z.string().min(3).max(800),
    actor: ActivityActorSchema,
    runId: RunIdSchema.nullable().default(null),
    createdAt: IsoDateTimeSchema,
    acknowledged: z.boolean().default(false),
    metadata: ActivityMetadataSchema
  })
  .strict();

export const ActivityFeedSchema = z
  .object({
    items: z.array(ActivityEventSchema),
    cursor: z.string().nullable().default(null),
    hasMore: z.boolean().default(false)
  })
  .strict();

export type ActivityActor = z.infer<typeof ActivityActorSchema>;
export type ActivityEvent = z.infer<typeof ActivityEventSchema>;
export type ActivitySeverity = z.infer<typeof SeveritySchema>;
export type ActivityEventType = z.infer<typeof ActivityEventTypeSchema>;
export type ActivityFeed = z.infer<typeof ActivityFeedSchema>;

const severityRank: Record<ActivitySeverity, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
  critical: 4
};

export function sortActivityByDate(items: readonly ActivityEvent[]): ActivityEvent[] {
  return [...items].sort((left, right) => Date.parse(right.createdAt) - Date.parse(left.createdAt));
}

export function filterActivityBySeverity(
  items: readonly ActivityEvent[],
  minimumSeverity: ActivitySeverity
): ActivityEvent[] {
  const minRank = severityRank[minimumSeverity];
  return items.filter((item) => severityRank[item.severity] >= minRank);
}

export function summarizeActivity(
  items: readonly ActivityEvent[]
): Record<ActivitySeverity, { readonly count: number; readonly acknowledged: number }> {
  const summary: Record<ActivitySeverity, { count: number; acknowledged: number }> = {
    debug: { count: 0, acknowledged: 0 },
    info: { count: 0, acknowledged: 0 },
    warn: { count: 0, acknowledged: 0 },
    error: { count: 0, acknowledged: 0 },
    critical: { count: 0, acknowledged: 0 }
  };

  for (const item of items) {
    summary[item.severity].count += 1;
    if (item.acknowledged) {
      summary[item.severity].acknowledged += 1;
    }
  }

  return summary;
}

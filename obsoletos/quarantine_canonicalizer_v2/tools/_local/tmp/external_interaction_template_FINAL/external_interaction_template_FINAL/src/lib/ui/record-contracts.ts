import { z } from "zod";

import { RECORD_STATES, type DispatchJob, type ExternalRecord, type RecordState, type Submission, type SyncEvent } from "@/lib/core/types";
import { clampItems, coerceDate, sanitizeOptionalText, sanitizeText, safeJson, sortByDateDesc, toDisplayText, uniqueBy } from "@/lib/ui/contracts";

export const recordStateSchema = z.enum(RECORD_STATES);

export interface PreviewFieldContract {
  label: string;
  value: string;
}

export interface TimelineEntryContract {
  id: string;
  kind: "submission" | "dispatch" | "sync";
  title: string;
  description?: string;
  createdAt: Date;
  state?: RecordState;
  detail?: string;
  meta?: string;
}

const previewFieldSchema = z.object({
  label: z.string().trim().min(1),
  value: z.string().trim().min(1)
});

export function ensureRecordState(value: unknown, fallback: RecordState = "draft"): RecordState {
  const parsed = recordStateSchema.safeParse(value);
  return parsed.success ? parsed.data : fallback;
}

export function normalizeRecordTitle(record: Pick<ExternalRecord, "title" | "id">): string {
  return sanitizeText(record.title, `Record ${record.id}`);
}

export function normalizePreviewFields(fields: unknown, limit = 4): PreviewFieldContract[] {
  if (!Array.isArray(fields)) return [];
  const normalized = fields
    .map((field) => previewFieldSchema.safeParse(field))
    .filter((result): result is { success: true; data: PreviewFieldContract } => result.success)
    .map((result) => result.data);

  return clampItems(uniqueBy(normalized, (field) => field.label.toLowerCase()), limit);
}

function describeSubmission(submission: Submission): { description: string; detail: string } {
  const payloadKeys = Object.keys(submission.payload ?? {});
  const count = payloadKeys.length;
  const source = sanitizeText(submission.stepId, "runtime");
  const description = count === 0 ? `Captured empty payload from ${source}.` : `Captured ${count} field ${count === 1 ? "update" : "updates"} from ${source}.`;
  return {
    description,
    detail: safeJson(submission.payload)
  };
}

function mapDispatchState(status: DispatchJob["status"]): RecordState {
  switch (status) {
    case "succeeded":
      return "dispatched";
    case "failed":
      return "failed";
    default:
      return "in_review";
  }
}

function mapSyncState(status: SyncEvent["status"]): RecordState {
  switch (status) {
    case "synced":
      return "synced";
    case "failed":
      return "failed";
    default:
      return "submitted";
  }
}

export function createTimelineEntries(params: {
  submissions?: Submission[];
  dispatchJobs?: DispatchJob[];
  syncEvents?: SyncEvent[];
  maxItems?: number;
}): TimelineEntryContract[] {
  const submissionEntries: TimelineEntryContract[] = (params.submissions ?? []).flatMap((submission) => {
    const createdAt = coerceDate(submission.createdAt);
    if (!createdAt) return [];
    const details = describeSubmission(submission);
    return [{
      id: `submission:${submission.id}`,
      kind: "submission",
      title: sanitizeText(submission.stepId, "Submission captured"),
      description: details.description,
      createdAt,
      state: "submitted",
      detail: details.detail,
      meta: sanitizeOptionalText(submission.actorId)
    }];
  });

  const dispatchEntries: TimelineEntryContract[] = (params.dispatchJobs ?? []).flatMap((job) => {
    const createdAt = coerceDate(job.updatedAt) ?? coerceDate(job.createdAt);
    if (!createdAt) return [];
    return [{
      id: `dispatch:${job.id}`,
      kind: "dispatch",
      title: `Dispatch ${sanitizeText(job.status, "pending")}`,
      description: `${sanitizeText(job.adapterId, "adapter")} • attempts: ${Math.max(0, job.attempts ?? 0)}`,
      createdAt,
      state: mapDispatchState(job.status),
      detail: sanitizeOptionalText(job.error) ?? sanitizeOptionalText(job.response ? safeJson(job.response) : undefined)
    }];
  });

  const syncEntries: TimelineEntryContract[] = (params.syncEvents ?? []).flatMap((event) => {
    const createdAt = coerceDate(event.createdAt);
    if (!createdAt) return [];
    return [{
      id: `sync:${event.id}`,
      kind: "sync",
      title: sanitizeText(event.summary, "Sync signal"),
      description: `${sanitizeText(event.direction, "flow")} • ${sanitizeText(event.adapterId, "adapter")}`,
      createdAt,
      state: mapSyncState(event.status),
      detail: sanitizeOptionalText(event.error) ?? sanitizeOptionalText(event.payload ? safeJson(event.payload) : undefined)
    }];
  });

  return clampItems(
    sortByDateDesc(uniqueBy([...submissionEntries, ...dispatchEntries, ...syncEntries], (item) => item.id), (item) => item.createdAt),
    params.maxItems ?? 24
  );
}

export function summarizeRecordFieldValue(value: unknown): string {
  return toDisplayText(value);
}

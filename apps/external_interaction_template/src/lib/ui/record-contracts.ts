import { z } from "zod";

import { RECORD_STATES, type DispatchJob, type ExternalRecord, type RecordState, type Submission, type SyncEvent } from "@/lib/core/types";
import { mapDispatchStatusLabelForLocale } from "@/lib/i18n/enum-labels";
import { translate } from "@/lib/i18n/dictionary";
import { clampItems, coerceDate, sanitizeOptionalText, sanitizeText, sortByDateDesc, toDisplayText, uniqueBy } from "@/lib/ui/contracts";
import { resolveActiveLocale } from "@/lib/utils";

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

const MAX_DETAIL_LINES = 14;
const MAX_DETAIL_NESTING = 3;

function timelineT(key: string, values?: Record<string, string | number>): string {
  return translate(resolveActiveLocale(), key, values);
}

function formatDetailLabel(key: string): string {
  const normalized = sanitizeText(key, timelineT("timeline.detail.valueLabel"))
    .replace(/[_\-.]+/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2");
  return normalized.replace(/\b\w/g, (character) => character.toUpperCase());
}

function toScalarDetail(value: unknown): string | undefined {
  if (value === undefined || value === null || value === "") return undefined;
  if (typeof value === "string") return sanitizeOptionalText(value);
  if (typeof value === "number" || typeof value === "bigint") return String(value);
  if (typeof value === "boolean") return value ? "true" : "false";
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? undefined : value.toISOString();
  return undefined;
}

function pushDetailLine(lines: string[], line: string) {
  if (lines.length >= MAX_DETAIL_LINES) return;
  const normalized = sanitizeOptionalText(line);
  if (!normalized) return;
  lines.push(normalized);
}

function appendDetailLines(
  lines: string[],
  value: unknown,
  label?: string,
  depth = 0,
  seen = new WeakSet<object>()
) {
  if (lines.length >= MAX_DETAIL_LINES) return;

  const scalar = toScalarDetail(value);
  if (scalar !== undefined) {
    pushDetailLine(lines, label ? `${label}: ${scalar}` : scalar);
    return;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      pushDetailLine(lines, label ? `${label}: -` : "-");
      return;
    }

    const scalarValues = value.map((entry) => toScalarDetail(entry));
    if (scalarValues.every((entry) => entry !== undefined)) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.itemsLabel")}: ${scalarValues.join(", ")}`);
      return;
    }

    if (depth >= MAX_DETAIL_NESTING) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.itemsLabel")}: ${value.length}`);
      return;
    }

    const preview = value.slice(0, 4);
    preview.forEach((entry, index) => {
      appendDetailLines(lines, entry, `${label ?? timelineT("timeline.detail.itemLabel")} ${index + 1}`, depth + 1, seen);
    });
    if (value.length > preview.length) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.itemsLabel")}: +${value.length - preview.length}`);
    }
    return;
  }

  if (value && typeof value === "object") {
    const objectValue = value as Record<string, unknown>;
    if (seen.has(objectValue)) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.detailsLabel")}: ${timelineT("timeline.detail.circular")}`);
      return;
    }
    seen.add(objectValue);

    const entries = Object.entries(objectValue);
    if (entries.length === 0) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.detailsLabel")}: -`);
      return;
    }

    if (depth >= MAX_DETAIL_NESTING) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.detailsLabel")}: ${entries.length}`);
      return;
    }

    const preview = entries.slice(0, 8);
    preview.forEach(([key, entryValue]) => {
      const childLabel = label ? `${label} > ${formatDetailLabel(key)}` : formatDetailLabel(key);
      appendDetailLines(lines, entryValue, childLabel, depth + 1, seen);
    });
    if (entries.length > preview.length) {
      pushDetailLine(lines, `${label ?? timelineT("timeline.detail.detailsLabel")}: +${entries.length - preview.length}`);
    }
  }
}

function formatStructuredDetail(value: unknown, label?: string): string | undefined {
  const lines: string[] = [];
  appendDetailLines(lines, value, label);
  if (lines.length === 0) return undefined;
  return lines.slice(0, MAX_DETAIL_LINES).join("\n");
}

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
  const source = sanitizeText(submission.stepId, timelineT("timeline.entry.submission.sourceFallback"));
  const description = count === 0
    ? timelineT("timeline.entry.submission.description.empty", { source })
    : timelineT("timeline.entry.submission.description", { count, source });
  const detail = formatStructuredDetail(submission.payload) ?? timelineT("timeline.detail.emptyPayload");
  return {
    description,
    detail
  };
}

function describeDispatch(job: DispatchJob): string | undefined {
  const lines: string[] = [];

  if (job.error) {
    pushDetailLine(lines, `${timelineT("timeline.detail.errorLabel")}: ${sanitizeText(job.error, timelineT("timeline.entry.dispatch.errorFallback"))}`);
  }

  const responseDetail = formatStructuredDetail(job.response, timelineT("timeline.detail.responseLabel"));
  if (responseDetail) {
    responseDetail.split("\n").forEach((line) => pushDetailLine(lines, line));
  } else {
    const payloadDetail = formatStructuredDetail(job.payload, timelineT("timeline.detail.payloadLabel"));
    if (payloadDetail) {
      payloadDetail.split("\n").forEach((line) => pushDetailLine(lines, line));
    }
  }

  return lines.length > 0 ? lines.join("\n") : undefined;
}

function describeSyncEvent(event: SyncEvent): string | undefined {
  const lines: string[] = [];

  if (event.error) {
    pushDetailLine(lines, `${timelineT("timeline.detail.errorLabel")}: ${sanitizeText(event.error, timelineT("timeline.entry.sync.errorFallback"))}`);
  }

  const payloadDetail = formatStructuredDetail(event.payload, timelineT("timeline.detail.payloadLabel"));
  if (payloadDetail) {
    payloadDetail.split("\n").forEach((line) => pushDetailLine(lines, line));
  }

  return lines.length > 0 ? lines.join("\n") : undefined;
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
      title: sanitizeText(submission.stepId, timelineT("timeline.entry.submission.titleFallback")),
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
      title: timelineT("timeline.entry.dispatch.title", { status: mapDispatchStatusLabelForLocale(job.status) }),
      description: timelineT("timeline.entry.dispatch.description", {
        adapterId: sanitizeText(job.adapterId, timelineT("timeline.entry.dispatch.adapterFallback")),
        attempts: Math.max(0, job.attempts ?? 0)
      }),
      createdAt,
      state: mapDispatchState(job.status),
      detail: describeDispatch(job)
    }];
  });

  const syncEntries: TimelineEntryContract[] = (params.syncEvents ?? []).flatMap((event) => {
    const createdAt = coerceDate(event.createdAt);
    if (!createdAt) return [];
    return [{
      id: `sync:${event.id}`,
      kind: "sync",
      title: sanitizeText(event.summary, timelineT("timeline.entry.sync.titleFallback")),
      description: timelineT("timeline.entry.sync.description", {
        direction: timelineT(`sync.direction.${event.direction}`),
        adapterId: sanitizeText(event.adapterId, timelineT("timeline.entry.sync.adapterFallback"))
      }),
      createdAt,
      state: mapSyncState(event.status),
      detail: describeSyncEvent(event)
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

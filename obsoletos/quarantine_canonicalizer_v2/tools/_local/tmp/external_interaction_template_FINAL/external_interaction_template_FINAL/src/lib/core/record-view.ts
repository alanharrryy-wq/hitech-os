import { getFieldById, getSchema } from "@/lib/core/schema-registry";
import { type ExternalRecord, type RecordState } from "@/lib/core/types";
import { formatHumanLabel, formatValue } from "@/lib/utils";

export const INBOX_STATE_ORDER: RecordState[] = [
  "failed",
  "awaiting_update",
  "submitted",
  "in_review",
  "approved",
  "dispatched",
  "draft",
  "synced",
  "rejected"
];

const stateRank = Object.fromEntries(INBOX_STATE_ORDER.map((state, index) => [state, index])) as Record<RecordState, number>;

export function stateTone(state: RecordState): "default" | "success" | "warning" | "danger" | "accent" {
  switch (state) {
    case "approved":
    case "synced":
      return "success";
    case "awaiting_update":
    case "submitted":
    case "in_review":
      return "warning";
    case "rejected":
    case "failed":
      return "danger";
    case "dispatched":
      return "accent";
    default:
      return "default";
  }
}

export function stateLabel(state: RecordState): string {
  return formatHumanLabel(state);
}

export function stateDescription(state: RecordState): string {
  switch (state) {
    case "draft":
      return "Collecting inputs before submission.";
    case "submitted":
      return "Waiting for reviewer triage.";
    case "in_review":
      return "Under active operator review.";
    case "awaiting_update":
      return "Needs another external update.";
    case "approved":
      return "Approved and ready for dispatch.";
    case "rejected":
      return "Closed with rejection outcome.";
    case "dispatched":
      return "Outbound dispatch has been triggered.";
    case "synced":
      return "External sync completed successfully.";
    case "failed":
      return "Requires intervention before continuing.";
    default:
      return "Status unavailable.";
  }
}

export function compareRecordsForInbox(left: ExternalRecord, right: ExternalRecord): number {
  const stateDelta = stateRank[left.state] - stateRank[right.state];
  if (stateDelta !== 0) {
    return stateDelta;
  }

  const updatedDelta = new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime();
  if (updatedDelta !== 0) {
    return updatedDelta;
  }

  return left.title.localeCompare(right.title);
}

export function sortRecordsForInbox(records: ExternalRecord[]): ExternalRecord[] {
  return [...records].sort(compareRecordsForInbox);
}

export function recordPreviewFields(record: ExternalRecord, limit = 4): Array<{ label: string; value: string }> {
  const schema = getSchema(record.recordTypeId);
  const candidateFieldIds = [...schema.views.listFields, ...schema.views.cardFields].filter(
    (fieldId, index, array) => array.indexOf(fieldId) === index
  );
  const preview: Array<{ label: string; value: string }> = [];
  const seenValues = new Set<string>();

  for (const fieldId of candidateFieldIds) {
    if (preview.length >= limit) break;
    const field = getFieldById(schema, fieldId);
    const rawValue = record.fields[fieldId];
    const value = formatValue(rawValue);

    if (value === "-") continue;
    if (typeof rawValue === "string" && rawValue.trim().toLowerCase() === record.title.trim().toLowerCase()) {
      continue;
    }
    const fingerprint = `${field.label}:${value}`;
    if (seenValues.has(fingerprint)) continue;
    seenValues.add(fingerprint);

    preview.push({
      label: field.label,
      value
    });
  }

  if (preview.length === 0) {
    preview.push({ label: "Record", value: record.id });
  }

  return preview;
}

import { getFieldById, getSchema } from "@/lib/core/schema-registry";
import { type ExternalRecord, type RecordState } from "@/lib/core/types";
import { mapRecordStateDescriptionForLocale, mapRecordStateLabelForLocale } from "@/lib/i18n/enum-labels";
import { formatValue, resolveActiveLocale } from "@/lib/utils";

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

export function stateLabel(state: RecordState, locale?: string | null): string {
  return mapRecordStateLabelForLocale(state, locale);
}

export function stateDescription(state: RecordState, locale?: string | null): string {
  return mapRecordStateDescriptionForLocale(state, locale);
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
    const activeLocale = resolveActiveLocale();
    preview.push({ label: activeLocale === "es" ? "Registro" : "Record", value: record.id });
  }

  return preview;
}

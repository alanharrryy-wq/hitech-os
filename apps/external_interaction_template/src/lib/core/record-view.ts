import { getFieldById, getSchema } from "@/lib/core/schema-registry";
import { type ExternalRecord, type RecordState } from "@/lib/core/types";

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
  return state.replace(/_/g, " ");
}

export function recordPreviewFields(record: ExternalRecord): Array<{ label: string; value: string }> {
  const schema = getSchema(record.recordTypeId);
  return schema.views.listFields.slice(0, 4).map((fieldId) => {
    const field = getFieldById(schema, fieldId);
    const value = record.fields[fieldId];
    const normalized =
      value === undefined || value === null || value === ""
        ? "-"
        : Array.isArray(value)
          ? `${value.length} items`
          : String(value);

    return {
      label: field.label,
      value: normalized
    };
  });
}

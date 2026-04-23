import { type ConditionalRule, type FieldDefinition } from "@/lib/core/types";

function evaluateRule(rule: ConditionalRule, values: Record<string, unknown>): boolean {
  const fieldValue = values[rule.fieldId];

  if (rule.equals !== undefined && fieldValue !== rule.equals) {
    return false;
  }

  if (rule.notEquals !== undefined && fieldValue === rule.notEquals) {
    return false;
  }

  if (rule.in && !rule.in.includes(fieldValue as string | number | boolean)) {
    return false;
  }

  return true;
}

export function isFieldVisible(
  field: FieldDefinition,
  values: Record<string, unknown>,
  role?: string
): boolean {
  if (field.visibleToRoles && role && !field.visibleToRoles.includes(role as never)) {
    return false;
  }
  if (!field.visibleWhen || field.visibleWhen.length === 0) {
    return true;
  }
  return field.visibleWhen.every((rule) => evaluateRule(rule, values));
}

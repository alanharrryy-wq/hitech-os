import { z } from "zod";

import { getFieldById } from "@/lib/core/schema-registry";
import { isFieldVisible } from "@/lib/core/visibility";
import { type RecordTypeSchema } from "@/lib/core/types";

function buildFieldSchema(kind: string, required = false) {
  let base: z.ZodTypeAny;

  switch (kind) {
    case "number":
      base = z.coerce.number({ invalid_type_error: "Must be a number" });
      break;
    case "checkbox":
      base = z.coerce.boolean();
      break;
    case "json":
      base = z
        .string()
        .transform((value) => {
          try {
            return JSON.parse(value);
          } catch {
            throw new Error("Invalid JSON");
          }
        })
        .or(z.record(z.unknown()));
      break;
    default:
      base = z.string().max(5000);
      break;
  }

  if (!required) {
    base = base.optional().nullable();
  }

  if (kind === "file") {
    base = z.any().optional();
  }

  return base;
}

export function validateStepPayload(
  schema: RecordTypeSchema,
  stepId: string,
  values: Record<string, unknown>,
  role?: string
): { ok: true; data: Record<string, unknown> } | { ok: false; errors: Record<string, string> } {
  const step = schema.flow.steps.find((stepEntry) => stepEntry.id === stepId);
  if (!step) {
    return {
      ok: false,
      errors: {
        step: `Unknown step '${stepId}'`
      }
    };
  }

  const errors: Record<string, string> = {};
  const validated: Record<string, unknown> = {};

  for (const fieldId of step.fieldIds) {
    const field = getFieldById(schema, fieldId);
    if (!isFieldVisible(field, values, role)) {
      continue;
    }

    const validator = buildFieldSchema(field.kind, field.required ?? false);
    const result = validator.safeParse(values[field.id]);
    if (!result.success) {
      errors[field.id] = result.error.issues[0]?.message ?? "Invalid value";
      continue;
    }

    const value = result.data;
    if ((field.required ?? false) && (value === undefined || value === null || value === "")) {
      errors[field.id] = "Required";
      continue;
    }

    validated[field.id] = value;
  }

  if (Object.keys(errors).length > 0) {
    return { ok: false, errors };
  }

  return { ok: true, data: validated };
}

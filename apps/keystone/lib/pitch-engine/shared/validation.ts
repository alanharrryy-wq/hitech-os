import { z } from "zod";
import { normalizePath, type ValidationIssue, type ValidationResult } from "./deterministic.js";

export class PitchEngineValidationError extends Error {
  public readonly issues: readonly ValidationIssue[];

  public constructor(message: string, issues: readonly ValidationIssue[]) {
    super(message);
    this.name = "PitchEngineValidationError";
    this.issues = issues;
  }
}

export function normalizeZodIssues(error: z.ZodError): readonly ValidationIssue[] {
  return error.issues.map((issue) => ({
    path: normalizePath(issue.path),
    message: issue.message,
    code: issue.code
  }));
}

export function formatValidationMessage(issues: readonly ValidationIssue[]): string {
  const first = issues[0];
  if (!first) {
    return "Validation failed";
  }

  return `Validation failed at ${first.path}: ${first.message}`;
}

export function parseWithSchema<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  input: unknown
): ValidationResult<z.infer<TSchema>> {
  const parsed = schema.safeParse(input);

  if (parsed.success) {
    return {
      ok: true,
      data: parsed.data,
      errors: []
    };
  }

  const errors = normalizeZodIssues(parsed.error);
  return {
    ok: false,
    errors
  };
}

export function parseOrThrow<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  input: unknown,
  context = "resource"
): z.infer<TSchema> {
  const parsed = schema.safeParse(input);
  if (parsed.success) {
    return parsed.data;
  }

  const issues = normalizeZodIssues(parsed.error);
  const message = `${context}: ${formatValidationMessage(issues)}`;
  throw new PitchEngineValidationError(message, issues);
}

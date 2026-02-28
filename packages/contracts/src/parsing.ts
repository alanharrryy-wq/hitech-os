import { z } from "zod";
import { ValidationError } from "./errors.js";
import { Result, err, ok } from "./result.js";

export interface NormalizedZodIssue {
  readonly path: string;
  readonly code: string;
  readonly message: string;
}

export interface NormalizedZodError {
  readonly name: "ValidationError";
  readonly message: string;
  readonly issues: readonly NormalizedZodIssue[];
}

function normalizePath(path: readonly (string | number)[]): string {
  if (path.length === 0) {
    return "<root>";
  }

  return path
    .map((segment) => (typeof segment === "number" ? `[${segment}]` : segment))
    .reduce<string>((acc, segment) => {
      if (segment.startsWith("[")) {
        return `${acc}${segment}`;
      }
      if (acc.length === 0) {
        return segment;
      }
      return `${acc}.${segment}`;
    }, "");
}

export function normalizeZodError(input: z.ZodError): NormalizedZodError {
  const issues = input.issues.map((issue) => ({
    path: normalizePath(issue.path),
    code: issue.code,
    message: issue.message
  }));

  const firstIssue = issues[0];
  const message = firstIssue
    ? `Validation failed at ${firstIssue.path}: ${firstIssue.message}`
    : "Validation failed";

  return {
    name: "ValidationError",
    message,
    issues
  };
}

export function parseOrThrow<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  input: unknown,
  context: {
    readonly resource?: string;
    readonly operation?: string;
  } = {}
): z.infer<TSchema> {
  const parsed = schema.safeParse(input);

  if (!parsed.success) {
    const normalized = normalizeZodError(parsed.error);
    throw new ValidationError(normalized.message, {
      ...context,
      details: {
        issues: normalized.issues
      },
      cause: parsed.error
    });
  }

  return parsed.data;
}

export function safeParseResult<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  input: unknown
): Result<z.infer<TSchema>, ValidationError> {
  const parsed = schema.safeParse(input);

  if (parsed.success) {
    return ok(parsed.data);
  }

  const normalized = normalizeZodError(parsed.error);
  return err(
    new ValidationError(normalized.message, {
      details: {
        issues: normalized.issues
      },
      cause: parsed.error
    })
  );
}

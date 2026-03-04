import { createHash } from "node:crypto";

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

export interface ValidationIssue {
  readonly path: string;
  readonly message: string;
  readonly code?: string;
}

export interface ValidationResult<T> {
  readonly ok: boolean;
  readonly data?: T;
  readonly errors: readonly ValidationIssue[];
}

function deepSort(value: JsonValue): JsonValue {
  if (Array.isArray(value)) {
    return value.map((entry) => deepSort(entry as JsonValue));
  }

  if (value && typeof value === "object") {
    const entries = Object.entries(value)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, entry]) => [key, deepSort(entry as JsonValue)] as const);

    return Object.fromEntries(entries) as JsonValue;
  }

  return value;
}

export function stableStringify(value: JsonValue): string {
  return JSON.stringify(deepSort(value));
}

export function stableHash(value: JsonValue): string {
  const text = stableStringify(value);
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export function cloneJson<T extends JsonValue>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

export function sortUniqueStrings(values: readonly string[]): readonly string[] {
  return [...new Set(values.map((value) => value.trim()).filter((value) => value.length > 0))].sort(
    (left, right) => left.localeCompare(right)
  );
}

export function isoUtcNow(): string {
  return new Date().toISOString();
}

export function isIsoUtcString(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value)) {
    return false;
  }

  const asDate = Date.parse(value);
  return Number.isFinite(asDate);
}

export function normalizePath(path: readonly (string | number)[]): string {
  if (path.length === 0) {
    return "<root>";
  }

  return path
    .map((part) => (typeof part === "number" ? `[${part}]` : part))
    .reduce<string>((accumulator, segment) => {
      if (segment.startsWith("[")) {
        return `${accumulator}${segment}`;
      }

      return accumulator.length === 0 ? segment : `${accumulator}.${segment}`;
    }, "");
}

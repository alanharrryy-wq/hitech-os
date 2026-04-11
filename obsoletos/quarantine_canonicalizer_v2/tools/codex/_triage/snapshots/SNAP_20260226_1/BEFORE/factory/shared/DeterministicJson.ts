export type JsonPrimitive = string | number | boolean | null;

export type JsonValue = JsonPrimitive | JsonObject | readonly JsonValue[];

export interface JsonObject {
  readonly [key: string]: JsonValue;
}

export interface CanonicalizeOptions {
  readonly sortArrayOfPrimitives?: boolean;
}

const PLAIN_OBJECT_PROTOTYPE = Object.getPrototypeOf({});

function isPlainObject(value: unknown): value is Record<string, unknown> {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const prototype = Object.getPrototypeOf(value);
  return prototype === PLAIN_OBJECT_PROTOTYPE || prototype === null;
}

function assertFiniteNumber(value: number): void {
  if (!Number.isFinite(value)) {
    throw new Error("JSON numbers must be finite.");
  }
}

function canonicalizeArray(
  value: readonly JsonValue[],
  options: CanonicalizeOptions,
): readonly JsonValue[] {
  const canonical = value.map((entry) => canonicalizeJsonValue(entry, options));
  if (options.sortArrayOfPrimitives !== true) {
    return canonical;
  }

  const hasNonPrimitive = canonical.some((entry) => {
    return typeof entry === "object" && entry !== null;
  });
  if (hasNonPrimitive) {
    return canonical;
  }

  const asStrings = canonical.map((entry) => JSON.stringify(entry));
  const sorted = [...asStrings].sort((left, right) => left.localeCompare(right));
  return sorted.map((entry) => JSON.parse(entry) as JsonPrimitive);
}

function canonicalizeObject(
  value: JsonObject,
  options: CanonicalizeOptions,
): JsonObject {
  const output: Record<string, JsonValue> = {};
  const keys = Object.keys(value).sort((left, right) => left.localeCompare(right));
  for (const key of keys) {
    const keyValue = value[key];
    if (keyValue === undefined) {
      throw new Error(`Missing key while canonicalizing object: ${key}`);
    }
    output[key] = canonicalizeJsonValue(keyValue, options);
  }
  return output;
}

export function isJsonPrimitive(value: unknown): value is JsonPrimitive {
  if (value === null) {
    return true;
  }

  if (typeof value === "string" || typeof value === "boolean") {
    return true;
  }

  if (typeof value === "number") {
    return Number.isFinite(value);
  }

  return false;
}

export function isJsonValue(value: unknown): value is JsonValue {
  if (isJsonPrimitive(value)) {
    return true;
  }

  if (Array.isArray(value)) {
    return value.every((entry) => isJsonValue(entry));
  }

  if (isPlainObject(value)) {
    return Object.values(value).every((entry) => isJsonValue(entry));
  }

  return false;
}

export function assertJsonValue(value: unknown, contextLabel: string): asserts value is JsonValue {
  if (!isJsonValue(value)) {
    throw new Error(`${contextLabel} must be a JSON-compatible value.`);
  }
}

export function assertJsonObject(value: unknown, contextLabel: string): asserts value is JsonObject {
  if (!isPlainObject(value)) {
    throw new Error(`${contextLabel} must be a JSON object.`);
  }

  const invalidKey = Object.keys(value).find((key) => !isJsonValue(value[key]));
  if (invalidKey !== undefined) {
    throw new Error(`${contextLabel}.${invalidKey} is not JSON-compatible.`);
  }
}

export function isJsonObject(value: JsonValue): value is JsonObject {
  return value !== null && !Array.isArray(value) && typeof value === "object";
}

export function canonicalizeJsonValue(
  value: JsonValue,
  options: CanonicalizeOptions = {},
): JsonValue {
  if (value === null) {
    return null;
  }

  if (typeof value === "string" || typeof value === "boolean") {
    return value;
  }

  if (typeof value === "number") {
    assertFiniteNumber(value);
    return value;
  }

  if (Array.isArray(value)) {
    return canonicalizeArray(value, options);
  }

  return canonicalizeObject(value as JsonObject, options);
}

export function stringifyCanonicalJson(
  value: JsonValue,
  options: CanonicalizeOptions = {},
): string {
  return JSON.stringify(canonicalizeJsonValue(value, options));
}

export function parseJsonObject(text: string, contextLabel: string): JsonObject {
  const parsed: unknown = JSON.parse(text);
  assertJsonObject(parsed, contextLabel);
  return canonicalizeJsonValue(parsed as JsonObject) as JsonObject;
}

export function stableObjectKeyList(input: Readonly<Record<string, unknown>>): readonly string[] {
  return Object.keys(input).sort((left, right) => left.localeCompare(right));
}

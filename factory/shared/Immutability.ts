import {
  JsonObject,
  JsonValue,
  assertJsonObject,
  canonicalizeJsonValue,
} from "./DeterministicJson";

type Primitive = string | number | boolean | null | undefined | symbol | bigint;

export type DeepReadonly<T> =
  T extends Primitive
    ? T
    : T extends readonly (infer U)[]
      ? readonly DeepReadonly<U>[]
      : T extends object
        ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
        : T;

function internalDeepFreeze<T>(value: T): DeepReadonly<T> {
  if (typeof value !== "object" || value === null) {
    return value as DeepReadonly<T>;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      internalDeepFreeze(item);
    }
    return Object.freeze(value) as DeepReadonly<T>;
  }

  const typedObject = value as Record<string, unknown>;
  const keys = Object.keys(typedObject);
  for (const key of keys) {
    internalDeepFreeze(typedObject[key]);
  }

  return Object.freeze(typedObject) as DeepReadonly<T>;
}

function cloneJsonArray(value: readonly JsonValue[]): readonly JsonValue[] {
  return value.map((entry) => cloneJsonValue(entry));
}

export function cloneJsonValue(value: JsonValue): JsonValue {
  if (value === null) {
    return null;
  }

  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return value;
  }

  if (Array.isArray(value)) {
    return cloneJsonArray(value);
  }

  const objectValue = value as JsonObject;
  const output: Record<string, JsonValue> = {};
  for (const key of Object.keys(objectValue)) {
    const child = objectValue[key];
    if (child === undefined) {
      throw new Error(`Missing key while cloning JSON object: ${key}`);
    }
    output[key] = cloneJsonValue(child);
  }
  return output;
}

export function cloneJsonObject(value: JsonObject): JsonObject {
  const cloned = cloneJsonValue(value);
  assertJsonObject(cloned, "cloneJsonObject");
  return cloned;
}

export function deepFreeze<T>(value: T): DeepReadonly<T> {
  return internalDeepFreeze(value);
}

export function cloneAndFreezeJsonObject(value: JsonObject): DeepReadonly<JsonObject> {
  const canonical = canonicalizeJsonValue(cloneJsonObject(value)) as JsonObject;
  return deepFreeze(canonical);
}

export function cloneAndFreezeJsonValue(value: JsonValue): DeepReadonly<JsonValue> {
  const canonical = canonicalizeJsonValue(cloneJsonValue(value));
  return deepFreeze(canonical);
}

export function deepReadonlyRecord<T extends string>(
  input: Readonly<Record<T, boolean>>,
): DeepReadonly<Readonly<Record<T, boolean>>> {
  const output: Record<T, boolean> = {} as Record<T, boolean>;
  for (const key of Object.keys(input).sort((left, right) => left.localeCompare(right))) {
    const typedKey = key as T;
    const value = input[typedKey];
    if (value === undefined) {
      throw new Error(`Missing boolean record entry for key ${typedKey}.`);
    }
    output[typedKey] = value;
  }
  return deepFreeze(output);
}

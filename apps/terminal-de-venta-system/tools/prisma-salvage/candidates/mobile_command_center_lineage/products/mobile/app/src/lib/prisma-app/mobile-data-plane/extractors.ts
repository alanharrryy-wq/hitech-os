import { centsFromUnknown, clampNonNegativeInt, clampInt } from "./money";

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

export function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export function pickRecord(value: unknown, ...keys: string[]): Record<string, unknown> {
  let current = asRecord(value);
  for (const key of keys) {
    const next = current[key];
    if (next && typeof next === "object" && !Array.isArray(next)) current = next as Record<string, unknown>;
  }
  return current;
}

export function pickArray(value: unknown, candidates: string[]): unknown[] {
  const root = asRecord(value);
  for (const key of candidates) {
    const direct = root[key];
    if (Array.isArray(direct)) return direct;
  }
  const data = asRecord(root.data);
  for (const key of candidates) {
    const fromData = data[key];
    if (Array.isArray(fromData)) return fromData;
  }
  return [];
}

export function readString(record: Record<string, unknown>, keys: string[], fallback = ""): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim().length > 0) return value.trim();
    if (typeof value === "number" && Number.isFinite(value)) return String(value);
  }
  return fallback;
}

export function readNumber(record: Record<string, unknown>, keys: string[], fallback = 0): number {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string" && value.trim().length > 0) {
      const parsed = Number.parseFloat(value.replace(/[$,\s]/g, ""));
      if (Number.isFinite(parsed)) return parsed;
    }
  }
  return fallback;
}

export function readInt(record: Record<string, unknown>, keys: string[], fallback = 0): number {
  for (const key of keys) {
    if (key in record) return clampInt(record[key], fallback);
  }
  return fallback;
}

export function readNonNegativeInt(record: Record<string, unknown>, keys: string[], fallback = 0): number {
  for (const key of keys) {
    if (key in record) return clampNonNegativeInt(record[key], fallback);
  }
  return fallback;
}

export function readCents(record: Record<string, unknown>, keys: string[], fallback = 0): number {
  for (const key of keys) {
    if (key in record) return centsFromUnknown(record[key]);
  }
  return fallback;
}

export function readDateIso(record: Record<string, unknown>, keys: string[], fallback = new Date().toISOString()): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string") {
      const parsed = Date.parse(value);
      if (Number.isFinite(parsed)) return new Date(parsed).toISOString();
    }
  }
  return fallback;
}

export function unwrapOkData(value: unknown): unknown {
  const root = asRecord(value);
  if (root.ok === true && "data" in root) return root.data;
  return value;
}

export function uniqueStable<T>(items: T[], key: (item: T) => string): T[] {
  const seen = new Set<string>();
  const out: T[] = [];
  for (const item of items) {
    const itemKey = key(item);
    if (seen.has(itemKey)) continue;
    seen.add(itemKey);
    out.push(item);
  }
  return out;
}

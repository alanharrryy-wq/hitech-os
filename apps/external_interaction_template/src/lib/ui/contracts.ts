import { z } from "zod";

export const uiToneSchema = z.enum(["default", "accent", "success", "warning", "danger"]);
export type UiTone = z.infer<typeof uiToneSchema>;

export const uiDensitySchema = z.enum(["compact", "comfortable", "spacious"]);
export type UiDensity = z.infer<typeof uiDensitySchema>;

export const uiMotionSchema = z.enum(["full", "reduced", "none"]);
export type UiMotion = z.infer<typeof uiMotionSchema>;

export const uiContrastSchema = z.enum(["normal", "more", "max"]);
export type UiContrast = z.infer<typeof uiContrastSchema>;

const genericDateSchema = z.union([z.date(), z.string(), z.number()]).optional();

export function sanitizeText(value: unknown, fallback = ""): string {
  if (typeof value !== "string") return fallback;
  const normalized = value.replace(/\s+/g, " ").trim();
  return normalized || fallback;
}

export function sanitizeOptionalText(value: unknown): string | undefined {
  const normalized = sanitizeText(value);
  return normalized || undefined;
}

export function toDisplayText(value: unknown, fallback = "-"): string {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "string") return sanitizeText(value, fallback);
  if (typeof value === "number" || typeof value === "bigint") return String(value);
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? fallback : value.toISOString();
  if (Array.isArray(value)) return value.length === 0 ? fallback : `${value.length} items`;
  if (typeof value === "object") {
    try {
      return JSON.stringify(value);
    } catch {
      return fallback;
    }
  }
  return fallback;
}

export function coerceDate(value: unknown): Date | undefined {
  const parsed = genericDateSchema.safeParse(value);
  if (!parsed.success || parsed.data === undefined) return undefined;
  const date = parsed.data instanceof Date ? parsed.data : new Date(parsed.data);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

export function sortByDateDesc<T>(items: readonly T[], getDate: (item: T) => unknown): T[] {
  return [...items].sort((left, right) => {
    const leftTime = coerceDate(getDate(left))?.getTime() ?? 0;
    const rightTime = coerceDate(getDate(right))?.getTime() ?? 0;
    return rightTime - leftTime;
  });
}

export function clampItems<T>(items: readonly T[], max: number): T[] {
  return [...items].slice(0, Math.max(0, max));
}

export function uniqueBy<T>(items: readonly T[], key: (item: T) => string): T[] {
  const seen = new Set<string>();
  const result: T[] = [];
  for (const item of items) {
    const id = key(item);
    if (seen.has(id)) continue;
    seen.add(id);
    result.push(item);
  }
  return result;
}

export function asArray<T>(value: readonly T[] | T[] | null | undefined): T[] {
  return Array.isArray(value) ? [...value] : [];
}

export function hasContent(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") return sanitizeText(value).length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

export function safeJson(value: unknown, spacing = 2): string {
  try {
    return JSON.stringify(value, null, spacing);
  } catch {
    return "{}";
  }
}

export function toneFromSeverity(value: unknown, fallback: UiTone = "default"): UiTone {
  return uiToneSchema.safeParse(value).success ? (value as UiTone) : fallback;
}

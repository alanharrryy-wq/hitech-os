import { normalizeUtcIso } from "./deterministic.ts";

export interface CoreClock {
  readonly source: "system" | "fixed";
  nowUtcIso(): string;
}

function normalizeOrNull(value: string | null | undefined): string | null {
  if (!value || value.trim().length === 0) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return normalizeUtcIso(parsed.toISOString());
}

export function createCoreClock(fixedNowUtc: string | null | undefined): CoreClock {
  const normalized = normalizeOrNull(fixedNowUtc);
  if (normalized) {
    return {
      source: "fixed",
      nowUtcIso: () => normalized
    };
  }

  return {
    source: "system",
    nowUtcIso: () => new Date().toISOString()
  };
}

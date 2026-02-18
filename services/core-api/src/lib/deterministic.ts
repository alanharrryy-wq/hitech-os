import { createHash } from "node:crypto";

export function deterministicJobId(jobId: string, kind: string): string {
  const source = `${jobId}|${kind}`;
  const hash = createHash("sha256").update(source).digest("hex");
  return `job_${hash.slice(0, 20)}`;
}

export function normalizeUtcIso(value: string): string {
  const asDate = new Date(value);
  if (Number.isNaN(asDate.getTime())) {
    return new Date(0).toISOString();
  }

  return asDate.toISOString();
}

export function stableSortObject<T extends Record<string, unknown>>(input: T): T {
  const sorted = Object.keys(input)
    .sort((left, right) => left.localeCompare(right))
    .reduce((accumulator, key) => {
      const value = input[key];
      if (Array.isArray(value)) {
        accumulator[key] = value.map((item) =>
          typeof item === "object" && item !== null ? stableSortObject(item as Record<string, unknown>) : item
        );
      } else if (typeof value === "object" && value !== null) {
        accumulator[key] = stableSortObject(value as Record<string, unknown>);
      } else {
        accumulator[key] = value;
      }
      return accumulator;
    }, {} as Record<string, unknown>);

  return sorted as T;
}

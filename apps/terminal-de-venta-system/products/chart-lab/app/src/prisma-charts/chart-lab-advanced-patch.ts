// PRISMA_CHART_LAB_ADVANCED_PATCH_V3
export type ChartLabAdvancedPatchValidation = {
  ok: boolean;
  patch: Record<string, unknown>;
  warnings: string[];
  errors: string[];
};

const blockedKeys = new Set(["__proto__", "prototype", "constructor"]);
const riskyFormatterKeys = new Set(["formatter", "renderItem"]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function sanitize(value: unknown, path: string, warnings: string[], errors: string[]): unknown {
  if (Array.isArray(value)) return value.map((item, index) => sanitize(item, `${path}[${index}]`, warnings, errors));
  if (!isRecord(value)) {
    if (typeof value === "function") errors.push(`Function value is not allowed at ${path}`);
    return value;
  }
  const next: Record<string, unknown> = {};
  for (const [key, raw] of Object.entries(value)) {
    const childPath = path ? `${path}.${key}` : key;
    if (blockedKeys.has(key)) {
      errors.push(`Blocked unsafe key: ${childPath}`);
      continue;
    }
    if (riskyFormatterKeys.has(key) && typeof raw === "string" && /=>|function\s*\(|new Function|eval\s*\(/.test(raw)) {
      warnings.push(`Formatter-like string retained as data only at ${childPath}; runtime execution is not allowed by this patch validator.`);
    }
    next[key] = sanitize(raw, childPath, warnings, errors);
  }
  return next;
}

function deepMerge(base: Record<string, unknown>, patch: Record<string, unknown>): Record<string, unknown> {
  const next: Record<string, unknown> = { ...base };
  for (const [key, value] of Object.entries(patch)) {
    const existing = next[key];
    next[key] = isRecord(existing) && isRecord(value) ? deepMerge(existing, value) : value;
  }
  return next;
}

export function validateChartLabAdvancedPatch(rawPatch: unknown): ChartLabAdvancedPatchValidation {
  const warnings: string[] = [];
  const errors: string[] = [];
  const patch = isRecord(rawPatch) ? (sanitize(rawPatch, "", warnings, errors) as Record<string, unknown>) : {};
  if (!isRecord(rawPatch)) errors.push("Advanced patch must be a JSON object.");
  return { ok: errors.length === 0, patch, warnings, errors };
}

export function parseChartLabAdvancedPatch(raw: string): ChartLabAdvancedPatchValidation {
  try {
    return validateChartLabAdvancedPatch(JSON.parse(raw));
  } catch (error) {
    return { ok: false, patch: {}, warnings: [], errors: [`Invalid JSON: ${error instanceof Error ? error.message : String(error)}`] };
  }
}

export function applyChartLabAdvancedPatch(option: Record<string, unknown>, rawPatch: unknown): ChartLabAdvancedPatchValidation & { option: Record<string, unknown> } {
  const validation = validateChartLabAdvancedPatch(rawPatch);
  return { ...validation, option: validation.ok ? deepMerge(option, validation.patch) : option };
}

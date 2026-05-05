import type { LicenseDocument } from "./license-types";

export type LicenseSchemaResult =
  | { ok: true; value: LicenseDocument }
  | { ok: false; issues: string[] };

const VALID_PLANS = new Set(["TABLET_SOLO", "TABLET_PRO", "TABLET_PC_REQUIRED", "DEVELOPMENT"]);
const VALID_STATES = new Set(["active", "suspended", "revoked", "development"]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isIsoDateLike(value: unknown): value is string {
  return typeof value === "string" && !Number.isNaN(Date.parse(value));
}

export function validateLicenseDocument(value: unknown): LicenseSchemaResult {
  const issues: string[] = [];
  if (!isRecord(value)) return { ok: false, issues: ["license must be an object"] };

  const required = ["schemaVersion", "licenseId", "customerId", "businessId", "plan", "state", "validFrom", "validUntil"];
  for (const key of required) {
    if (!(key in value)) issues.push(`missing required field: ${key}`);
  }

  if (typeof value.schemaVersion !== "string") issues.push("schemaVersion must be a string");
  if (typeof value.licenseId !== "string") issues.push("licenseId must be a string");
  if (typeof value.customerId !== "string") issues.push("customerId must be a string");
  if (typeof value.businessId !== "string") issues.push("businessId must be a string");
  if (typeof value.plan !== "string" || !VALID_PLANS.has(value.plan)) issues.push("plan is not supported");
  if (typeof value.state !== "string" || !VALID_STATES.has(value.state)) issues.push("state is not supported");
  if (!isIsoDateLike(value.validFrom)) issues.push("validFrom must be an ISO date string");
  if (!isIsoDateLike(value.validUntil)) issues.push("validUntil must be an ISO date string");
  if ("issuedAt" in value && value.issuedAt !== undefined && !isIsoDateLike(value.issuedAt)) issues.push("issuedAt must be an ISO date string");
  if ("offlineGraceDays" in value && value.offlineGraceDays !== undefined && (typeof value.offlineGraceDays !== "number" || value.offlineGraceDays < 0)) issues.push("offlineGraceDays must be a non-negative number");
  if ("features" in value && value.features !== undefined && !isRecord(value.features)) issues.push("features must be an object when present");
  if ("limits" in value && value.limits !== undefined && !isRecord(value.limits)) issues.push("limits must be an object when present");
  if ("notes" in value && value.notes !== undefined && !Array.isArray(value.notes)) issues.push("notes must be an array when present");

  if (issues.length > 0) return { ok: false, issues };
  return { ok: true, value: value as LicenseDocument };
}

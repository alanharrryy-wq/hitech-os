export const LICENSE_ERROR_CODES = {
  MISSING: "LICENSE_MISSING",
  INVALID_JSON: "LICENSE_INVALID_JSON",
  INVALID_SCHEMA: "LICENSE_INVALID_SCHEMA",
  EXPIRED: "LICENSE_EXPIRED",
  SUSPENDED: "LICENSE_SUSPENDED",
  REVOKED: "LICENSE_REVOKED",
  FEATURE_DENIED: "LICENSE_FEATURE_DENIED"
} as const;

export class LicenseRuntimeError extends Error {
  readonly code: string;
  readonly details: Record<string, unknown>;

  constructor(code: string, message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.name = "LicenseRuntimeError";
    this.code = code;
    this.details = details;
  }
}

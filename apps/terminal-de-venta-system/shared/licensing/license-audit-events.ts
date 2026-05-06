export const LICENSE_AUDIT_EVENTS = [
  "license.loaded",
  "license.missing",
  "license.invalid",
  "license.expired",
  "license.grace_started",
  "license.feature_allowed",
  "license.feature_denied",
  "license.enforcement_soft_denied",
  "license.enforcement_hard_denied"
] as const;

export type LicenseAuditEvent = (typeof LICENSE_AUDIT_EVENTS)[number];

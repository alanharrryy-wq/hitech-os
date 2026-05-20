import type { LicenseAssignmentState, LicenseDenialReason, LicenseDocument, LicenseOperationalDecision, LicenseSource, NormalizedLicenseStatus, NormalizedLicenseState } from "./license-types";

const DAY_MS = 24 * 60 * 60 * 1000;

function daysBetween(from: Date, to: Date): number {
  return Math.ceil((to.getTime() - from.getTime()) / DAY_MS);
}

function calculateState(document: LicenseDocument, now: Date): NormalizedLicenseState {
  if (document.state === "development") return "development";
  if (document.state === "suspended") return "suspended";
  if (document.state === "revoked") return "revoked";

  const validUntil = new Date(document.validUntil);
  if (validUntil.getTime() >= now.getTime()) return "active";

  const graceDays = Math.max(0, document.offlineGraceDays ?? 0);
  const graceUntil = new Date(validUntil.getTime() + graceDays * DAY_MS);
  return graceUntil.getTime() >= now.getTime() ? "offline_grace" : "expired";
}

function assignmentState(document: LicenseDocument): LicenseAssignmentState {
  return document.assignmentState ?? "assigned";
}

function denialReason(state: NormalizedLicenseState, assignment: LicenseAssignmentState): LicenseDenialReason | null {
  if (assignment === "unassigned") return "device_unassigned";
  if (assignment === "wrong_business") return "wrong_business";
  if (assignment === "wrong_store") return "wrong_store";
  if (assignment === "wrong_device") return "wrong_device";
  if (assignment === "wrong_terminal") return "wrong_terminal";
  if (assignment === "exceeded_limit") return "limit_exceeded";
  if (state === "invalid") return "license_invalid";
  if (state === "missing") return "license_missing";
  if (state === "expired") return "license_expired";
  if (state === "suspended") return "license_suspended";
  if (state === "revoked") return "license_revoked";
  return null;
}

function operationalDecision(state: NormalizedLicenseState, assignment: LicenseAssignmentState): LicenseOperationalDecision {
  if (["unassigned", "wrong_business", "wrong_store", "wrong_device", "wrong_terminal", "exceeded_limit"].includes(assignment)) return "deny";
  if (state === "invalid" || state === "revoked") return "deny";
  if (state === "missing" || state === "expired" || state === "suspended") return "degrade";
  if (state === "offline_grace") return "allow_with_warning";
  return "allow";
}

export function normalizeLicenseDocument(document: LicenseDocument, options: { source: LicenseSource; path: string | null; now?: Date }): NormalizedLicenseStatus {
  const now = options.now ?? new Date();
  const validUntil = new Date(document.validUntil);
  const state = calculateState(document, now);
  const daysRemaining = state === "expired" ? 0 : daysBetween(now, validUntil);
  const warnings = [];
  const assignment = assignmentState(document);
  const reason = denialReason(state, assignment);
  const decision = operationalDecision(state, assignment);

  if (state === "offline_grace") warnings.push({ code: "LICENSE_OFFLINE_GRACE", message: "La licencia venció, pero está dentro del periodo de gracia." });
  if (state === "expired") warnings.push({ code: "LICENSE_EXPIRED", message: "La licencia está vencida." });
  if (state === "suspended") warnings.push({ code: "LICENSE_SUSPENDED", message: "La licencia está suspendida." });
  if (state === "revoked") warnings.push({ code: "LICENSE_REVOKED", message: "La licencia fue revocada." });
  if (assignment !== "assigned" && assignment !== "unknown") warnings.push({ code: `LICENSE_ASSIGNMENT_${assignment.toUpperCase()}`, message: "La licencia no está asignada correctamente a este cliente, negocio, tienda o terminal." });

  return {
    ok: decision === "allow" || decision === "allow_with_warning",
    state,
    plan: document.plan,
    customerId: document.customerId,
    businessId: document.businessId,
    storeId: document.storeId ?? null,
    branchId: document.branchId ?? document.storeId ?? null,
    deviceId: document.deviceId ?? document.tabletId ?? null,
    tabletId: document.tabletId ?? document.deviceId ?? null,
    terminalId: document.terminalId ?? null,
    licenseId: document.licenseId,
    assignmentState: assignment,
    validFrom: document.validFrom,
    validUntil: document.validUntil,
    issuedAt: document.issuedAt ?? null,
    capabilities: { ...(document.features ?? {}), ...(document.capabilities ?? {}) },
    limits: document.limits ?? {},
    lastSeenAt: document.lastSeenAt ?? null,
    lastRefreshAt: document.lastRefreshAt ?? null,
    lastDecisionAt: now.toISOString(),
    denialReason: reason,
    evidenceEvent: {
      topic: reason ? "license.decision.denied_or_degraded" : "license.decision.allowed",
      occurredAt: now.toISOString(),
      source: "local_license",
      customerId: document.customerId,
      businessId: document.businessId,
      storeId: document.storeId ?? null,
      deviceId: document.deviceId ?? document.tabletId ?? null,
      terminalId: document.terminalId ?? null,
      licenseId: document.licenseId,
      reason
    },
    operationalDecision: decision,
    offlineGraceDays: document.offlineGraceDays ?? 0,
    daysRemaining,
    source: options.source,
    path: options.path,
    warnings,
    raw: document
  };
}

export function missingLicenseStatus(path: string | null): NormalizedLicenseStatus {
  const now = new Date().toISOString();
  return {
    ok: false,
    state: "missing",
    plan: "TABLET_SOLO_FALLBACK",
    customerId: null,
    businessId: null,
    storeId: null,
    branchId: null,
    deviceId: null,
    tabletId: null,
    terminalId: null,
    licenseId: null,
    assignmentState: "unassigned",
    validFrom: null,
    validUntil: null,
    issuedAt: null,
    capabilities: {},
    limits: {},
    lastSeenAt: null,
    lastRefreshAt: null,
    lastDecisionAt: now,
    denialReason: "license_missing",
    evidenceEvent: {
      topic: "license.missing",
      occurredAt: now,
      source: "fallback_policy",
      customerId: null,
      businessId: null,
      storeId: null,
      deviceId: null,
      terminalId: null,
      licenseId: null,
      reason: "license_missing"
    },
    operationalDecision: "degrade",
    offlineGraceDays: 0,
    daysRemaining: null,
    source: "missing_license",
    path,
    warnings: [{ code: "LICENSE_MISSING", message: "No se encontró licencia local. La venta básica sigue disponible en modo limitado." }]
  };
}

export function invalidLicenseStatus(path: string | null, issues: string[]): NormalizedLicenseStatus {
  const now = new Date().toISOString();
  return {
    ok: false,
    state: "invalid",
    plan: "TABLET_SOLO_FALLBACK",
    customerId: null,
    businessId: null,
    storeId: null,
    branchId: null,
    deviceId: null,
    tabletId: null,
    terminalId: null,
    licenseId: null,
    assignmentState: "unknown",
    validFrom: null,
    validUntil: null,
    issuedAt: null,
    capabilities: {},
    limits: {},
    lastSeenAt: null,
    lastRefreshAt: null,
    lastDecisionAt: now,
    denialReason: "license_invalid",
    evidenceEvent: {
      topic: "license.invalid",
      occurredAt: now,
      source: "local_license",
      customerId: null,
      businessId: null,
      storeId: null,
      deviceId: null,
      terminalId: null,
      licenseId: null,
      reason: "license_invalid"
    },
    operationalDecision: "deny",
    offlineGraceDays: 0,
    daysRemaining: null,
    source: "invalid_license",
    path,
    warnings: [{ code: "LICENSE_INVALID", message: issues.join("; ") }]
  };
}

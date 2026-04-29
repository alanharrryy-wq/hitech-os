import type { LicenseDocument, LicenseSource, NormalizedLicenseStatus, NormalizedLicenseState } from "./license-types";

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

export function normalizeLicenseDocument(document: LicenseDocument, options: { source: LicenseSource; path: string | null; now?: Date }): NormalizedLicenseStatus {
  const now = options.now ?? new Date();
  const validUntil = new Date(document.validUntil);
  const state = calculateState(document, now);
  const daysRemaining = state === "expired" ? 0 : daysBetween(now, validUntil);
  const warnings = [];

  if (state === "offline_grace") warnings.push({ code: "LICENSE_OFFLINE_GRACE", message: "La licencia venció, pero está dentro del periodo de gracia." });
  if (state === "expired") warnings.push({ code: "LICENSE_EXPIRED", message: "La licencia está vencida." });
  if (state === "suspended") warnings.push({ code: "LICENSE_SUSPENDED", message: "La licencia está suspendida." });
  if (state === "revoked") warnings.push({ code: "LICENSE_REVOKED", message: "La licencia fue revocada." });

  return {
    ok: state === "active" || state === "development" || state === "offline_grace",
    state,
    plan: document.plan,
    customerId: document.customerId,
    businessId: document.businessId,
    licenseId: document.licenseId,
    validFrom: document.validFrom,
    validUntil: document.validUntil,
    issuedAt: document.issuedAt ?? null,
    offlineGraceDays: document.offlineGraceDays ?? 0,
    daysRemaining,
    source: options.source,
    path: options.path,
    warnings,
    raw: document
  };
}

export function missingLicenseStatus(path: string | null): NormalizedLicenseStatus {
  return {
    ok: false,
    state: "missing",
    plan: "TABLET_SOLO_FALLBACK",
    customerId: null,
    businessId: null,
    licenseId: null,
    validFrom: null,
    validUntil: null,
    issuedAt: null,
    offlineGraceDays: 0,
    daysRemaining: null,
    source: "missing_license",
    path,
    warnings: [{ code: "LICENSE_MISSING", message: "No se encontró licencia local. La venta básica sigue disponible en modo limitado." }]
  };
}

export function invalidLicenseStatus(path: string | null, issues: string[]): NormalizedLicenseStatus {
  return {
    ok: false,
    state: "invalid",
    plan: "TABLET_SOLO_FALLBACK",
    customerId: null,
    businessId: null,
    licenseId: null,
    validFrom: null,
    validUntil: null,
    issuedAt: null,
    offlineGraceDays: 0,
    daysRemaining: null,
    source: "invalid_license",
    path,
    warnings: [{ code: "LICENSE_INVALID", message: issues.join("; ") }]
  };
}

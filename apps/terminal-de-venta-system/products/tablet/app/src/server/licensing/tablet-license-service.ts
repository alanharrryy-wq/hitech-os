import { FEATURE_KEYS, getLicenseGovernorSnapshot } from "../../../../../../shared/licensing";
import type { FeatureResolution, LicenseGovernorSnapshot, NormalizedLicenseStatus } from "../../../../../../shared/licensing";

export type TabletLicenseReadiness = {
  state: "ready" | "warning" | "blocked";
  label: string;
  blockers: string[];
  warnings: string[];
  features: { allowed: number; blocked: number; posOpenAllowed: boolean | null };
  deviceScope: {
    documentedLimit: number | null;
    authorizedTabletDevices: number;
    currentDeviceAuthorization: "confirmed" | "not_confirmed" | "not_assessable";
    claimState: "not_projected";
    note: string;
  };
  handoff: { code: string; evidenceTopic: string; recordedAt: string; nextStep: string; delivery: "local_evidence_only" };
};

export function getTabletLicenseStatus(): NormalizedLicenseStatus {
  return getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: getTabletFeatureKeys() }).status;
}

export function resolveTabletFeature(featureKey: string): FeatureResolution {
  return getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: [featureKey] }).decisions[0];
}

export function getTabletFeatureList(): FeatureResolution[] {
  return getTabletLicenseGovernor().decisions;
}

export function getTabletLicenseGovernor(): LicenseGovernorSnapshot {
  return getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: getTabletFeatureKeys() });
}

export function getTabletLicenseReadiness(): TabletLicenseReadiness {
  const governor = getTabletLicenseGovernor();
  const { status, decisions } = governor;
  const blockers: string[] = [];
  const warnings = status.warnings.map((warning) => warning.message);
  const posOpen = decisions.find((decision) => decision.key === "pos.open");
  const allowed = decisions.filter((decision) => decision.allowed).length;
  const blocked = decisions.length - allowed;
  const documentedLimit = status.limits.maxTabletDevices ?? status.limits.maxDevices ?? null;
  const authorizedTabletDevices = status.authorizedDevices.filter((device) => device.role === "tablet").length;
  const currentDeviceAuthorization = status.deviceId
    ? status.authorizedDevices.some((device) => device.role === "tablet" && device.deviceId === status.deviceId)
      ? "confirmed"
      : "not_confirmed"
    : "not_assessable";

  if (status.operationalDecision === "deny") blockers.push(`La decisión operativa de licencia es ${status.operationalDecision}.`);
  if (status.assignmentState !== "assigned" && status.assignmentState !== "unknown") blockers.push(`La asignación del dispositivo está en estado ${status.assignmentState}.`);
  if (posOpen && !posOpen.allowed) blockers.push("La capacidad pos.open está bloqueada por la licencia actual.");
  if (blocked > 0 && blockers.length === 0) warnings.push(`${blocked} capacidad(es) Tablet están restringidas por el plan o el estado actual.`);
  if (documentedLimit === null) warnings.push("El documento de licencia no declara un límite específico de Tablets.");

  const state = blockers.length > 0 ? "blocked" : warnings.length > 0 || status.operationalDecision !== "allow" ? "warning" : "ready";
  const label = state === "ready" ? "Listo para operar" : state === "warning" ? "Operable con avisos" : "Bloqueado por licencia";
  const code = status.raw?.activation?.supportCode || status.denialReason || (status.warnings[0]?.code ?? "OK");

  return {
    state,
    label,
    blockers,
    warnings,
    features: { allowed, blocked, posOpenAllowed: posOpen?.allowed ?? null },
    deviceScope: {
      documentedLimit,
      authorizedTabletDevices,
      currentDeviceAuthorization,
      claimState: "not_projected",
      note: "El límite y los dispositivos autorizados se leen del documento local; los claims durables se consultan en Customer Setup mediante el Cloud License Gateway."
    },
    handoff: {
      code,
      evidenceTopic: status.evidenceEvent.topic,
      recordedAt: status.lastDecisionAt,
      nextStep: blockers.length > 0
        ? "Conserva este código y la evidencia local para el flujo de soporte autorizado."
        : "No requiere handoff mientras la decisión permanezca operable.",
      delivery: "local_evidence_only"
    }
  };
}

function getTabletFeatureKeys(): string[] {
  return FEATURE_KEYS.filter((key) => key.startsWith("pos.") || key.startsWith("shift.") || key.startsWith("inventory.local") || key.startsWith("event.") || key.startsWith("export.") || key.startsWith("report."));
}

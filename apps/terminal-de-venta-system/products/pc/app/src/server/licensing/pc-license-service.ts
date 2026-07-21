// PRISMA_PRICING_OWNER_V1
import { FEATURE_KEYS, getLicenseGovernorSnapshot } from "../../../../../../shared/licensing";
import type { FeatureResolution, LicenseGovernorSnapshot, NormalizedLicenseStatus } from "../../../../../../shared/licensing";

export type PcLicenseReadiness = {
  state: "ready" | "warning" | "blocked";
  label: string;
  blockers: string[];
  warnings: string[];
  features: {
    allowed: number;
    blocked: number;
    pcOpenAllowed: boolean | null;
  };
  deviceScope: {
    documentedLimit: number | null;
    authorizedPcDevices: number;
    currentDeviceAuthorization: "confirmed" | "not_confirmed" | "not_assessable";
    claimState: "not_projected";
    note: string;
  };
  handoff: {
    code: string;
    evidenceTopic: string;
    recordedAt: string;
    nextStep: string;
    delivery: "local_evidence_only";
  };
};

function getPcFeatureKeys(): string[] {
  return FEATURE_KEYS.filter((key) => key.startsWith("pc.") || key.startsWith("sync.") || key.startsWith("catalog.") || key.startsWith("pricing.") || key.startsWith("stock.") || key.startsWith("inventory.") || key.startsWith("purchase.") || key.startsWith("receiving.") || key.startsWith("replenishment.") || key.startsWith("audit.") || key.startsWith("export.") || key.startsWith("multi.") || key.startsWith("forecast.") || key.startsWith("advanced."));
}

export function getPcLicenseGovernor(): LicenseGovernorSnapshot {
  return getLicenseGovernorSnapshot({ surface: "pc", featureKeys: getPcFeatureKeys() });
}

export function getPcLicenseStatus(): NormalizedLicenseStatus {
  return getPcLicenseGovernor().status;
}

function supportIssueCode(status: NormalizedLicenseStatus) {
  const reason = status.denialReason || status.assignmentState;
  const codes: Record<string, string> = {
    license_missing: "LICENSE_LOCAL_MISSING",
    license_invalid: "LICENSE_LOCAL_INVALID",
    license_expired: "LICENSE_EXPIRED",
    license_suspended: "LICENSE_LOCAL_INVALID",
    license_revoked: "LICENSE_LOCAL_INVALID",
    wrong_customer: "LICENSE_ASSIGNMENT_WRONG_CUSTOMER",
    wrong_business: "LICENSE_ASSIGNMENT_WRONG_BUSINESS",
    wrong_store: "LICENSE_ASSIGNMENT_WRONG_STORE",
    wrong_device: "PC_DEVICE_ASSIGNMENT_MISMATCH",
    wrong_terminal: "LICENSE_ASSIGNMENT_WRONG_TERMINAL",
    feature_not_entitled: "PC_FEATURES_BLOCKED_BY_LICENSE",
    device_unassigned: "PC_ADMIN_SLOT_NOT_CLAIMED",
    limit_exceeded: "PC_DEVICE_LIMIT_EXCEEDED"
  };

  if (status.operationalDecision === "deny") return codes[reason || ""] || "PC_SUPPORT_STATUS_CONTRADICTION";
  if (status.warnings.length > 0) return status.warnings[0]?.code || "PC_SUPPORT_STATUS_CONTRADICTION";
  return "OK";
}

export function getPcLicenseReadiness(): PcLicenseReadiness {
  const governor = getPcLicenseGovernor();
  const { status, decisions } = governor;
  const blockers: string[] = [];
  const warnings = status.warnings.map((warning) => warning.message);
  const pcOpen = decisions.find((decision) => decision.key === "pc.open");
  const allowed = decisions.filter((decision) => decision.allowed).length;
  const blocked = decisions.length - allowed;
  const documentedLimit = status.limits.maxPcDevices ?? status.limits.maxDevices ?? null;
  const authorizedPcDevices = status.authorizedDevices.filter((device) => device.role === "pc").length;
  const currentDeviceAuthorization = status.deviceId
    ? status.authorizedDevices.some((device) => device.role === "pc" && device.deviceId === status.deviceId)
      ? "confirmed"
      : "not_confirmed"
    : "not_assessable";

  if (status.operationalDecision === "deny") {
    blockers.push(`La decisión operativa de licencia es ${status.operationalDecision}.`);
  }
  if (status.assignmentState !== "assigned" && status.assignmentState !== "unknown") {
    blockers.push(`La asignación del dispositivo está en estado ${status.assignmentState}.`);
  }
  if (pcOpen && !pcOpen.allowed) {
    blockers.push("La capacidad pc.open está bloqueada por la licencia actual.");
  }
  if (blocked > 0 && blockers.length === 0) {
    warnings.push(`${blocked} capacidad(es) PC están restringidas por el plan o el estado actual.`);
  }
  if (documentedLimit === null) {
    warnings.push("El documento de licencia no declara un límite específico de dispositivos PC.");
  }

  const state = blockers.length > 0 ? "blocked" : warnings.length > 0 || status.operationalDecision !== "allow" ? "warning" : "ready";
  const label = state === "ready" ? "Listo para operar" : state === "warning" ? "Operable con avisos" : "Bloqueado por licencia";
  const issueCode = status.raw?.activation?.supportCode || supportIssueCode(status);

  return {
    state,
    label,
    blockers,
    warnings,
    features: {
      allowed,
      blocked,
      pcOpenAllowed: pcOpen?.allowed ?? null
    },
    deviceScope: {
      documentedLimit,
      authorizedPcDevices,
      currentDeviceAuthorization,
      claimState: "not_projected",
      note: "El límite y los dispositivos autorizados se leen del documento local; los claims durables se consultan en Customer Setup mediante el Cloud License Gateway."
    },
    handoff: {
      code: issueCode,
      evidenceTopic: status.evidenceEvent.topic,
      recordedAt: status.lastDecisionAt,
      nextStep: blockers.length > 0
        ? "Conserva este código y la evidencia local para el flujo de soporte autorizado."
        : "No requiere handoff mientras la decisión permanezca operable.",
      delivery: "local_evidence_only"
    }
  };
}

export function resolvePcFeature(featureKey: string): FeatureResolution {
  return getLicenseGovernorSnapshot({ surface: "pc", featureKeys: [featureKey] }).decisions[0];
}

export function getPcFeatureList(): FeatureResolution[] {
  return getPcLicenseGovernor().decisions;
}

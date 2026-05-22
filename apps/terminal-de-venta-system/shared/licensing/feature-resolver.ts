import { BASIC_POS_FEATURES } from "./feature-keys";
import { planIncludesFeature, requiredPlanForFeature } from "./plan-catalog";
import type { FeatureResolution, LicenseFeatureSource, LicensePlan, NormalizedLicenseStatus } from "./license-types";

function allowedResolution(status: NormalizedLicenseStatus, key: string, source: LicenseFeatureSource, reason: string): FeatureResolution {
  return {
    key,
    allowed: true,
    enforcement: status.warnings.length ? "warn" : "allow",
    reason,
    source,
    plan: status.plan,
    state: status.state,
    saleBasicsStillAvailable: true,
    assignmentState: status.assignmentState,
    denialReason: null,
    evidenceEvent: {
      ...status.evidenceEvent,
      topic: "license.feature.allowed",
      source: source === "fallback_policy" ? "fallback_policy" : "feature_gate",
      reason
    },
    operationalDecision: status.operationalDecision,
    warnings: status.warnings
  };
}

function deniedResolution(status: NormalizedLicenseStatus, key: string, reason: string, enforcement: "soft_deny" | "hard_deny" = "soft_deny"): FeatureResolution {
  const denialReason = status.denialReason ?? "feature_not_entitled";
  return {
    key,
    allowed: false,
    enforcement,
    reason,
    source: status.state === "missing" ? "missing_license" : status.state === "invalid" ? "invalid_license" : "license",
    plan: status.plan,
    state: status.state,
    requiredPlan: requiredPlanForFeature(key),
    saleBasicsStillAvailable: status.operationalDecision !== "deny",
    assignmentState: status.assignmentState,
    denialReason,
    evidenceEvent: {
      ...status.evidenceEvent,
      topic: "license.feature.denied",
      source: "feature_gate",
      reason: denialReason
    },
    operationalDecision: status.operationalDecision === "allow" ? "deny" : status.operationalDecision,
    warnings: status.warnings
  };
}

export function resolveFeature(status: NormalizedLicenseStatus, key: string): FeatureResolution {
  const rawOverrides = status.raw?.features ?? {};
  const capabilityOverrides = status.capabilities ?? {};

  if (status.state === "missing") {
    if (BASIC_POS_FEATURES.has(key)) return allowedResolution(status, key, "fallback_policy", "Venta básica permitida por política de continuidad.");
    return deniedResolution(status, key, "La licencia local no está disponible o es inválida. Funciones avanzadas desactivadas.");
  }

  if (["unassigned", "wrong_business", "wrong_store", "wrong_device", "wrong_terminal", "exceeded_limit"].includes(status.assignmentState)) {
    return deniedResolution(status, key, "Equipo no asignado correctamente a esta licencia. Revisa cliente, negocio, tienda y terminal.", "hard_deny");
  }

  if (status.state === "invalid") {
    return deniedResolution(status, key, "Licencia inválida o alterada. Revisa diagnóstico antes de operar.", "hard_deny");
  }

  if (status.state === "revoked") {
    return deniedResolution(status, key, "Licencia revocada. Revisa soporte y evidencia de activación.", "hard_deny");
  }

  if (capabilityOverrides[key] === true) return allowedResolution(status, key, "license", "Capacidad habilitada explícitamente por la licencia local.");
  if (capabilityOverrides[key] === false) return deniedResolution(status, key, "Capacidad deshabilitada explícitamente por la licencia local.");
  if (rawOverrides[key] === true) return allowedResolution(status, key, "license", "Feature habilitada explícitamente por la licencia local.");
  if (rawOverrides[key] === false) return deniedResolution(status, key, "Feature deshabilitada explícitamente por la licencia local.");

  if (status.state === "development") return allowedResolution(status, key, "license", "Modo development habilita esta función.");

  if (status.state === "suspended") {
    if (BASIC_POS_FEATURES.has(key)) return allowedResolution(status, key, "fallback_policy", "Modo emergencia: la venta básica sigue disponible, funciones avanzadas quedan bloqueadas.");
    return deniedResolution(status, key, `Licencia ${status.state}. Funciones avanzadas bloqueadas.`, "hard_deny");
  }

  if (status.state === "expired") {
    if (BASIC_POS_FEATURES.has(key)) return allowedResolution(status, key, "fallback_policy", "Licencia expirada: venta básica permitida en modo limitado.");
    return deniedResolution(status, key, "La licencia expiró y la función avanzada queda bloqueada.");
  }

  if (status.state === "offline_grace") {
    if (BASIC_POS_FEATURES.has(key)) return allowedResolution(status, key, "fallback_policy", "Periodo de gracia: venta básica permitida.");
    if (planIncludesFeature(status.plan, key)) return allowedResolution(status, key, "license", "Función incluida, operando en periodo de gracia.");
    return deniedResolution(status, key, "La función no está incluida en el plan actual.");
  }

  if (planIncludesFeature(status.plan, key)) return allowedResolution(status, key, "license", `Función incluida en ${status.plan}.`);
  return deniedResolution(status, key, `La función requiere ${requiredPlanForFeature(key) ?? "un plan superior"}.`);
}

export function resolveFeatures(status: NormalizedLicenseStatus, keys: string[]): FeatureResolution[] {
  return keys.map((key) => resolveFeature(status, key));
}

export function minimumPlanForFeature(key: string): LicensePlan | undefined {
  return requiredPlanForFeature(key);
}

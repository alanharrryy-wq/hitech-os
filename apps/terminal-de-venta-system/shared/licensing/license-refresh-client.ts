import { canonicalJson } from "./canonical-json";
import { getLicenseRefreshConfig } from "./license-refresh-config";
import { defaultRefreshState, type LicenseRefreshResult, type LicenseRefreshState } from "./license-refresh-state";
import { readLicenseRefreshState, writeLicenseAtomically, writeLicenseRefreshState } from "./local-license-store";
import { loadLocalLicense } from "./license-loader";
import { isSignedLicenseEnvelope } from "./signed-license-types";
import { validateSignedLicenseEnvelope, verifySignedLicenseEnvelope } from "./license-signature";

function statusFromLocal(enabled: boolean): LicenseRefreshState {
  const persisted = readLicenseRefreshState(enabled);
  const local = loadLocalLicense();
  const nextState = local.state === "offline_grace" ? "offline_grace" : local.state === "revoked" ? "revoked" : local.state === "suspended" ? "suspended" : persisted.state;
  return {
    ...persisted,
    enabled,
    state: nextState,
    configurationState: enabled ? "configured" : "refresh_disabled",
    operationalDecision: nextState === "revoked" || nextState === "suspended" ? "license_blocking" : "refresh_available",
    licenseId: local.licenseId,
    plan: local.plan
  };
}

export function getLicenseRefreshStatus(): LicenseRefreshState {
  const config = getLicenseRefreshConfig();
  if (!config.enabled) return { ...defaultRefreshState(false), ...readLicenseRefreshState(false), enabled: false, state: "refresh_disabled", configurationState: "refresh_disabled", operationalDecision: "informational" };
  if (!config.serverUrl || !config.deviceId) {
    const local = loadLocalLicense();
    return {
      ...defaultRefreshState(false),
      enabled: true,
      state: "refresh_disabled",
      configurationState: !config.serverUrl ? "missing_server_url" : "missing_device_id",
      operationalDecision: "informational",
      licenseId: local.licenseId,
      plan: local.plan
    };
  }
  return statusFromLocal(true);
}

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

export async function refreshLocalLicenseFromRemote(): Promise<LicenseRefreshResult> {
  const config = getLicenseRefreshConfig();
  if (!config.enabled || !config.serverUrl || !config.deviceId) {
    const status: LicenseRefreshState = {
      ...defaultRefreshState(false),
      state: "refresh_disabled",
      enabled: config.enabled,
      configurationState: !config.enabled ? "refresh_disabled" : !config.serverUrl ? "missing_server_url" : "missing_device_id",
      operationalDecision: "informational"
    };
    writeLicenseRefreshState(status);
    return { ok: true, state: "refresh_disabled", message: "Refresh remoto no configurado. La operación local continúa si la licencia local es válida.", status };
  }

  const startedAt = new Date().toISOString();
  const current = loadLocalLicense();
  const previous = readLicenseRefreshState(true);
  writeLicenseRefreshState({ ...previous, enabled: true, lastRefreshAt: startedAt, source: "remote", licenseId: current.licenseId, plan: current.plan });

  try {
    const response = await fetchWithTimeout(`${config.serverUrl}/licenses/refresh`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        deviceId: config.deviceId,
        licenseId: current.licenseId,
        customerId: current.customerId,
        businessId: current.businessId,
        plan: current.plan,
        state: current.state
      })
    }, config.timeoutMs);

    if (!response.ok) throw new Error(`HTTP_${response.status}`);
    const body = await response.json() as unknown;
    const envelope = isSignedLicenseEnvelope(body) ? body : isSignedLicenseEnvelope((body as { license?: unknown }).license) ? (body as { license: unknown }).license : null;
    if (!envelope) throw new Error("LICENSE_REFRESH_RESPONSE_MISSING_SIGNED_LICENSE");

    const validation = validateSignedLicenseEnvelope(envelope);
    if (!validation.ok) throw new Error(validation.issues.join("; "));
    const signature = verifySignedLicenseEnvelope(validation.value);
    if (!signature.ok) throw new Error(signature.issues.join("; "));

    writeLicenseAtomically(JSON.stringify(validation.value, null, 2));
    const local = loadLocalLicense();
    const state = local.state === "revoked" ? "revoked" : local.state === "suspended" ? "suspended" : "fresh";
    const status: LicenseRefreshState = {
      state,
      enabled: true,
      lastRefreshAt: startedAt,
      configurationState: "configured",
      operationalDecision: state === "revoked" || state === "suspended" ? "license_blocking" : "refresh_available",
      lastSuccessAt: new Date().toISOString(),
      lastFailureAt: previous.lastFailureAt,
      lastError: null,
      source: "remote",
      licenseId: local.licenseId,
      plan: local.plan
    };
    writeLicenseRefreshState(status);
    return { ok: true, state, message: "Licencia actualizada desde servidor remoto.", status };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const local = loadLocalLicense();
    const state = local.state === "offline_grace" ? "offline_grace" : "refresh_failed";
    const status: LicenseRefreshState = {
      ...previous,
      enabled: true,
      state,
      configurationState: "configured",
      operationalDecision: state === "offline_grace" ? "informational" : "refresh_failed",
      lastRefreshAt: startedAt,
      lastFailureAt: new Date().toISOString(),
      lastError: message,
      source: "remote",
      licenseId: local.licenseId,
      plan: local.plan
    };
    writeLicenseRefreshState(status);
    return { ok: false, state, message: `No se pudo refrescar licencia: ${message}`, status };
  }
}

export function serializeSignedLicenseForStore(value: unknown): string {
  if (!isSignedLicenseEnvelope(value)) throw new Error("LICENSE_SIGNED_ENVELOPE_INVALID");
  return canonicalJson(value);
}

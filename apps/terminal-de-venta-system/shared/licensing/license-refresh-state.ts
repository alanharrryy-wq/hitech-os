export type LicenseRefreshStateCode =
  | "refresh_disabled"
  | "disabled"
  | "never_refreshed"
  | "fresh"
  | "stale"
  | "refresh_failed"
  | "offline_grace"
  | "revoked"
  | "suspended";

export type LicenseRefreshState = {
  state: LicenseRefreshStateCode;
  enabled: boolean;
  configurationState: "configured" | "refresh_disabled" | "missing_server_url" | "missing_device_id";
  operationalDecision: "informational" | "refresh_available" | "refresh_failed" | "license_blocking";
  lastRefreshAt: string | null;
  lastSuccessAt: string | null;
  lastFailureAt: string | null;
  lastError: string | null;
  source: "none" | "local_state" | "remote";
  licenseId: string | null;
  plan: string | null;
};

export type LicenseRefreshResult = {
  ok: boolean;
  state: LicenseRefreshStateCode;
  message: string;
  status: LicenseRefreshState;
};

export function defaultRefreshState(enabled = false): LicenseRefreshState {
  return {
    state: enabled ? "never_refreshed" : "refresh_disabled",
    enabled,
    configurationState: enabled ? "configured" : "refresh_disabled",
    operationalDecision: enabled ? "refresh_available" : "informational",
    lastRefreshAt: null,
    lastSuccessAt: null,
    lastFailureAt: null,
    lastError: null,
    source: "none",
    licenseId: null,
    plan: null
  };
}

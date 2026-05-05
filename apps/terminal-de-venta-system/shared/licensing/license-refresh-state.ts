export type LicenseRefreshStateCode =
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
    state: enabled ? "never_refreshed" : "disabled",
    enabled,
    lastRefreshAt: null,
    lastSuccessAt: null,
    lastFailureAt: null,
    lastError: null,
    source: "none",
    licenseId: null,
    plan: null
  };
}

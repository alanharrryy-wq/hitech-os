export const LICFLOW3_CLOUD_CONTRACT_SCHEMA_VERSION = "1.0.0";
export const LICFLOW3_CLOUD_CONTRACT_ID = "LICFLOW3_CLOUDFLARE_HOSTED_LICENSING_SUPPORT_BRIDGE";
export const LICFLOW3_CLOUD_BASE_URL = "https://app.hitechrts.com";
export const LICFLOW3_TENANT_SLUG = "prisma-original-customer";

export type Licflow3EndpointClassification = "REUSE" | "EXTEND" | "CREATE" | "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED";
export type Licflow3EndpointKey =
  | "health"
  | "capabilities"
  | "tenantStatus"
  | "clientContract"
  | "licenseActivate"
  | "licenseRefresh"
  | "licenseRevoke"
  | "deviceRegister"
  | "integrationReceipt"
  | "supportDiagnostics"
  | "adminSelftest"
  | "commercialSummary"
  | "tenantSnapshot"
  | "tenantNotes";

export type Licflow3EndpointContract = {
  key: Licflow3EndpointKey;
  label: string;
  method: "GET" | "POST";
  path: string;
  capability:
    | "health"
    | "capabilities"
    | "tenant_status"
    | "contract_fetch"
    | "activate"
    | "refresh"
    | "revoke"
    | "register_device"
    | "integration_receipt"
    | "support_diagnostics"
    | "admin_selftest"
    | "commercial_summary"
    | "tenant_snapshot"
    | "tenant_notes";
  mutatesCloud: boolean;
  adminRequired: boolean;
  safeSummaryCall: boolean;
  classification: Licflow3EndpointClassification;
};

export type Licflow3CloudContractStatus = {
  ok: boolean;
  schemaVersion: string;
  contractId: string;
  baseUrl: string;
  tenantSlug: string;
  configuredBaseUrl: string;
  baseUrlMatches: boolean;
  missing: Licflow3EndpointKey[];
  mismatched: Array<{ key: Licflow3EndpointKey; expected: string; actual: string }>;
  endpoints: Array<Licflow3EndpointContract & { configured: boolean; configuredPath: string | null }>;
  hostedCloudEvidenceStatus: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED" | "LIVE_EVIDENCE_PRESENT";
  claim: "contract_ready" | "contract_incomplete";
  safety: typeof LICFLOW3_CLOUD_CONTRACT.safety;
};

export const LICFLOW3_CLOUD_ENDPOINTS: readonly Licflow3EndpointContract[] = [
  {
    key: "health",
    label: "Health",
    method: "GET",
    path: "/health",
    capability: "health",
    mutatesCloud: false,
    adminRequired: false,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "capabilities",
    label: "Capabilities",
    method: "GET",
    path: "/api/public/capabilities",
    capability: "capabilities",
    mutatesCloud: false,
    adminRequired: false,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "tenantStatus",
    label: "Tenant Status",
    method: "GET",
    path: `/api/public/tenants/${LICFLOW3_TENANT_SLUG}/status`,
    capability: "tenant_status",
    mutatesCloud: false,
    adminRequired: false,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "clientContract",
    label: "Client Contract",
    method: "GET",
    path: `/api/client/contract?tenant=${LICFLOW3_TENANT_SLUG}`,
    capability: "contract_fetch",
    mutatesCloud: false,
    adminRequired: false,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "licenseActivate",
    label: "License Activate",
    method: "POST",
    path: "/api/licenses/activate",
    capability: "activate",
    mutatesCloud: true,
    adminRequired: true,
    safeSummaryCall: false,
    classification: "CREATE"
  },
  {
    key: "licenseRefresh",
    label: "License Refresh",
    method: "POST",
    path: "/api/licenses/refresh",
    capability: "refresh",
    mutatesCloud: true,
    adminRequired: true,
    safeSummaryCall: false,
    classification: "CREATE"
  },
  {
    key: "licenseRevoke",
    label: "License Revoke",
    method: "POST",
    path: "/api/licenses/revoke",
    capability: "revoke",
    mutatesCloud: true,
    adminRequired: true,
    safeSummaryCall: false,
    classification: "CREATE"
  },
  {
    key: "deviceRegister",
    label: "Register Device",
    method: "POST",
    path: "/api/devices/register",
    capability: "register_device",
    mutatesCloud: true,
    adminRequired: true,
    safeSummaryCall: false,
    classification: "EXTEND"
  },
  {
    key: "integrationReceipt",
    label: "Integration Receipt",
    method: "POST",
    path: "/api/client/integration-receipt",
    capability: "integration_receipt",
    mutatesCloud: true,
    adminRequired: true,
    safeSummaryCall: false,
    classification: "EXTEND"
  },
  {
    key: "supportDiagnostics",
    label: "Support Diagnostics",
    method: "GET",
    path: `/api/support/diagnostics?tenant=${LICFLOW3_TENANT_SLUG}`,
    capability: "support_diagnostics",
    mutatesCloud: false,
    adminRequired: true,
    safeSummaryCall: true,
    classification: "CREATE"
  },
  {
    key: "adminSelftest",
    label: "Admin Selftest",
    method: "GET",
    path: "/api/admin/selftest",
    capability: "admin_selftest",
    mutatesCloud: false,
    adminRequired: true,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "commercialSummary",
    label: "Commercial Summary",
    method: "GET",
    path: "/api/admin/commercial-summary",
    capability: "commercial_summary",
    mutatesCloud: false,
    adminRequired: true,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "tenantSnapshot",
    label: "Tenant Snapshot",
    method: "GET",
    path: `/api/admin/tenants/${LICFLOW3_TENANT_SLUG}/snapshot`,
    capability: "tenant_snapshot",
    mutatesCloud: false,
    adminRequired: true,
    safeSummaryCall: true,
    classification: "REUSE"
  },
  {
    key: "tenantNotes",
    label: "Tenant Notes",
    method: "POST",
    path: `/api/admin/tenants/${LICFLOW3_TENANT_SLUG}/notes`,
    capability: "tenant_notes",
    mutatesCloud: true,
    adminRequired: true,
    safeSummaryCall: false,
    classification: "REUSE"
  }
] as const;

export const LICFLOW3_REQUIRED_CAPABILITIES = [
  "activate",
  "refresh",
  "revoke",
  "register_device",
  "integration_receipt",
  "tenant_status",
  "support_diagnostics",
  "capabilities",
  "commercial_summary",
  "contract_fetch"
] as const;

export const LICFLOW3_CLOUD_CONTRACT = {
  schemaVersion: LICFLOW3_CLOUD_CONTRACT_SCHEMA_VERSION,
  contractId: LICFLOW3_CLOUD_CONTRACT_ID,
  phase: "LICFLOW3",
  name: "PRISMA Cloudflare Hosted Licensing / Support Bridge",
  baseUrl: LICFLOW3_CLOUD_BASE_URL,
  tenantSlug: LICFLOW3_TENANT_SLUG,
  endpoints: LICFLOW3_CLOUD_ENDPOINTS,
  requiredCapabilities: LICFLOW3_REQUIRED_CAPABILITIES,
  hostedCloudEvidenceStatus: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
  safety: {
    cockpit: "127.0.0.1:3160",
    noDeployByDefault: true,
    noDnsMutationByDefault: true,
    noTunnelMutationByDefault: true,
    noSecretValuesInRepo: true,
    noDbFilesInEvidence: true,
    noMutatingEndpointAutocall: true,
    tabletOfflineMustRemainValid: true,
    licflow2RemainsCanonicalLocalActivation: true
  }
} as const;

export function buildLicflow3EndpointMap(): Record<Licflow3EndpointKey, Licflow3EndpointContract> {
  return Object.fromEntries(LICFLOW3_CLOUD_ENDPOINTS.map((endpoint) => [endpoint.key, endpoint])) as Record<Licflow3EndpointKey, Licflow3EndpointContract>;
}

export function buildLicflow3CloudContractStatus(config: {
  apiBaseUrl?: string;
  tenantSlug?: string;
  endpoints?: Partial<Record<Licflow3EndpointKey, string>>;
  liveEvidenceOk?: boolean;
}): Licflow3CloudContractStatus {
  const configuredBaseUrl = (config.apiBaseUrl || "").replace(/\/+$/, "");
  const endpoints = config.endpoints ?? {};
  const missing: Licflow3EndpointKey[] = [];
  const mismatched: Licflow3CloudContractStatus["mismatched"] = [];
  const resolvedEndpoints = LICFLOW3_CLOUD_ENDPOINTS.map((endpoint) => {
    const configuredPath = endpoints[endpoint.key] || null;
    if (!configuredPath) {
      missing.push(endpoint.key);
    } else if (configuredPath !== endpoint.path) {
      mismatched.push({ key: endpoint.key, expected: endpoint.path, actual: configuredPath });
    }
    return {
      ...endpoint,
      configured: Boolean(configuredPath),
      configuredPath
    };
  });
  const baseUrlMatches = configuredBaseUrl === LICFLOW3_CLOUD_BASE_URL;
  const ok = baseUrlMatches && missing.length === 0 && mismatched.length === 0;
  return {
    ok,
    schemaVersion: LICFLOW3_CLOUD_CONTRACT_SCHEMA_VERSION,
    contractId: LICFLOW3_CLOUD_CONTRACT_ID,
    baseUrl: LICFLOW3_CLOUD_BASE_URL,
    tenantSlug: config.tenantSlug || LICFLOW3_TENANT_SLUG,
    configuredBaseUrl,
    baseUrlMatches,
    missing,
    mismatched,
    endpoints: resolvedEndpoints,
    hostedCloudEvidenceStatus: config.liveEvidenceOk ? "LIVE_EVIDENCE_PRESENT" : "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
    claim: ok ? "contract_ready" : "contract_incomplete",
    safety: LICFLOW3_CLOUD_CONTRACT.safety
  };
}

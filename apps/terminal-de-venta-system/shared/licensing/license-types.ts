export type LicensePlan =
  | "TABLET_SOLO"
  | "TABLET_PRO"
  | "TABLET_PC_MANAGED"
  | "DEVELOPMENT"
  | "TABLET_SOLO_FALLBACK";

export type RawLicenseState = "active" | "suspended" | "revoked" | "development";

export type NormalizedLicenseState =
  | "active"
  | "missing"
  | "invalid"
  | "expired"
  | "offline_grace"
  | "suspended"
  | "revoked"
  | "development";

export type LicenseSource = "local_file" | "dev_file" | "fallback_policy" | "missing_license" | "invalid_license";

export type LicenseSurface = "tablet" | "pc" | "mobile" | "control" | "shared";

export type LicenseFeatureSource = "license" | "fallback_policy" | "default" | "missing_license" | "invalid_license";

export type LicenseEnforcement = "allow" | "warn" | "soft_deny" | "hard_deny";

export type LicenseAssignmentState =
  | "assigned"
  | "unassigned"
  | "wrong_customer"
  | "wrong_business"
  | "wrong_store"
  | "wrong_device"
  | "wrong_terminal"
  | "exceeded_limit"
  | "unknown";

export type LicenseOperationalDecision = "allow" | "allow_with_warning" | "degrade" | "deny";

export type LicenseActivationMode = "OFFLINE_PACKAGE" | "ONLINE_ACTIVATION" | "HYBRID";

export type LicenseActivationMetadata = {
  schemaVersion: string;
  mode: LicenseActivationMode;
  status: "prepared" | "activated" | "refresh_pending" | "refresh_failed" | "revoked";
  channel: "local_package" | "local_loopback_contract" | "hybrid_package_with_refresh";
  receiptId: string;
  activatedAt: string;
  issuedBy: string;
  hostedCloud: boolean;
  supportCode: string;
};

export type LicenseDenialReason =
  | "license_missing"
  | "license_invalid"
  | "license_expired"
  | "license_suspended"
  | "license_revoked"
  | "device_unassigned"
  | "wrong_customer"
  | "wrong_business"
  | "wrong_store"
  | "wrong_device"
  | "wrong_terminal"
  | "limit_exceeded"
  | "feature_not_entitled";

export type LicenseEvidenceEvent = {
  topic: string;
  occurredAt: string;
  source: "local_license" | "refresh_state" | "feature_gate" | "fallback_policy";
  customerId: string | null;
  businessId: string | null;
  storeId: string | null;
  deviceId: string | null;
  terminalId: string | null;
  licenseId: string | null;
  reason: string | null;
};

export type LicenseDocument = {
  schemaVersion: string;
  licenseId: string;
  customerId: string;
  businessId: string;
  storeId?: string;
  branchId?: string;
  deviceId?: string;
  tabletId?: string;
  terminalId?: string;
  authorizedDevices?: AuthorizedLicenseDevice[];
  assignmentState?: LicenseAssignmentState;
  plan: Exclude<LicensePlan, "TABLET_SOLO_FALLBACK">;
  state: RawLicenseState;
  validFrom: string;
  validUntil: string;
  issuedAt?: string;
  lastSeenAt?: string;
  lastRefreshAt?: string;
  offlineGraceDays?: number;
  activation?: LicenseActivationMetadata;
  features?: Record<string, boolean>;
  capabilities?: Record<string, boolean>;
  limits?: Record<string, number>;
  notes?: string[];
};

export type AuthorizedLicenseDevice = {
  deviceId: string;
  role: "pc" | "tablet" | "mobile" | "control" | "shared";
  terminalId?: string;
  storeId?: string;
};

export type LicenseWarning = {
  code: string;
  message: string;
};

export type NormalizedLicenseStatus = {
  ok: boolean;
  state: NormalizedLicenseState;
  plan: LicensePlan;
  customerId: string | null;
  businessId: string | null;
  storeId: string | null;
  branchId: string | null;
  deviceId: string | null;
  tabletId: string | null;
  terminalId: string | null;
  authorizedDevices: AuthorizedLicenseDevice[];
  licenseId: string | null;
  assignmentState: LicenseAssignmentState;
  validFrom: string | null;
  validUntil: string | null;
  issuedAt: string | null;
  capabilities: Record<string, boolean>;
  limits: Record<string, number>;
  lastSeenAt: string | null;
  lastRefreshAt: string | null;
  lastDecisionAt: string;
  denialReason: LicenseDenialReason | null;
  evidenceEvent: LicenseEvidenceEvent;
  operationalDecision: LicenseOperationalDecision;
  offlineGraceDays: number;
  daysRemaining: number | null;
  source: LicenseSource;
  path: string | null;
  warnings: LicenseWarning[];
  raw?: LicenseDocument;
};

export type FeatureResolution = {
  key: string;
  allowed: boolean;
  enforcement: LicenseEnforcement;
  reason: string;
  source: LicenseFeatureSource;
  plan: LicensePlan;
  state: NormalizedLicenseState;
  requiredPlan?: LicensePlan;
  saleBasicsStillAvailable: boolean;
  assignmentState: LicenseAssignmentState;
  denialReason: LicenseDenialReason | null;
  evidenceEvent: LicenseEvidenceEvent;
  operationalDecision: LicenseOperationalDecision;
  warnings: LicenseWarning[];
};

export type LicenseApiEnvelope<T> = {
  ok: boolean;
  data?: T;
  code?: string;
  message?: string;
  details?: Record<string, unknown>;
  meta?: Record<string, unknown>;
};

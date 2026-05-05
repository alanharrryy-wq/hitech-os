export type LicensePlan =
  | "TABLET_SOLO"
  | "TABLET_PRO"
  | "TABLET_PC_REQUIRED"
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

export type LicenseSurface = "tablet" | "pc" | "shared";

export type LicenseFeatureSource = "license" | "fallback_policy" | "default" | "missing_license" | "invalid_license";

export type LicenseEnforcement = "allow" | "warn" | "soft_deny" | "hard_deny";

export type LicenseDocument = {
  schemaVersion: string;
  licenseId: string;
  customerId: string;
  businessId: string;
  plan: Exclude<LicensePlan, "TABLET_SOLO_FALLBACK">;
  state: RawLicenseState;
  validFrom: string;
  validUntil: string;
  issuedAt?: string;
  offlineGraceDays?: number;
  features?: Record<string, boolean>;
  limits?: Record<string, number>;
  notes?: string[];
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
  licenseId: string | null;
  validFrom: string | null;
  validUntil: string | null;
  issuedAt: string | null;
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

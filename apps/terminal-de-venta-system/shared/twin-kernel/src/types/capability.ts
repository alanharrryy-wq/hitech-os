export const TWIN_SURFACES = ["pc", "tablet"] as const;
export type TwinSurface = (typeof TWIN_SURFACES)[number];

export const TWIN_CAPABILITY_DOMAINS = [
  "core",
  "catalog",
  "inventory",
  "procurement",
  "sales",
  "cash",
  "returns",
  "sync",
  "audit",
  "customer",
  "reporting"
] as const;
export type TwinCapabilityDomain = (typeof TWIN_CAPABILITY_DOMAINS)[number];

export const TWIN_CAPABILITY_STATUSES = ["ready", "partial", "planned", "blocked"] as const;
export type TwinCapabilityStatus = (typeof TWIN_CAPABILITY_STATUSES)[number];

export const TWIN_PARITY_MODES = [
  "authoritative_control",
  "local_execution",
  "mirror_observer",
  "bidirectional_bridge",
  "planned_bridge"
] as const;
export type TwinParityMode = (typeof TWIN_PARITY_MODES)[number];

export const TWIN_SYNC_DIRECTIONS = ["none", "pc_to_tablet", "tablet_to_pc", "bidirectional"] as const;
export type TwinSyncDirection = (typeof TWIN_SYNC_DIRECTIONS)[number];

export const TWIN_OFFLINE_MODES = ["none", "read_only", "queue_required", "full_local"] as const;
export type TwinOfflineMode = (typeof TWIN_OFFLINE_MODES)[number];

export const TWIN_AUDIT_LEVELS = ["none", "summary", "transaction", "regulatory"] as const;
export type TwinAuditLevel = (typeof TWIN_AUDIT_LEVELS)[number];

export type TwinSurfaceRole = "source_of_truth" | "executor" | "mirror" | "observer";

export type TwinCapabilityEventRef = {
  name: string;
  producedBy: TwinSurface[];
  consumedBy: TwinSurface[];
  required: boolean;
  notes?: string;
};

export type TwinSurfaceBinding = {
  surface: TwinSurface;
  moduleKey: string;
  route: string;
  role: TwinSurfaceRole;
  ownsWrites: boolean;
  requiredScreens: string[];
  allowedEvents: string[];
  offlineMode: TwinOfflineMode;
  auditLevel: TwinAuditLevel;
};

export type TwinCapabilityManifest = {
  id: string;
  version: "1.0.0";
  updatedAt: string;
  domain: TwinCapabilityDomain;
  title: string;
  businessOutcome: string;
  owner: TwinSurface;
  parityKey: string;
  status: TwinCapabilityStatus;
  mode: TwinParityMode;
  syncDirection: TwinSyncDirection;
  surfaces: TwinSurfaceBinding[];
  invariants: string[];
  events: TwinCapabilityEventRef[];
  acceptance: string[];
  risks: string[];
};

export type TwinCapabilityValidationIssue = {
  capabilityId: string;
  severity: "error" | "warning";
  code: string;
  message: string;
  path?: string;
};

export type TwinCapabilityValidationResult = {
  ok: boolean;
  errors: TwinCapabilityValidationIssue[];
  warnings: TwinCapabilityValidationIssue[];
};

export type TwinCapabilityScorecardRow = {
  id: string;
  title: string;
  domain: TwinCapabilityDomain;
  status: TwinCapabilityStatus;
  pcRole: TwinSurfaceRole | "missing";
  tabletRole: TwinSurfaceRole | "missing";
  syncDirection: TwinSyncDirection;
  requiredEventCount: number;
  acceptanceCount: number;
  riskCount: number;
};

export const FOUNDATION_ROLES = ["operator", "admin", "auditor"] as const;
export const SUPPLIER_LIFECYCLES = ["approved", "active", "blocked"] as const;
export const DOCUMENT_LIFECYCLES = ["present", "missing", "in-progress", "expired"] as const;
export const TEMPERATURE_PROFILES = [
  "2C-8C",
  "15C-25C",
  "-20C",
  "-70C",
  "Ambient Controlled"
] as const;
export const STORAGE_CONDITIONS = [
  "Cold Room A",
  "Cold Room B",
  "Ambient Cage",
  "Quarantine Bay",
  "DEA Cage"
] as const;
export const INCOTERMS = ["EXW", "FCA", "CPT", "CIP", "DAP", "DDP"] as const;

export type FoundationRole = (typeof FOUNDATION_ROLES)[number];
export type SupplierLifecycle = (typeof SUPPLIER_LIFECYCLES)[number];
export type DocumentLifecycle = (typeof DOCUMENT_LIFECYCLES)[number];
export type TemperatureProfile = (typeof TEMPERATURE_PROFILES)[number];
export type StorageCondition = (typeof STORAGE_CONDITIONS)[number];
export type Incoterm = (typeof INCOTERMS)[number];

export interface InventoryFoundationFields {
  readonly sku: string;
  readonly lot: string;
  readonly batch: string;
  readonly barcode: string;
  readonly supplierCode: string;
  readonly incoterm: Incoterm;
  readonly temperatureProfile: TemperatureProfile;
  readonly storageCondition: StorageCondition;
}

export interface SupplierProfile {
  readonly code: string;
  readonly legalName: string;
  readonly lifecycle: SupplierLifecycle;
  readonly country: string;
  readonly qaScore: number;
  readonly leadTimeDays: number;
  readonly route: string;
  readonly gmpLevel: "A" | "B" | "C";
  readonly activeLots: number;
  readonly lastAuditDate: string;
  readonly tempExcursions90d: number;
  readonly notes: readonly string[];
}

export interface FoundationLotProfile {
  readonly id: string;
  readonly sku: string;
  readonly lot: string;
  readonly batch: string;
  readonly barcode: string;
  readonly supplierCode: string;
  readonly temperatureProfile: TemperatureProfile;
  readonly storageCondition: StorageCondition;
  readonly expiryDate: string;
  readonly mfgDate: string;
  readonly excursionCount30d: number;
  readonly holdFlag: boolean;
  readonly releaseWindowHours: number;
}

export interface TemperatureExcursionRecord {
  readonly id: string;
  readonly lot: string;
  readonly observedAt: string;
  readonly durationMinutes: number;
  readonly peakCelsius: number;
  readonly thresholdCelsius: number;
  readonly action: string;
}

export interface VaultDocumentDefinition {
  readonly id: string;
  readonly label: string;
  readonly category: "customs" | "quality" | "finance" | "logistics";
  readonly critical: boolean;
  readonly ownerRole: FoundationRole;
  readonly expiryDate: string;
  readonly linkedSupplierCodes: readonly string[];
  readonly actionPlaybook: readonly string[];
}

export interface VaultDocumentState {
  readonly documentId: string;
  readonly lifecycle: DocumentLifecycle;
  readonly touchedByRole: FoundationRole;
  readonly touchedAt: string;
  readonly comment: string;
}

export interface RbacCapability {
  readonly id: string;
  readonly label: string;
  readonly domain: "receiving" | "vault" | "quality" | "release";
  readonly neededDocuments: readonly string[];
  readonly reason: string;
}

export interface RbacMatrixRow {
  readonly role: FoundationRole;
  readonly displayName: string;
  readonly capabilities: readonly RbacCapability[];
  readonly defaultGate: "open" | "review" | "blocked";
  readonly tooltip: string;
}

export interface RbacStatusRow {
  readonly role: FoundationRole;
  readonly displayName: string;
  readonly gate: "open" | "review" | "blocked";
  readonly reasons: readonly string[];
  readonly capabilities: readonly RbacCapability[];
  readonly tooltip: string;
}

export interface ReadinessBreakdownItem {
  readonly id: string;
  readonly label: string;
  readonly score: number;
  readonly maxScore: number;
  readonly reason: string;
  readonly nextAction: string;
}

export interface ComplianceChip {
  readonly lifecycle: DocumentLifecycle;
  readonly count: number;
  readonly tone: "success" | "warning" | "danger" | "neutral" | "accent";
}

export interface HoldReason {
  readonly id: string;
  readonly severity: "critical" | "major" | "minor";
  readonly reason: string;
  readonly nextStep: string;
}

export interface FoundationReadinessSnapshot {
  readonly totalScore: number;
  readonly maxScore: number;
  readonly percentage: number;
  readonly breakdown: readonly ReadinessBreakdownItem[];
  readonly holdReasons: readonly HoldReason[];
  readonly chips: readonly ComplianceChip[];
}

export interface InventoryFoundationTimelineEntry {
  readonly id: string;
  readonly kind:
    | "field.change"
    | "role.change"
    | "supplier.change"
    | "doc.lifecycle"
    | "gating.recompute";
  readonly actorRole: FoundationRole;
  readonly at: string;
  readonly message: string;
  readonly details: readonly string[];
}

export interface InventoryFoundationState {
  readonly fields: InventoryFoundationFields;
  readonly role: FoundationRole;
  readonly suppliers: readonly SupplierProfile[];
  readonly selectedSupplierCode: string;
  readonly documents: readonly VaultDocumentDefinition[];
  readonly documentStates: Readonly<Record<string, VaultDocumentState>>;
  readonly rbacRows: readonly RbacMatrixRow[];
  readonly rbacSearch: string;
  readonly rbacGateFilter: "all" | "open" | "review" | "blocked";
  readonly timeline: readonly InventoryFoundationTimelineEntry[];
}

export interface InventoryFoundationComputed {
  readonly selectedSupplier: SupplierProfile | null;
  readonly readiness: FoundationReadinessSnapshot;
  readonly rbacStatusRows: readonly RbacStatusRow[];
  readonly rbacGateSummary: readonly string[];
  readonly filteredRbacRows: readonly RbacStatusRow[];
  readonly canProceedToRun2: boolean;
  readonly supplierGate: "open" | "blocked";
  readonly foundationGate: "open" | "hold";
}

export interface InventoryFoundationActions {
  readonly setField: <K extends keyof InventoryFoundationFields>(
    key: K,
    value: InventoryFoundationFields[K]
  ) => void;
  readonly setRole: (role: FoundationRole) => void;
  readonly setSupplierCode: (supplierCode: string) => void;
  readonly setSupplierLifecycle: (supplierCode: string, lifecycle: SupplierLifecycle) => void;
  readonly cycleDocumentLifecycle: (documentId: string) => void;
  readonly setRbacSearch: (value: string) => void;
  readonly setRbacGateFilter: (filter: "all" | "open" | "review" | "blocked") => void;
  readonly reset: () => void;
}

export interface InventoryFoundationStore
  extends InventoryFoundationState,
    InventoryFoundationActions {}

export interface InventoryFoundationPanelContext {
  readonly state: InventoryFoundationState;
  readonly computed: InventoryFoundationComputed;
  readonly actions: InventoryFoundationActions;
}

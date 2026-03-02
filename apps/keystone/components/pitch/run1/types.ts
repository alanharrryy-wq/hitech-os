export type FoundationRole = "operator" | "admin" | "auditor";

export type SupplierStatus = "approved" | "active" | "blocked";

export type DocumentStatus = "present" | "missing" | "expired" | "in-progress";

export type IncotermCode =
  | "EXW"
  | "FCA"
  | "FOB"
  | "CFR"
  | "CIF"
  | "CPT"
  | "CIP"
  | "DAP"
  | "DPU"
  | "DDP";

export type TemperatureProfileCode =
  | "ambient"
  | "cool"
  | "cold"
  | "deep-cold"
  | "frozen"
  | "controlled-room";

export type StorageConditionCode =
  | "dry"
  | "cold-room"
  | "freezer"
  | "hazmat-cabinet"
  | "clean-room"
  | "vault";

export interface FoundationFieldState {
  readonly sku: string;
  readonly lot: string;
  readonly batch: string;
  readonly barcode: string;
  readonly supplierId: string;
  readonly incoterm: IncotermCode;
  readonly temperatureProfile: TemperatureProfileCode;
  readonly storageCondition: StorageConditionCode;
}

export type FoundationFieldKey = keyof FoundationFieldState;

export interface FoundationSupplier {
  readonly id: string;
  readonly legalName: string;
  readonly siteCode: string;
  readonly status: SupplierStatus;
  readonly region: string;
  readonly country: string;
  readonly lastAuditDate: string;
  readonly nextAuditDate: string;
  readonly gmpGrade: "A" | "B" | "C";
  readonly qualityAgreementSigned: boolean;
  readonly sanctionsWatch: boolean;
  readonly logisticsLane: string;
  readonly preferredPort: string;
  readonly leadTimeDays: number;
  readonly deviationCount30d: number;
  readonly avgExcursionEvents: number;
  readonly contactName: string;
  readonly contactEmail: string;
  readonly contactPhone: string;
}

export interface FoundationDocument {
  readonly id: string;
  readonly code: string;
  readonly title: string;
  readonly category:
    | "quality"
    | "customs"
    | "commercial"
    | "logistics"
    | "temperature"
    | "regulatory";
  readonly ownerTeam: string;
  readonly critical: boolean;
  readonly status: DocumentStatus;
  readonly issuedAt: string;
  readonly expiresAt: string;
  readonly lotScoped: boolean;
  readonly requiresWetSignature: boolean;
  readonly description: string;
  readonly whyRequired: string;
  readonly nextAction: string;
  readonly remediationPlaybook: readonly string[];
}

export interface RbacCapability {
  readonly id: string;
  readonly domain:
    | "master-data"
    | "documents"
    | "quality"
    | "receiving"
    | "audit"
    | "shipping"
    | "finance"
    | "security"
    | "warehouse";
  readonly capability: string;
  readonly description: string;
  readonly allowedRoles: readonly FoundationRole[];
  readonly dataSensitivity: "internal" | "confidential" | "restricted";
  readonly preconditions: readonly string[];
  readonly blockerWhenDenied: string;
  readonly escalationPath: string;
}

export interface RbacEvaluation {
  readonly capabilityId: string;
  readonly roleAllowed: boolean;
  readonly preconditionsMet: boolean;
  readonly gated: boolean;
  readonly reasons: readonly string[];
  readonly action: string;
}

export interface ReadinessBreakdown {
  readonly fields: number;
  readonly supplier: number;
  readonly documents: number;
  readonly rbac: number;
}

export interface ReadinessSummary {
  readonly total: number;
  readonly grade: "critical" | "low" | "watch" | "ready";
  readonly breakdown: ReadinessBreakdown;
  readonly blockers: readonly string[];
  readonly readyToReceive: boolean;
}

export interface DocumentCounts {
  readonly present: number;
  readonly missing: number;
  readonly expired: number;
  readonly inProgress: number;
  readonly criticalTotal: number;
  readonly criticalIssueCount: number;
}

export interface SupplierHealth {
  readonly supplierId: string;
  readonly status: SupplierStatus;
  readonly laneRisk: "low" | "medium" | "high";
  readonly complianceRisk: "low" | "medium" | "high";
  readonly overallRisk: "low" | "medium" | "high";
  readonly blockers: readonly string[];
  readonly recommendations: readonly string[];
}

export interface FoundationHoldBannerModel {
  readonly visible: boolean;
  readonly title: string;
  readonly subtitle: string;
  readonly reasons: readonly string[];
  readonly nextSteps: readonly string[];
}

export interface FoundationDashboardMetric {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly tone: "neutral" | "accent" | "success" | "warning" | "danger";
  readonly helper: string;
}

export interface FoundationActivityEvent {
  readonly id: string;
  readonly kind: "field" | "document" | "rbac" | "supplier" | "gate";
  readonly timestamp: string;
  readonly actor: string;
  readonly summary: string;
  readonly details: string;
}

export interface FoundationStatusLegend {
  readonly id: string;
  readonly label: string;
  readonly status: DocumentStatus | SupplierStatus | FoundationRole;
  readonly colorToken: string;
  readonly description: string;
}

export interface FieldOption<TCode extends string> {
  readonly code: TCode;
  readonly label: string;
  readonly note: string;
  readonly expectedStorage: StorageConditionCode[];
}

export interface IncotermOption {
  readonly code: IncotermCode;
  readonly label: string;
  readonly transferPoint: string;
  readonly insuranceOwner: string;
  readonly customsOwner: string;
  readonly defaultRisk: "low" | "medium" | "high";
  readonly summary: string;
}

export interface StorageConditionOption {
  readonly code: StorageConditionCode;
  readonly label: string;
  readonly minCelsius: number;
  readonly maxCelsius: number;
  readonly humidityRange: string;
  readonly controls: readonly string[];
  readonly alarms: readonly string[];
}

export interface RoleDescriptor {
  readonly role: FoundationRole;
  readonly title: string;
  readonly description: string;
  readonly canOverrideCriticalHold: boolean;
  readonly seesSupplierFinance: boolean;
  readonly defaultFilterDomain: RbacCapability["domain"];
}

export interface FoundationScenarioSnapshot {
  readonly id: string;
  readonly name: string;
  readonly fields: Partial<FoundationFieldState>;
  readonly role: FoundationRole;
  readonly supplierId: string;
  readonly docStatusOverrides: Record<string, DocumentStatus>;
  readonly expectedReadiness: number;
  readonly commentary: string;
}

export interface FoundationStoreState {
  readonly fields: FoundationFieldState;
  readonly activeRole: FoundationRole;
  readonly rbacSearch: string;
  readonly rbacDomainFilter: RbacCapability["domain"] | "all";
  readonly rbacShowOnlyGated: boolean;
  readonly suppliers: readonly FoundationSupplier[];
  readonly documents: readonly FoundationDocument[];
  readonly capabilities: readonly RbacCapability[];
  readonly activity: readonly FoundationActivityEvent[];
  readonly selectedScenarioId: string;
  readonly selectedDocumentCategory: FoundationDocument["category"] | "all";
  readonly setField: <K extends FoundationFieldKey>(key: K, value: FoundationFieldState[K]) => void;
  readonly setRole: (role: FoundationRole) => void;
  readonly setSupplier: (supplierId: string) => void;
  readonly cycleDocumentStatus: (docId: string) => void;
  readonly setRbacSearch: (value: string) => void;
  readonly setRbacDomainFilter: (domain: RbacCapability["domain"] | "all") => void;
  readonly setRbacShowOnlyGated: (show: boolean) => void;
  readonly setDocumentCategoryFilter: (category: FoundationDocument["category"] | "all") => void;
  readonly applyScenario: (scenarioId: string) => void;
  readonly resetAll: () => void;
}

export interface FoundationComputedModel {
  readonly readiness: ReadinessSummary;
  readonly documentCounts: DocumentCounts;
  readonly holdBanner: FoundationHoldBannerModel;
  readonly supplierHealth: SupplierHealth;
  readonly rbacEvaluations: readonly RbacEvaluation[];
  readonly filteredRbacEvaluations: readonly RbacEvaluation[];
  readonly filteredDocuments: readonly FoundationDocument[];
  readonly dashboardMetrics: readonly FoundationDashboardMetric[];
  readonly nextGate: string;
  readonly nextGateReason: string;
}

export const DOCUMENT_STATUS_ORDER: readonly DocumentStatus[] = [
  "present",
  "missing",
  "expired",
  "in-progress"
] as const;

export const FOUNDATION_ROLE_ORDER: readonly FoundationRole[] = [
  "operator",
  "admin",
  "auditor"
] as const;

export const SUPPLIER_STATUS_ORDER: readonly SupplierStatus[] = [
  "approved",
  "active",
  "blocked"
] as const;

export const FOUNDATION_STATUS_LEGEND: readonly FoundationStatusLegend[] = [
  {
    id: "doc-present",
    label: "Present",
    status: "present",
    colorToken: "success",
    description: "Documento vigente y trazable contra lote/batch activo"
  },
  {
    id: "doc-missing",
    label: "Missing",
    status: "missing",
    colorToken: "danger",
    description: "Documento no cargado; bloquea gate de recepción y liberación"
  },
  {
    id: "doc-expired",
    label: "Expired",
    status: "expired",
    colorToken: "warning",
    description: "Documento vencido; requiere renovación y evidencia de revisión"
  },
  {
    id: "doc-in-progress",
    label: "In Progress",
    status: "in-progress",
    colorToken: "accent",
    description: "Documento en trámite con responsable y ETA de cierre"
  },
  {
    id: "supplier-approved",
    label: "Supplier Approved",
    status: "approved",
    colorToken: "success",
    description: "Proveedor aprobado por QA + Regulatory + Trade"
  },
  {
    id: "supplier-active",
    label: "Supplier Active",
    status: "active",
    colorToken: "accent",
    description: "Proveedor activo en lane actual con monitoreo continuo"
  },
  {
    id: "supplier-blocked",
    label: "Supplier Blocked",
    status: "blocked",
    colorToken: "danger",
    description: "Proveedor bloqueado por hallazgo crítico o sanción logística"
  },
  {
    id: "role-operator",
    label: "Operator",
    status: "operator",
    colorToken: "neutral",
    description: "Opera recepción y registro; no puede sobreescribir holds críticos"
  },
  {
    id: "role-admin",
    label: "Admin",
    status: "admin",
    colorToken: "accent",
    description: "Gestiona master data, gates y aprobaciones operativas"
  },
  {
    id: "role-auditor",
    label: "Auditor",
    status: "auditor",
    colorToken: "warning",
    description: "Solo lectura, trazabilidad y evidencia regulatoria"
  }
] as const;

export const FOUNDATION_ROLE_DESCRIPTORS: readonly RoleDescriptor[] = [
  {
    role: "operator",
    title: "Warehouse Operator",
    description: "Captura de recepción, verificación física, cuarentena inicial.",
    canOverrideCriticalHold: false,
    seesSupplierFinance: false,
    defaultFilterDomain: "receiving"
  },
  {
    role: "admin",
    title: "Control Tower Admin",
    description: "Administra gates, aprobaciones y excepciones documentales.",
    canOverrideCriticalHold: true,
    seesSupplierFinance: true,
    defaultFilterDomain: "documents"
  },
  {
    role: "auditor",
    title: "QA / GDP Auditor",
    description: "Supervisión de compliance, cadena de custodia y trazabilidad.",
    canOverrideCriticalHold: false,
    seesSupplierFinance: false,
    defaultFilterDomain: "audit"
  }
] as const;

export const FIELD_COMPLETION_HINTS: Readonly<Record<FoundationFieldKey, string>> = {
  sku: "SKU debe coincidir con registro maestro farmacéutico",
  lot: "Lot vinculado a certificados y ventana de expiración",
  batch: "Batch para trazabilidad de manufactura y liberación",
  barcode: "Código GS1/EAN usado en recepción y put-away",
  supplierId: "Proveedor debe estar activo o aprobado",
  incoterm: "Incoterm define ownership de riesgo aduanal",
  temperatureProfile: "Perfil térmico determina documentos críticos",
  storageCondition: "Condición de almacenamiento valida capacidad local"
} as const;

export function isDocumentStatus(value: string): value is DocumentStatus {
  return DOCUMENT_STATUS_ORDER.includes(value as DocumentStatus);
}

export function isFoundationRole(value: string): value is FoundationRole {
  return FOUNDATION_ROLE_ORDER.includes(value as FoundationRole);
}

export function isSupplierStatus(value: string): value is SupplierStatus {
  return SUPPLIER_STATUS_ORDER.includes(value as SupplierStatus);
}
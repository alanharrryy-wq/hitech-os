export const RECEIVING_STATES = ["ARRIVED", "DOCS_HOLD", "RECEIVED", "QUARANTINE"] as const;
export const PACK_DOC_STATUSES = ["present", "missing", "in-progress", "expired"] as const;
export const RECEIVING_INCOTERMS = ["EXW", "FCA", "CPT", "CIP", "DAP", "DDP"] as const;

export type ReceivingStateCode = (typeof RECEIVING_STATES)[number];
export type CustomsDocStatus = (typeof PACK_DOC_STATUSES)[number];
export type ReceivingIncoterm = (typeof RECEIVING_INCOTERMS)[number];

export interface ShipmentControlBoardFields {
  readonly awbBl: string;
  readonly eta: string;
  readonly ata: string;
  readonly incoterm: ReceivingIncoterm;
  readonly carrier: string;
  readonly port: string;
  readonly quantityDeclared: number;
  readonly quantityReceived: number;
  readonly lotDeclared: string;
  readonly lotReceived: string;
  readonly temperatureExcursion: boolean;
}

export interface CustomsDocumentRequirement {
  readonly id: string;
  readonly label: string;
  readonly critical: boolean;
  readonly owner: "broker" | "qa" | "finance" | "logistics";
  readonly status: CustomsDocStatus;
  readonly expiryDate: string;
  readonly guidance: readonly string[];
}

export interface ShipmentManifestProfile {
  readonly id: string;
  readonly awbBl: string;
  readonly product: string;
  readonly lot: string;
  readonly quantity: number;
  readonly unit: "vial" | "carton" | "shipper";
  readonly tempProfile: string;
  readonly origin: string;
  readonly destinationPort: string;
  readonly eta: string;
  readonly carrier: string;
  readonly status: ReceivingStateCode;
  readonly laneRisk: "low" | "medium" | "high";
  readonly notes: readonly string[];
}

export interface PortRiskProfile {
  readonly port: string;
  readonly country: string;
  readonly customsCongestion: number;
  readonly coldChainReliability: number;
  readonly strikeAlert: boolean;
  readonly note: string;
}

export interface TransitionGuardEvaluation {
  readonly allowed: boolean;
  readonly reasons: readonly string[];
  readonly nextState: ReceivingStateCode;
}

export interface ReceivingTimelineEntry {
  readonly id: string;
  readonly sequence: number;
  readonly action:
    | "ADVANCE"
    | "RESET"
    | "FORCE_QUARANTINE"
    | "DOC_STATUS"
    | "FIELD_UPDATE"
    | "MISMATCH_DETECTED";
  readonly from: ReceivingStateCode;
  readonly to: ReceivingStateCode;
  readonly at: string;
  readonly note: string;
  readonly reasons: readonly string[];
}

export interface DeviationTicket {
  readonly id: string;
  readonly active: boolean;
  readonly category: "qty-mismatch" | "lot-mismatch" | "temp-excursion" | "customs-doc";
  readonly severity: "minor" | "major" | "critical";
  readonly createdAt: string;
  readonly requiredSteps: readonly string[];
}

export interface ReceivingRiskPanel {
  readonly score: number;
  readonly level: "low" | "medium" | "high";
  readonly reasons: readonly string[];
}

export interface NextGatePanel {
  readonly state: "READY" | "HOLD" | "BLOCKED";
  readonly title: string;
  readonly blockers: readonly string[];
  readonly nextActions: readonly string[];
}

export interface ImportReceivingState {
  readonly shipmentState: ReceivingStateCode;
  readonly fields: ShipmentControlBoardFields;
  readonly customsPack: readonly CustomsDocumentRequirement[];
  readonly manifests: readonly ShipmentManifestProfile[];
  readonly selectedManifestId: string;
  readonly timeline: readonly ReceivingTimelineEntry[];
  readonly deviationTicket: DeviationTicket | null;
}

export interface ImportReceivingComputed {
  readonly selectedManifest: ShipmentManifestProfile | null;
  readonly customsCompleteness: number;
  readonly customsCounts: Readonly<Record<CustomsDocStatus, number>>;
  readonly transition: TransitionGuardEvaluation;
  readonly riskPanel: ReceivingRiskPanel;
  readonly nextGate: NextGatePanel;
  readonly mismatchDetected: boolean;
}

export interface ImportReceivingActions {
  readonly setField: <K extends keyof ShipmentControlBoardFields>(
    key: K,
    value: ShipmentControlBoardFields[K]
  ) => void;
  readonly setSelectedManifest: (manifestId: string) => void;
  readonly cycleCustomsDocStatus: (documentId: string) => void;
  readonly advance: () => void;
  readonly reset: () => void;
  readonly forceQuarantine: () => void;
}

export interface ImportReceivingStore extends ImportReceivingState, ImportReceivingActions {}

export interface ImportReceivingPanelContext {
  readonly state: ImportReceivingState;
  readonly computed: ImportReceivingComputed;
  readonly actions: ImportReceivingActions;
}

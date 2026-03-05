import { PITCH_SCREEN_FIXTURES, type PitchScreen05, type PitchScreen06 } from "@hitech/contracts";

type PitchStatus =
  PitchScreen05["foundationStatus"]["rbacMatrixSnapshot"]["rows"][number]["status"];

export const DEMO_ROLES = ["admin", "operator", "auditor", "supervisor"] as const;
export const DEMO_SUPPLIER_STATUSES = ["APPROVED", "ACTIVE", "BLOCKED"] as const;
export const DEMO_DOCUMENT_LIFECYCLES = ["PRESENT", "MISSING", "EXPIRED"] as const;
export const DEMO_SHIPMENT_STATES = ["ARRIVED", "DOCS_HOLD", "RECEIVED", "QUARANTINE"] as const;

const SHIPMENT_TRANSITIONS: Readonly<Record<DemoShipmentState, readonly DemoShipmentState[]>> = {
  ARRIVED: ["ARRIVED", "DOCS_HOLD", "RECEIVED", "QUARANTINE"],
  DOCS_HOLD: ["DOCS_HOLD", "ARRIVED", "RECEIVED", "QUARANTINE"],
  RECEIVED: ["RECEIVED", "QUARANTINE"],
  QUARANTINE: ["QUARANTINE", "ARRIVED", "DOCS_HOLD", "RECEIVED"]
};

export type DemoRole = (typeof DEMO_ROLES)[number];
export type DemoSupplierStatus = (typeof DEMO_SUPPLIER_STATUSES)[number];
export type DemoDocumentLifecycle = (typeof DEMO_DOCUMENT_LIFECYCLES)[number];
export type DemoShipmentState = (typeof DEMO_SHIPMENT_STATES)[number];

export type Role = "admin" | "operator" | "auditor";
export type SupplierStatus = "APPROVED" | "BLOCKED";
export type DocStatus = "PRESENT" | "MISSING" | "EXPIRED";
export type ShipmentState = "ARRIVED" | "DOCS_HOLD" | "RECEIVED" | "QUARANTINE";

export type DemoDocumentId = "COA" | "TEMP_REPORT" | "IMPORT_PERMIT";

export interface DemoDocumentDescriptor {
  readonly id: DemoDocumentId;
  readonly label: string;
  readonly critical: boolean;
}

export const DEMO_DOCUMENTS: readonly DemoDocumentDescriptor[] = [
  { id: "COA", label: "Certificate of Analysis", critical: true },
  { id: "TEMP_REPORT", label: "Temperature Report", critical: true },
  { id: "IMPORT_PERMIT", label: "Import Permit", critical: true }
];

export type DemoAction =
  | "ADVANCE"
  | "RESET"
  | "FORCE_QUARANTINE"
  | { readonly type: "SET_ROLE"; readonly role: DemoRole }
  | { readonly type: "SET_SUPPLIER_STATUS"; readonly supplierStatus: DemoSupplierStatus }
  | { readonly type: "TOGGLE_DOCS_COMPLETE" }
  | { readonly type: "TOGGLE_TEMP_EXCURSION" }
  | { readonly type: "SHIPMENT_ADVANCE"; readonly to: DemoShipmentState };

export type PitchDemoAction = DemoAction;

export type DemoActionLabel =
  | "ADVANCE"
  | "RESET"
  | "FORCE_QUARANTINE"
  | "SET_ROLE"
  | "SET_SUPPLIER_STATUS"
  | "TOGGLE_DOCS_COMPLETE"
  | "TOGGLE_TEMP_EXCURSION"
  | "SHIPMENT_ADVANCE";

export interface GuardEvaluation {
  readonly allowed: boolean;
  readonly reasons: readonly string[];
}

export interface DemoGuardsSnapshot {
  readonly role: DemoRole;
  readonly supplierStatus: DemoSupplierStatus;
  readonly docsComplete: boolean;
  readonly tempExcursion: boolean;
  readonly shipmentState: DemoShipmentState;
}

export interface DemoTransitionLogEntry {
  readonly id: string;
  readonly sequence: number;
  readonly action: DemoActionLabel;
  readonly from: DemoShipmentState;
  readonly to: DemoShipmentState;
  readonly reason: string;
  readonly guardsSnapshot: DemoGuardsSnapshot;
}

export interface PitchDemoState {
  readonly role: DemoRole;
  readonly supplierStatus: DemoSupplierStatus;
  readonly supplierApproved: boolean;
  readonly docsComplete: boolean;
  readonly tempExcursion: boolean;
  readonly documents: Readonly<Record<DemoDocumentId, DemoDocumentLifecycle>>;
  readonly shipmentState: DemoShipmentState;
  readonly transitionLog: readonly DemoTransitionLogEntry[];
}

export interface CreateDemoStateInput {
  readonly role?: DemoRole;
  readonly supplierStatus?: DemoSupplierStatus;
  readonly docsComplete?: boolean;
  readonly tempExcursion?: boolean;
  readonly shipmentState?: DemoShipmentState;
  readonly documents?: Partial<Record<DemoDocumentId, DemoDocumentLifecycle>>;
}

export interface DemoGuardIndicators {
  readonly docs_complete: boolean;
  readonly temp_excursion: boolean;
  readonly supplier_status: boolean;
  readonly role_gating: boolean;
}

export interface DemoHoldState {
  readonly active: boolean;
  readonly reasons: readonly string[];
}

export type DemoReceiveReason =
  | "OK"
  | "ROLE_FORBIDDEN"
  | "DOCS_INCOMPLETE"
  | "SUPPLIER_BLOCKED"
  | "TEMP_EXCURSION";

export interface DemoReceiveTransitionInput {
  readonly role: DemoRole;
  readonly docsComplete: boolean;
  readonly tempExcursion: boolean;
  readonly supplierStatus: DemoSupplierStatus;
  readonly currentState: DemoShipmentState;
}

export interface DemoReceiveTransitionResult {
  readonly allowed: boolean;
  readonly nextState: DemoShipmentState;
  readonly reason: DemoReceiveReason;
}

export interface DemoAffordances {
  readonly canReceive: boolean;
  readonly canProceedToShipments: boolean;
  readonly canApproveRelease: boolean;
  readonly hasCriticalDocumentHold: boolean;
  readonly nextShipmentState: DemoShipmentState;
  readonly receiveReason: DemoReceiveReason;
}

export interface PitchDemoScreens {
  readonly inventoryFoundation: PitchScreen05;
  readonly shipmentsReceiving: PitchScreen06;
}

const DEFAULT_DOCUMENTS: Readonly<Record<DemoDocumentId, DemoDocumentLifecycle>> = {
  COA: "PRESENT",
  TEMP_REPORT: "PRESENT",
  IMPORT_PERMIT: "PRESENT"
};

function firstDocumentValue(
  documents: Partial<Record<DemoDocumentId, DemoDocumentLifecycle>> | undefined,
  key: DemoDocumentId
): DemoDocumentLifecycle {
  return documents?.[key] ?? DEFAULT_DOCUMENTS[key];
}

function computeDocsComplete(
  documents: Readonly<Record<DemoDocumentId, DemoDocumentLifecycle>>
): boolean {
  return DEMO_DOCUMENTS.every(
    (document) => !document.critical || documents[document.id] === "PRESENT"
  );
}

function normalizeState(
  state: Omit<PitchDemoState, "supplierApproved" | "docsComplete">
): PitchDemoState {
  const supplierApproved = state.supplierStatus !== "BLOCKED";
  const docsComplete = computeDocsComplete(state.documents);
  return {
    ...state,
    supplierApproved,
    docsComplete
  };
}

function buildGuardsSnapshot(state: PitchDemoState): DemoGuardsSnapshot {
  return {
    role: state.role,
    supplierStatus: state.supplierStatus,
    docsComplete: state.docsComplete,
    tempExcursion: state.tempExcursion,
    shipmentState: state.shipmentState
  };
}

function appendTransition(
  state: PitchDemoState,
  action: DemoActionLabel,
  to: DemoShipmentState,
  reason: string
): PitchDemoState {
  const nextState = normalizeState({
    ...state,
    shipmentState: to,
    transitionLog: [
      ...state.transitionLog,
      {
        id: `transition-${state.transitionLog.length + 1}`,
        sequence: state.transitionLog.length + 1,
        action,
        from: state.shipmentState,
        to,
        reason,
        guardsSnapshot: buildGuardsSnapshot(state)
      }
    ]
  });

  return nextState;
}

function nextDocumentLifecycle(current: DemoDocumentLifecycle): DemoDocumentLifecycle {
  if (current === "PRESENT") {
    return "MISSING";
  }
  if (current === "MISSING") {
    return "EXPIRED";
  }
  return "PRESENT";
}

function mapDocumentLifecycleToPitchStatus(lifecycle: DemoDocumentLifecycle): PitchStatus {
  if (lifecycle === "PRESENT") {
    return "DONE";
  }
  if (lifecycle === "MISSING") {
    return "MISSING";
  }
  return "IN_PROGRESS";
}

function coerceRole(value: string | undefined): DemoRole {
  if (!value) {
    return "operator";
  }
  const normalized = value.trim().toLowerCase();
  if (normalized === "auditor") {
    return "auditor";
  }
  if (normalized === "admin") {
    return "admin";
  }
  if (normalized === "supervisor") {
    return "operator";
  }
  return "operator";
}

function coerceSupplierStatus(value: string | undefined): DemoSupplierStatus {
  if (!value) {
    return "ACTIVE";
  }
  const normalized = value.trim().toUpperCase();
  if (normalized === "BLOCKED") {
    return "BLOCKED";
  }
  if (normalized === "ACTIVE") {
    return "ACTIVE";
  }
  return "APPROVED";
}

function coerceBoolean(value: string | undefined, fallback = false): boolean {
  if (!value) {
    return fallback;
  }
  const normalized = value.trim().toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) {
    return true;
  }
  if (["0", "false", "no", "off"].includes(normalized)) {
    return false;
  }
  return fallback;
}

function readFirstParam(value: DemoSearchParamValue): string | undefined {
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    return typeof value[0] === "string" ? value[0] : undefined;
  }
  return undefined;
}

function resolveRbacStatusForRole(
  role: DemoRole,
  rowRole: PitchScreen05["foundationStatus"]["rbacMatrixSnapshot"]["rows"][number]["role"]
): PitchStatus {
  if (role === "admin") {
    return "DONE";
  }
  if (role === "operator") {
    return rowRole === "Warehouse Operator" ? "DONE" : "PENDING";
  }
  if (role === "supervisor") {
    return rowRole === "Quality Inspector" ? "IN_PROGRESS" : "DONE";
  }
  return "PENDING";
}

export function formatRoleLabel(role: DemoRole): string {
  if (role === "admin") {
    return "Admin";
  }
  if (role === "operator") {
    return "Operator";
  }
  if (role === "supervisor") {
    return "Supervisor";
  }
  return "Auditor";
}

export function formatDocumentLifecycleLabel(lifecycle: DemoDocumentLifecycle): string {
  if (lifecycle === "PRESENT") {
    return "present";
  }
  if (lifecycle === "MISSING") {
    return "missing";
  }
  return "expired";
}

export function createInitialDemoState(seed: CreateDemoStateInput = {}): PitchDemoState {
  const mergedDocuments: Record<DemoDocumentId, DemoDocumentLifecycle> = {
    COA: firstDocumentValue(seed.documents, "COA"),
    TEMP_REPORT: firstDocumentValue(seed.documents, "TEMP_REPORT"),
    IMPORT_PERMIT: firstDocumentValue(seed.documents, "IMPORT_PERMIT")
  };

  const base = normalizeState({
    role: seed.role ?? "operator",
    supplierStatus: seed.supplierStatus ?? "ACTIVE",
    tempExcursion: seed.tempExcursion ?? false,
    shipmentState: seed.shipmentState ?? "ARRIVED",
    documents: mergedDocuments,
    transitionLog: []
  });

  if (typeof seed.docsComplete === "boolean") {
    return setDocsComplete(base, seed.docsComplete);
  }

  return base;
}

export const DEFAULT_PITCH_DEMO_STATE: PitchDemoState = createInitialDemoState();

export function createDemoState(seed?: CreateDemoStateInput): PitchDemoState {
  return createInitialDemoState(seed);
}

export function setRole(state: PitchDemoState, role: DemoRole): PitchDemoState {
  return normalizeState({ ...state, role });
}

export function setSupplierStatus(
  state: PitchDemoState,
  supplierStatus: DemoSupplierStatus
): PitchDemoState {
  return normalizeState({ ...state, supplierStatus });
}

export function toggleSupplierStatus(state: PitchDemoState): PitchDemoState {
  return setSupplierStatus(state, state.supplierStatus === "BLOCKED" ? "ACTIVE" : "BLOCKED");
}

export function setTempExcursion(state: PitchDemoState, nextValue: boolean): PitchDemoState {
  const updated = normalizeState({ ...state, tempExcursion: nextValue });

  if (nextValue && updated.shipmentState !== "QUARANTINE") {
    return appendTransition(
      updated,
      "FORCE_QUARANTINE",
      "QUARANTINE",
      "Temp excursion forced immediate quarantine"
    );
  }

  return updated;
}

export function setDocsComplete(state: PitchDemoState, nextValue: boolean): PitchDemoState {
  const documents: Record<DemoDocumentId, DemoDocumentLifecycle> = nextValue
    ? { COA: "PRESENT", TEMP_REPORT: "PRESENT", IMPORT_PERMIT: "PRESENT" }
    : { ...state.documents, IMPORT_PERMIT: "MISSING" };

  return normalizeState({
    ...state,
    documents
  });
}

export function toggleDocsComplete(state: PitchDemoState): PitchDemoState {
  return setDocsComplete(state, !state.docsComplete);
}

export function cycleDocumentLifecycle(
  state: PitchDemoState,
  documentId: DemoDocumentId
): PitchDemoState {
  const current = state.documents[documentId];
  const documents: Record<DemoDocumentId, DemoDocumentLifecycle> = {
    ...state.documents,
    [documentId]: nextDocumentLifecycle(current)
  };

  return normalizeState({
    ...state,
    documents
  });
}

export function canPerformReceivingAction(role: DemoRole): boolean {
  return role !== "auditor";
}

export function resolveReceiveTransition(
  input: DemoReceiveTransitionInput
): DemoReceiveTransitionResult {
  if (input.tempExcursion) {
    return {
      allowed: false,
      nextState: "QUARANTINE",
      reason: "TEMP_EXCURSION"
    };
  }

  if (!canPerformReceivingAction(input.role)) {
    return {
      allowed: false,
      nextState: input.currentState,
      reason: "ROLE_FORBIDDEN"
    };
  }

  if (input.supplierStatus === "BLOCKED") {
    return {
      allowed: false,
      nextState: "DOCS_HOLD",
      reason: "SUPPLIER_BLOCKED"
    };
  }

  if (!input.docsComplete) {
    return {
      allowed: false,
      nextState: "DOCS_HOLD",
      reason: "DOCS_INCOMPLETE"
    };
  }

  return {
    allowed: true,
    nextState: "RECEIVED",
    reason: "OK"
  };
}

export function canReceive(
  state: Pick<
    PitchDemoState,
    "role" | "docsComplete" | "tempExcursion" | "supplierStatus" | "shipmentState"
  >
): GuardEvaluation {
  const reasons: string[] = [];

  if (state.role === "auditor") {
    reasons.push("ROLE_FORBIDDEN");
  }

  if (state.supplierStatus === "BLOCKED" && state.role !== "admin") {
    reasons.push("SUPPLIER_BLOCKED");
  }

  if (!state.docsComplete) {
    reasons.push("DOCS_INCOMPLETE");
  }

  if (state.tempExcursion) {
    reasons.push("TEMP_EXCURSION");
  }

  if (state.shipmentState === "QUARANTINE") {
    reasons.push("QUARANTINE_LOCKED");
  }

  return {
    allowed: reasons.length === 0,
    reasons
  };
}

export function canAdvanceTo(
  state: Pick<
    PitchDemoState,
    "role" | "docsComplete" | "tempExcursion" | "supplierStatus" | "shipmentState"
  >,
  next: DemoShipmentState
): GuardEvaluation {
  const reasons: string[] = [];
  const allowedTargets = SHIPMENT_TRANSITIONS[state.shipmentState];

  if (!allowedTargets.includes(next)) {
    reasons.push(`INVALID_TRANSITION_${state.shipmentState}_TO_${next}`);
  }

  if (state.role === "auditor") {
    reasons.push("ROLE_FORBIDDEN");
  }

  if (state.tempExcursion && next !== "QUARANTINE") {
    reasons.push("TEMP_EXCURSION_FORCES_QUARANTINE");
  }

  if (next === "RECEIVED") {
    const receive = canReceive(state);
    reasons.push(...receive.reasons.map((reason) => `RECEIVE_GUARD_${reason}`));
    if (!state.docsComplete) {
      reasons.push("DOCS_INCOMPLETE_ROUTE_DOCS_HOLD");
    }
  }

  return {
    allowed: reasons.length === 0,
    reasons
  };
}

export function getGuardBadges(
  state: Pick<
    PitchDemoState,
    "role" | "docsComplete" | "tempExcursion" | "supplierStatus" | "shipmentState"
  >
): readonly { readonly label: string; readonly ok: boolean }[] {
  const receiveGate = canReceive(state);
  return [
    { label: "role_gating", ok: state.role !== "auditor" },
    { label: "supplier_status", ok: state.supplierStatus !== "BLOCKED" || state.role === "admin" },
    { label: "docs_complete", ok: state.docsComplete },
    { label: "temp_excursion", ok: !state.tempExcursion },
    { label: "can_receive", ok: receiveGate.allowed }
  ];
}

export function getAllowedActions(state: PitchDemoState): readonly string[] {
  const actions: string[] = ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"];

  if (state.role !== "auditor") {
    actions.push("TOGGLE_DOCS_COMPLETE", "TOGGLE_TEMP_EXCURSION");
  }

  for (const candidate of DEMO_SHIPMENT_STATES) {
    if (canAdvanceTo(state, candidate).allowed) {
      actions.push(`SHIPMENT_ADVANCE:${candidate}`);
    }
  }

  return actions;
}

export function getGuardIndicators(state: PitchDemoState): DemoGuardIndicators {
  return {
    docs_complete: state.docsComplete,
    temp_excursion: !state.tempExcursion,
    supplier_status: state.supplierStatus !== "BLOCKED",
    role_gating: canPerformReceivingAction(state.role)
  };
}

export function getHoldState(state: PitchDemoState): DemoHoldState {
  const reasons: string[] = [];
  if (!state.docsComplete) {
    reasons.push("Critical customs documents are incomplete.");
  }
  if (state.supplierStatus === "BLOCKED") {
    reasons.push("Supplier status is BLOCKED.");
  }
  if (state.tempExcursion) {
    reasons.push("Temperature excursion requires quarantine.");
  }
  if (state.role === "auditor") {
    reasons.push("Auditor role is read-only.");
  }
  return {
    active: reasons.length > 0,
    reasons
  };
}

export function getDemoAffordances(state: PitchDemoState): DemoAffordances {
  const transition = resolveReceiveTransition({
    role: state.role,
    docsComplete: state.docsComplete,
    tempExcursion: state.tempExcursion,
    supplierStatus: state.supplierStatus,
    currentState: state.shipmentState
  });

  return {
    canReceive: transition.allowed,
    canProceedToShipments: state.supplierStatus !== "BLOCKED",
    canApproveRelease: state.role === "admin",
    hasCriticalDocumentHold: !state.docsComplete || state.supplierStatus === "BLOCKED",
    nextShipmentState: transition.nextState,
    receiveReason: transition.reason
  };
}

export function applyAction(state: PitchDemoState, action: DemoAction): PitchDemoState {
  if (action === "RESET") {
    const reset = createInitialDemoState();
    const sequence = state.transitionLog.length + 1;
    return {
      ...reset,
      transitionLog: [
        ...state.transitionLog,
        {
          id: `transition-${sequence}`,
          sequence,
          action: "RESET",
          from: state.shipmentState,
          to: reset.shipmentState,
          reason: "State reset to baseline",
          guardsSnapshot: buildGuardsSnapshot(reset)
        }
      ]
    };
  }

  if (typeof action === "object") {
    if (action.type === "SET_ROLE") {
      const next = setRole(state, action.role);
      return appendTransition(next, "SET_ROLE", state.shipmentState, `Role set to ${action.role}`);
    }

    if (state.role === "auditor") {
      return appendTransition(
        state,
        action.type === "SHIPMENT_ADVANCE" ? "SHIPMENT_ADVANCE" : action.type,
        state.shipmentState,
        "Action denied: auditor is read-only"
      );
    }

    if (action.type === "SET_SUPPLIER_STATUS") {
      const next = setSupplierStatus(state, action.supplierStatus);
      return appendTransition(
        next,
        "SET_SUPPLIER_STATUS",
        state.shipmentState,
        `Supplier set to ${action.supplierStatus}`
      );
    }

    if (action.type === "TOGGLE_DOCS_COMPLETE") {
      const next = toggleDocsComplete(state);
      return appendTransition(
        next,
        "TOGGLE_DOCS_COMPLETE",
        state.shipmentState,
        "Docs completeness toggled"
      );
    }

    if (action.type === "TOGGLE_TEMP_EXCURSION") {
      const next = setTempExcursion(state, !state.tempExcursion);
      return appendTransition(
        next,
        "TOGGLE_TEMP_EXCURSION",
        state.shipmentState,
        "Temp excursion toggled"
      );
    }

    const requested = action.to;
    const target = state.tempExcursion
      ? "QUARANTINE"
      : !state.docsComplete && requested === "RECEIVED"
        ? "DOCS_HOLD"
        : requested;
    const guard = canAdvanceTo(state, target);
    if (!guard.allowed) {
      return appendTransition(
        state,
        "SHIPMENT_ADVANCE",
        state.shipmentState,
        `Advance to ${requested} blocked: ${guard.reasons.join(", ")}`
      );
    }
    return appendTransition(state, "SHIPMENT_ADVANCE", target, `Advance to ${target} approved`);
  }

  if (action === "FORCE_QUARANTINE") {
    if (state.role === "auditor") {
      return appendTransition(
        state,
        "FORCE_QUARANTINE",
        state.shipmentState,
        "Action denied: auditor is read-only"
      );
    }
    return appendTransition(state, "FORCE_QUARANTINE", "QUARANTINE", "Manual quarantine trigger");
  }

  if (state.role === "auditor") {
    return appendTransition(
      state,
      "ADVANCE",
      state.shipmentState,
      "Action denied: auditor is read-only"
    );
  }

  const transition = resolveReceiveTransition({
    role: state.role,
    docsComplete: state.docsComplete,
    tempExcursion: state.tempExcursion,
    supplierStatus: state.supplierStatus,
    currentState: state.shipmentState
  });

  const reason = transition.allowed
    ? "Advance succeeded"
    : `Advance blocked by ${transition.reason}`;

  return appendTransition(state, "ADVANCE", transition.nextState, reason);
}

export const applyPitchDemoAction = applyAction;

export type DemoSearchParamValue = string | readonly string[] | undefined;
export type DemoSearchParams = Readonly<Record<string, DemoSearchParamValue>>;

export function parseDemoStateFromSearchParams(
  searchParams: DemoSearchParams = {}
): Omit<DemoReceiveTransitionInput, "currentState"> {
  const role = coerceRole(readFirstParam(searchParams["role"]));
  const supplierStatus = coerceSupplierStatus(readFirstParam(searchParams["supplierStatus"]));
  const docsComplete = coerceBoolean(readFirstParam(searchParams["docsComplete"]), false);
  const tempExcursion = coerceBoolean(readFirstParam(searchParams["tempExcursion"]), false);

  return {
    role,
    supplierStatus,
    docsComplete,
    tempExcursion
  };
}

export function buildDemoScreens(state: PitchDemoState): PitchDemoScreens {
  const inventoryBase = PITCH_SCREEN_FIXTURES["05-inventory-foundation"];
  const shipmentsBase = PITCH_SCREEN_FIXTURES["06-shipments-receiving"];
  const affordances = getDemoAffordances(state);

  const inventoryFoundation: PitchScreen05 = {
    ...inventoryBase,
    foundationStatus: {
      ...inventoryBase.foundationStatus,
      rbacMatrixSnapshot: {
        ...inventoryBase.foundationStatus.rbacMatrixSnapshot,
        rows: inventoryBase.foundationStatus.rbacMatrixSnapshot.rows.map((row) => ({
          ...row,
          status: resolveRbacStatusForRole(state.role, row.role)
        }))
      },
      supplierOnboardingStatus: {
        ...inventoryBase.foundationStatus.supplierOnboardingStatus,
        suppliers: inventoryBase.foundationStatus.supplierOnboardingStatus.suppliers.map(
          (supplier) => ({
            ...supplier,
            status: state.supplierStatus !== "BLOCKED" ? "DONE" : "MISSING"
          })
        )
      }
    },
    documentVaultBaseline: {
      ...inventoryBase.documentVaultBaseline,
      requiredDocs: inventoryBase.documentVaultBaseline.requiredDocs.map((document) => {
        if (document.document === "Certificate of Origin") {
          return {
            ...document,
            status: mapDocumentLifecycleToPitchStatus(state.documents.COA)
          };
        }
        if (document.document === "Import Permit") {
          return {
            ...document,
            status: mapDocumentLifecycleToPitchStatus(state.documents.IMPORT_PERMIT)
          };
        }
        return {
          ...document,
          status: state.docsComplete ? "DONE" : document.status
        };
      })
    }
  };

  const shipmentsReceiving: PitchScreen06 = {
    ...shipmentsBase,
    shipmentControlBoard: {
      ...shipmentsBase.shipmentControlBoard,
      placeholders: shipmentsBase.shipmentControlBoard.placeholders.map((placeholder) => {
        if (placeholder.label === "ATA") {
          return {
            ...placeholder,
            value:
              state.shipmentState === "RECEIVED" || state.shipmentState === "QUARANTINE"
                ? "ATA-VERIFIED"
                : "ATA-TBD"
          };
        }
        return placeholder;
      }),
      customsPackCompleteness: {
        ...shipmentsBase.shipmentControlBoard.customsPackCompleteness,
        status: state.docsComplete ? "DONE" : "PENDING"
      }
    },
    receivingFlow: {
      ...shipmentsBase.receivingFlow,
      states: shipmentsBase.receivingFlow.states.map((step) => {
        if (step.code === state.shipmentState) {
          return {
            ...step,
            note: `${step.note} (current)`
          };
        }
        if (step.code === "DOCS_HOLD" && !state.docsComplete) {
          return {
            ...step,
            note: "Critical docs missing. Receiving stays in DOCS_HOLD."
          };
        }
        if (step.code === "RECEIVED" && affordances.canReceive) {
          return {
            ...step,
            note: "All guards passed. Receiving can progress to RECEIVED."
          };
        }
        if (step.code === "QUARANTINE" && state.tempExcursion) {
          return {
            ...step,
            note: "Temp excursion active. Quarantine is mandatory."
          };
        }
        return step;
      })
    },
    mismatchHandling: {
      ...shipmentsBase.mismatchHandling,
      qtyLotMismatch: state.tempExcursion
        ? "Temp excursion triggers deviation + quarantine workflow."
        : shipmentsBase.mismatchHandling.qtyLotMismatch
    },
    nextGate: {
      ...shipmentsBase.nextGate,
      text: shipmentsBase.nextGate.text
    }
  };

  return {
    inventoryFoundation,
    shipmentsReceiving
  };
}

// BEGIN INDUSTRIAL_CATALOG
export interface IndustrialCatalogState {
  readonly role: Role;
  readonly supplierStatus: SupplierStatus;
  readonly docsComplete: boolean;
  readonly tempExcursion: boolean;
  readonly shipmentState: ShipmentState;
}

export interface IndustrialCatalogTransition {
  readonly to: ShipmentState;
  readonly allowed: boolean;
  readonly reasons: readonly string[];
}

export interface IndustrialCatalogEntry {
  readonly id: string;
  readonly key: string;
  readonly state: IndustrialCatalogState;
  readonly receiveGate: GuardEvaluation;
  readonly guardBadges: readonly { readonly label: string; readonly ok: boolean }[];
  readonly allowedActions: readonly string[];
  readonly transitions: readonly IndustrialCatalogTransition[];
}

export interface IndustrialStoryboard {
  readonly id: string;
  readonly entryId: string;
  readonly key: string;
  readonly focus: string;
  readonly title: string;
  readonly initialState: IndustrialCatalogState;
  readonly actions: readonly DemoAction[];
  readonly notes: readonly string[];
}

export const INDUSTRIAL_CATALOG_ENTRIES: readonly IndustrialCatalogEntry[] = [
  {
    id: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_QUARANTINE_LOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_QUARANTINE_LOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE", "RECEIVE_GUARD_TEMP_EXCURSION"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: true,
      reasons: []
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: true
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:RECEIVED",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_QUARANTINE_LOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_DOCS_INCOMPLETE", "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["DOCS_INCOMPLETE", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_SUPPLIER_BLOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_SUPPLIER_BLOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_SUPPLIER_BLOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["RECEIVE_GUARD_SUPPLIER_BLOCKED", "RECEIVE_GUARD_QUARANTINE_LOCKED"]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: true
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: [
      "RESET",
      "SET_ROLE",
      "SET_SUPPLIER_STATUS",
      "TOGGLE_DOCS_COMPLETE",
      "TOGGLE_TEMP_EXCURSION",
      "SHIPMENT_ADVANCE:ARRIVED",
      "SHIPMENT_ADVANCE:DOCS_HOLD",
      "SHIPMENT_ADVANCE:QUARANTINE"
    ],
    transitions: [
      {
        to: "ARRIVED",
        allowed: true,
        reasons: []
      },
      {
        to: "DOCS_HOLD",
        allowed: true,
        reasons: []
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: true,
        reasons: []
      }
    ]
  },
  {
    id: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_ARRIVED",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "RECEIVE_GUARD_ROLE_FORBIDDEN"]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "RECEIVE_GUARD_ROLE_FORBIDDEN"]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "RECEIVE_GUARD_ROLE_FORBIDDEN"]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_ARRIVED",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "DOCS_INCOMPLETE", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: true
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_ARRIVED",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "TEMP_EXCURSION", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: true
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_QUARANTINE_LOCKED"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "TEMP_EXCURSION"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_ARRIVED",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: [
          "INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD",
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE"
        ]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: [
        "ROLE_FORBIDDEN",
        "SUPPLIER_BLOCKED",
        "DOCS_INCOMPLETE",
        "TEMP_EXCURSION",
        "QUARANTINE_LOCKED"
      ]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: false
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN", "TEMP_EXCURSION_FORCES_QUARANTINE"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "TEMP_EXCURSION_FORCES_QUARANTINE",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_TEMP_EXCURSION",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_ARRIVED", "ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["INVALID_TRANSITION_RECEIVED_TO_DOCS_HOLD", "ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  },
  {
    id: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    state: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    receiveGate: {
      allowed: false,
      reasons: ["ROLE_FORBIDDEN", "SUPPLIER_BLOCKED", "DOCS_INCOMPLETE", "QUARANTINE_LOCKED"]
    },
    guardBadges: [
      {
        label: "role_gating",
        ok: false
      },
      {
        label: "supplier_status",
        ok: false
      },
      {
        label: "docs_complete",
        ok: false
      },
      {
        label: "temp_excursion",
        ok: true
      },
      {
        label: "can_receive",
        ok: false
      }
    ],
    allowedActions: ["RESET", "SET_ROLE", "SET_SUPPLIER_STATUS"],
    transitions: [
      {
        to: "ARRIVED",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "DOCS_HOLD",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      },
      {
        to: "RECEIVED",
        allowed: false,
        reasons: [
          "ROLE_FORBIDDEN",
          "RECEIVE_GUARD_ROLE_FORBIDDEN",
          "RECEIVE_GUARD_SUPPLIER_BLOCKED",
          "RECEIVE_GUARD_DOCS_INCOMPLETE",
          "RECEIVE_GUARD_QUARANTINE_LOCKED",
          "DOCS_INCOMPLETE_ROUTE_DOCS_HOLD"
        ]
      },
      {
        to: "QUARANTINE",
        allowed: false,
        reasons: ["ROLE_FORBIDDEN"]
      }
    ]
  }
];

export const INDUSTRIAL_STORYBOARDS: readonly IndustrialStoryboard[] = [
  {
    id: "IND_SB_00001",
    entryId: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00002",
    entryId: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00003",
    entryId: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00004",
    entryId: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00005",
    entryId: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00006",
    entryId: "IND_STATE_0001",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00007",
    entryId: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00008",
    entryId: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00009",
    entryId: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00010",
    entryId: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00011",
    entryId: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00012",
    entryId: "IND_STATE_0002",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00013",
    entryId: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00014",
    entryId: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00015",
    entryId: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00016",
    entryId: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00017",
    entryId: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00018",
    entryId: "IND_STATE_0003",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00019",
    entryId: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00020",
    entryId: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00021",
    entryId: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00022",
    entryId: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00023",
    entryId: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00024",
    entryId: "IND_STATE_0004",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00025",
    entryId: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00026",
    entryId: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00027",
    entryId: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00028",
    entryId: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00029",
    entryId: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00030",
    entryId: "IND_STATE_0005",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00031",
    entryId: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00032",
    entryId: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00033",
    entryId: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00034",
    entryId: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00035",
    entryId: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00036",
    entryId: "IND_STATE_0006",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00037",
    entryId: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00038",
    entryId: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00039",
    entryId: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00040",
    entryId: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00041",
    entryId: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00042",
    entryId: "IND_STATE_0007",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00043",
    entryId: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00044",
    entryId: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00045",
    entryId: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00046",
    entryId: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00047",
    entryId: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00048",
    entryId: "IND_STATE_0008",
    key: "admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00049",
    entryId: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00050",
    entryId: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00051",
    entryId: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00052",
    entryId: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00053",
    entryId: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00054",
    entryId: "IND_STATE_0009",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00055",
    entryId: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00056",
    entryId: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00057",
    entryId: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00058",
    entryId: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00059",
    entryId: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00060",
    entryId: "IND_STATE_0010",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00061",
    entryId: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00062",
    entryId: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00063",
    entryId: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00064",
    entryId: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00065",
    entryId: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00066",
    entryId: "IND_STATE_0011",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00067",
    entryId: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00068",
    entryId: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00069",
    entryId: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00070",
    entryId: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00071",
    entryId: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00072",
    entryId: "IND_STATE_0012",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00073",
    entryId: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00074",
    entryId: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00075",
    entryId: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00076",
    entryId: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00077",
    entryId: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00078",
    entryId: "IND_STATE_0013",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00079",
    entryId: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00080",
    entryId: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00081",
    entryId: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00082",
    entryId: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00083",
    entryId: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00084",
    entryId: "IND_STATE_0014",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00085",
    entryId: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00086",
    entryId: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00087",
    entryId: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00088",
    entryId: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00089",
    entryId: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00090",
    entryId: "IND_STATE_0015",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00091",
    entryId: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00092",
    entryId: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00093",
    entryId: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00094",
    entryId: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00095",
    entryId: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00096",
    entryId: "IND_STATE_0016",
    key: "admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00097",
    entryId: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00098",
    entryId: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00099",
    entryId: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00100",
    entryId: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00101",
    entryId: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00102",
    entryId: "IND_STATE_0017",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00103",
    entryId: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00104",
    entryId: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00105",
    entryId: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00106",
    entryId: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00107",
    entryId: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00108",
    entryId: "IND_STATE_0018",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00109",
    entryId: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00110",
    entryId: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00111",
    entryId: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00112",
    entryId: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00113",
    entryId: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00114",
    entryId: "IND_STATE_0019",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00115",
    entryId: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00116",
    entryId: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00117",
    entryId: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00118",
    entryId: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00119",
    entryId: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00120",
    entryId: "IND_STATE_0020",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00121",
    entryId: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00122",
    entryId: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00123",
    entryId: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00124",
    entryId: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00125",
    entryId: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00126",
    entryId: "IND_STATE_0021",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00127",
    entryId: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00128",
    entryId: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00129",
    entryId: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00130",
    entryId: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00131",
    entryId: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00132",
    entryId: "IND_STATE_0022",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00133",
    entryId: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00134",
    entryId: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00135",
    entryId: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00136",
    entryId: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00137",
    entryId: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00138",
    entryId: "IND_STATE_0023",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00139",
    entryId: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00140",
    entryId: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00141",
    entryId: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00142",
    entryId: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00143",
    entryId: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00144",
    entryId: "IND_STATE_0024",
    key: "admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00145",
    entryId: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00146",
    entryId: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00147",
    entryId: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00148",
    entryId: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00149",
    entryId: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00150",
    entryId: "IND_STATE_0025",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00151",
    entryId: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00152",
    entryId: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00153",
    entryId: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00154",
    entryId: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00155",
    entryId: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00156",
    entryId: "IND_STATE_0026",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00157",
    entryId: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00158",
    entryId: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00159",
    entryId: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00160",
    entryId: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00161",
    entryId: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00162",
    entryId: "IND_STATE_0027",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00163",
    entryId: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00164",
    entryId: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00165",
    entryId: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00166",
    entryId: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00167",
    entryId: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00168",
    entryId: "IND_STATE_0028",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00169",
    entryId: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00170",
    entryId: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00171",
    entryId: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00172",
    entryId: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00173",
    entryId: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00174",
    entryId: "IND_STATE_0029",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00175",
    entryId: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00176",
    entryId: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00177",
    entryId: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00178",
    entryId: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00179",
    entryId: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00180",
    entryId: "IND_STATE_0030",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00181",
    entryId: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00182",
    entryId: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00183",
    entryId: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00184",
    entryId: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00185",
    entryId: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00186",
    entryId: "IND_STATE_0031",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00187",
    entryId: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00188",
    entryId: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00189",
    entryId: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00190",
    entryId: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00191",
    entryId: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00192",
    entryId: "IND_STATE_0032",
    key: "admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | admin|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "admin",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00193",
    entryId: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00194",
    entryId: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00195",
    entryId: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00196",
    entryId: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00197",
    entryId: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00198",
    entryId: "IND_STATE_0033",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00199",
    entryId: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00200",
    entryId: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00201",
    entryId: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00202",
    entryId: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00203",
    entryId: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00204",
    entryId: "IND_STATE_0034",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00205",
    entryId: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00206",
    entryId: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00207",
    entryId: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00208",
    entryId: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00209",
    entryId: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00210",
    entryId: "IND_STATE_0035",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00211",
    entryId: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00212",
    entryId: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00213",
    entryId: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00214",
    entryId: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00215",
    entryId: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00216",
    entryId: "IND_STATE_0036",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00217",
    entryId: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00218",
    entryId: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00219",
    entryId: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00220",
    entryId: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00221",
    entryId: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00222",
    entryId: "IND_STATE_0037",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00223",
    entryId: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00224",
    entryId: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00225",
    entryId: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00226",
    entryId: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00227",
    entryId: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00228",
    entryId: "IND_STATE_0038",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00229",
    entryId: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00230",
    entryId: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00231",
    entryId: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00232",
    entryId: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00233",
    entryId: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00234",
    entryId: "IND_STATE_0039",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00235",
    entryId: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00236",
    entryId: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00237",
    entryId: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00238",
    entryId: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00239",
    entryId: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00240",
    entryId: "IND_STATE_0040",
    key: "operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00241",
    entryId: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00242",
    entryId: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00243",
    entryId: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00244",
    entryId: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00245",
    entryId: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00246",
    entryId: "IND_STATE_0041",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00247",
    entryId: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00248",
    entryId: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00249",
    entryId: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00250",
    entryId: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00251",
    entryId: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00252",
    entryId: "IND_STATE_0042",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00253",
    entryId: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00254",
    entryId: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00255",
    entryId: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00256",
    entryId: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00257",
    entryId: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00258",
    entryId: "IND_STATE_0043",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00259",
    entryId: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00260",
    entryId: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00261",
    entryId: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00262",
    entryId: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00263",
    entryId: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00264",
    entryId: "IND_STATE_0044",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00265",
    entryId: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00266",
    entryId: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00267",
    entryId: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00268",
    entryId: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00269",
    entryId: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00270",
    entryId: "IND_STATE_0045",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00271",
    entryId: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00272",
    entryId: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00273",
    entryId: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00274",
    entryId: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00275",
    entryId: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00276",
    entryId: "IND_STATE_0046",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00277",
    entryId: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00278",
    entryId: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00279",
    entryId: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00280",
    entryId: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00281",
    entryId: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00282",
    entryId: "IND_STATE_0047",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00283",
    entryId: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00284",
    entryId: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00285",
    entryId: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00286",
    entryId: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00287",
    entryId: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00288",
    entryId: "IND_STATE_0048",
    key: "operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00289",
    entryId: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00290",
    entryId: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00291",
    entryId: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00292",
    entryId: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00293",
    entryId: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00294",
    entryId: "IND_STATE_0049",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00295",
    entryId: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00296",
    entryId: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00297",
    entryId: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00298",
    entryId: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00299",
    entryId: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00300",
    entryId: "IND_STATE_0050",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00301",
    entryId: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00302",
    entryId: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00303",
    entryId: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00304",
    entryId: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00305",
    entryId: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00306",
    entryId: "IND_STATE_0051",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00307",
    entryId: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00308",
    entryId: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00309",
    entryId: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00310",
    entryId: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00311",
    entryId: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00312",
    entryId: "IND_STATE_0052",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00313",
    entryId: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00314",
    entryId: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00315",
    entryId: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00316",
    entryId: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00317",
    entryId: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00318",
    entryId: "IND_STATE_0053",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00319",
    entryId: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00320",
    entryId: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00321",
    entryId: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00322",
    entryId: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00323",
    entryId: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00324",
    entryId: "IND_STATE_0054",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00325",
    entryId: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00326",
    entryId: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00327",
    entryId: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00328",
    entryId: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00329",
    entryId: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00330",
    entryId: "IND_STATE_0055",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00331",
    entryId: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00332",
    entryId: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00333",
    entryId: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00334",
    entryId: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00335",
    entryId: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00336",
    entryId: "IND_STATE_0056",
    key: "operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00337",
    entryId: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00338",
    entryId: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00339",
    entryId: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00340",
    entryId: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00341",
    entryId: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00342",
    entryId: "IND_STATE_0057",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00343",
    entryId: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00344",
    entryId: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00345",
    entryId: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00346",
    entryId: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00347",
    entryId: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00348",
    entryId: "IND_STATE_0058",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00349",
    entryId: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00350",
    entryId: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00351",
    entryId: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00352",
    entryId: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00353",
    entryId: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00354",
    entryId: "IND_STATE_0059",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00355",
    entryId: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00356",
    entryId: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00357",
    entryId: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00358",
    entryId: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00359",
    entryId: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00360",
    entryId: "IND_STATE_0060",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00361",
    entryId: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00362",
    entryId: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00363",
    entryId: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00364",
    entryId: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00365",
    entryId: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00366",
    entryId: "IND_STATE_0061",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00367",
    entryId: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00368",
    entryId: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00369",
    entryId: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00370",
    entryId: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00371",
    entryId: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00372",
    entryId: "IND_STATE_0062",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00373",
    entryId: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00374",
    entryId: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00375",
    entryId: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00376",
    entryId: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00377",
    entryId: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00378",
    entryId: "IND_STATE_0063",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00379",
    entryId: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00380",
    entryId: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00381",
    entryId: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00382",
    entryId: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00383",
    entryId: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00384",
    entryId: "IND_STATE_0064",
    key: "operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | operator|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "operator",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00385",
    entryId: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00386",
    entryId: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00387",
    entryId: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00388",
    entryId: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00389",
    entryId: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00390",
    entryId: "IND_STATE_0065",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00391",
    entryId: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00392",
    entryId: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00393",
    entryId: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00394",
    entryId: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00395",
    entryId: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00396",
    entryId: "IND_STATE_0066",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00397",
    entryId: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00398",
    entryId: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00399",
    entryId: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00400",
    entryId: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00401",
    entryId: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00402",
    entryId: "IND_STATE_0067",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00403",
    entryId: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00404",
    entryId: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00405",
    entryId: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00406",
    entryId: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00407",
    entryId: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00408",
    entryId: "IND_STATE_0068",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00409",
    entryId: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00410",
    entryId: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00411",
    entryId: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00412",
    entryId: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00413",
    entryId: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00414",
    entryId: "IND_STATE_0069",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00415",
    entryId: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00416",
    entryId: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00417",
    entryId: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00418",
    entryId: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00419",
    entryId: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00420",
    entryId: "IND_STATE_0070",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00421",
    entryId: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00422",
    entryId: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00423",
    entryId: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00424",
    entryId: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00425",
    entryId: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00426",
    entryId: "IND_STATE_0071",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00427",
    entryId: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00428",
    entryId: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00429",
    entryId: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00430",
    entryId: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00431",
    entryId: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00432",
    entryId: "IND_STATE_0072",
    key: "auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00433",
    entryId: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00434",
    entryId: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00435",
    entryId: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00436",
    entryId: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00437",
    entryId: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00438",
    entryId: "IND_STATE_0073",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00439",
    entryId: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00440",
    entryId: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00441",
    entryId: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00442",
    entryId: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00443",
    entryId: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00444",
    entryId: "IND_STATE_0074",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00445",
    entryId: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00446",
    entryId: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00447",
    entryId: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00448",
    entryId: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00449",
    entryId: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00450",
    entryId: "IND_STATE_0075",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00451",
    entryId: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00452",
    entryId: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00453",
    entryId: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00454",
    entryId: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00455",
    entryId: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00456",
    entryId: "IND_STATE_0076",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00457",
    entryId: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00458",
    entryId: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00459",
    entryId: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00460",
    entryId: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00461",
    entryId: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00462",
    entryId: "IND_STATE_0077",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00463",
    entryId: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00464",
    entryId: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00465",
    entryId: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00466",
    entryId: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00467",
    entryId: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00468",
    entryId: "IND_STATE_0078",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00469",
    entryId: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00470",
    entryId: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00471",
    entryId: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00472",
    entryId: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00473",
    entryId: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00474",
    entryId: "IND_STATE_0079",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00475",
    entryId: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00476",
    entryId: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00477",
    entryId: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00478",
    entryId: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00479",
    entryId: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00480",
    entryId: "IND_STATE_0080",
    key: "auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|APPROVED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "APPROVED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00481",
    entryId: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00482",
    entryId: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00483",
    entryId: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00484",
    entryId: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00485",
    entryId: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00486",
    entryId: "IND_STATE_0081",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00487",
    entryId: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00488",
    entryId: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00489",
    entryId: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00490",
    entryId: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00491",
    entryId: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00492",
    entryId: "IND_STATE_0082",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00493",
    entryId: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00494",
    entryId: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00495",
    entryId: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00496",
    entryId: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00497",
    entryId: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00498",
    entryId: "IND_STATE_0083",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00499",
    entryId: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00500",
    entryId: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00501",
    entryId: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00502",
    entryId: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00503",
    entryId: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00504",
    entryId: "IND_STATE_0084",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00505",
    entryId: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00506",
    entryId: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00507",
    entryId: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00508",
    entryId: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00509",
    entryId: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00510",
    entryId: "IND_STATE_0085",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00511",
    entryId: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00512",
    entryId: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00513",
    entryId: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00514",
    entryId: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00515",
    entryId: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00516",
    entryId: "IND_STATE_0086",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00517",
    entryId: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00518",
    entryId: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00519",
    entryId: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00520",
    entryId: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00521",
    entryId: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00522",
    entryId: "IND_STATE_0087",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00523",
    entryId: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00524",
    entryId: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00525",
    entryId: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00526",
    entryId: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00527",
    entryId: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00528",
    entryId: "IND_STATE_0088",
    key: "auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_COMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: true,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00529",
    entryId: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00530",
    entryId: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00531",
    entryId: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00532",
    entryId: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00533",
    entryId: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00534",
    entryId: "IND_STATE_0089",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00535",
    entryId: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00536",
    entryId: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00537",
    entryId: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00538",
    entryId: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00539",
    entryId: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00540",
    entryId: "IND_STATE_0090",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00541",
    entryId: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00542",
    entryId: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00543",
    entryId: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00544",
    entryId: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00545",
    entryId: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00546",
    entryId: "IND_STATE_0091",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00547",
    entryId: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00548",
    entryId: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00549",
    entryId: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00550",
    entryId: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00551",
    entryId: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00552",
    entryId: "IND_STATE_0092",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_ALERT|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: true,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00553",
    entryId: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00554",
    entryId: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00555",
    entryId: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00556",
    entryId: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00557",
    entryId: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00558",
    entryId: "IND_STATE_0093",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|ARRIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "ARRIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00559",
    entryId: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00560",
    entryId: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00561",
    entryId: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00562",
    entryId: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00563",
    entryId: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00564",
    entryId: "IND_STATE_0094",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|DOCS_HOLD",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "DOCS_HOLD"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00565",
    entryId: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00566",
    entryId: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00567",
    entryId: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00568",
    entryId: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00569",
    entryId: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00570",
    entryId: "IND_STATE_0095",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|RECEIVED",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "RECEIVED"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  },
  {
    id: "IND_SB_00571",
    entryId: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "receive_path",
    title: "Receive Path | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      "ADVANCE"
    ],
    notes: [
      "Evaluates direct receiving eligibility.",
      "Confirms quarantine escalation route.",
      "Replays default advance semantics."
    ]
  },
  {
    id: "IND_SB_00572",
    entryId: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "docs_cycle",
    title: "Docs Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      },
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      "ADVANCE"
    ],
    notes: [
      "Flips docs completeness guard.",
      "Attempts receive with docs pressure.",
      "Restores docs and retries."
    ]
  },
  {
    id: "IND_SB_00573",
    entryId: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "temp_cycle",
    title: "Temp Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "ARRIVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "QUARANTINE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      }
    ],
    notes: [
      "Activates temp excursion.",
      "Verifies forced quarantine behavior.",
      "Clears excursion for release path."
    ]
  },
  {
    id: "IND_SB_00574",
    entryId: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "supplier_cycle",
    title: "Supplier Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "BLOCKED"
      },
      "ADVANCE",
      {
        type: "SET_SUPPLIER_STATUS",
        supplierStatus: "APPROVED"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Forces supplier gate block.",
      "Attempts receive while blocked.",
      "Restores approved supplier and retries."
    ]
  },
  {
    id: "IND_SB_00575",
    entryId: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "role_cycle",
    title: "Role Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "SET_ROLE",
        role: "auditor"
      },
      "ADVANCE",
      {
        type: "SET_ROLE",
        role: "admin"
      },
      {
        type: "SHIPMENT_ADVANCE",
        to: "RECEIVED"
      }
    ],
    notes: [
      "Switches to auditor read-only mode.",
      "Confirms auditor advance denial.",
      "Restores admin override path."
    ]
  },
  {
    id: "IND_SB_00576",
    entryId: "IND_STATE_0096",
    key: "auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    focus: "reset_cycle",
    title: "Reset Cycle | auditor|BLOCKED|DOCS_INCOMPLETE|TEMP_STABLE|QUARANTINE",
    initialState: {
      role: "auditor",
      supplierStatus: "BLOCKED",
      docsComplete: false,
      tempExcursion: false,
      shipmentState: "QUARANTINE"
    },
    actions: [
      {
        type: "TOGGLE_DOCS_COMPLETE"
      },
      {
        type: "TOGGLE_TEMP_EXCURSION"
      },
      "RESET"
    ],
    notes: ["Mutates docs and temperature flags.", "Resets to baseline deterministically."]
  }
];

export const INDUSTRIAL_CATALOG_ENTRY_INDEX: Readonly<Record<string, IndustrialCatalogEntry>> =
  INDUSTRIAL_CATALOG_ENTRIES.reduce<Record<string, IndustrialCatalogEntry>>(
    (accumulator, entry) => {
      accumulator[entry.key] = entry;
      return accumulator;
    },
    {}
  );

export function getIndustrialCatalogEntryByKey(key: string): IndustrialCatalogEntry | null {
  return INDUSTRIAL_CATALOG_ENTRY_INDEX[key] ?? null;
}

export function getIndustrialStoryboardsForEntry(entryId: string): readonly IndustrialStoryboard[] {
  return INDUSTRIAL_STORYBOARDS.filter((storyboard) => storyboard.entryId === entryId);
}

export function makeCatalogSeedState(seed: IndustrialCatalogState): PitchDemoState {
  return createInitialDemoState({
    role: seed.role,
    supplierStatus: seed.supplierStatus,
    docsComplete: seed.docsComplete,
    tempExcursion: seed.tempExcursion,
    shipmentState: seed.shipmentState,
    documents: seed.docsComplete
      ? { COA: "PRESENT", TEMP_REPORT: "PRESENT", IMPORT_PERMIT: "PRESENT" }
      : { COA: "PRESENT", TEMP_REPORT: "PRESENT", IMPORT_PERMIT: "MISSING" }
  });
}

export function runIndustrialStoryboard(storyboardId: string): PitchDemoState | null {
  const storyboard = INDUSTRIAL_STORYBOARDS.find((entry) => entry.id === storyboardId);
  if (!storyboard) {
    return null;
  }

  return storyboard.actions.reduce<PitchDemoState>(
    (state, action) => applyAction(state, action),
    makeCatalogSeedState(storyboard.initialState)
  );
}
// END INDUSTRIAL_CATALOG

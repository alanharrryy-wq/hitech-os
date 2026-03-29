"use client";

import { create } from "zustand";
import {
  FOUNDATION_DEFAULT_FIELDS,
  FOUNDATION_DOCUMENTS,
  FOUNDATION_INCOTERM_RISK,
  FOUNDATION_LOT_CATALOG,
  FOUNDATION_RBAC_ROWS,
  FOUNDATION_SUPPLIERS,
  FOUNDATION_TEMPERATURE_EXCURSIONS
} from "./data";
import type {
  ComplianceChip,
  DocumentLifecycle,
  FoundationReadinessSnapshot,
  FoundationRole,
  HoldReason,
  InventoryFoundationComputed,
  InventoryFoundationFields,
  InventoryFoundationPanelContext,
  InventoryFoundationState,
  InventoryFoundationStore,
  ReadinessBreakdownItem,
  RbacStatusRow,
  SupplierLifecycle,
  SupplierProfile,
  VaultDocumentState
} from "./types";

const DOC_LIFECYCLE_ORDER: readonly DocumentLifecycle[] = [
  "present",
  "missing",
  "in-progress",
  "expired"
];

const DEFAULT_CRITICAL_STATUS: Readonly<Record<string, DocumentLifecycle>> = {
  "doc-coa": "present",
  "doc-temperature-report": "in-progress",
  "doc-import-permit": "missing",
  "doc-hs-classification": "present",
  "doc-certificate-origin": "present",
  "doc-packing-list": "present",
  "doc-commercial-invoice": "present"
};

const BASE_TS = Date.parse("2026-03-02T08:00:00.000Z");

function timestampFromSequence(sequence: number): string {
  return new Date(BASE_TS + sequence * 60_000).toISOString();
}

function normalizeFieldValue(value: string): string {
  return value.trim().toLowerCase();
}

function cycleLifecycle(lifecycle: DocumentLifecycle): DocumentLifecycle {
  const index = DOC_LIFECYCLE_ORDER.indexOf(lifecycle);
  const nextIndex = (index + 1) % DOC_LIFECYCLE_ORDER.length;
  return DOC_LIFECYCLE_ORDER[nextIndex] ?? "present";
}

function makeInitialDocumentStates(): Readonly<Record<string, VaultDocumentState>> {
  const states: Record<string, VaultDocumentState> = {};

  for (const document of FOUNDATION_DOCUMENTS) {
    const lifecycle = DEFAULT_CRITICAL_STATUS[document.id] ?? "present";
    states[document.id] = {
      documentId: document.id,
      lifecycle,
      touchedByRole: "operator",
      touchedAt: "2026-03-02T08:00:00.000Z",
      comment: "Bootstrapped from deterministic baseline."
    };
  }

  return states;
}

function getDocumentState(
  state: InventoryFoundationState,
  documentId: string
): VaultDocumentState | null {
  return state.documentStates[documentId] ?? null;
}

function resolveSupplierByCode(
  suppliers: readonly SupplierProfile[],
  code: string
): SupplierProfile | null {
  return suppliers.find((supplier) => supplier.code === code) ?? null;
}

function evaluateRbacRow(
  state: InventoryFoundationState,
  row: InventoryFoundationState["rbacRows"][number]
): RbacStatusRow {
  const reasons: string[] = [];
  let gate: "open" | "review" | "blocked" = row.defaultGate;

  if (state.role === "auditor" && row.role !== "auditor") {
    reasons.push("Auditor role is read-only for execution capabilities.");
    gate = "review";
  }

  const selectedSupplier = resolveSupplierByCode(state.suppliers, state.selectedSupplierCode);
  if (selectedSupplier?.lifecycle === "blocked" && row.role !== "auditor") {
    reasons.push("Selected supplier is BLOCKED.");
    gate = "blocked";
  }

  for (const capability of row.capabilities) {
    for (const neededDocument of capability.neededDocuments) {
      const docState = getDocumentState(state, neededDocument);
      if (!docState) {
        reasons.push(`${capability.label} missing ${neededDocument}.`);
        gate = "blocked";
        continue;
      }

      if (docState.lifecycle !== "present") {
        reasons.push(`${capability.label} gated by ${neededDocument} (${docState.lifecycle}).`);
        gate = "blocked";
      }
    }
  }

  if (row.role === "admin" && state.role !== "admin") {
    reasons.push("Admin approvals require admin runtime role.");
    gate = gate === "blocked" ? "blocked" : "review";
  }

  if (reasons.length === 0) {
    reasons.push("No active blockers.");
    gate = "open";
  }

  return {
    role: row.role,
    displayName: row.displayName,
    gate,
    reasons,
    capabilities: row.capabilities,
    tooltip: row.tooltip
  };
}

function summarizeRbacRows(rows: readonly RbacStatusRow[]): readonly string[] {
  const open = rows.filter((row) => row.gate === "open").length;
  const review = rows.filter((row) => row.gate === "review").length;
  const blocked = rows.filter((row) => row.gate === "blocked").length;

  const summary: string[] = [
    `${open} role(s) OPEN`,
    `${review} role(s) REVIEW`,
    `${blocked} role(s) BLOCKED`
  ];

  for (const row of rows) {
    if (row.gate !== "blocked") {
      continue;
    }
    summary.push(`${row.displayName}: ${row.reasons.slice(0, 2).join(" | ")}`);
  }

  return summary;
}

function buildComplianceChips(state: InventoryFoundationState): readonly ComplianceChip[] {
  const counters: Record<DocumentLifecycle, number> = {
    present: 0,
    missing: 0,
    "in-progress": 0,
    expired: 0
  };

  for (const value of Object.values(state.documentStates)) {
    counters[value.lifecycle] += 1;
  }

  return [
    { lifecycle: "present", count: counters.present, tone: "success" },
    { lifecycle: "in-progress", count: counters["in-progress"], tone: "accent" },
    { lifecycle: "missing", count: counters.missing, tone: "danger" },
    { lifecycle: "expired", count: counters.expired, tone: "warning" }
  ];
}

function buildHoldReasons(
  state: InventoryFoundationState,
  selectedSupplier: SupplierProfile | null
): readonly HoldReason[] {
  const reasons: HoldReason[] = [];

  for (const document of state.documents) {
    if (!document.critical) {
      continue;
    }

    const status = getDocumentState(state, document.id);
    if (!status || status.lifecycle === "present") {
      continue;
    }

    reasons.push({
      id: `hold-doc-${document.id}`,
      severity: status.lifecycle === "expired" ? "critical" : "major",
      reason: `${document.label} is ${status.lifecycle}.`,
      nextStep: document.actionPlaybook[0] ?? "Upload compliant revision."
    });
  }

  if (selectedSupplier?.lifecycle === "blocked") {
    reasons.push({
      id: "hold-supplier-blocked",
      severity: "critical",
      reason: `Supplier ${selectedSupplier.code} is BLOCKED.`,
      nextStep: "Re-open supplier onboarding and close CAPA before receiving."
    });
  }

  const unresolvedFields = Object.entries(state.fields).filter(([, value]) => value === "");
  if (unresolvedFields.length > 0) {
    reasons.push({
      id: "hold-fields-incomplete",
      severity: "major",
      reason: `${unresolvedFields.length} mandatory field(s) are empty.`,
      nextStep: "Complete SKU, lot, supplier and storage fields."
    });
  }

  const lot = FOUNDATION_LOT_CATALOG.find((entry) => entry.lot === state.fields.lot) ?? null;
  if (lot?.holdFlag) {
    reasons.push({
      id: "hold-lot-flag",
      severity: "major",
      reason: `${lot.lot} has an active hold flag from baseline lot catalog.`,
      nextStep: `Run release checklist after ${lot.releaseWindowHours}h stability window.`
    });
  }

  const lotExcursionCount = FOUNDATION_TEMPERATURE_EXCURSIONS.filter(
    (record) => record.lot === state.fields.lot && record.durationMinutes > 45
  ).length;
  if (lotExcursionCount > 0) {
    reasons.push({
      id: "hold-temp-excursions",
      severity: "major",
      reason: `${lotExcursionCount} temperature excursion event(s) exceed threshold.`,
      nextStep: "Keep lot in quarantine until QA trend review closes."
    });
  }

  return reasons;
}

function buildReadinessBreakdown(
  state: InventoryFoundationState,
  rbacRows: readonly RbacStatusRow[],
  selectedSupplier: SupplierProfile | null
): readonly ReadinessBreakdownItem[] {
  const populatedFieldCount = Object.values(state.fields).filter((value) => value !== "").length;
  const fieldScore = Math.round((populatedFieldCount / 8) * 25);

  const criticalDocuments = state.documents.filter((document) => document.critical);
  const criticalPresentCount = criticalDocuments.filter((document) => {
    const status = getDocumentState(state, document.id);
    return status?.lifecycle === "present";
  }).length;
  const documentsScore = Math.round((criticalPresentCount / Math.max(criticalDocuments.length, 1)) * 30);

  const openRbacCount = rbacRows.filter((row) => row.gate === "open").length;
  const rbacScore = Math.round((openRbacCount / Math.max(rbacRows.length, 1)) * 20);

  let supplierScore = 0;
  if (selectedSupplier) {
    const lifecycleWeight =
      selectedSupplier.lifecycle === "approved"
        ? 12
        : selectedSupplier.lifecycle === "active"
          ? 8
          : 0;
    const qaWeight = Math.min(8, Math.round(selectedSupplier.qaScore / 12));
    const excursionPenalty = Math.min(5, selectedSupplier.tempExcursions90d);
    supplierScore = Math.max(0, lifecycleWeight + qaWeight - excursionPenalty);
  }

  const incotermRisk = FOUNDATION_INCOTERM_RISK[state.fields.incoterm];
  const coldChainScore = Math.max(0, 25 - incotermRisk);

  return [
    {
      id: "fields",
      label: "Master data completeness",
      score: fieldScore,
      maxScore: 25,
      reason: `${populatedFieldCount}/8 key fields populated.`,
      nextAction: "Complete empty identifiers and storage controls."
    },
    {
      id: "documents",
      label: "Critical document vault",
      score: documentsScore,
      maxScore: 30,
      reason: `${criticalPresentCount}/${criticalDocuments.length} critical docs present.`,
      nextAction: "Resolve missing or expired critical files."
    },
    {
      id: "rbac",
      label: "RBAC execution readiness",
      score: rbacScore,
      maxScore: 20,
      reason: `${openRbacCount}/${rbacRows.length} role lanes open.`,
      nextAction: "Clear row blockers with missing doc evidence."
    },
    {
      id: "supplier",
      label: "Supplier onboarding health",
      score: supplierScore,
      maxScore: 20,
      reason: selectedSupplier
        ? `${selectedSupplier.code} ${selectedSupplier.lifecycle.toUpperCase()} | QA ${selectedSupplier.qaScore}`
        : "No supplier selected.",
      nextAction: "Activate supplier and close CAPA deltas."
    },
    {
      id: "cold-chain",
      label: "Incoterm + cold-chain risk",
      score: coldChainScore,
      maxScore: 25,
      reason: `${state.fields.incoterm} route risk baseline ${incotermRisk}.`,
      nextAction: "Use lower-risk term or tighten lane controls."
    }
  ];
}

function computeReadiness(
  state: InventoryFoundationState,
  rbacRows: readonly RbacStatusRow[],
  selectedSupplier: SupplierProfile | null
): FoundationReadinessSnapshot {
  const breakdown = buildReadinessBreakdown(state, rbacRows, selectedSupplier);
  const holdReasons = buildHoldReasons(state, selectedSupplier);
  const chips = buildComplianceChips(state);

  const totalScore = breakdown.reduce((total, item) => total + item.score, 0);
  const maxScore = breakdown.reduce((total, item) => total + item.maxScore, 0);
  const percentage = Math.round((totalScore / Math.max(maxScore, 1)) * 100);

  return {
    totalScore,
    maxScore,
    percentage,
    breakdown,
    holdReasons,
    chips
  };
}

function filterRbacRows(
  rows: readonly RbacStatusRow[],
  search: string,
  gateFilter: InventoryFoundationState["rbacGateFilter"]
): readonly RbacStatusRow[] {
  const normalized = normalizeFieldValue(search);

  return rows.filter((row) => {
    const gatePass = gateFilter === "all" || row.gate === gateFilter;
    if (!gatePass) {
      return false;
    }

    if (normalized.length === 0) {
      return true;
    }

    return (
      normalizeFieldValue(row.displayName).includes(normalized) ||
      row.capabilities.some((capability) => normalizeFieldValue(capability.label).includes(normalized))
    );
  });
}

function addTimelineEntry(
  current: InventoryFoundationState,
  kind: InventoryFoundationState["timeline"][number]["kind"],
  actorRole: FoundationRole,
  message: string,
  details: readonly string[]
): InventoryFoundationState {
  const sequence = current.timeline.length + 1;
  const entry = {
    id: `foundation-event-${sequence}`,
    kind,
    actorRole,
    at: timestampFromSequence(sequence),
    message,
    details
  } as const;

  return {
    ...current,
    timeline: [...current.timeline, entry]
  };
}

function withGateRecompute(
  current: InventoryFoundationState,
  actorRole: FoundationRole,
  summary: readonly string[]
): InventoryFoundationState {
  return addTimelineEntry(
    current,
    "gating.recompute",
    actorRole,
    "Recomputed readiness and RBAC gates",
    summary
  );
}

function createInitialState(): InventoryFoundationState {
  return {
    fields: FOUNDATION_DEFAULT_FIELDS,
    role: "operator",
    suppliers: FOUNDATION_SUPPLIERS,
    selectedSupplierCode: FOUNDATION_DEFAULT_FIELDS.supplierCode,
    documents: FOUNDATION_DOCUMENTS,
    documentStates: makeInitialDocumentStates(),
    rbacRows: FOUNDATION_RBAC_ROWS,
    rbacSearch: "",
    rbacGateFilter: "all",
    timeline: [
      {
        id: "foundation-event-0",
        kind: "gating.recompute",
        actorRole: "operator",
        at: "2026-03-02T08:00:00.000Z",
        message: "Control room initialized",
        details: ["Deterministic baseline loaded for Screen 05."]
      }
    ]
  };
}

const INITIAL_STATE = createInitialState();

export const useInventoryFoundationStore = create<InventoryFoundationStore>((set) => ({
  ...INITIAL_STATE,
  setField: (key, value) => {
    set((current) => {
      const next = addTimelineEntry(
        {
          ...current,
          fields: {
            ...current.fields,
            [key]: value
          }
        },
        "field.change",
        current.role,
        `Updated field ${key}`,
        [`${String(key)} => ${String(value)}`]
      );

      if (key === "supplierCode") {
        const withSupplier = {
          ...next,
          selectedSupplierCode: value
        };
        const computed = computeInventoryFoundationDerived(withSupplier);
        return withGateRecompute(withSupplier, current.role, computed.rbacGateSummary);
      }

      const computed = computeInventoryFoundationDerived(next);
      return withGateRecompute(next, current.role, computed.rbacGateSummary);
    });
  },
  setRole: (role) => {
    set((current) => {
      const next = addTimelineEntry(
        { ...current, role },
        "role.change",
        role,
        `Runtime role switched to ${role.toUpperCase()}`,
        ["RBAC matrix and gating reasons recalculated."]
      );
      const computed = computeInventoryFoundationDerived(next);
      return withGateRecompute(next, role, computed.rbacGateSummary);
    });
  },
  setSupplierCode: (supplierCode) => {
    set((current) => {
      const next = addTimelineEntry(
        {
          ...current,
          selectedSupplierCode: supplierCode,
          fields: {
            ...current.fields,
            supplierCode
          }
        },
        "supplier.change",
        current.role,
        `Selected supplier ${supplierCode}`,
        ["Supplier gate and readiness recalculated."]
      );
      const computed = computeInventoryFoundationDerived(next);
      return withGateRecompute(next, current.role, computed.rbacGateSummary);
    });
  },
  setSupplierLifecycle: (supplierCode, lifecycle) => {
    set((current) => {
      const suppliers = current.suppliers.map((supplier) =>
        supplier.code === supplierCode ? { ...supplier, lifecycle } : supplier
      );
      const next = addTimelineEntry(
        { ...current, suppliers },
        "supplier.change",
        current.role,
        `Supplier ${supplierCode} moved to ${lifecycle.toUpperCase()}`,
        ["Supplier approval gate updated."]
      );
      const computed = computeInventoryFoundationDerived(next);
      return withGateRecompute(next, current.role, computed.rbacGateSummary);
    });
  },
  cycleDocumentLifecycle: (documentId) => {
    set((current) => {
      const existing = current.documentStates[documentId];
      if (!existing) {
        return current;
      }

      const nextLifecycle = cycleLifecycle(existing.lifecycle);
      const documentStates = {
        ...current.documentStates,
        [documentId]: {
          ...existing,
          lifecycle: nextLifecycle,
          touchedByRole: current.role,
          touchedAt: timestampFromSequence(current.timeline.length + 1),
          comment: `Lifecycle cycled to ${nextLifecycle}.`
        }
      };

      const next = addTimelineEntry(
        { ...current, documentStates },
        "doc.lifecycle",
        current.role,
        `Document ${documentId} cycled to ${nextLifecycle}`,
        ["Critical hold banner auto-updated."]
      );

      const computed = computeInventoryFoundationDerived(next);
      return withGateRecompute(next, current.role, computed.rbacGateSummary);
    });
  },
  setRbacSearch: (value) => {
    set((current) => ({
      ...current,
      rbacSearch: value
    }));
  },
  setRbacGateFilter: (filter) => {
    set((current) => ({
      ...current,
      rbacGateFilter: filter
    }));
  },
  reset: () => {
    set(() => INITIAL_STATE);
  }
}));

export function computeInventoryFoundationDerived(
  state: InventoryFoundationState
): InventoryFoundationComputed {
  const selectedSupplier = resolveSupplierByCode(state.suppliers, state.selectedSupplierCode);
  const rbacStatusRows = state.rbacRows.map((row) => evaluateRbacRow(state, row));
  const rbacGateSummary = summarizeRbacRows(rbacStatusRows);
  const readiness = computeReadiness(state, rbacStatusRows, selectedSupplier);
  const filteredRbacRows = filterRbacRows(rbacStatusRows, state.rbacSearch, state.rbacGateFilter);
  const supplierGate = selectedSupplier?.lifecycle === "blocked" ? "blocked" : "open";
  const foundationGate = readiness.holdReasons.length > 0 ? "hold" : "open";
  const canProceedToRun2 =
    foundationGate === "open" &&
    supplierGate === "open" &&
    state.role !== "auditor" &&
    readiness.percentage >= 70;

  return {
    selectedSupplier,
    readiness,
    rbacStatusRows,
    rbacGateSummary,
    filteredRbacRows,
    canProceedToRun2,
    supplierGate,
    foundationGate
  };
}

export function useInventoryFoundationPanelContext(): InventoryFoundationPanelContext {
  const state = useInventoryFoundationStore();
  const computed = computeInventoryFoundationDerived(state);

  return {
    state,
    computed,
    actions: {
      setField: state.setField,
      setRole: state.setRole,
      setSupplierCode: state.setSupplierCode,
      setSupplierLifecycle: state.setSupplierLifecycle,
      cycleDocumentLifecycle: state.cycleDocumentLifecycle,
      setRbacSearch: state.setRbacSearch,
      setRbacGateFilter: state.setRbacGateFilter,
      reset: state.reset
    }
  };
}

export const inventoryFoundationSelectors = {
  fields: (state: InventoryFoundationState): InventoryFoundationFields => state.fields,
  role: (state: InventoryFoundationState): FoundationRole => state.role,
  selectedSupplierCode: (state: InventoryFoundationState): string => state.selectedSupplierCode,
  documentStates: (state: InventoryFoundationState): Readonly<Record<string, VaultDocumentState>> =>
    state.documentStates,
  suppliers: (state: InventoryFoundationState): readonly SupplierProfile[] => state.suppliers
};

export const inventoryFoundationHelpers = {
  cycleLifecycle,
  timestampFromSequence
};

export function getSupplierLifecycleTone(
  lifecycle: SupplierLifecycle
): "success" | "warning" | "danger" {
  if (lifecycle === "approved") {
    return "success";
  }
  if (lifecycle === "active") {
    return "warning";
  }
  return "danger";
}

export function getDocumentLifecycleTone(
  lifecycle: DocumentLifecycle
): "success" | "warning" | "danger" | "accent" {
  if (lifecycle === "present") {
    return "success";
  }
  if (lifecycle === "missing") {
    return "danger";
  }
  if (lifecycle === "expired") {
    return "warning";
  }
  return "accent";
}

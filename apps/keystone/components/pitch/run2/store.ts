"use client";

import { create } from "zustand";
import {
  CUSTOMS_PACK_BASELINE,
  PORT_RISK_PROFILES,
  RECEIVING_DEFAULT_FIELDS,
  RECEIVING_INCOTERM_RISK,
  RECEIVING_MANIFEST_LIBRARY
} from "./data";
import type {
  CustomsDocStatus,
  CustomsDocumentRequirement,
  DeviationTicket,
  ImportReceivingComputed,
  ImportReceivingPanelContext,
  ImportReceivingState,
  ImportReceivingStore,
  ReceivingRiskPanel,
  ReceivingStateCode,
  ReceivingTimelineEntry
} from "./types";

const CUSTOMS_CYCLE_ORDER: readonly CustomsDocStatus[] = [
  "present",
  "missing",
  "in-progress",
  "expired"
];

const STATE_SEQUENCE: readonly ReceivingStateCode[] = [
  "ARRIVED",
  "DOCS_HOLD",
  "RECEIVED",
  "QUARANTINE"
];

const BASE_TS = Date.parse("2026-03-02T11:00:00.000Z");

function timestampFromSequence(sequence: number): string {
  return new Date(BASE_TS + sequence * 75_000).toISOString();
}

function cycleDocStatus(status: CustomsDocStatus): CustomsDocStatus {
  const index = CUSTOMS_CYCLE_ORDER.indexOf(status);
  const nextIndex = (index + 1) % CUSTOMS_CYCLE_ORDER.length;
  return CUSTOMS_CYCLE_ORDER[nextIndex] ?? "present";
}

function computeDocsCriticalComplete(customsPack: readonly CustomsDocumentRequirement[]): boolean {
  return customsPack.every((document) => !document.critical || document.status === "present");
}

function computeMismatchDetected(fields: ImportReceivingState["fields"]): boolean {
  return (
    fields.quantityDeclared !== fields.quantityReceived ||
    fields.lotDeclared.trim().toLowerCase() !== fields.lotReceived.trim().toLowerCase()
  );
}

function buildDeviationTicket(
  state: ImportReceivingState,
  category: DeviationTicket["category"],
  severity: DeviationTicket["severity"],
  sequence: number
): DeviationTicket {
  return {
    id: `DEV-${String(sequence).padStart(5, "0")}`,
    active: true,
    category,
    severity,
    createdAt: timestampFromSequence(sequence),
    requiredSteps: [
      "Lock received lot in quarantine stock location.",
      "Notify QA + customs broker with discrepancy evidence.",
      "Attach photo evidence and signed receiving variance form.",
      "Approve deviation closure before release to available inventory."
    ]
  };
}

function appendTimeline(
  state: ImportReceivingState,
  action: ReceivingTimelineEntry["action"],
  to: ReceivingStateCode,
  note: string,
  reasons: readonly string[]
): ImportReceivingState {
  const sequence = state.timeline.length + 1;
  const entry: ReceivingTimelineEntry = {
    id: `receiving-event-${sequence}`,
    sequence,
    action,
    from: state.shipmentState,
    to,
    at: timestampFromSequence(sequence),
    note,
    reasons
  };

  return {
    ...state,
    shipmentState: to,
    timeline: [...state.timeline, entry]
  };
}

function getPortRiskScore(portCode: string): number {
  const risk = PORT_RISK_PROFILES.find((profile) => profile.port === portCode);
  if (!risk) {
    return 40;
  }
  const congestionWeight = Math.round(risk.customsCongestion * 0.55);
  const reliabilityPenalty = Math.round((100 - risk.coldChainReliability) * 0.45);
  const strikePenalty = risk.strikeAlert ? 18 : 0;
  return congestionWeight + reliabilityPenalty + strikePenalty;
}

function computeRiskPanel(state: ImportReceivingState): ReceivingRiskPanel {
  const reasons: string[] = [];
  let score = 0;

  const incotermRisk = RECEIVING_INCOTERM_RISK[state.fields.incoterm];
  score += incotermRisk;
  reasons.push(`${state.fields.incoterm} incoterm baseline risk ${incotermRisk}.`);

  const portRisk = getPortRiskScore(state.fields.port);
  score += Math.round(portRisk * 0.35);
  reasons.push(`Port ${state.fields.port} risk contribution ${Math.round(portRisk * 0.35)}.`);

  if (state.fields.temperatureExcursion) {
    score += 32;
    reasons.push("Temperature excursion flag is ON.");
  }

  const mismatchDetected = computeMismatchDetected(state.fields);
  if (mismatchDetected) {
    score += 26;
    reasons.push("Quantity or lot mismatch detected.");
  }

  const missingCritical = state.customsPack.filter(
    (document) => document.critical && document.status !== "present"
  ).length;
  if (missingCritical > 0) {
    score += missingCritical * 10;
    reasons.push(`${missingCritical} critical customs doc(s) not present.`);
  }

  if (state.shipmentState === "QUARANTINE") {
    score += 22;
    reasons.push("Shipment currently in QUARANTINE.");
  }

  const bounded = Math.min(100, score);
  const level: ReceivingRiskPanel["level"] =
    bounded >= 70 ? "high" : bounded >= 40 ? "medium" : "low";

  return {
    score: bounded,
    level,
    reasons
  };
}

function evaluateTransition(state: ImportReceivingState): {
  readonly allowed: boolean;
  readonly reasons: readonly string[];
  readonly nextState: ReceivingStateCode;
} {
  const reasons: string[] = [];
  const mismatch = computeMismatchDetected(state.fields);
  const docsComplete = computeDocsCriticalComplete(state.customsPack);

  if (state.fields.temperatureExcursion) {
    reasons.push("Temperature excursion requires immediate quarantine.");
    return {
      allowed: true,
      reasons,
      nextState: "QUARANTINE"
    };
  }

  if (mismatch) {
    reasons.push("Mismatch detected; deviation ticket is mandatory.");
    return {
      allowed: false,
      reasons,
      nextState: "QUARANTINE"
    };
  }

  if (!docsComplete) {
    reasons.push("Critical customs pack is incomplete.");
    return {
      allowed: false,
      reasons,
      nextState: "DOCS_HOLD"
    };
  }

  const index = STATE_SEQUENCE.indexOf(state.shipmentState);
  const next = STATE_SEQUENCE[Math.min(index + 1, STATE_SEQUENCE.length - 1)] ?? "QUARANTINE";

  return {
    allowed: true,
    reasons: ["All guards satisfied for next transition."],
    nextState: next
  };
}

function computeNextGate(state: ImportReceivingState, transition: ReturnType<typeof evaluateTransition>) {
  const blockers: string[] = [];
  const nextActions: string[] = [];

  if (transition.allowed) {
    nextActions.push(`Advance shipment to ${transition.nextState}.`);
  } else {
    blockers.push(...transition.reasons);
  }

  const docsComplete = computeDocsCriticalComplete(state.customsPack);
  if (!docsComplete) {
    blockers.push("Resolve customs pack checklist before receiving.");
    nextActions.push("Cycle missing docs to PRESENT after verification.");
  }

  if (computeMismatchDetected(state.fields)) {
    blockers.push("Mismatch deviation ticket must be opened and acknowledged.");
    nextActions.push("Align received quantity/lot or approve formal deviation.");
  }

  if (state.fields.temperatureExcursion) {
    blockers.push("Temperature excursion active.");
    nextActions.push("Keep shipment quarantined pending QA review.");
  }

  const gateState: "READY" | "HOLD" | "BLOCKED" =
    blockers.length === 0 ? "READY" : blockers.some((item) => item.includes("quarantine")) ? "BLOCKED" : "HOLD";

  return {
    state: gateState,
    title:
      gateState === "READY"
        ? `Next gate: ${transition.nextState}`
        : gateState === "BLOCKED"
          ? "Next gate: BLOCKED"
          : "Next gate: HOLD",
    blockers,
    nextActions
  } as const;
}

function createInitialState(): ImportReceivingState {
  return {
    shipmentState: "ARRIVED",
    fields: RECEIVING_DEFAULT_FIELDS,
    customsPack: CUSTOMS_PACK_BASELINE,
    manifests: RECEIVING_MANIFEST_LIBRARY,
    selectedManifestId: "manifest-0001",
    timeline: [
      {
        id: "receiving-event-0",
        sequence: 0,
        action: "RESET",
        from: "ARRIVED",
        to: "ARRIVED",
        at: "2026-03-02T11:00:00.000Z",
        note: "Receiving control room initialized",
        reasons: ["Deterministic baseline loaded for Screen 06."]
      }
    ],
    deviationTicket: null
  };
}

const INITIAL_STATE = createInitialState();

export const useImportReceivingStore = create<ImportReceivingStore>((set) => ({
  ...INITIAL_STATE,
  setField: (key, value) => {
    set((current) => {
      const fields = {
        ...current.fields,
        [key]: value
      };

      let next = appendTimeline(
        {
          ...current,
          fields
        },
        "FIELD_UPDATE",
        current.shipmentState,
        `Field ${key} updated`,
        [`${String(key)} => ${String(value)}`]
      );

      const mismatch = computeMismatchDetected(fields);
      if (mismatch) {
        const sequence = next.timeline.length + 1;
        next = appendTimeline(
          {
            ...next,
            deviationTicket: buildDeviationTicket(next, "qty-mismatch", "major", sequence)
          },
          "MISMATCH_DETECTED",
          "DOCS_HOLD",
          "Mismatch detected and deviation ticket opened",
          ["Quantity/Lot mismatch triggered DOCS_HOLD."]
        );
      }

      if (fields.temperatureExcursion && next.shipmentState !== "QUARANTINE") {
        next = appendTimeline(
          {
            ...next,
            deviationTicket: buildDeviationTicket(next, "temp-excursion", "critical", next.timeline.length + 1)
          },
          "FORCE_QUARANTINE",
          "QUARANTINE",
          "Temperature excursion forced quarantine",
          ["Cold-chain excursion threshold exceeded."]
        );
      }

      return next;
    });
  },
  setSelectedManifest: (manifestId) => {
    set((current) => {
      const manifest = current.manifests.find((entry) => entry.id === manifestId);
      if (!manifest) {
        return current;
      }

      const fields = {
        ...current.fields,
        awbBl: manifest.awbBl,
        eta: manifest.eta,
        ata: current.fields.ata,
        carrier: manifest.carrier,
        port: manifest.destinationPort,
        quantityDeclared: manifest.quantity,
        lotDeclared: manifest.lot
      };

      return appendTimeline(
        {
          ...current,
          selectedManifestId: manifestId,
          shipmentState: manifest.status,
          fields
        },
        "FIELD_UPDATE",
        manifest.status,
        `Manifest ${manifestId} loaded`,
        [manifest.product, `${manifest.origin} -> ${manifest.destinationPort}`]
      );
    });
  },
  cycleCustomsDocStatus: (documentId) => {
    set((current) => {
      const customsPack = current.customsPack.map((document) =>
        document.id === documentId
          ? {
              ...document,
              status: cycleDocStatus(document.status)
            }
          : document
      );

      return appendTimeline(
        {
          ...current,
          customsPack
        },
        "DOC_STATUS",
        current.shipmentState,
        `Customs doc ${documentId} cycled`,
        ["Customs completeness and gate blockers recomputed."]
      );
    });
  },
  advance: () => {
    set((current) => {
      const transition = evaluateTransition(current);
      if (!transition.allowed) {
        if (transition.nextState === "QUARANTINE") {
          return appendTimeline(
            {
              ...current,
              deviationTicket:
                current.deviationTicket ??
                buildDeviationTicket(current, "lot-mismatch", "major", current.timeline.length + 1)
            },
            "ADVANCE",
            current.shipmentState,
            "Advance blocked by guards",
            transition.reasons
          );
        }

        return appendTimeline(
          current,
          "ADVANCE",
          transition.nextState,
          "Advance routed to DOCS_HOLD",
          transition.reasons
        );
      }

      return appendTimeline(
        current,
        "ADVANCE",
        transition.nextState,
        `Advance accepted to ${transition.nextState}`,
        transition.reasons
      );
    });
  },
  reset: () => {
    set((current) => {
      const baseline = createInitialState();
      return {
        ...baseline,
        timeline: [
          ...current.timeline,
          {
            id: `receiving-event-${current.timeline.length + 1}`,
            sequence: current.timeline.length + 1,
            action: "RESET",
            from: current.shipmentState,
            to: "ARRIVED",
            at: timestampFromSequence(current.timeline.length + 1),
            note: "State reset to baseline",
            reasons: ["Manual reset from control panel."]
          }
        ]
      };
    });
  },
  forceQuarantine: () => {
    set((current) =>
      appendTimeline(
        {
          ...current,
          deviationTicket:
            current.deviationTicket ??
            buildDeviationTicket(current, "customs-doc", "critical", current.timeline.length + 1)
        },
        "FORCE_QUARANTINE",
        "QUARANTINE",
        "Manual force quarantine",
        ["Operator requested quarantine lock."]
      )
    );
  }
}));

export function computeImportReceivingDerived(state: ImportReceivingState): ImportReceivingComputed {
  const selectedManifest = state.manifests.find((entry) => entry.id === state.selectedManifestId) ?? null;
  const counters: Record<CustomsDocStatus, number> = {
    present: 0,
    missing: 0,
    "in-progress": 0,
    expired: 0
  };

  for (const document of state.customsPack) {
    counters[document.status] += 1;
  }

  const customsCompleteness = Math.round(
    (counters.present / Math.max(state.customsPack.length, 1)) * 100
  );
  const transition = evaluateTransition(state);
  const riskPanel = computeRiskPanel(state);
  const nextGate = computeNextGate(state, transition);
  const mismatchDetected = computeMismatchDetected(state.fields);

  return {
    selectedManifest,
    customsCompleteness,
    customsCounts: counters,
    transition,
    riskPanel,
    nextGate,
    mismatchDetected
  };
}

export function useImportReceivingPanelContext(): ImportReceivingPanelContext {
  const state = useImportReceivingStore();
  const computed = computeImportReceivingDerived(state);

  return {
    state,
    computed,
    actions: {
      setField: state.setField,
      setSelectedManifest: state.setSelectedManifest,
      cycleCustomsDocStatus: state.cycleCustomsDocStatus,
      advance: state.advance,
      reset: state.reset,
      forceQuarantine: state.forceQuarantine
    }
  };
}

export function getCustomsStatusTone(
  status: CustomsDocStatus
): "success" | "danger" | "warning" | "accent" {
  if (status === "present") {
    return "success";
  }
  if (status === "missing") {
    return "danger";
  }
  if (status === "expired") {
    return "warning";
  }
  return "accent";
}

export function getReceivingStateTone(
  state: ReceivingStateCode
): "accent" | "warning" | "success" | "danger" {
  if (state === "ARRIVED") {
    return "accent";
  }
  if (state === "DOCS_HOLD") {
    return "warning";
  }
  if (state === "RECEIVED") {
    return "success";
  }
  return "danger";
}

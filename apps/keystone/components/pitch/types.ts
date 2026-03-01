import type {
  PitchDeck,
  PitchNavigationLink,
  PitchScreen,
  PitchScreen01,
  PitchScreen02,
  PitchScreen03,
  PitchScreen04,
  PitchScreen05,
  PitchScreen06
} from "@hitech/contracts";

export interface PitchRouteParams {
  readonly searchParams?: Record<string, string | string[] | undefined>;
}

export interface PitchScreenPageProps {
  readonly deck: PitchDeck;
  readonly screen: PitchScreen;
}

export interface PitchHeaderModel {
  readonly title: string;
  readonly subtitle?: string;
  readonly eyebrow?: string;
  readonly orderLabel?: string;
}

export interface PitchNavModel {
  readonly links: readonly PitchNavigationLink[];
  readonly activeSlug?: PitchScreen["slug"];
}

export interface EngineColumnModel {
  readonly heading: string;
  readonly bullets: readonly string[];
  readonly microcopy: readonly string[];
}

export interface DoubleEngineScreenModel {
  readonly title: string;
  readonly left: EngineColumnModel;
  readonly right: EngineColumnModel;
  readonly implicitMessage: string;
}

export interface IndustrialFlowScreenModel {
  readonly title: string;
  readonly kpis: ReadonlyArray<{ label: string; value: string; note?: string }>;
  readonly cycleLabel: string;
  readonly microcopy: string;
}

export interface HiTechOsScreenModel {
  readonly title: string;
  readonly features: readonly string[];
  readonly strongLine: string;
}

export interface ValuationScreenModel {
  readonly title: string;
  readonly blocks: ReadonlyArray<{
    heading: string;
    items: readonly string[];
    phase1?: string;
    phase2?: string;
  }>;
  readonly combinedLine: string;
  readonly comparisonHeaders: readonly string[];
  readonly comparisonRows: ReadonlyArray<readonly string[]>;
}

type PitchStatus =
  PitchScreen05["foundationStatus"]["rbacMatrixSnapshot"]["rows"][number]["status"];
type ReceivingStateCode = PitchScreen06["receivingFlow"]["states"][number]["code"];

export interface InventoryFoundationScreenModel {
  readonly title: string;
  readonly readinessKpis: ReadonlyArray<{
    label: string;
    value: string;
    note: string;
  }>;
  readonly rbacMatrix: {
    readonly heading: string;
    readonly rows: ReadonlyArray<{
      readonly role: string;
      readonly permissions: readonly string[];
      readonly status: PitchStatus;
    }>;
  };
  readonly suppliers: {
    readonly heading: string;
    readonly approved: readonly string[];
    readonly blocked: readonly string[];
  };
  readonly productsSkuBaseline: {
    readonly heading: string;
    readonly fields: ReadonlyArray<{
      readonly label: string;
      readonly value: string;
    }>;
  };
  readonly documentVaultBaseline: {
    readonly heading: string;
    readonly checklist: ReadonlyArray<{
      readonly document: string;
      readonly status: PitchStatus;
      readonly lifecycle: "present" | "missing" | "expired";
    }>;
  };
}

export interface ShipmentsReceivingScreenModel {
  readonly title: string;
  readonly shipmentControlBoard: {
    readonly heading: string;
    readonly fields: ReadonlyArray<{
      readonly label: string;
      readonly value: string;
    }>;
  };
  readonly customsPackChecklist: {
    readonly heading: string;
    readonly overallStatus: PitchStatus;
    readonly items: ReadonlyArray<{
      readonly label: string;
      readonly status: PitchStatus;
    }>;
  };
  readonly receivingFlow: {
    readonly heading: string;
    readonly states: ReadonlyArray<{
      readonly code: ReceivingStateCode;
      readonly note: string;
      readonly order: number;
    }>;
  };
  readonly mismatchHandling: {
    readonly heading: string;
    readonly qtyLotMismatch: string;
    readonly deviationPlaceholder: string;
  };
  readonly nextGate: string;
}

export function toDoubleEngineModel(screen: PitchScreen01): DoubleEngineScreenModel {
  return {
    title: screen.title,
    left: {
      heading: screen.leftColumn.heading,
      bullets: screen.leftColumn.bullets.map((entry) => entry.text),
      microcopy: screen.leftColumn.microcopy.map((entry) => entry.text)
    },
    right: {
      heading: screen.rightColumn.heading,
      bullets: screen.rightColumn.bullets.map((entry) => entry.text),
      microcopy: screen.rightColumn.microcopy.map((entry) => entry.text)
    },
    implicitMessage: screen.implicitMessage.text
  };
}

export function toIndustrialFlowModel(screen: PitchScreen02): IndustrialFlowScreenModel {
  return {
    title: screen.title,
    kpis: screen.kpis.map((kpi) => ({
      label: kpi.label,
      value: kpi.value,
      ...(kpi.note ? { note: kpi.note } : {})
    })),
    cycleLabel: screen.cycleLabel.text,
    microcopy: screen.microcopy.text
  };
}

export function toHiTechOsModel(screen: PitchScreen03): HiTechOsScreenModel {
  return {
    title: screen.title,
    features: screen.features.map((entry) => entry.text),
    strongLine: screen.strongLine.text
  };
}

export function toValuationModel(screen: PitchScreen04): ValuationScreenModel {
  return {
    title: screen.title,
    blocks: screen.blocks.map((block) => ({
      heading: block.heading,
      items: block.items.map((entry) => entry.text),
      ...(block.phase1 ? { phase1: block.phase1 } : {}),
      ...(block.phase2 ? { phase2: block.phase2 } : {})
    })),
    combinedLine: screen.combinedValuationLine.text,
    comparisonHeaders: screen.comparison.headers,
    comparisonRows: screen.comparison.rows
  };
}

export function toInventoryFoundationModel(screen: PitchScreen05): InventoryFoundationScreenModel {
  const rbacRows = screen.foundationStatus.rbacMatrixSnapshot.rows.map((row) => ({
    role: row.role,
    permissions: row.permissions,
    status: row.status
  }));

  const approvedSuppliers = screen.foundationStatus.supplierOnboardingStatus.suppliers
    .filter((supplier) => supplier.status === "DONE")
    .map((supplier) => supplier.supplier);
  const blockedSuppliers = screen.foundationStatus.supplierOnboardingStatus.suppliers
    .filter((supplier) => supplier.status !== "DONE")
    .map((supplier) => supplier.supplier);

  const checklist = screen.documentVaultBaseline.requiredDocs.map((entry) => {
    const lifecycle: InventoryFoundationScreenModel["documentVaultBaseline"]["checklist"][number]["lifecycle"] =
      entry.status === "DONE" ? "present" : entry.status === "MISSING" ? "missing" : "expired";

    return {
      document: entry.document,
      status: entry.status,
      lifecycle
    };
  });

  const presentDocs = checklist.filter((entry) => entry.lifecycle === "present").length;
  const readyRoles = rbacRows.filter((row) => row.status === "DONE").length;

  return {
    title: screen.title,
    readinessKpis: [
      {
        label: "Foundation readiness",
        value: `${presentDocs}/${checklist.length}`,
        note: "Document vault files currently present"
      },
      {
        label: "RBAC readiness",
        value: `${readyRoles}/${rbacRows.length}`,
        note: "Roles with approved access profile"
      },
      {
        label: "Supplier readiness",
        value: `${approvedSuppliers.length}/${screen.foundationStatus.supplierOnboardingStatus.suppliers.length}`,
        note: `${blockedSuppliers.length} blocked supplier(s)`
      }
    ],
    rbacMatrix: {
      heading: screen.foundationStatus.rbacMatrixSnapshot.heading,
      rows: rbacRows
    },
    suppliers: {
      heading: screen.foundationStatus.supplierOnboardingStatus.heading,
      approved: approvedSuppliers,
      blocked: blockedSuppliers
    },
    productsSkuBaseline: {
      heading: screen.productsSkuBaseline.heading,
      fields: screen.productsSkuBaseline.fields.map((entry) => ({
        label: entry.label,
        value: entry.value
      }))
    },
    documentVaultBaseline: {
      heading: screen.documentVaultBaseline.heading,
      checklist
    }
  };
}

function buildCustomsChecklist(overallStatus: PitchStatus): readonly PitchStatus[] {
  if (overallStatus === "DONE") {
    return ["DONE", "DONE", "DONE", "DONE"];
  }

  if (overallStatus === "MISSING") {
    return ["MISSING", "MISSING", "MISSING", "MISSING"];
  }

  if (overallStatus === "PENDING") {
    return ["PENDING", "PENDING", "PENDING", "PENDING"];
  }

  return ["DONE", "DONE", "IN_PROGRESS", "PENDING"];
}

export function toShipmentsReceivingModel(screen: PitchScreen06): ShipmentsReceivingScreenModel {
  const placeholderByLabel = new Map(
    screen.shipmentControlBoard.placeholders.map((placeholder) => [
      placeholder.label,
      placeholder.value
    ])
  );
  const checklistStatuses = buildCustomsChecklist(
    screen.shipmentControlBoard.customsPackCompleteness.status
  );
  const checklistLabels = [
    "Commercial Invoice",
    "Packing List",
    "Import Permits",
    "COA Placeholder"
  ] as const;

  return {
    title: screen.title,
    shipmentControlBoard: {
      heading: screen.shipmentControlBoard.heading,
      fields: [
        {
          label: "AWB / BL",
          value: placeholderByLabel.get("AWB / BL") ?? "AWB-BL-PENDING"
        },
        { label: "ETA", value: placeholderByLabel.get("ETA") ?? "ETA-TBD" },
        { label: "ATA", value: placeholderByLabel.get("ATA") ?? "ATA-TBD" },
        {
          label: "Incoterm",
          value: placeholderByLabel.get("Incoterm") ?? "INCOTERM-TBD"
        }
      ]
    },
    customsPackChecklist: {
      heading: screen.shipmentControlBoard.customsPackCompleteness.text,
      overallStatus: screen.shipmentControlBoard.customsPackCompleteness.status,
      items: checklistLabels.map((label, index) => ({
        label,
        status: checklistStatuses[index] ?? "PENDING"
      }))
    },
    receivingFlow: {
      heading: screen.receivingFlow.heading,
      states: [...screen.receivingFlow.states]
        .sort((left, right) => left.order - right.order)
        .map((state) => ({
          code: state.code,
          note: state.note,
          order: state.order
        }))
    },
    mismatchHandling: {
      heading: screen.mismatchHandling.heading,
      qtyLotMismatch: screen.mismatchHandling.qtyLotMismatch,
      deviationPlaceholder: screen.mismatchHandling.deviationPlaceholder
    },
    nextGate: screen.nextGate.text
  };
}

export type PrismaSurface = "pc" | "tablet" | "mobile" | "pos" | "chart_lab";

export type PrismaPriority = "low" | "normal" | "high" | "critical";

export type PrismaVisualBudget =
  | "pc-home-premium"
  | "pc-operational"
  | "pc-operational-dense"
  | "pc-sync"
  | "pc-reporting"
  | "pc-analysis-studio"
  | "pc-system"
  | "pc-settings-quiet"
  | string;

export type PrismaEvidenceRef = {
  source?: string;
  query?: string;
  confidence?: "low" | "medium" | "high" | string;
  freshness?: string;
  auditTrail?: boolean;
  notes?: string;
};

export type PrismaInterfaceContract = {
  id: string;
  route: string;
  surface: PrismaSurface;
  module: string;
  question: string;
  visualBudget: PrismaVisualBudget;
  requiredBlocks?: string[];
  evidenceRequired?: boolean;
};

export type PrismaPanelContract = {
  id: string;
  route?: string;
  question?: string;
  role:
    | "decision-header"
    | "attention-summary"
    | "next-best-action"
    | "operational-detail"
    | "evidence"
    | "chart-insight"
    | "table"
    | "form"
    | "drawer"
    | string;
  priority?: PrismaPriority;
  evidence?: PrismaEvidenceRef | string;
  action?: string;
  visualBudget?: PrismaVisualBudget;
  technicalDrawer?: boolean;
};

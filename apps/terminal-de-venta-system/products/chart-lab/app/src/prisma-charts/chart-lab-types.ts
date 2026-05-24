// PRISMA_CHART_LAB_POWER_STUDIO_V3_FINAL_INFRASTRUCTURE
import type { ComponentType } from "react";
import type { PrismaChartRenderer, PrismaChartSurface } from "../../../../../shared/prisma-charts/prismaChartContracts";

export type LabChartFamily =
  | "flow"
  | "density"
  | "network"
  | "treemap"
  | "timeline"
  | "waterfall"
  | "strip"
  | "matrix"
  | "stack"
  | "radar"
  | "rings"
  | "sparks"
  | "bands"
  | "future";

export type LabChartReadiness = "working" | "placeholder" | "unavailable";
export type LabChartDataStatus = "lab/mock" | "shared/mock" | "partial/adapter-ready" | "runtime" | "stale" | "invalid" | "unavailable";
export type LabChartThemeMode = "prisma-crystal" | "precision-paper";
export type LabChartDensity = "calm" | "dense";
export type LabChartSize = "focus" | "wide" | "compact";
export type LabChartScenario = "clean" | "critical" | "partial" | "stale" | "offline" | "dense";
export type LabChartThemePreset = "crystal-light" | "executive-dense" | "forensic" | "high-contrast";
export type LabChartPreviewFrame = "pc" | "tablet" | "mobile";
export type LabChartInspectorTab =
  | "preview"
  | "controls"
  | "option-studio"
  | "passport"
  | "maps"
  | "data"
  | "promotion"
  | "intent"
  | "states"
  | "health";
export type LabChartControlType = "segmented" | "select" | "chip-group" | "toggle" | "range" | "numeric" | "search";
export type LabChartControlValue = string | number | boolean | string[];

export type LabChartControlOption = {
  label: string;
  value: string;
};

export type LabChartRuntimeControl = {
  id: string;
  label: string;
  type: LabChartControlType;
  defaultValue: LabChartControlValue;
  value?: LabChartControlValue;
  options?: LabChartControlOption[];
  min?: number;
  max?: number;
  step?: number;
  affectedLayer: string;
  affectedOptionPath?: string;
  affectedDataTransform?: string;
  validation: string;
  risk: "low" | "medium" | "high";
  resetBehavior: string;
  disabledReason?: string;
  powerTab?: "visual" | "motion" | "interaction" | "labels" | "data" | "advanced" | "code";
};

export type LabChartControlState = Record<string, LabChartControlValue>;

export type LabChartRenderProps = {
  entry: LabChartEntry;
  density: LabChartDensity;
  size: LabChartSize;
  themeMode: LabChartThemeMode;
};

export type LabChartEntry = {
  id: string;
  title: string;
  shortName: string;
  surface: PrismaChartSurface | "web";
  family: LabChartFamily;
  chartType: string;
  description: string;
  operationalQuestion: string;
  readiness: LabChartReadiness;
  dataStatus: LabChartDataStatus;
  mockDataLabel: string;
  confidence: number;
  freshnessLabel: string;
  promotionTarget: string;
  promotionBoundary: string;
  sourceModule: string;
  componentPath: string;
  mockPath: string;
  registryPath: string;
  optionBuilderName?: string;
  renderer?: PrismaChartRenderer;
  defaultHeight: number;
  getOption?: () => Record<string, unknown>;
  Component?: ComponentType<LabChartRenderProps>;
  unavailableReason?: string;
};

// PRISMA_CHART_LAB_CONTROL_CONTRACTS_V3
import { chartControlSchemas } from "./chart-lab-control-model";
import type { LabChartRuntimeControl } from "./chart-lab-types";

export type ChartLabControlContractIssue = {
  chartId: string;
  controlId: string;
  severity: "error" | "warning";
  message: string;
};

const powerTabs = new Set(["visual", "motion", "interaction", "labels", "data", "advanced"]);

export function validateChartLabControl(control: LabChartRuntimeControl, chartId = "*"): ChartLabControlContractIssue[] {
  const issues: ChartLabControlContractIssue[] = [];
  const push = (severity: "error" | "warning", message: string) => issues.push({ chartId, controlId: control.id || "<missing>", severity, message });
  if (!control.id) push("error", "Missing control id");
  if (!control.label) push("error", "Missing human label");
  if (!control.type) push("error", "Missing control type");
  if (!control.affectedLayer) push("error", "Missing affectedLayer");
  if (!control.validation) push("error", "Missing validation description");
  if (!control.resetBehavior) push("warning", "Missing resetBehavior description");
  if (!control.powerTab || !powerTabs.has(control.powerTab)) push("error", "Missing or invalid powerTab");
  if ((control.type === "range" || control.type === "numeric") && (typeof control.min !== "number" || typeof control.max !== "number")) push("error", "Numeric control missing min/max range");
  if ((control.type === "select" || control.type === "segmented" || control.type === "chip-group") && !control.options?.length) push("error", "Choice control missing options");
  if (!control.affectedOptionPath && !control.affectedDataTransform && !/recipe|data|motion|interaction|visual|label|advanced/i.test(control.affectedLayer)) push("warning", "Potential ghost control: no affectedOptionPath or data transform");
  return issues;
}

export function validateChartLabControlContracts(): ChartLabControlContractIssue[] {
  const issues: ChartLabControlContractIssue[] = [];
  for (const [chartId, controls] of Object.entries(chartControlSchemas)) {
    const seen = new Set<string>();
    for (const control of controls) {
      if (seen.has(control.id)) issues.push({ chartId, controlId: control.id, severity: "error", message: "Duplicate control id" });
      seen.add(control.id);
      issues.push(...validateChartLabControl(control, chartId));
    }
  }
  return issues;
}

export function summarizeChartLabControlContracts() {
  const issues = validateChartLabControlContracts();
  return {
    ok: !issues.some((issue) => issue.severity === "error"),
    errors: issues.filter((issue) => issue.severity === "error"),
    warnings: issues.filter((issue) => issue.severity === "warning")
  };
}

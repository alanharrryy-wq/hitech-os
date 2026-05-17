#!/usr/bin/env node
import fs from "node:fs";
import { pass, rel, warn, writeEvidence } from "./chart-lab-script-utils.mjs";

const registryPath = rel("src", "prisma-charts", "chart-data-registry.json");
const report = { generatedAt: new Date().toISOString(), readiness: "NOT_READY", reasons: [] };

if (!fs.existsSync(registryPath)) {
  report.reasons.push("chart-data-registry missing");
} else {
  const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
  const mockOnly = (registry.charts || []).filter((chart) => chart.sourceMode === "mock").map((chart) => chart.chartId);
  if (mockOnly.length) report.reasons.push(`mock-only charts: ${mockOnly.join(", ")}`);
  if (!mockOnly.length) report.readiness = "READY";
}

const reportPath = writeEvidence("visual-baseline-readiness-report.json", report);
if (report.readiness === "READY") pass(`visual baseline readiness READY: ${reportPath}`);
else warn(`visual baseline readiness NOT_READY: ${report.reasons.join("; ")}`);
console.log(JSON.stringify(report, null, 2));

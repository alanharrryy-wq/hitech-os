#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { chartOpsIds, fail, pass, rel, terminalRoot, warn, writeEvidence } from "./chart-lab-script-utils.mjs";

const registryPath = rel("src", "prisma-charts", "chart-data-registry.json");
const allowed = new Set(["mock", "fixture", "recorded-real", "live-real"]);
const requiredMeta = ["sourceMode", "sourceLabel", "confidence", "freshnessStatus", "generatedAt", "source"];
const report = {
  generatedAt: new Date().toISOString(),
  registryPath,
  charts: [],
  findings: []
};

function add(status, chartId, message) {
  report.findings.push({ status, chartId, message });
  if (status === "FAIL") fail(`${chartId}: ${message}`);
  else if (status === "WARN") warn(`${chartId}: ${message}`);
  else pass(`${chartId}: ${message}`);
}

if (!fs.existsSync(registryPath)) {
  fail(`chart data registry missing: ${registryPath}`);
} else {
  const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
  const charts = Array.isArray(registry.charts) ? registry.charts : [];
  const byId = new Map(charts.map((chart) => [chart.chartId, chart]));
  const expected = chartOpsIds();

  for (const id of expected) {
    const chart = byId.get(id);
    if (!chart) {
      add("FAIL", id, "missing from chart-data-registry");
      continue;
    }
    report.charts.push(chart);
    for (const field of requiredMeta) {
      if (chart[field] === undefined || chart[field] === null || chart[field] === "") add("FAIL", id, `missing metadata ${field}`);
    }
    if (!allowed.has(chart.sourceMode)) add("FAIL", id, `invalid sourceMode ${chart.sourceMode}`);
    if (chart.sourceMode === "live-real" && !chart.adapterPath) add("FAIL", id, "live-real requires adapterPath");
    if (chart.sourceMode === "live-real" && String(chart.source || "").includes("prismaChartMocks")) add("FAIL", id, "live-real points at mock source");
    if ((chart.sourceMode === "fixture" || chart.sourceMode === "recorded-real") && !chart.fixturePath) add("FAIL", id, `${chart.sourceMode} requires fixturePath`);
    if (chart.sourceMode === "mock") add("PASS", id, "honestly labeled as mock");
  }

  const extra = charts.filter((chart) => !expected.includes(chart.chartId));
  for (const chart of extra) add("WARN", chart.chartId, "extra chart data registry entry not in 14 ChartOps set");

  if (report.charts.length === expected.length) pass(`all ${expected.length} ChartOps charts have source metadata`);
  else fail(`expected ${expected.length} ChartOps charts, found ${report.charts.length}`);
}

const reportPath = writeEvidence("chart-source-modes-report.json", report);
console.log(`chart source modes report: ${reportPath}`);
if (!process.exitCode) pass("chart source modes verification complete");

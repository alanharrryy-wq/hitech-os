#!/usr/bin/env node
import fs from "node:fs";
import { chartOpsIds, fail, pass, read, rel, run, warn, writeEvidence } from "./chart-lab-script-utils.mjs";

const registryPath = rel("src", "prisma-charts", "chart-data-registry.json");
const promoteScript = read("scripts/promote-chart.mjs");
const maps = read("src/prisma-charts/maps/chart-lab-maps.ts");
const registry = fs.existsSync(registryPath) ? JSON.parse(fs.readFileSync(registryPath, "utf8")) : { charts: [] };
const byId = new Map((registry.charts || []).map((chart) => [chart.chartId, chart]));
const report = { generatedAt: new Date().toISOString(), charts: [], policy: {}, findings: [] };

function finding(status, chartId, message) {
  report.findings.push({ status, chartId, message });
  if (status === "FAIL") fail(`${chartId}: ${message}`);
  else if (status === "WARN") warn(`${chartId}: ${message}`);
  else pass(`${chartId}: ${message}`);
}

const policyChecks = [
  ["dry run mode exists", promoteScript.includes("--dry-run")],
  ["apply is blocked by default", promoteScript.includes("BLOCKED_BY_DEFAULT_SAFE_POLICY")],
  ["rollback manifest path exists", promoteScript.includes("promotion-rollback-manifest.json")],
  ["feature flag default false", promoteScript.includes("_PREVIEW=false")],
  ["promotionManifestMap exported", maps.includes("promotionManifestMap")]
];

for (const [name, ok] of policyChecks) {
  report.policy[name] = ok;
  if (ok) pass(name);
  else fail(name);
}

for (const id of chartOpsIds()) {
  const chart = byId.get(id);
  if (!chart) {
    finding("FAIL", id, "missing chart data registry entry");
    continue;
  }
  const readiness = chart.sourceMode === "live-real" ? "ready" : "partial";
  report.charts.push({ chartId: id, sourceMode: chart.sourceMode, readiness });
  if (chart.sourceMode === "live-real" && String(chart.source || "").includes("prismaChartMocks")) {
    finding("FAIL", id, "live-real cannot point at mock source");
  } else if (chart.sourceMode === "mock") {
    finding("WARN", id, "promotion blocked from live use because sourceMode is mock");
  } else {
    finding("PASS", id, `promotion readiness ${readiness}`);
  }
}

for (const args of [
  ["--chart=pc.causal-flow-ribbon", "--target=pc", "--dry-run"],
  ["--chart=tablet.shift-pulse-strip", "--target=tablet", "--dry-run"],
  ["--chart=mobile.owner-pulse-timeline", "--target=mobile", "--dry-run"]
]) {
  const result = run("node", ["scripts/promote-chart.mjs", ...args]);
  if (result.status === 0) pass(`promotion dry-run works: ${args.join(" ")}`);
  else fail(`promotion dry-run failed: ${args.join(" ")}\n${result.stderr}`);
}

const reportPath = writeEvidence("promotion-readiness-report.json", report);
console.log(`promotion readiness report: ${reportPath}`);
if (!process.exitCode) pass("promotion readiness policy verification complete");

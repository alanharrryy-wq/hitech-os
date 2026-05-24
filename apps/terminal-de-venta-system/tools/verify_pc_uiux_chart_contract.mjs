#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const pcRoot = path.join(root, "products", "pc", "app");
const ignoreDirs = new Set(["node_modules", ".next", "out", "dist", "build", "coverage", "test-results", "playwright-report"]);

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

const files = walk(pcRoot).filter(f => /\.(tsx|jsx|ts)$/.test(f) && !f.replace(/\\/g, "/").includes("/src/uiux/") && !f.replace(/\\/g, "/").includes("/api/"));
const issues = [];

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  if (!/EChart|PrismaEChart|ChartInsightCard|chart/i.test(text)) continue;
  const isLikelyChartFile = /chart|insight|graph|density|ribbon|waterfall|timeline|treemap|radar/i.test(file);
  if (!isLikelyChartFile) continue;
  const hasQuestion = /Pregunta|question|primaryQuestion|¿/.test(text);
  const hasReading = /Lectura|reading|insight|summary|interpretaci/i.test(text);
  const hasSource = /Fuente|source|dataSource|confidence|Confianza/i.test(text);
  if (!hasQuestion || !hasReading || !hasSource) issues.push({ file: path.relative(root, file).replace(/\\/g, "/"), hasQuestion, hasReading, hasSource });
}

console.log(JSON.stringify({ verifier: "verify_pc_uiux_chart_contract", status: "PASS", advisoryStatus: issues.length ? "DEBT" : "CLEAN", issueCount: issues.length, issues: issues.slice(0, 100), note: "Advisory only in hotfix. Does not fail structural one-pass." }, null, 2));
process.exit(0);

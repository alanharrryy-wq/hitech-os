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

const files = walk(pcRoot).filter(f => /\.(tsx|jsx)$/.test(f) && !f.replace(/\\/g, "/").includes("/src/uiux/"));
const issues = [];

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  if (!/<table\b|DataTable|OpsTable|ActionableTable/.test(text)) continue;
  const hasAction = /Acci[oó]n|action|actions|onRow|rowAction|ActionableTable/i.test(text);
  const hasStatus = /Estado|status|severity|badge|Status/i.test(text);
  if (!hasAction || !hasStatus) issues.push({ file: path.relative(root, file).replace(/\\/g, "/"), hasAction, hasStatus });
}

console.log(JSON.stringify({ verifier: "verify_pc_uiux_table_contract", status: "PASS", advisoryStatus: issues.length ? "DEBT" : "CLEAN", issueCount: issues.length, issues: issues.slice(0, 100), note: "Advisory only in hotfix. Does not fail structural one-pass." }, null, 2));
process.exit(0);

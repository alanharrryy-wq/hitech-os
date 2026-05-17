#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const reportRoot = process.env.PRISMA_REPORT_ROOT || "F:\\descargasf";
const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "_");
const jsonReport = path.join(reportRoot, `MOBILE_SNAPSHOT_QUALITY_REPORT_${stamp}.json`);
const mdReport = path.join(reportRoot, `MOBILE_SNAPSHOT_QUALITY_REPORT_${stamp}.md`);
const fixtureArg = process.argv.includes("--fixture") ? process.argv[process.argv.indexOf("--fixture") + 1] : null;
const urlArg = process.argv.includes("--url") ? process.argv[process.argv.indexOf("--url") + 1] : null;

function read(rel) {
  return fs.readFileSync(path.join(appRoot, rel), "utf8");
}

function check(list, status, message, detail = null) {
  list.push({ status, message, detail });
}

async function loadPayload(checks) {
  if (fixtureArg) {
    const parsed = JSON.parse(fs.readFileSync(path.resolve(fixtureArg), "utf8"));
    check(checks, "PASS", `fixture loaded: ${path.resolve(fixtureArg)}`);
    return parsed;
  }
  if (urlArg) {
    const response = await fetch(urlArg, { redirect: "follow" });
    const parsed = await response.json();
    check(checks, response.ok ? "PASS" : "WARN", `url loaded with status ${response.status}`, urlArg);
    return parsed;
  }
  return null;
}

function validateSnapshotShape(payload, checks) {
  const envelope = payload?.ok === true && payload?.data ? payload : { data: payload, meta: payload?.meta };
  const data = envelope.data || {};
  const meta = envelope.meta || {};
  check(checks, meta.generatedAt ? "PASS" : "FAIL", "meta.generatedAt present");
  check(checks, meta.source ? "PASS" : "FAIL", "meta.source present");
  check(checks, meta.runtimeMode ? "PASS" : "FAIL", "meta.runtimeMode present");
  check(checks, data.summary ? "PASS" : "FAIL", "summary present");
  check(checks, Array.isArray(data.alerts?.alerts) || Array.isArray(data.alerts) ? "PASS" : "WARN", "alerts shape present");
  check(checks, data.actionInbox || data.actionInboxPriorityStack || data.commandCenter ? "PASS" : "WARN", "action inbox/command center data present");
  check(checks, data.healthRadar || data.healthRadarCompact || data.health ? "PASS" : "WARN", "health radar/health data present");
  check(checks, data.dataQuality || data.summary?.dataReadiness ? "PASS" : "WARN", "data quality/readiness present");
}

const checks = [];
const payload = await loadPayload(checks);

if (payload) {
  validateSnapshotShape(payload, checks);
} else {
  const contract = read("src/lib/prisma-app/prisma-mobile-snapshot-contract.ts");
  const types = read("src/lib/prisma-app/mobile-data-plane/types.ts");
  const readiness = read("src/lib/prisma-app/mobile-data-plane/data-readiness.ts");
  check(checks, contract.includes("generatedAt") ? "PASS" : "FAIL", "snapshot contract includes generatedAt");
  check(checks, contract.includes("source") && contract.includes("runtimeMode") ? "PASS" : "FAIL", "snapshot contract includes source/runtimeMode");
  check(checks, types.includes("sourceStatuses") && types.includes("freshnessSeconds") ? "PASS" : "FAIL", "data plane tracks source status/freshness");
  check(checks, readiness.includes("confidence") || readiness.includes("sourceSummary") ? "PASS" : "WARN", "data readiness exposes confidence/source summary");
  check(checks, "SKIP", "no --fixture or --url supplied; source contracts inspected read-only");
}

const statuses = checks.map((item) => item.status);
const overall = statuses.includes("FAIL") ? "FAIL" : statuses.includes("WARN") ? "WARN" : statuses.includes("SKIP") ? "SKIP" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, mode: payload ? (fixtureArg ? "fixture" : "url") : "source-contract", fixture: fixtureArg || null, url: urlArg || null, checks };

fs.mkdirSync(reportRoot, { recursive: true });
fs.writeFileSync(jsonReport, `${JSON.stringify(report, null, 2)}\n`, "utf8");
fs.writeFileSync(mdReport, [
  "# Mobile Snapshot Quality Report",
  "",
  `Overall: ${overall}`,
  `Mode: ${report.mode}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.message}${item.detail ? ` - ${item.detail}` : ""}`)
].join("\n") + "\n", "utf8");

console.log(`${overall} mobile snapshot quality report: ${mdReport}`);
if (overall === "FAIL") process.exit(1);

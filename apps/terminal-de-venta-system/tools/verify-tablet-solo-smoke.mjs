#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

const normalizer = read("shared/licensing/license-normalizer.ts");
const featureResolver = read("shared/licensing/feature-resolver.ts");
const page = read("products/tablet/app/app/settings/license/page.tsx");
const card = read("products/tablet/app/components/license/license-status-card.tsx");
const loader = read("shared/licensing/license-loader.ts");
const refresh = read("shared/licensing/license-refresh-client.ts");

const checks = [
  {
    name: "missing license customer mode has pending install copy",
    status: normalizer.includes("LICENSE_CUSTOMER_PENDING") && card.includes("Instalación pendiente de licencia local") ? "PASS" : "FAIL"
  },
  {
    name: "missing license does not mark assignment unassigned",
    status: normalizer.includes('assignmentState: "unknown"') ? "PASS" : "FAIL"
  },
  {
    name: "basic POS fallback is resolved before assignment hard deny",
    status: featureResolver.indexOf('status.state === "missing"') >= 0 && featureResolver.indexOf('status.state === "missing"') < featureResolver.indexOf('"wrong_device"') ? "PASS" : "FAIL"
  },
  {
    name: "wrong device is explicit assignment failure",
    status: loader.includes('return "wrong_device"') ? "PASS" : "FAIL"
  },
  {
    name: "Tablet page consumes governor snapshot, not raw license parsing",
    status: page.includes("getTabletLicenseGovernor") && !page.includes("fs") && !page.includes("ProgramData") ? "PASS" : "FAIL"
  },
  {
    name: "refresh disabled remains informational",
    status: refresh.includes("Refresh remoto no configurado") && refresh.includes("La operación local continúa") ? "PASS" : "FAIL"
  },
  {
    name: "UI shows runtime provenance",
    status: card.includes("Origen config") && card.includes("Modo runtime") && card.includes("Archivo licencia") ? "PASS" : "FAIL"
  }
];

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, checks };
const files = reportPaths("PRISMA_TABLET_SOLO_SMOKE");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA Tablet Solo Smoke",
  "",
  `Overall: ${overall}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name}`)
].join("\n") + "\n");

console.log(`${overall} tablet solo smoke report: ${files.md}`);
if (overall !== "PASS") process.exit(1);

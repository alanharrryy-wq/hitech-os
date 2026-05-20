#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

const api = read("prisma-control-center/internal/py/license_ops_api.py");
const panel = read("prisma-control-center/internal/py/panel_3150.py");
const html = read("prisma-control-center/internal/web/index.html");
const js = read("prisma-control-center/internal/web/license_ops_console.js");
const css = read("prisma-control-center/internal/web/license_ops_console.css");
const qualityJs = read("prisma-control-center/internal/web/quality_bay.js");

const requiredActions = [
  "detect-runtime",
  "provision-tablet-solo",
  "provision-tablet-solo-dry-run",
  "import-local-license",
  "validate-runtime-config",
  "validate-provisioning",
  "tablet-solo-smoke",
  "no-direct-db-in-ui",
  "customer-smoke",
  "export-evidence-zip",
  "open-programdata",
  "start-tablet-runtime-config",
];

const dangerousTokens = ["rm -rf", "git reset --hard", "git clean -fdx", "del /s /q"];

const checks = [
  {
    name: "Control Center panel routes /api/license-ops",
    status: panel.includes("license_ops_api") && panel.includes("/api/license-ops") ? "PASS" : "FAIL",
  },
  {
    name: "License Ops API has all requested actions",
    status: requiredActions.every((action) => api.includes(`"${action}"`) || api.includes(`'${action}'`)) ? "PASS" : "FAIL",
  },
  {
    name: "License Ops API calls existing runtime/provisioning verifiers",
    status: ["tools/verify-runtime-config.mjs", "tools/verify-tablet-provisioning.mjs", "tools/verify-tablet-solo-smoke.mjs", "scripts/verify-no-direct-db-in-ui.mjs"].every((token) => api.includes(token)) ? "PASS" : "FAIL",
  },
  {
    name: "License Ops imports safe action helpers and report writer",
    status: api.includes("start_detached_process") && api.includes("export_support_bundle") ? "PASS" : "FAIL",
  },
  {
    name: "License Ops Explorer is read-only and server-side",
    status: api.includes("mode=ro") && api.includes("readOnly") && api.includes("serverBoundary") ? "PASS" : "FAIL",
  },
  {
    name: "Control Center web exposes Licencias surface",
    status: html.includes("license_ops_console.js") && html.includes("license_ops_console.css") && html.includes('data-prisma-interface-target="license"') ? "PASS" : "FAIL",
  },
  {
    name: "License Ops JS renders actions and explorer",
    status: js.includes("Runtime and Data Explorer") && js.includes("data-license-ops-action") && js.includes("/api/license-ops/explorer") ? "PASS" : "FAIL",
  },
  {
    name: "Quality switch supports license mode",
    status: qualityJs.includes('name === "license"') && qualityJs.includes("PRISMA License Ops") ? "PASS" : "FAIL",
  },
  {
    name: "License Ops CSS isolates license surface without hiding operation permanently",
    status: css.includes('body[data-prisma-interface="license"]') && css.includes("#licenseOpsSurface") ? "PASS" : "FAIL",
  },
  {
    name: "No destructive tokens in License Ops API",
    status: dangerousTokens.some((token) => api.includes(token)) ? "FAIL" : "PASS",
  },
];

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, checks };
const files = reportPaths("PRISMA_LICENSE_OPS_CONSOLE");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA License Ops Console Verify",
  "",
  `Overall: ${overall}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name}`)
].join("\n") + "\n");

console.log(`${overall} license ops console report: ${files.md}`);
if (overall !== "PASS") process.exit(1);

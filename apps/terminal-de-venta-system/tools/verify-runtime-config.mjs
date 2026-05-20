#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

const requiredFiles = [
  "shared/runtime/runtime-context-types.ts",
  "shared/runtime/runtime-paths.ts",
  "shared/runtime/runtime-context-resolver.ts",
  "shared/runtime/runtime-context-validator.ts",
  "shared/runtime/device-identity.ts",
  "shared/licensing/license-loader.ts",
  "shared/licensing/license-paths.ts"
];

const checks = [];

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

function check(name, ok, detail = "") {
  checks.push({ name, status: ok ? "PASS" : "FAIL", detail });
}

for (const rel of requiredFiles) {
  check(`file exists ${rel}`, fs.existsSync(path.join(terminalRoot, rel)), rel);
}

const resolver = read("shared/runtime/runtime-context-resolver.ts");
const validator = read("shared/runtime/runtime-context-validator.ts");
const licensePaths = read("shared/licensing/license-paths.ts");
const loader = read("shared/licensing/license-loader.ts");

check("precedence includes PRISMA_RUNTIME_CONFIG", resolver.includes("PRISMA_RUNTIME_CONFIG"));
check("canonical vertical ProgramData layout includes Commerce Config", resolver.includes("Commerce") && resolver.includes("Config"));
check("dev fallback isolated to runtimeMode dev", licensePaths.includes("context.runtimeMode === \"dev\"") && loader.includes("context.runtimeMode === \"dev\""));
check("customer mode blocks repo paths", validator.includes("RUNTIME_PATH_POINTS_TO_REPO"));
check("customer mode blocks dev license fallback", validator.includes("CUSTOMER_USES_DEV_LICENSE_FALLBACK"));
check("identity fields are required in customer mode", validator.includes("BUSINESS_ID_MISSING") && validator.includes("DEVICE_IDENTITY_MISSING"));
check("license assignment validates wrong device", loader.includes("wrong_device") && loader.includes("wrong_business") && loader.includes("wrong_terminal"));
check("missing license reports customer pending", read("shared/licensing/license-normalizer.ts").includes("LICENSE_CUSTOMER_PENDING"));

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, checks };
const files = reportPaths("PRISMA_RUNTIME_CONFIG_VERIFY");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA Runtime Config Verify",
  "",
  `Overall: ${overall}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name}${item.detail ? ` (${item.detail})` : ""}`)
].join("\n") + "\n");

console.log(`${overall} runtime config report: ${files.md}`);
if (overall !== "PASS") process.exit(1);

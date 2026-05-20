#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { reportPaths, reportRoot, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

const tmpRoot = path.join(reportRoot, "PRISMA_TABLET_PROVISIONING_VERIFY_RUNTIME");
fs.mkdirSync(tmpRoot, { recursive: true });

const command = [
  "tools/provision-prisma-runtime.mjs",
  "--apply",
  "--runtime-mode", "customer",
  "--runtime-root", tmpRoot,
  "--vertical", "commerce",
  "--role", "tablet",
  "--business-id", "verify-business",
  "--store-id", "verify-store",
  "--terminal-id", "verify-terminal",
  "--device-id", "verify-device",
  "--package-type", "TABLET_SOLO"
];

const result = spawnSync(process.execPath, command, { cwd: terminalRoot, encoding: "utf8", shell: false });
const runtimeJson = path.join(tmpRoot, "Config", "runtime.json");
const identityJson = path.join(tmpRoot, "Config", "device-identity.json");
const checks = [
  { name: "provisioning command exits 0", status: result.status === 0 ? "PASS" : "FAIL", detail: result.stdout || result.stderr },
  { name: "runtime.json created", status: fs.existsSync(runtimeJson) ? "PASS" : "FAIL", detail: runtimeJson },
  { name: "device identity created", status: fs.existsSync(identityJson) ? "PASS" : "FAIL", detail: identityJson }
];

if (fs.existsSync(runtimeJson)) {
  const runtime = JSON.parse(fs.readFileSync(runtimeJson, "utf8"));
  checks.push({ name: "runtime uses customer mode", status: runtime.runtimeMode === "customer" ? "PASS" : "FAIL", detail: runtime.runtimeMode });
  checks.push({ name: "license path is canonical Config", status: String(runtime.paths?.licenseFile || "").endsWith(path.join("Config", "license.json")) ? "PASS" : "FAIL", detail: runtime.paths?.licenseFile });
  checks.push({ name: "runtime root outside repo", status: !runtime.runtimeRoot.startsWith(terminalRoot) ? "PASS" : "FAIL", detail: runtime.runtimeRoot });
  checks.push({ name: "Tablet Solo invariant preserved", status: runtime.sync?.enabled === false ? "PASS" : "FAIL", detail: JSON.stringify(runtime.sync) });
}

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, tmpRoot, command, checks };
const files = reportPaths("PRISMA_TABLET_PROVISIONING_VERIFY");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA Tablet Provisioning Verify",
  "",
  `Overall: ${overall}`,
  `Temp root: ${tmpRoot}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name} ${item.detail ? `:: ${String(item.detail).slice(0, 240)}` : ""}`)
].join("\n") + "\n");

console.log(`${overall} tablet provisioning verifier: ${files.md}`);
if (overall !== "PASS") process.exit(1);

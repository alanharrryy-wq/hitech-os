#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const terminalRoot = path.resolve(appRoot, "..", "..", "..");

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

const checks = [];
function check(name, ok) {
  checks.push({ name, status: ok ? "PASS" : "FAIL" });
}

const normalizer = read("shared/licensing/license-normalizer.ts");
const resolver = read("shared/licensing/feature-resolver.ts");
const card = read("products/tablet/app/components/license/license-status-card.tsx");
const page = read("products/tablet/app/app/settings/license/page.tsx");

check("missing customer copy exists", normalizer.includes("LICENSE_CUSTOMER_PENDING") && card.includes("Instalación pendiente de licencia local"));
check("missing license keeps assignment unknown", normalizer.includes('assignmentState: "unknown"'));
check("basic fallback precedes assignment hard deny", resolver.indexOf('status.state === "missing"') < resolver.indexOf('"wrong_device"'));
check("license UI uses governor snapshot", page.includes("getTabletLicenseGovernor"));
check("UI does not parse license file directly", !card.includes("fs") && !card.includes("readFile") && !page.includes("ProgramData"));

const failed = checks.filter((item) => item.status === "FAIL");
for (const item of checks) console.log(`${item.status} ${item.name}`);
if (failed.length) process.exit(1);

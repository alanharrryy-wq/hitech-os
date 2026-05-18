#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const terminalRoot = path.resolve(appRoot, "..", "..", "..");
const mode = process.argv[2] || "verify";
const lanesDoc = path.join(terminalRoot, "docs", "release", "prisma-round2", "RELEASE_LANES.md");
const workspace = path.join(terminalRoot, "pnpm-workspace.yaml");

const lanes = fs.existsSync(lanesDoc) ? fs.readFileSync(lanesDoc, "utf8") : "";
const workspaceText = fs.existsSync(workspace) ? fs.readFileSync(workspace, "utf8") : "";
const offReleaseDocumented = lanes.includes("products/web/app") && lanes.includes("Off-release");
const inactiveWorkspace = !workspaceText
  .split(/\r?\n/)
  .map((line) => line.trim().replace(/^-\s*/, ""))
  .includes("products/web/app");

if (!offReleaseDocumented || !inactiveWorkspace) {
  console.error(JSON.stringify({
    status: "FAIL",
    mode,
    reason: "products/web/app is no longer consistently documented as an off-release non-workspace lane.",
    offReleaseDocumented,
    inactiveWorkspace,
  }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({
  status: "OFF_RELEASE_NON_BLOCKING",
  mode,
  package: "@hitech/prisma-web-eit",
  reason: "products/web/app is intentionally preserved outside the active PRISMA workspace until dependencies are pinned and lockfile importer is approved.",
  evidence: {
    lanesDoc,
    workspace,
    offReleaseDocumented,
    inactiveWorkspace,
  },
}, null, 2));

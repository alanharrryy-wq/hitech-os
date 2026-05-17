#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportRoot, run, terminalRoot, timestamp, writeJson, writeText, zipDirectory } from "./prisma-codex-utils.mjs";

const waveName = process.argv.includes("--wave-name") ? process.argv[process.argv.indexOf("--wave-name") + 1] : "materialization";
const stamp = timestamp();
const outDir = path.join(reportRoot, `prisma-wave-report-${waveName}-${stamp}`);
fs.mkdirSync(outDir, { recursive: true });

function safeCopy(filePath, targetName = path.basename(filePath)) {
  if (!fs.existsSync(filePath)) return null;
  const target = path.join(outDir, targetName);
  fs.copyFileSync(filePath, target);
  return target;
}

const recentReports = fs.existsSync(reportRoot)
  ? fs.readdirSync(reportRoot)
      .filter((name) => /PRISMA_|OUTBOX_|SYNC_|NO_DIRECT_|BACKUP_|MOBILE_|CHART_|PROMOTION_|VISUAL_/.test(name))
      .map((name) => path.join(reportRoot, name))
      .filter((filePath) => fs.existsSync(filePath) && fs.statSync(filePath).isFile())
      .sort()
      .slice(-40)
  : [];

const copied = recentReports.map((filePath) => safeCopy(filePath)).filter(Boolean);
const gitStatus = run("git", ["-C", path.resolve(terminalRoot, "..", ".."), "status", "--porcelain=v1", "-uall", "--", "apps/terminal-de-venta-system"]);
const packageJson = JSON.parse(fs.readFileSync(path.join(terminalRoot, "package.json"), "utf8"));
const manifest = {
  schemaVersion: "2026-05-12.wave-report.v1",
  generatedAt: new Date().toISOString(),
  waveName,
  terminalRoot,
  copiedReports: copied,
  packageVersion: packageJson.version,
  gitStatus: gitStatus.stdout.split(/\r?\n/).filter(Boolean)
};

writeJson(path.join(outDir, "wave-report-manifest.json"), manifest);
writeText(path.join(outDir, "WAVE_REPORT_SUMMARY.md"), [
  "# PRISMA Wave Report",
  "",
  `Wave: ${waveName}`,
  `Generated: ${manifest.generatedAt}`,
  `Terminal root: ${terminalRoot}`,
  "",
  "## Copied Reports",
  ...(copied.length ? copied.map((item) => `- ${item}`) : ["- none"]),
  "",
  "## Git Status",
  ...(manifest.gitStatus.length ? manifest.gitStatus.map((item) => `- ${item}`) : ["- clean for apps/terminal-de-venta-system"])
].join("\n") + "\n");

const zipPath = `${outDir}.zip`;
zipDirectory(outDir, zipPath);
console.log(`PASS wave report zip: ${zipPath}`);

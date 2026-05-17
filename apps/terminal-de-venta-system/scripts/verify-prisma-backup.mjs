#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { latestManifest, readJson, reportPaths, sha256, statusRank, writeJson, writeText } from "./prisma-codex-utils.mjs";

const manifestArg = process.argv.includes("--manifest") ? process.argv[process.argv.indexOf("--manifest") + 1] : null;
const manifestPath = manifestArg || latestManifest("prisma-backup-before-migration-");
const checks = [];

function check(name, ok, detail) {
  checks.push({ name, status: ok ? "PASS" : "FAIL", detail });
}

if (!manifestPath || !fs.existsSync(manifestPath)) {
  check("manifest exists", false, manifestPath || "No manifest found");
} else {
  const manifest = readJson(manifestPath);
  check("manifest json parses", true, manifestPath);
  check("backup dir exists", fs.existsSync(manifest.backupDir), manifest.backupDir);
  check("zip exists", fs.existsSync(manifest.zipPath), manifest.zipPath);
  for (const entry of manifest.files || []) {
    const exists = fs.existsSync(entry.targetPath);
    check(`file copied: ${path.basename(entry.targetPath)}`, exists, entry.targetPath);
    if (exists) check(`sha256 matches: ${path.basename(entry.targetPath)}`, sha256(entry.targetPath) === entry.sha256, entry.sourcePath);
  }
}

const overall = statusRank(checks.map((item) => item.status));
const report = { generatedAt: new Date().toISOString(), manifestPath, overall, checks };
const paths = reportPaths("PRISMA_BACKUP_VERIFY_REPORT");
writeJson(paths.json, report);
writeText(paths.md, [
  "# PRISMA Backup Verify Report",
  "",
  `Overall: ${overall}`,
  `Manifest: ${manifestPath || "missing"}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name} - ${item.detail}`)
].join("\n") + "\n");

console.log(`${overall} backup verification report: ${paths.md}`);
if (overall === "FAIL") process.exit(1);

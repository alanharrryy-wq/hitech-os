#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import {
  ensureDir,
  reportRoot,
  sha256,
  terminalRoot,
  timestamp,
  toWindowsPath,
  writeJson,
  writeText,
  zipDirectory
} from "./prisma-codex-utils.mjs";

const dryRun = process.argv.includes("--dry-run");
const stamp = timestamp();
const backupName = `prisma-backup-before-migration-${stamp}`;
const backupDir = path.join(reportRoot, backupName);
const zipPath = `${backupDir}.zip`;

const explicitCandidates = [
  path.join(terminalRoot, "products", "tablet", "app", "data", "tablet-pos.db"),
  path.join(terminalRoot, "products", "tablet", "app", "prisma", "data", "tablet-pos.db"),
  path.join(terminalRoot, "products", "tablet", "data", "tablet-pos.db"),
  path.join(path.resolve(terminalRoot, "..", ".."), "tools", "_local", "data", "terminal-de-venta-system", "canonical.db")
];

function collectSchemasAndMigrations() {
  const candidates = [
    path.join(terminalRoot, "prisma", "schema.prisma"),
    path.join(terminalRoot, "products", "tablet", "app", "prisma", "schema.prisma"),
    path.join(terminalRoot, "products", "pc", "app", "prisma", "schema.prisma")
  ].filter((filePath) => fs.existsSync(filePath));

  for (const migrationsRoot of [
    path.join(terminalRoot, "prisma", "migrations"),
    path.join(terminalRoot, "products", "tablet", "app", "prisma", "migrations")
  ]) {
    if (!fs.existsSync(migrationsRoot)) continue;
    for (const entry of fs.readdirSync(migrationsRoot, { recursive: true, withFileTypes: true })) {
      if (entry.isFile()) candidates.push(path.join(entry.parentPath, entry.name));
    }
  }
  return candidates;
}

function kindOf(filePath) {
  if (/\.(db|sqlite|sqlite3)$/i.test(filePath)) return "sqlite-db";
  if (filePath.endsWith("schema.prisma")) return "prisma-schema";
  if (filePath.includes(`${path.sep}migrations${path.sep}`)) return "prisma-migration";
  return "support";
}

function targetFor(filePath) {
  const absolute = path.resolve(filePath);
  const relative = absolute.startsWith(terminalRoot)
    ? path.relative(terminalRoot, absolute)
    : path.join("_external", absolute.replace(/^[A-Za-z]:\\/, "").replace(/[\\/:*?"<>|]/g, "_"));
  return path.join(backupDir, relative);
}

const sourceFiles = [...new Set([...explicitCandidates.filter((filePath) => fs.existsSync(filePath)), ...collectSchemasAndMigrations()])];
const manifest = {
  schemaVersion: "2026-05-12.prisma-backup.v1",
  generatedAt: new Date().toISOString(),
  mode: dryRun ? "dry-run" : "apply",
  terminalRoot: toWindowsPath(terminalRoot),
  backupDir: toWindowsPath(backupDir),
  zipPath: toWindowsPath(zipPath),
  files: [],
  warnings: []
};

for (const sourcePath of sourceFiles) {
  const stat = fs.statSync(sourcePath);
  const entry = {
    sourcePath: toWindowsPath(sourcePath),
    targetPath: toWindowsPath(targetFor(sourcePath)),
    kind: kindOf(sourcePath),
    size: stat.size,
    sha256: sha256(sourcePath)
  };
  if (entry.kind === "sqlite-db" && stat.size === 0) {
    entry.warning = "ZERO_BYTE_DB_NOT_OPERATIONAL_PROOF";
    manifest.warnings.push(`${entry.sourcePath} is 0 bytes`);
  }
  manifest.files.push(entry);
}

if (!dryRun) {
  ensureDir(backupDir);
  for (const entry of manifest.files) {
    ensureDir(path.dirname(entry.targetPath));
    fs.copyFileSync(entry.sourcePath, entry.targetPath);
  }
}

const summary = [
  "# PRISMA Backup Before Migration",
  "",
  `Generated: ${manifest.generatedAt}`,
  `Mode: ${manifest.mode}`,
  `Terminal root: ${manifest.terminalRoot}`,
  `Backup dir: ${manifest.backupDir}`,
  `ZIP: ${manifest.zipPath}`,
  "",
  "## Files",
  "",
  ...manifest.files.map((entry) => `- ${entry.kind}: ${entry.sourcePath} (${entry.size} bytes, sha256 ${entry.sha256})${entry.warning ? ` WARN ${entry.warning}` : ""}`),
  "",
  "## Warnings",
  "",
  ...(manifest.warnings.length ? manifest.warnings.map((item) => `- ${item}`) : ["- none"])
].join("\n");

if (dryRun) {
  const dryManifest = path.join(reportRoot, `${backupName}-dry-run.json`);
  const drySummary = path.join(reportRoot, `${backupName}-dry-run.md`);
  writeJson(dryManifest, manifest);
  writeText(drySummary, `${summary}\n`);
  console.log(`DRY_RUN backup manifest: ${dryManifest}`);
  process.exit(0);
}

writeJson(path.join(backupDir, "backup-manifest.json"), manifest);
writeText(path.join(backupDir, "BACKUP_SUMMARY.md"), `${summary}\n`);
zipDirectory(backupDir, zipPath);
if (!fs.existsSync(zipPath)) {
  console.error(`FAIL zip was not created: ${zipPath}`);
  process.exit(1);
}
console.log(`PASS backup created: ${zipPath}`);

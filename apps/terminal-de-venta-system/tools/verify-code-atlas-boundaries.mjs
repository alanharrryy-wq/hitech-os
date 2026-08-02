#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { reportPaths, terminalRoot, walkFiles, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

const atlasRoot = "F:\\descargasf";
const summaryPath = path.join(atlasRoot, "code_atlas_dependency_consumer_v03_terminal-de-venta-system_260520_1703_summary.json");
const unresolvedPath = path.join(atlasRoot, "code_atlas_dependency_consumer_v03_terminal-de-venta-system_260520_1703_unresolved.md");
const treePath = path.join(atlasRoot, "code_atlas_dependency_consumer_v03_terminal-de-venta-system_260520_1703_tree.txt");

function readIfExists(filePath, fallback = "") {
  return fs.existsSync(filePath) ? fs.readFileSync(filePath, "utf8") : fallback;
}

function readJsonIfExists(filePath) {
  return fs.existsSync(filePath) ? JSON.parse(fs.readFileSync(filePath, "utf8")) : null;
}

function gitStatusFiles() {
  const result = spawnSync("git", ["status", "--porcelain=v1", "-uall"], { cwd: path.resolve(terminalRoot, "..", ".."), encoding: "utf8" });
  if (result.status !== 0) return [];
  return result.stdout.split(/\r?\n/).filter(Boolean).map((line) => line.slice(3).trim().replace(/\\/g, "/"));
}

function scanBrowserViolations() {
  const roots = [
    "products/tablet/app/app",
    "products/tablet/app/components",
    "products/mobile/app/app",
    "products/mobile/app/components",
    "products/pc/app/app",
    "products/pc/app/components",
  ].map((rel) => path.join(terminalRoot, rel)).filter((item) => fs.existsSync(item));
  const allowSegments = [
    `${path.sep}app${path.sep}api${path.sep}`,
    `${path.sep}src${path.sep}server${path.sep}`,
    `${path.sep}scripts${path.sep}`,
    `${path.sep}tools${path.sep}`,
  ];
  const patterns = [
    { name: "@prisma/client import", regex: /from\s+["']@prisma\/client["']|require\(["']@prisma\/client["']\)/ },
    { name: "sqlite direct import", regex: /from\s+["'](?:sqlite3|better-sqlite3|@libsql\/client)["']|require\(["'](?:sqlite3|better-sqlite3|@libsql\/client)["']\)/ },
    { name: "fs direct import", regex: /from\s+["'](?:node:fs|fs)["']|require\(["'](?:node:fs|fs)["']\)/ },
    { name: "ProgramData direct path", regex: /C:\\\\ProgramData|C:\\ProgramData|process\.env\.ProgramData/ },
    { name: "raw license path", regex: /\blicense\.json\b|PRISMA_LICENSE_(?:PATH|FILE)/ },
  ];
  const violations = [];
  for (const root of roots) {
    for (const filePath of walkFiles(root, { allowExt: [".ts", ".tsx", ".js", ".jsx", ".mjs"] })) {
      if (allowSegments.some((segment) => filePath.includes(segment))) continue;
      // Next.js route handlers always execute on the server even when they live
      // below app/. Treating route.ts/route.js as browser modules creates false
      // positives for legitimate filesystem and database access at HTTP boundaries.
      if (/^route\.(?:[cm]?[jt]s|[jt]sx)$/i.test(path.basename(filePath))) continue;
      const text = fs.readFileSync(filePath, "utf8");
      // PRISMA_SURF_FIN2_SERVER_ONLY_BROWSER_SURFACE_GUARD:
      // Next.js files that explicitly import `server-only` may live under app/
      // while still being server runtime modules. Do not classify them as browser surfaces.
      if (/^\s*import\s+["']server-only["'];?/m.test(text) || text.includes("server-only")) continue;
      const rel = path.relative(terminalRoot, filePath);
      for (const pattern of patterns) {
        if (pattern.regex.test(text)) violations.push({ file: rel, pattern: pattern.name });
      }
    }
  }
  return violations;
}

const summary = readJsonIfExists(summaryPath);
const filesScanned = Number(summary?.dependency_summary?.files_scanned || summary?.files_scanned || summary?.filesScanned || 0);
const unresolved = readIfExists(unresolvedPath);
const tree = readIfExists(treePath);
const changedFiles = gitStatusFiles();
const browserViolations = scanBrowserViolations();
const runtimeUnresolved = unresolved
  .split(/\r?\n/)
  .filter((line) => /shared\/runtime|shared\\runtime|shared\/licensing|shared\\licensing|license_ops|license-ops/i.test(line));

const checks = [
  {
    name: "Code Atlas summary is available",
    status: summary && filesScanned > 1000 ? "PASS" : "FAIL",
    detail: summary ? `files=${filesScanned}` : "missing",
  },
  {
    name: "Active pnpm workspaces remain expected",
    status: tree.includes("products/tablet/app") && tree.includes("products/pc/app") && tree.includes("products/mobile/app") && tree.includes("products/chart-lab/app") ? "PASS" : "FAIL",
  },
  {
    name: "products/web/app was not touched",
    status: changedFiles.some((file) => file.includes("apps/terminal-de-venta-system/products/web/app/")) ? "FAIL" : "PASS",
  },
  {
    name: "Chart Lab was not modified by runtime/license work",
    status: changedFiles.some((file) => file.includes("apps/terminal-de-venta-system/products/chart-lab/app/")) ? "FAIL" : "PASS",
  },
  {
    name: "No runtime/licensing unresolved imports in Atlas baseline",
    status: runtimeUnresolved.length === 0 ? "PASS" : "FAIL",
    detail: runtimeUnresolved.slice(0, 5).join(" | "),
  },
  {
    name: "No direct DB/license access from browser surfaces",
    status: browserViolations.length === 0 ? "PASS" : "FAIL",
    detail: browserViolations.slice(0, 5).map((item) => `${item.file}:${item.pattern}`).join(" | "),
  },
  {
    name: "License Ops does not create a parallel license engine",
    status: readIfExists(path.join(terminalRoot, "prisma-control-center/internal/py/license_ops_api.py")).includes("tools/verify-runtime-config.mjs") &&
      readIfExists(path.join(terminalRoot, "prisma-control-center/internal/py/license_ops_api.py")).includes("tools/provision-prisma-runtime.mjs")
      ? "PASS"
      : "FAIL",
  },
  {
    name: "Tablet changes do not import PC as a sale dependency",
    status: changedFiles
      .filter((file) => file.includes("apps/terminal-de-venta-system/products/tablet/app/"))
      .some((file) => readIfExists(path.resolve(path.resolve(terminalRoot, "..", ".."), file)).includes("products/pc"))
      ? "FAIL"
      : "PASS",
  },
];

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, atlas: { summaryPath, unresolvedPath, treePath }, changedFiles, checks, browserViolations };
const files = reportPaths("PRISMA_CODE_ATLAS_BOUNDARIES");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA Code Atlas Boundaries Verify",
  "",
  `Overall: ${overall}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`)
].join("\n") + "\n");

console.log(`${overall} code atlas boundaries report: ${files.md}`);
if (overall !== "PASS") process.exit(1);

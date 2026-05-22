#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, walkFiles, writeJson, writeText } from "./prisma-codex-utils.mjs";

const roots = [
  "products/chart-lab/app/app",
  "products/chart-lab/app/src",
  "products/mobile/app/app",
  "products/mobile/app/src",
  "products/tablet/app/app",
  "products/tablet/app/components",
  "products/tablet/app/src",
  "products/pc/app/components",
  "products/pc/app/app",
  "products/pc/app/src"
].map((rel) => path.join(terminalRoot, rel));

const allowSegments = [
  `${path.sep}app${path.sep}api${path.sep}`,
  `${path.sep}src${path.sep}server${path.sep}`,
  `${path.sep}scripts${path.sep}`,
  `${path.sep}tools${path.sep}`,
  `${path.sep}data-adapters${path.sep}`,
  `${path.sep}adapters${path.sep}`
];
const patterns = [
  { name: "@prisma/client import", regex: /from\s+["']@prisma\/client["']|require\(["']@prisma\/client["']\)/ },
  { name: "PrismaClient construction", regex: /\bnew\s+PrismaClient\b/ },
  { name: "sqlite direct import", regex: /from\s+["'](?:sqlite3|better-sqlite3|@libsql\/client)["']|require\(["'](?:sqlite3|better-sqlite3|@libsql\/client)["']\)/ },
  { name: "fs direct import in UI", regex: /from\s+["']node:fs["']|from\s+["']fs["']|require\(["'](?:node:fs|fs)["']\)/ },
  { name: "DATABASE_URL in UI", regex: /\bDATABASE_URL\b/ },
  { name: "ProgramData direct path/env in UI", regex: /process\.env\.ProgramData|C:\\\\ProgramData|C:\\ProgramData/ },
  { name: "direct license path in UI", regex: /\blicense\.json\b|PRISMA_LICENSE_(?:PATH|FILE)/ },
  { name: "direct db path in UI", regex: /\.(?:db|sqlite|sqlite3)\b/i }
];

function isAllowed(filePath) {
  const normalized = filePath;
  return allowSegments.some((segment) => normalized.includes(segment));
}

const violations = [];
for (const root of roots) {
  for (const filePath of walkFiles(root, { allowExt: [".ts", ".tsx", ".js", ".jsx", ".mjs"] })) {
    if (isAllowed(filePath)) continue;
    const text = fs.readFileSync(filePath, "utf8");
    const lines = text.split(/\r?\n/);
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      for (const pattern of patterns) {
        if (pattern.regex.test(line)) {
          violations.push({
            file: path.resolve(filePath),
            line: index + 1,
            pattern: pattern.name,
            excerpt: line.trim().slice(0, 180)
          });
        }
      }
    }
  }
}

const overall = violations.length ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, scannedRoots: roots.map((root) => path.resolve(root)), violations };
const paths = reportPaths("NO_DIRECT_DB_IN_UI_REPORT");
writeJson(paths.json, report);
writeText(paths.md, [
  "# No Direct DB In UI Report",
  "",
  `Overall: ${overall}`,
  "",
  ...(violations.length
    ? violations.map((item) => `- FAIL: ${item.file}:${item.line} ${item.pattern} ${item.excerpt}`)
    : ["- PASS: no direct DB access found in scanned UI surfaces."])
].join("\n") + "\n");

console.log(`${overall} no-direct-db-in-ui report: ${paths.md}`);
if (violations.length) process.exit(1);

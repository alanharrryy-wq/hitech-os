#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const pcRoot = path.join(root, "products", "pc", "app");
const terms = ["runtime", "ingest", "payload", "ack", "dispatcher", "canonical", "feature gate", "raw", "adapter", "registry", "manifest", "tri-db", "delta", "event payload", "source map", "debug", "hydration", "endpoint"];
const allowedPathHints = ["/docs/", "/api/", "/src/server/", "/server/", "/src/uiux/", "/tools/", "/scripts/", "/prisma/"];
const technicalHints = ["EvidenceDrawer", "TechnicalDetails", "DebugPanel", "DevOnlyPanel", "InternalDocs", "TechnicalInfo", "Diagnostics", "DiagnosticsPanel"];
const ignoreDirs = new Set(["node_modules", ".next", "out", "dist", "build", "coverage", "test-results", "playwright-report"]);

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

function isAllowedFile(file) {
  const norm = file.replace(/\\/g, "/");
  return allowedPathHints.some(h => norm.includes(h));
}

function inTechnicalWindow(text, idx) {
  const w = text.slice(Math.max(0, idx - 1800), Math.min(text.length, idx + 800));
  return technicalHints.some(h => w.includes(h));
}

function visibleChunks(text) {
  const chunks = [];
  let m;
  const jsx = />\s*([^<>{}\n][^<>{}]{2,220})\s*</g;
  while ((m = jsx.exec(text))) chunks.push({ text: m[1], index: m.index });
  const attr = /(aria-label|title|placeholder)\s*=\s*["'`]([^"'`]{2,220})["'`]/g;
  while ((m = attr.exec(text))) chunks.push({ text: m[2], index: m.index });
  return chunks;
}

function termRegex(term) {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^A-Za-z0-9_])${escaped}([^A-Za-z0-9_]|$)`, "i");
}

const files = walk(pcRoot).filter(f => /\.(tsx|jsx)$/.test(f) && !isAllowedFile(f));
const hits = [];

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  for (const chunk of visibleChunks(text)) {
    if (inTechnicalWindow(text, chunk.index)) continue;
    for (const term of terms) {
      if (termRegex(term).test(chunk.text)) {
        const line = text.slice(0, chunk.index).split(/\r?\n/).length;
        hits.push({ file: path.relative(root, file).replace(/\\/g, "/"), line, term, sample: chunk.text.trim().slice(0, 180) });
      }
    }
  }
}

console.log(JSON.stringify({ verifier: "verify_pc_uiux_no_jargon", status: hits.length ? "FAIL" : "PASS", scannedFiles: files.length, hitCount: hits.length, hits: hits.slice(0, 200), note: "Uses word-boundary matching, so backoffice no longer trips ack." }, null, 2));
process.exit(hits.length ? 1 : 0);

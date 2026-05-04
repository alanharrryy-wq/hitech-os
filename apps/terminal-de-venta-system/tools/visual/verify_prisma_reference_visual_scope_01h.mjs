#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const requiredFiles = [
  "products/shared-ui/prisma/effects/prisma-reference-effects.css",
  "docs/design/PRISMA_REFERENCE_VISUAL_TARGET_01H.md",
  "docs/design/PRISMA_REFERENCE_VISUAL_SCOPE_01H.json",
  "docs/qa/PRISMA_REFERENCE_VISUAL_SCREENSHOT_MATRIX_01H.md",
  "tools/visual/verify_prisma_reference_visual_scope_01h.mjs",
  "tools/visual/capture_prisma_reference_screens_01h.mjs",
  "manifests/PRISMA_REFERENCE_VISUAL_FOUNDATION_01H_NEW_FILES.manifest.json"
];

const blocked = [
  "products/tablet/app/components/pos/pos-screen.tsx",
  "products/tablet/app/components/pos/pos-product-list.tsx",
  "products/tablet/app/components/pos/pos-ticket-panel.tsx",
  "products/pc/app/components/backoffice/executive-dashboard.tsx",
  "products/pc/app/components/layout/app-shell.tsx",
  "products/mobile/app/app/prisma-app/page.tsx"
];

function argValue(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1) return fallback;
  return process.argv[index + 1] ?? fallback;
}

const root = path.resolve(argValue("--root", process.cwd()));
const changedListPath = argValue("--changed-list", "");
const missing = requiredFiles.filter((file) => !fs.existsSync(path.join(root, file)));

if (missing.length) {
  console.error("FAIL missing required 01H files:");
  for (const file of missing) console.error(`- ${file}`);
  process.exit(1);
}

if (changedListPath) {
  const listFile = path.resolve(changedListPath);
  const changed = fs.readFileSync(listFile, "utf8").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const blockedHits = changed.filter((file) => blocked.includes(file));
  const sharedHits = changed.filter((file) => file.startsWith("shared/") || file.startsWith("packages/shared-kernel/"));
  if (blockedHits.length || sharedHits.length) {
    console.error("FAIL visual scope touched blocked files:");
    for (const file of [...blockedHits, ...sharedHits]) console.error(`- ${file}`);
    process.exit(1);
  }
}

console.log("OK PRISMA_REFERENCE_VISUAL_FOUNDATION_01H scope files are present.");
process.exit(0);

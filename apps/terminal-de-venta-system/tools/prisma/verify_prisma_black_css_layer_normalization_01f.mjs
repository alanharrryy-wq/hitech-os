#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
function argValue(name, fallback = null) {
  const index = args.indexOf(name);
  if (index >= 0 && index + 1 < args.length) return args[index + 1];
  return fallback;
}
const root = path.resolve(argValue("--root", process.cwd()));
const asJson = args.includes("--json");
const marker = "PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F";
const requiredFiles = [
  "docs/design/PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F.md",
  "docs/qa/PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F_QA.md",
  "shared/contracts/ui/prisma-black-css-layer-normalization-01f.contract.json",
  "manifests/PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F.manifest.json",
  "tools/prisma/verify_prisma_black_css_layer_normalization_01f.mjs"
];
const cssFiles = [
  "products/shared-ui/prisma/tokens/prisma-theme.css",
  "products/shared-ui/prisma/components/prisma-components.css",
  "products/tablet/app/components/pos/pos.module.css",
  "products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css",
  "products/pc/app/app/globals.css",
  "products/tablet/app/app/globals.css"
];
const terms = ["radial-gradient", "linear-gradient", "mix-blend-mode", "backdrop-filter", "filter:", "animation", "transition", "box-shadow"];

function read(rel) {
  const abs = path.join(root, rel);
  return fs.readFileSync(abs, "utf8");
}
function count(text, term) {
  return text.split(term).length - 1;
}

const missing = [];
const markerMissing = [];
const inventory = [];
for (const rel of requiredFiles) {
  if (!fs.existsSync(path.join(root, rel))) missing.push(rel);
}
for (const rel of cssFiles) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) {
    missing.push(rel);
    continue;
  }
  const text = read(rel);
  if (!text.includes(marker)) markerMissing.push(rel);
  const counts = {};
  for (const term of terms) counts[term] = count(text, term);
  inventory.push({ path: rel, lines: text.split(/\r?\n/).length, counts });
}

const warnings = [];
const theme = inventory.find((item) => item.path.endsWith("prisma-theme.css"));
const shared = inventory.find((item) => item.path.endsWith("prisma-components.css"));
if (theme && theme.counts["radial-gradient"] > 40) {
  warnings.push(`${theme.path}: radial-gradient alto (${theme.counts["radial-gradient"]}). 01F lo conserva; dedupe visual queda para 01G.`);
}
if (shared && shared.counts["mix-blend-mode"] > 8) {
  warnings.push(`${shared.path}: mix-blend-mode alto (${shared.counts["mix-blend-mode"]}). 01F lo inventaria; reemplazo queda para 01G.`);
}

const ok = missing.length === 0 && markerMissing.length === 0;
const result = { ok, root, requiredFiles: { expected: requiredFiles.length, missing }, cssMarkers: { expected: cssFiles.length, missing: markerMissing }, inventory, warnings };

if (asJson) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(ok ? "PRISMA Black CSS layer normalization 01F está instalado." : "PRISMA Black CSS layer normalization 01F está incompleto.");
  console.log(`Root: ${root}`);
  console.log(`Required files missing: ${missing.length}`);
  console.log(`CSS marker missing: ${markerMissing.length}`);
  console.log("Inventory:");
  for (const item of inventory) {
    console.log(`- ${item.path}: radial=${item.counts["radial-gradient"]}, blend=${item.counts["mix-blend-mode"]}, blur=${item.counts["backdrop-filter"]}, shadow=${item.counts["box-shadow"]}`);
  }
  if (warnings.length) {
    console.log("Warnings:");
    for (const warning of warnings) console.log(`- ${warning}`);
  }
  if (missing.length) {
    console.log("Missing files:");
    for (const item of missing) console.log(`- ${item}`);
  }
  if (markerMissing.length) {
    console.log("Missing CSS markers:");
    for (const item of markerMissing) console.log(`- ${item}`);
  }
}
process.exit(ok ? 0 : 1);

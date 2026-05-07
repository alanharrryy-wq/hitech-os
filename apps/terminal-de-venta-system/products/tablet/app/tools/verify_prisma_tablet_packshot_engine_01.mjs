#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const toolDir = dirname(fileURLToPath(import.meta.url));
const appRoot = dirname(toolDir);

const requiredFiles = [
  "components/pos/pos-packshots.ts",
  "components/pos/use-prisma-packshot-skin.ts",
  "components/pos/pos-product-list.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "public/products/packshots/light/README.md",
  "public/products/packshots/dark/README.md"
];

const requiredDirs = [
  "public/products/packshots/light",
  "public/products/packshots/dark"
];

const requiredNeedles = [
  ["components/pos/pos-packshots.ts", "PRISMA_TABLET_PACKSHOT_ENGINE_01"],
  ["components/pos/pos-packshots.ts", "/products/packshots"],
  ["components/pos/pos-packshots.ts", "resolveNextPackshotSrc"],
  ["components/pos/use-prisma-packshot-skin.ts", "usePrismaPackshotSkin"],
  ["components/pos/pos-product-list.tsx", "usePrismaPackshotSkin"],
  ["components/pos/pos-product-list.tsx", "resolveNextPackshotSrc"],
  ["components/pos/pos-ticket-panel.tsx", "usePrismaPackshotSkin"],
  ["components/pos/pos-ticket-panel.tsx", "resolveNextPackshotSrc"]
];

function fail(message) {
  console.error(`[BLOCKED] ${message}`);
  process.exitCode = 1;
}

function countPngs(dir) {
  if (!existsSync(dir)) return 0;
  let total = 0;
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    const stat = statSync(path);
    if (stat.isDirectory()) total += countPngs(path);
    else if (name.toLowerCase().endsWith(".png")) total += 1;
  }
  return total;
}

console.log("PRISMA Tablet packshot engine verifier 01");
console.log(`App root: ${appRoot}`);

for (const rel of requiredFiles) {
  const full = join(appRoot, rel);
  if (!existsSync(full)) fail(`Missing required file: ${rel}`);
}

for (const rel of requiredDirs) {
  const full = join(appRoot, rel);
  if (!existsSync(full)) fail(`Missing required directory: ${rel}`);
}

for (const [rel, needle] of requiredNeedles) {
  const full = join(appRoot, rel);
  if (!existsSync(full)) continue;
  const text = readFileSync(full, "utf8");
  if (!text.includes(needle)) fail(`Missing expected marker '${needle}' in ${rel}`);
}

const lightDir = join(appRoot, "public/products/packshots/light");
const darkDir = join(appRoot, "public/products/packshots/dark");
const lightCount = countPngs(lightDir);
const darkCount = countPngs(darkDir);

console.log(`Light PNGs: ${lightCount} (${relative(appRoot, lightDir)})`);
console.log(`Dark PNGs: ${darkCount} (${relative(appRoot, darkDir)})`);

if (lightCount === 0 || darkCount === 0) {
  console.log("[READY_WITH_CAVEATS] Engine installed; one or both skin folders still have no PNGs. Drop images later or rerun the installer to sync staging folders.");
} else {
  console.log("[READY] Engine installed and both skin folders contain PNGs.");
}

if (!process.exitCode) console.log("Verification complete.");

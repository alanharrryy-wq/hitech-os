#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const checks = [
  ["components/pos/pos-screen.tsx", "FEATURED_CATEGORY = \"Más vendidos\""],
  ["components/pos/pos-screen.tsx", "buildFeaturedProducts"],
  ["components/pos/pos-screen.tsx", "SHOWCASE_FAMILIES"],
  ["components/pos/pos-packshots.ts", "PRISMA_TABLET_PACKSHOT_ENGINE_03"],
  ["components/pos/pos-packshots.ts", "agua-con-gas-burbuja-fina-600ml"],
  ["components/pos/pos.module.css", "PRISMA_TABLET_PACKSHOT_ENGINE_03_SIZE_AND_SHELF::START"],
  ["components/pos/pos.module.css", ".productPackshot_water"],
  ["docs/PRISMA_TABLET_PACKSHOT_ENGINE_03.md", "Visual-only patch"]
];

let failed = false;
for (const [rel, needle] of checks) {
  const abs = path.join(appRoot, rel);
  if (!fs.existsSync(abs)) {
    console.error(`[FAIL] missing ${rel}`);
    failed = true;
    continue;
  }
  const text = fs.readFileSync(abs, "utf8");
  if (!text.includes(needle)) {
    console.error(`[FAIL] ${rel} missing marker: ${needle}`);
    failed = true;
  } else {
    console.log(`[OK] ${rel} contains ${needle}`);
  }
}

const lightDir = path.join(appRoot, "public/products/packshots/light");
const darkDir = path.join(appRoot, "public/products/packshots/dark");
const countPngs = (dir) => fs.existsSync(dir) ? fs.readdirSync(dir).filter((name) => name.toLowerCase().endsWith(".png")).length : 0;
console.log(`[INFO] Light PNGs: ${countPngs(lightDir)}`);
console.log(`[INFO] Dark PNGs: ${countPngs(darkDir)}`);

if (failed) process.exit(1);
console.log("[OK] PRISMA_TABLET_PACKSHOT_ENGINE_03 verifier passed");

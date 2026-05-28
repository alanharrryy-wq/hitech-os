#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { normalizeRouteBudget, validateRecipeForRoute } from "./surface-runtime-adapter.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "../../..");

const required = [
  "tools/prisma-surface-governor/surface-runtime-adapter/prisma.surface-runtime-adapter.schema.json",
  "tools/prisma-surface-governor/surface-runtime-adapter/surface-runtime-adapter.mjs",
  "tools/prisma-surface-governor/surface-runtime-adapter/README.md",
  "tools/prisma-surface-governor/route-budget-enforcer/prisma.route-budget.policy.json",
  "products/pc/app/src/prisma-surface-governor/surface-runtime-adapter.ts",
  "products/tablet/app/src/prisma-surface-governor/surface-runtime-adapter.ts",
  "products/mobile/app/src/prisma-surface-governor/surface-runtime-adapter.ts",
  "products/chart-lab/app/public/surface-visual-governor/runtime-adapter/latest/index.json",
  "products/pc/app/public/surface-visual-governor/runtime-adapter/latest/index.json",
  "products/tablet/app/public/surface-visual-governor/runtime-adapter/latest/index.json",
  "products/mobile/app/public/surface-visual-governor/runtime-adapter/latest/index.json"
];

const failures = [];
for (const rel of required) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) failures.push(`missing required file: ${rel}`);
}

const tabletPosBudget = normalizeRouteBudget({ surface: "tablet", route: "/pos" });
if (!tabletPosBudget.budget.posSafe) failures.push("tablet /pos budget must be posSafe");
if (tabletPosBudget.budget.allowWebgl) failures.push("tablet /pos must not allow WebGL");
if (tabletPosBudget.budget.allowPixi) failures.push("tablet /pos must not allow Pixi");
if (tabletPosBudget.budget.allowDarkStorm) failures.push("tablet /pos must not allow dark storm");

const validation = validateRecipeForRoute(
  { backgroundAsset: "tablet-soft-gray-clouds", material: "light-safe" },
  tabletPosBudget
);
if (!validation.ok) failures.push(`safe recipe should validate: ${validation.failures.join("; ")}`);

const unsafe = validateRecipeForRoute(
  { backgroundAsset: "storm-cloud-operations-real" },
  tabletPosBudget
);
if (unsafe.ok) failures.push("unsafe POS recipe should be rejected");

const publicRoots = [
  "products/chart-lab/app/public/surface-visual-governor/runtime-adapter",
  "products/pc/app/public/surface-visual-governor/runtime-adapter",
  "products/tablet/app/public/surface-visual-governor/runtime-adapter",
  "products/mobile/app/public/surface-visual-governor/runtime-adapter"
];

for (const relRoot of publicRoots) {
  const fullRoot = path.join(root, relRoot);
  if (!fs.existsSync(fullRoot)) continue;
  const stack = [fullRoot];
  while (stack.length) {
    const dir = stack.pop();
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) stack.push(full);
      if (entry.isFile() && /\.(json|md|txt|js|ts|tsx|css)$/i.test(entry.name)) {
        const txt = fs.readFileSync(full, "utf8");
        if (/[A-Z]:\\/.test(txt)) failures.push(`public local path leak: ${path.relative(root, full)}`);
        if (/\.(sqlite|sqlite3)/i.test(txt)) failures.push(`public sqlite token leak: ${path.relative(root, full)}`);
        const blockedDbNameToken = ["tablet", "pos"].join("-");
        if (txt.toLowerCase().includes(blockedDbNameToken)) failures.push(`public db name token leak: ${path.relative(root, full)}`);
      }
    }
  }
}

const result = { pilot: "17_surface_runtime_adapter_v1", status: failures.length ? "FAIL" : "PASS", failures };
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exit(1);

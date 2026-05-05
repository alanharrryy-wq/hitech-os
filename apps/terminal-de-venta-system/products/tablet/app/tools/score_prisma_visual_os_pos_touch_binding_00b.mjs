#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const arg = (name, fallback) => {
  const idx = process.argv.indexOf(name);
  return idx >= 0 ? process.argv[idx + 1] : fallback;
};
const root = arg("--root", process.cwd());
const outDir = arg("--out-dir", null);
const read = (relative) => readFileSync(join(root, relative), "utf8");

const checks = [
  ["control-hook", () => read("products/tablet/app/components/pos/pos-screen.tsx").includes('data-prisma-vos="00B"')],
  ["shell-surface", () => read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx").includes("data-prisma-visual-surface")],
  ["pos-css-scope", () => read("products/tablet/app/components/pos/pos.module.css").includes('.posWorkspace[data-prisma-vos="00B"]')],
  ["touch-target", () => read("products/tablet/app/components/pos/pos.module.css").includes("--vos-pos-hit-target: 54px")],
  ["checkout-emphasis", () => read("products/tablet/app/components/pos/pos.module.css").includes('[data-prisma-cart-state="active"] .checkoutLink')],
  ["reduced-motion", () => read("products/tablet/app/components/pos/pos.module.css").includes("prefers-reduced-motion")],
  ["shell-binding", () => read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css").includes('.shell[data-prisma-visual-surface="tablet-pos"]')],
  ["search-counts", () => read("products/tablet/app/components/pos/pos-screen.tsx").includes("activeProductCount")],
];

const results = checks.map(([name, fn]) => ({ name, pass: Boolean(fn()) }));
const score = Math.round((results.filter((r) => r.pass).length / results.length) * 100);
const report = {
  package: "PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B_20260503_v01",
  score,
  pass: score >= 100,
  results,
  generatedAt: new Date().toISOString(),
};

console.log(`[VOS 00B SCORE] ${score} pass=${report.pass}`);
if (outDir) {
  mkdirSync(outDir, { recursive: true });
  const base = `prisma_visual_os_pos_touch_00b_${new Date().toISOString().replace(/[-:T]/g, "").slice(0, 12)}`;
  writeFileSync(join(outDir, `${base}.json`), JSON.stringify(report, null, 2), "utf8");
  writeFileSync(join(outDir, `${base}.md`), `# PRISMA Visual OS POS Touch 00B Score\n\nScore: **${score}**\n\nPass: **${report.pass}**\n\n` + results.map((r) => `- ${r.pass ? "OK" : "FAIL"} ${r.name}`).join("\n") + "\n", "utf8");
}
if (!report.pass) process.exit(1);

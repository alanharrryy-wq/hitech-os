import fs from "node:fs";
import path from "node:path";

const targetRoot = process.argv[2] || process.cwd();
const cssPath = path.join(targetRoot, "apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css");

if (!fs.existsSync(cssPath)) {
  console.error(`Missing CSS file: ${cssPath}`);
  process.exit(1);
}

const css = fs.readFileSync(cssPath, "utf8");
const needles = [
  "PRISMA_TABLET_SIDEBAR_GLASS_CLEANUP_FIX_01::START",
  ".navGroupSummary",
  ".navGroupMeta",
  '.navFlowHint',
  ':global([data-prisma-component="SkinSelector"]) select'
];
const missing = needles.filter((needle) => !css.includes(needle));
if (missing.length) {
  console.error("Verifier failed. Missing markers/selectors:");
  for (const item of missing) console.error(` - ${item}`);
  process.exit(2);
}

console.log("Verifier OK: PRISMA Tablet sidebar glass cleanup fix markers are present.");

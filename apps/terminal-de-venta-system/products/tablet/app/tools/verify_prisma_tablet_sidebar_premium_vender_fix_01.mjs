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
  "PRISMA_TABLET_SIDEBAR_PREMIUM_VENDER_01::START",
  "prismaPrimaryFloat",
  '.navActive[data-primary="true"]',
  ".navPrimary .navText small"
];

const missing = needles.filter((needle) => !css.includes(needle));
if (missing.length > 0) {
  console.error("Verifier failed. Missing selectors/markers:");
  for (const item of missing) console.error(` - ${item}`);
  process.exit(2);
}

console.log("Verifier OK: PRISMA Tablet sidebar premium Vender fix is present.");

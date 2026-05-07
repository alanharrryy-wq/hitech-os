import fs from "node:fs";
import path from "node:path";

const root = process.argv[2] || process.cwd();
const cssPath = path.join(root, "apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css");
const logoPath = path.join(root, "apps/terminal-de-venta-system/products/tablet/app/public/prisma/logo-prisma-primary.png");

for (const file of [cssPath, logoPath]) {
  if (!fs.existsSync(file)) {
    console.error(`Missing file: ${file}`);
    process.exit(1);
  }
}

const css = fs.readFileSync(cssPath, "utf8");
const checks = [
  "PRISMA_TABLET_LOGO_INJECTION_01::START",
  "url('/prisma/logo-prisma-primary.png')",
  ".brandMark",
  ".brandText"
];

const missing = checks.filter((needle) => !css.includes(needle));
if (missing.length) {
  console.error("Verifier failed. Missing markers/selectors:");
  for (const item of missing) console.error(` - ${item}`);
  process.exit(2);
}

const stat = fs.statSync(logoPath);
if (stat.size < 10000) {
  console.error(`Logo file looks too small: ${stat.size} bytes`);
  process.exit(3);
}

console.log("Verifier OK: PRISMA Tablet logo injection is present.");

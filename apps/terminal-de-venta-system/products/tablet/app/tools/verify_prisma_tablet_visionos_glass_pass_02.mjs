import fs from "node:fs";
import path from "node:path";

const root = process.argv[2] || process.cwd();
const cssPath = path.join(root, "apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css");
const selectorPath = path.join(root, "apps/terminal-de-venta-system/products/tablet/app/components/ui/prisma-skin-selector.module.css");

for (const file of [cssPath, selectorPath]) {
  if (!fs.existsSync(file)) {
    console.error(`Missing file: ${file}`);
    process.exit(1);
  }
}

const css = fs.readFileSync(cssPath, "utf8");
const selector = fs.readFileSync(selectorPath, "utf8");
const checks = [
  [css, "PRISMA_TABLET_VISIONOS_GLASS_PASS_02::START"],
  [css, "prismaVisionCtaFloat"],
  [css, ".navGroupMeta"],
  [css, ".navFlowHint"],
  [selector, "PRISMA_TABLET_VISIONOS_GLASS_PASS_02_SELECTOR::START"]
];

const missing = checks.filter(([haystack, needle]) => !haystack.includes(needle)).map(([, needle]) => needle);
if (missing.length) {
  console.error("Verifier failed. Missing markers:");
  for (const item of missing) console.error(` - ${item}`);
  process.exit(2);
}

console.log("Verifier OK: PRISMA Tablet VisionOS Glass Pass 02 markers are present.");

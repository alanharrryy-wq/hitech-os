import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "config/prisma-visual-os/prisma-visual-controls.active.json",
  "styles/prisma-visual-os/prisma-visual-layers.css",
  "styles/prisma-visual-os/prisma-visual-controls.generated.css",
  "products/tablet/app/app/globals.css",
  "products/tablet/app/app/visual-os/page.tsx",
  "products/tablet/app/components/visual-os/prisma-visual-controls-panel.tsx",
  "products/tablet/app/components/pos/pos-screen.tsx",
  "products/tablet/app/components/checkout/checkout-screen.tsx",
  "products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx"
];
const missing = required.filter((rel) => !fs.existsSync(path.join(root, rel)));
if (missing.length) {
  for (const rel of missing) console.error(`ERROR missing ${rel}`);
  process.exit(1);
}
const checks = [
  ["products/tablet/app/app/globals.css", "prisma-visual-controls.generated.css"],
  ["products/tablet/app/components/pos/pos-screen.tsx", "data-prisma-vos-stage=\"00F_00I\""],
  ["products/tablet/app/components/checkout/checkout-screen.tsx", "visualSurface=\"tablet-checkout\""],
  ["products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx", "data-prisma-vos-runtime=\"00E\""],
  ["products/tablet/app/components/visual-os/prisma-visual-controls-panel.tsx", "POS_TOUCH_REFERENCE"],
  ["products/tablet/app/components/pos/pos.module.css", "PRISMA_TABLET_VISUAL_CONTROLLED_00F_00G_00H_00I"],
  ["products/tablet/app/components/checkout/checkout.module.css", "Checkout/cobro focus"],
  ["products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css", "Tablet shell governance"],
  ["products/tablet/app/package.json", "verify:visual-os-tablet-00f-00i"]
];
for (const [rel, needle] of checks) {
  const text = fs.readFileSync(path.join(root, rel), "utf8");
  if (!text.includes(needle)) {
    console.error(`ERROR ${rel} no contiene ${needle}`);
    process.exit(1);
  }
}
console.log("OK PRISMA Tablet visual controlled 00F/00G/00H/00I verified");

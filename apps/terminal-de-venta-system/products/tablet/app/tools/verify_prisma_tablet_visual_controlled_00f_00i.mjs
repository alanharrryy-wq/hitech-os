import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "products/tablet/app/app/globals.css",
  "products/tablet/app/app/layout.tsx",
  "products/tablet/app/app/prisma-tablet-nocturne-canonical.css",
  "products/tablet/app/components/pos/pos-screen.tsx",
  "products/tablet/app/components/checkout/checkout-screen.tsx",
  "products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx",
  "products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css",
  "products/tablet/app/package.json"
];
const missing = required.filter((rel) => !fs.existsSync(path.join(root, rel)));
if (missing.length) {
  for (const rel of missing) console.error(`ERROR missing ${rel}`);
  process.exit(1);
}
const checks = [
  ["products/tablet/app/app/layout.tsx", "prisma-tablet-nocturne-canonical.css"],
  ["products/tablet/app/app/layout.tsx", "data-prisma-canonical-shell=\"nocturne-reference-1607\""],
  ["products/tablet/app/app/prisma-tablet-nocturne-canonical.css", "--prisma-canonical-card-backdrop-count: 0"],
  ["products/tablet/app/app/prisma-tablet-nocturne-canonical.css", "prefers-reduced-transparency"],
  ["products/tablet/app/components/pos/pos-screen.tsx", "visualSurface=\"tablet-pos-nocturne\""],
  ["products/tablet/app/components/pos/pos-screen.tsx", "PosTerminalSurface"],
  ["products/tablet/app/components/checkout/checkout-screen.tsx", "completeCartSale"],
  ["products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx", "data-prisma-canonical-shell=\"nocturne-reference-1607\""],
  ["products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css", "prefers-reduced-transparency"],
  ["products/tablet/app/package.json", "verify:visual-os-tablet-00f-00i"]
];
for (const [rel, needle] of checks) {
  const text = fs.readFileSync(path.join(root, rel), "utf8");
  if (!text.includes(needle)) {
    console.error(`ERROR ${rel} no contiene ${needle}`);
    process.exit(1);
  }
}
console.log("OK PRISMA Tablet canonical visual contract verified (legacy 00F/00I entrypoint reconciled)");

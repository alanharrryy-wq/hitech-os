import fs from "node:fs";
import path from "node:path";

const repo = process.argv[2] || process.cwd();
const app = path.join(repo, "apps", "terminal-de-venta-system", "products", "pc", "app");

const targets = {
  layout: path.join(app, "app", "layout.tsx"),
  premiumCss: path.join(app, "app", "prisma-pc-premium-visual-system.css"),
  runtime: path.join(app, "app", "components", "PrismaPcPremiumRuntime.tsx"),
  primitives: path.join(app, "components", "premium", "prisma-premium-radix-primitives.tsx"),
  tokens: path.join(app, "components", "premium", "pc-premium.css.ts"),
  inventoryCss: path.join(app, "components", "inventory", "pc-inventory-master-detail.module.css")
};

function read(file) {
  if (!fs.existsSync(file)) throw new Error(`Missing file: ${file}`);
  return fs.readFileSync(file, "utf8");
}

function assertIncludes(name, text, needle) {
  if (!text.includes(needle)) throw new Error(`${name} missing ${needle}`);
}

function assertClean(name, text) {
  const blocked = "!" + "important";
  if (text.includes(blocked)) throw new Error(`${name} contains forbidden priority override token`);
}

const layout = read(targets.layout);
const css = read(targets.premiumCss);
const runtime = read(targets.runtime);
const primitives = read(targets.primitives);
const tokens = read(targets.tokens);
const inventoryCss = read(targets.inventoryCss);

for (const [name, text] of Object.entries({ layout, css, runtime, primitives, tokens, inventoryCss })) {
  assertClean(name, text);
}

assertIncludes("layout", layout, 'import "./prisma-pc-premium-visual-system.css";');
assertIncludes("layout", layout, 'PrismaPcPremiumRuntime');
assertIncludes("layout", layout, 'PC_PREMIUM_LIGHT_SYS1');

assertIncludes("premium css", css, "PRISMA PC Premium Visual System SYS1");
assertIncludes("premium css", css, "prisma-pc-premium-ambient");
assertIncludes("premium css", css, "html[data-prisma-surface=\"pc-backoffice\"] .card");
assertIncludes("premium css", css, "html[data-prisma-surface=\"pc-backoffice\"] .topbar");

assertIncludes("runtime", runtime, 'await import("ogl")');
assertIncludes("runtime", runtime, "data-prisma-component=\"PrismaPcPremiumRuntime\"");

for (const lib of [
  "@radix-ui/react-dialog",
  "@radix-ui/react-dropdown-menu",
  "@radix-ui/react-scroll-area",
  "@radix-ui/react-select",
  "@radix-ui/react-tabs",
  "@radix-ui/react-tooltip",
  "@radix-ui/react-slot"
]) {
  assertIncludes("premium primitives", primitives, lib);
}

assertIncludes("vanilla tokens", tokens, "@vanilla-extract/css");
assertIncludes("inventory css", inventoryCss, "Inventory Premium SYS1");
assertIncludes("inventory css", inventoryCss, "linear-gradient(135deg, rgba(255, 255, 255");
assertIncludes("inventory css", inventoryCss, ".tableFrame tr:hover td");
assertIncludes("inventory css", inventoryCss, ".timelineEvent");

const legacyDarkTokens = [
  "rgba(15, 23, 42",
  "rgba(2, 6, 23",
  "#05070d"
];
for (const token of legacyDarkTokens) {
  if (inventoryCss.includes(token)) throw new Error(`inventory css still contains legacy dark token ${token}`);
}

console.log("PC PREMIUM VISUAL CLEANUP SYS1 VERIFY OK");

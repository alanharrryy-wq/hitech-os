import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const mustExist = [
  "components/operational-screen/prisma-operational-screen.tsx",
  "components/operational-screen/prisma-operational-screen.module.css",
  "components/operational-screen/index.ts",
  "src/lib/ui/prisma-operational-screen-contract.ts",
  "src/lib/ui/prisma-operational-screen-engine.ts",
  "app/screen-standard-preview/page.tsx",
  "docs/ux/PRISMA_TABLET_SCREEN_STANDARD_01A.md",
  "docs/qa/tablet-screen-standard-01a/acceptance.md"
];

function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) throw new Error(`Missing ${rel}`);
  return fs.readFileSync(file, "utf8");
}

for (const rel of mustExist) {
  read(rel);
  console.log(`OK exists ${rel}`);
}

const component = read("components/operational-screen/prisma-operational-screen.tsx");
const engine = read("src/lib/ui/prisma-operational-screen-engine.ts");
const preview = read("app/screen-standard-preview/page.tsx");
const css = read("components/operational-screen/prisma-operational-screen.module.css");

const requiredSnippets = [
  [component, "PrismaTabletShellUnified", "component uses tablet shell"],
  [component, "readyOperationalScreen", "component normalizes model"],
  [engine, "assertNoPlaceholderCopy", "engine blocks placeholder copy"],
  [engine, "moneyMXN", "engine formats MXN"],
  [preview, "PrismaOperationalScreen", "preview renders standard"],
  [css, "backdrop-filter", "css includes premium glass"],
  [css, "masthead", "css includes masthead system"]
];

for (const [text, snippet, label] of requiredSnippets) {
  if (!text.includes(snippet)) throw new Error(`Missing ${label}: ${snippet}`);
  console.log(`OK ${label}`);
}

const forbidden = [
  "new PrismaClient({ datasources",
  "sqlite:",
  "tablet-screen-standard.db"
];

const allText = mustExist.map((rel) => read(rel)).join("\n");
for (const snippet of forbidden) {
  if (allText.includes(snippet)) throw new Error(`Forbidden DB mutation marker found: ${snippet}`);
}
console.log("OK no DB creation markers");

const placeholderFiles = [
  "app/returns/page.tsx",
  "app/sales/page.tsx",
  "app/shift/page.tsx",
  "app/stock/page.tsx",
  "app/sync/page.tsx"
];
for (const rel of placeholderFiles) {
  if (fs.existsSync(path.join(root, rel))) console.log(`INFO unchanged target placeholder route present: ${rel}`);
}

console.log("OK PRISMA_TABLET_SCREEN_STANDARD_01A verification passed");

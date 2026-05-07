import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const posPackshots = path.join(appRoot, "components", "pos", "pos-packshots.ts");
const lightDir = path.join(appRoot, "public", "products", "packshots", "light");
const darkDir = path.join(appRoot, "public", "products", "packshots", "dark");

const requiredSnippets = [
  "PRISMA_TABLET_PACKSHOT_ENGINE_02",
  "GENERATED_PRODUCT_RULES",
  "aceite-vegetal",
  "atun-en-agua-140g",
  "avena-hojuelas-500g",
  "azucar-refinada-1kg",
  "cafe-soluble-200g",
  "CATEGORY_SKIN_FALLBACK_SLUGS"
];

function fail(message) {
  console.error(`[FAIL] ${message}`);
  process.exitCode = 1;
}

function ok(message) {
  console.log(`[OK] ${message}`);
}

function warn(message) {
  console.warn(`[WARN] ${message}`);
}

if (!fs.existsSync(posPackshots)) {
  fail(`Missing ${posPackshots}`);
} else {
  const text = fs.readFileSync(posPackshots, "utf8");
  for (const snippet of requiredSnippets) {
    if (!text.includes(snippet)) {
      fail(`pos-packshots.ts missing snippet: ${snippet}`);
    }
  }
  ok("pos-packshots.ts contains v02 alias resolver contract.");
}

function countPngs(dir) {
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir).filter((name) => name.toLowerCase().endsWith(".png")).length;
}

const lightCount = countPngs(lightDir);
const darkCount = countPngs(darkDir);

if (lightCount === 0) warn(`No light PNGs found under ${lightDir}`);
else ok(`Light PNGs: ${lightCount}`);

if (darkCount === 0) warn(`No dark PNGs found under ${darkDir}`);
else ok(`Dark PNGs: ${darkCount}`);

const critical = [
  ["light", "aceite-vegetal.png"],
  ["light", "atun-en-agua-140g.png"],
  ["light", "avena-hojuelas-500g.png"],
  ["light", "azucar-refinada-1kg.png"],
  ["light", "cafe-soluble-200g.png"],
  ["dark", "aceite-vegetal.png"],
  ["dark", "atun-en-agua-140g.png"],
  ["dark", "avena-hojuelas-500g.png"],
  ["dark", "azucar-refinada-1kg.png"],
  ["dark", "cafe-soluble-200g.png"]
];

for (const [skin, file] of critical) {
  const full = path.join(appRoot, "public", "products", "packshots", skin, file);
  if (!fs.existsSync(full)) warn(`Critical packshot not present yet: ${full}`);
}

if (!process.exitCode) ok("PRISMA Tablet Packshot Engine 02 verifier passed.");

import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "app/catalog/page.tsx",
  "app/api/pos/products/create/route.ts",
  "app/api/pos/products/update/route.ts",
  "app/api/pos/products/barcodes/validate/route.ts",
  "components/catalog/catalog-screen.tsx",
  "components/catalog/catalog-product-table.tsx",
  "components/catalog/catalog-product-form.tsx",
  "components/catalog/catalog-product-drawer.tsx",
  "components/catalog/catalog-barcode-field.tsx",
  "components/catalog/catalog-stock-field.tsx",
  "components/catalog/catalog-empty-state.tsx",
  "components/catalog/catalog.module.css",
  "src/server/pos-api/product-mutations.prisma.ts",
  "src/server/pos-api/product-mutation-validators.ts",
  "src/lib/catalog/product-form-state.ts",
  "src/lib/catalog/product-visible-errors.ts",
  "docs/qa/catalog-products-03/acceptance.md",
  "docs/qa/catalog-products-03/product-cases.json"
];

function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}

let ok = true;
for (const rel of required) {
  const exists = fs.existsSync(path.join(root, rel));
  console.log(`${exists ? "OK" : "FAIL"} ${rel}`);
  ok = ok && exists;
}

const page = read("app/catalog/page.tsx");
const screen = read("components/catalog/catalog-screen.tsx");
const form = read("components/catalog/catalog-product-form.tsx");
const mutations = read("src/server/pos-api/product-mutations.prisma.ts");
const pkg = JSON.parse(read("package.json"));

const checks = [
  ["/catalog usa CatalogScreen", page.includes("CatalogScreen") && !page.includes("TouchPosApp")],
  ["UI tiene Nuevo producto", screen.includes("Nuevo producto") || screen.includes("Crear producto") || form.includes("Nuevo producto") || form.includes("Crear producto")],
  ["UI llama create", screen.includes("/api/pos/products/create")],
  ["UI llama update", screen.includes("/api/pos/products/update")],
  ["Mutaciones crean outbox", mutations.includes("catalog.product.created") && mutations.includes("catalog.product.updated")],
  ["Valida duplicado barcode", mutations.includes("DUPLICATE_BARCODE")],
  ["package verify script", Boolean(pkg.scripts?.["verify:catalog-products-03"])]
];

for (const [label, passed] of checks) {
  console.log(`${passed ? "OK" : "FAIL"} ${label}`);
  ok = ok && passed;
}

if (!ok) process.exit(1);
console.log("PASS verify_tablet_catalog_products_03");

#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const toolsDir = path.dirname(__filename);
const appRoot = path.resolve(toolsDir, "..");

function exists(p) {
  return fs.existsSync(p);
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function check(checks, id, ok, detail) {
  checks.push({ id, ok, detail });
}

const checks = [];
const packagePath = path.join(appRoot, "package.json");
const catalogPath = path.join(appRoot, "data", "tablet-catalog.local.json");
const modulePath = path.join(appRoot, "src", "server", "local-catalog", "index.ts");
const productsRoute = path.join(appRoot, "app", "api", "pos", "catalog", "products", "route.ts");
const resolveRoute = path.join(appRoot, "app", "api", "pos", "catalog", "resolve", "route.ts");
const importRoute = path.join(appRoot, "app", "api", "pos", "catalog", "import", "route.ts");

check(checks, "I02-001 package.json exists", exists(packagePath), packagePath);
check(checks, "I02-002 local catalog file exists", exists(catalogPath), catalogPath);
check(checks, "I02-003 local catalog module exists", exists(modulePath), modulePath);
check(checks, "I02-004 products route exists", exists(productsRoute), productsRoute);
check(checks, "I02-005 resolve route exists", exists(resolveRoute), resolveRoute);
check(checks, "I02-006 import route exists", exists(importRoute), importRoute);

if (exists(packagePath)) {
  const pkg = readJson(packagePath);
  check(checks, "I02-007 verify:i02-catalogo script registered", Boolean(pkg.scripts && pkg.scripts["verify:i02-catalogo"]), "package.json scripts.verify:i02-catalogo");
  check(checks, "I02-008 tablet:i02:catalogo script registered", Boolean(pkg.scripts && pkg.scripts["tablet:i02:catalogo"]), "package.json scripts.tablet:i02:catalogo");
}

if (exists(catalogPath)) {
  const catalog = readJson(catalogPath);
  const products = Array.isArray(catalog.products) ? catalog.products : [];
  const active = products.filter((p) => p.isActive !== false);
  const inactive = products.filter((p) => p.isActive === false);
  const hasSku = products.some((p) => typeof p.sku === "string" && p.sku.length > 0);
  const hasBarcode = products.some((p) => typeof p.barcode === "string" && p.barcode.length > 0);
  const hasPrice = products.every((p) => Number.isFinite(p.priceCents) && p.priceCents >= 0);
  const hasStock = products.every((p) => Number.isFinite(p.stockOnHand));

  check(checks, "I02-009 catalog has products", products.length >= 2, `count=${products.length}`);
  check(checks, "I02-010 catalog has active product", active.length >= 1, `active=${active.length}`);
  check(checks, "I02-011 catalog has inactive product fixture", inactive.length >= 1, `inactive=${inactive.length}`);
  check(checks, "I02-012 catalog has SKU", hasSku, "sku present");
  check(checks, "I02-013 catalog has barcode", hasBarcode, "barcode present");
  check(checks, "I02-014 catalog has valid priceCents", hasPrice, "priceCents valid");
  check(checks, "I02-015 catalog has stockOnHand", hasStock, "stockOnHand valid");
}

for (const [id, file, patterns] of [
  ["I02-016 module exports list/resolve/import", modulePath, ["listLocalCatalogProducts", "resolveLocalCatalogProduct", "importLocalCatalogProducts"]],
  ["I02-017 products route returns source metadata", productsRoute, ["tablet-local-catalog", "NextResponse.json"]],
  ["I02-018 resolve route has human error", resolveRoute, ["LOCAL_PRODUCT_NOT_FOUND", "catálogo local"]],
  ["I02-019 import route validates products", importRoute, ["LOCAL_CATALOG_PRODUCTS_REQUIRED", "products"]],
]) {
  if (exists(file)) {
    const text = fs.readFileSync(file, "utf8");
    const ok = patterns.every((pattern) => text.includes(pattern));
    check(checks, id, ok, file);
  } else {
    check(checks, id, false, `${file} missing`);
  }
}

const ok = checks.every((item) => item.ok);
const evidenceDir = path.join(appRoot, "evidence", "verifier-output");
fs.mkdirSync(evidenceDir, { recursive: true });
const report = {
  ok,
  appRoot,
  catalogPath,
  checks,
  verdict: ok ? "PASS" : "FAIL",
  note: "I02 validates local operational catalog scaffolding for Tablet Solo. HTTP runtime smoke requires Next dev server."
};
fs.writeFileSync(path.join(evidenceDir, "verify_tablet_i02_catalogo.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report, null, 2));
process.exit(ok ? 0 : 2);

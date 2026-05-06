#!/usr/bin/env node
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { TABLET_CONVENIENCE_PRODUCTS_04B } from "../scripts/tablet-seed-catalog.mjs";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fail = (message) => {
  console.error(`[verify_tablet_mass_catalog_04b] FAIL ${message}`);
  process.exit(1);
};

const products = TABLET_CONVENIENCE_PRODUCTS_04B;
if (products.length < 120) fail(`expected >=120 products, got ${products.length}`);

const ids = new Set();
const skus = new Set();
const barcodes = new Set();
let publicCodes = 0;
for (const product of products) {
  if (!product.id || !product.sku || !product.name || !product.category) fail(`missing required fields: ${JSON.stringify(product)}`);
  if (/demo/i.test(product.name)) fail(`demo copy in product name: ${product.name}`);
  if (!Number.isInteger(product.priceCents) || product.priceCents <= 0) fail(`invalid price for ${product.name}`);
  if (!Number.isInteger(product.costCents) || product.costCents < 0) fail(`invalid cost for ${product.name}`);
  if (!Number.isInteger(product.stockOnHand) || product.stockOnHand < 0) fail(`invalid stock for ${product.name}`);
  if (!/^\d{8}$|^\d{12,14}$/.test(String(product.barcode))) fail(`barcode must be GTIN-like numeric for ${product.name}: ${product.barcode}`);
  if (ids.has(product.id)) fail(`duplicate id ${product.id}`);
  if (skus.has(product.sku)) fail(`duplicate sku ${product.sku}`);
  if (barcodes.has(product.barcode)) fail(`duplicate barcode ${product.barcode}`);
  ids.add(product.id);
  skus.add(product.sku);
  barcodes.add(product.barcode);
  if (product.barcodeSource === "public") publicCodes += 1;
}
if (publicCodes < 10) fail(`expected at least 10 public barcode references, got ${publicCodes}`);

const packshots = readFileSync(path.join(appRoot, "components", "pos", "pos-packshots.ts"), "utf8");
if (!packshots.includes("return null;")) fail("packshot resolver must stay disabled for no-image catalog");

const productList = readFileSync(path.join(appRoot, "components", "pos", "pos-product-list.tsx"), "utf8");
for (const token of ["pageSize = 8", "productBarcode", "Mostrando", "catalog-page-"]) {
  if (!productList.includes(token)) fail(`missing UI token ${token}`);
}

console.log(JSON.stringify({ ok: true, products: products.length, publicBarcodeReferences: publicCodes, internalOperationalCodes: products.length - publicCodes }, null, 2));

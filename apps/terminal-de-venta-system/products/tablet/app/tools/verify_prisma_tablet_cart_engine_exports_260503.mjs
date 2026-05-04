#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const enginePath = path.join(root, "src", "lib", "pos", "cart-engine.ts");
const viewModelPath = path.join(root, "src", "lib", "pos", "cart-view-model.ts");
const paymentViewModelPath = path.join(root, "src", "lib", "pos", "payment-view-model.ts");
const corpusPath = path.join(root, "docs", "qa", "prisma-tablet-cart-engine-typecheck-regression-260503.jsonl");

let failed = false;
function ok(message) { console.log(`OK ${message}`); }
function fail(message) { console.error(`FAIL ${message}`); failed = true; }
function read(file) { return fs.readFileSync(file, "utf8"); }

const engine = read(enginePath);
const viewModel = read(viewModelPath);
const payment = read(paymentViewModelPath);
const requiredExports = [
  "CART_LIMITS",
  "sanitizeCart",
  "sanitizeCartLine",
  "addProductToCart",
  "incrementCartLine",
  "decrementCartLine",
  "removeCartLine",
  "clearCart",
  "calculateCartTotalCents",
  "calculateCartTotalQty",
  "getCartLineStockSignal",
  "validateCartForCheckout",
  "serializeCart",
  "hydrateCart",
  "buildCheckoutPayload"
];
for (const symbol of requiredExports) {
  const pattern = symbol === "CART_LIMITS" ? `export const ${symbol}` : `export function ${symbol}`;
  engine.includes(pattern) ? ok(`cart-engine exports ${symbol}`) : fail(`cart-engine missing ${symbol}`);
}

for (const symbol of ["calculateCartTotalCents", "calculateCartTotalQty", "getCartLineStockSignal", "validateCartForCheckout"]) {
  viewModel.includes(symbol) ? ok(`cart-view-model consumes ${symbol}`) : fail(`cart-view-model missing ${symbol}`);
}

payment.includes("validateCartForCheckout") ? ok("payment-view-model still consumes validateCartForCheckout") : fail("payment-view-model missing validateCartForCheckout");
engine.includes('reason: "Listo para cobrar."') ? ok("ready checkout keeps reason string") : fail("ready checkout reason missing");
engine.includes('tone: "warn"') && engine.includes('tone: "danger"') && engine.includes('tone: "ok"') ? ok("stock tones are explicit") : fail("stock tones incomplete");

if (fs.existsSync(corpusPath)) {
  const lines = read(corpusPath).trim().split(/\r?\n/).filter(Boolean);
  let parsed = 0;
  for (const line of lines) {
    const item = JSON.parse(line);
    if (!item.caseId || !item.expect) fail("corpus row missing caseId/expect");
    parsed += 1;
  }
  ok(`regression corpus parsed ${parsed} vectors`);
} else {
  fail(`missing corpus ${corpusPath}`);
}

if (failed) process.exit(1);
ok("PRISMA_TABLET_CART_ENGINE_EXPORTS_TYPECHECK_260503 verified export contract");

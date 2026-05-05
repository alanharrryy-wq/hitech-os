#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const fixturePath = path.join(root, "tools", "fixtures", "tablet_cart_03d_engine_cases.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
const engineSource = fs.readFileSync(path.join(root, "src", "lib", "pos", "cart-engine.ts"), "utf8");
let failed = false;
function ok(message) { console.log(`OK ${message}`); }
function fail(message) { console.error(`FAIL ${message}`); failed = true; }

function normalizeCartQuantity(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 1;
  return Math.max(1, Math.min(999, Math.trunc(parsed)));
}
function sanitizeCartLine(line) {
  if (!line?.product?.id) return null;
  if (!line.product.isActive) return null;
  const qty = normalizeCartQuantity(line.qty);
  return { ...line, qty };
}
function sanitizeCart(lines) {
  const byProduct = new Map();
  for (const raw of lines) {
    const line = sanitizeCartLine(raw);
    if (!line) continue;
    const current = byProduct.get(line.product.id);
    if (!current) { byProduct.set(line.product.id, line); continue; }
    byProduct.set(line.product.id, { ...current, qty: normalizeCartQuantity(current.qty + line.qty) });
  }
  return [...byProduct.values()].slice(0, 120);
}
function addProductToCart(lines, product) {
  if (!product?.id) return { lines, changed: false };
  if (!product.isActive) return { lines, changed: false };
  const current = sanitizeCart(lines);
  const existing = current.find((line) => line.product.id === product.id);
  if (existing) return incrementCartLine(current, product.id);
  if (current.length >= 120) return { lines: current, changed: false };
  return { lines: [...current, { product, qty: 1 }], changed: true };
}
function incrementCartLine(lines, productId) {
  const current = sanitizeCart(lines);
  let changed = false;
  const next = current.map((line) => {
    if (line.product.id !== productId) return line;
    const qty = normalizeCartQuantity(line.qty + 1);
    changed = qty !== line.qty;
    return { ...line, qty };
  });
  return { lines: next, changed };
}
function decrementCartLine(lines, productId) {
  const current = sanitizeCart(lines);
  let changed = false;
  const next = current.flatMap((line) => {
    if (line.product.id !== productId) return [line];
    changed = true;
    if (line.qty <= 1) return [];
    return [{ ...line, qty: line.qty - 1 }];
  });
  return { lines: next, changed };
}
function removeCartLine(lines, productId) {
  const current = sanitizeCart(lines);
  const next = current.filter((line) => line.product.id !== productId);
  return { lines: next, changed: next.length !== current.length };
}
function clearCart(lines) { return { lines: [], changed: lines.length > 0 }; }
function calculateCartTotalCents(lines) { return sanitizeCart(lines).reduce((sum, line) => sum + Math.max(0, line.product.priceCents) * line.qty, 0); }
function calculateCartTotalQty(lines) { return sanitizeCart(lines).reduce((sum, line) => sum + line.qty, 0); }
function getCartLineStockSignal(line) {
  if (line.product.stockOnHand <= 0) return { blocksCheckout: true };
  if (line.qty > line.product.stockOnHand) return { blocksCheckout: true };
  return { blocksCheckout: false };
}
function validateCartForCheckout(lines) {
  const current = sanitizeCart(lines);
  if (!current.length) return { ready: false, totalCents: 0, totalQty: 0, blockingProductIds: [] };
  const blocking = current.filter((line) => getCartLineStockSignal(line).blocksCheckout).map((line) => line.product.id);
  const totalCents = calculateCartTotalCents(current);
  const totalQty = calculateCartTotalQty(current);
  if (blocking.length) return { ready: false, totalCents, totalQty, blockingProductIds: blocking };
  if (totalCents <= 0) return { ready: false, totalCents, totalQty, blockingProductIds: [] };
  return { ready: true, totalCents, totalQty, blockingProductIds: [] };
}

const requiredSourceSignals = [
  "CART_LIMITS",
  "sanitizeCart",
  "validateCartForCheckout",
  "getCartLineStockSignal",
  "buildCheckoutPayload",
  "hydrateCart",
  "serializeCart"
];
for (const signal of requiredSourceSignals) {
  engineSource.includes(signal) ? ok(`source contains ${signal}`) : fail(`source missing ${signal}`);
}

for (const scenario of fixture.cases) {
  let result;
  if (scenario.command === "add") result = addProductToCart(scenario.initial, scenario.product);
  if (scenario.command === "sanitize") result = { lines: sanitizeCart(scenario.initial) };
  if (scenario.command === "decrement") result = decrementCartLine(scenario.initial, scenario.productId);
  if (scenario.command === "remove") result = removeCartLine(scenario.initial, scenario.productId);
  if (scenario.command === "clear") result = clearCart(scenario.initial);
  if (scenario.command === "readiness") result = validateCartForCheckout(scenario.initial);
  if (!result) { fail(`scenario ${scenario.name} has unknown command ${scenario.command}`); continue; }
  const expected = scenario.expected || {};
  if (Object.hasOwn(expected, "changed") && result.changed !== expected.changed) fail(`${scenario.name}: changed expected ${expected.changed} got ${result.changed}`);
  if (Object.hasOwn(expected, "ready") && result.ready !== expected.ready) fail(`${scenario.name}: ready expected ${expected.ready} got ${result.ready}`);
  if (Object.hasOwn(expected, "totalCents") && result.totalCents !== expected.totalCents) fail(`${scenario.name}: totalCents expected ${expected.totalCents} got ${result.totalCents}`);
  if (Object.hasOwn(expected, "totalQty") && result.totalQty !== expected.totalQty) fail(`${scenario.name}: totalQty expected ${expected.totalQty} got ${result.totalQty}`);
  if (Object.hasOwn(expected, "qty")) {
    const qty = result.lines ? calculateCartTotalQty(result.lines) : 0;
    if (qty !== expected.qty) fail(`${scenario.name}: qty expected ${expected.qty} got ${qty}`);
  }
  if (Array.isArray(expected.blocking)) {
    const blocking = result.blockingProductIds || [];
    for (const id of expected.blocking) if (!blocking.includes(id)) fail(`${scenario.name}: missing blocking ${id}`);
  }
  if (Array.isArray(expected.remaining)) {
    const remaining = (result.lines || []).map((line) => line.product.id);
    for (const id of expected.remaining) if (!remaining.includes(id)) fail(`${scenario.name}: missing remaining ${id}`);
  }
  ok(`cart scenario ${scenario.name}`);
}

if (failed) process.exit(1);
ok(`cart engine scenario runner passed ${fixture.cases.length} cases`);

#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "src/lib/pos/cart-engine.ts",
  "src/lib/pos/cart-view-model.ts",
  "src/lib/pos/cart-state.ts",
  "components/pos/pos-screen.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "docs/ux/PRISMA_TABLET_SELL_CART_03D_FOUNDATION.md"
];
let failed = false;
function ok(msg){ console.log(`OK ${msg}`); }
function fail(msg){ console.error(`FAIL ${msg}`); failed = true; }
function read(rel){ const file=path.join(root,rel); if(!fs.existsSync(file)){ fail(`missing ${rel}`); return "";} return fs.readFileSync(file,"utf8"); }
for (const rel of required) { read(rel); ok(`exists ${rel}`); }
const engine = read("src/lib/pos/cart-engine.ts");
[
  "addProductToCart",
  "incrementCartLine",
  "decrementCartLine",
  "removeCartLine",
  "clearCart",
  "validateCartForCheckout",
  "buildCheckoutPayload",
  "hydrateCart",
  "serializeCart"
].forEach((needle)=> engine.includes(needle) ? ok(`cart engine ${needle}`) : fail(`cart engine missing ${needle}`));
const screen = read("components/pos/pos-screen.tsx");
[
  "addProductToCart",
  "incrementCartLine",
  "decrementCartLine",
  "removeCartLine",
  "clearCart"
].forEach((needle)=> screen.includes(needle) ? ok(`pos screen uses ${needle}`) : fail(`pos screen missing ${needle}`));
const ticket = read("components/pos/pos-ticket-panel.tsx");
[
  "buildCartPanelViewModel",
  "view.checkoutReady",
  "title={view.checkoutReason}"
].forEach((needle)=> ticket.includes(needle) ? ok(`ticket panel uses ${needle}`) : fail(`ticket panel missing ${needle}`));
if (engine.includes("Math.random()") || engine.includes("Date.now()")) fail("cart engine should be deterministic"); else ok("cart engine deterministic");
if (failed) process.exit(1);
ok("PRISMA_TABLET_SELL_CART_03D_FOUNDATION verify complete");

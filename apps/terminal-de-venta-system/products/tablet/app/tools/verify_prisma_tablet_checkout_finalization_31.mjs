#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
function read(rel) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) throw new Error(`Missing ${rel}`);
  return fs.readFileSync(full, 'utf8');
}
function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}
const paymentFlow = read('products/tablet/app/src/lib/pos/payment-flow.ts');
assert(paymentFlow.includes('const checkout = buildCheckoutPayload({'), 'payment-flow must build checkout object explicitly');
assert(paymentFlow.includes('items: checkout.items'), 'payment-flow must send checkout.items array to API');
assert(!paymentFlow.includes('const items = buildCheckoutPayload(input.lines)'), 'payment-flow still sends nested checkout payload as items');
assert(paymentFlow.includes('if (!checkout.ready) throw new Error(checkout.reason);'), 'payment-flow must fail before API on invalid cart');

const cartState = read('products/tablet/app/src/lib/pos/cart-state.ts');
assert(cartState.includes('POS_API_INVALID_RESPONSE'), 'requestJson must detect invalid JSON responses');
assert(cartState.includes('POS_API_HTTP_ERROR'), 'requestJson must expose HTTP errors');

const panel = read('products/tablet/app/components/pos/pos-payment-panel.tsx');
assert(panel.includes('data-prisma-checkout-finalize="31"'), 'finalize button marker missing');
assert(panel.includes('role="alert"'), 'payment error must be announced as alert');
assert(panel.includes('paymentBusyNote'), 'payment busy note missing');

const css = read('products/tablet/app/components/pos/pos.module.css');
assert(css.includes('PRISMA Tablet 31 - checkout finalization fix'), 'CSS marker missing');
assert(css.includes('.paymentError'), 'paymentError CSS missing');
assert(css.includes('.paymentBusyNote'), 'paymentBusyNote CSS missing');

console.log('OK PRISMA Tablet checkout finalization fix 31 verified');

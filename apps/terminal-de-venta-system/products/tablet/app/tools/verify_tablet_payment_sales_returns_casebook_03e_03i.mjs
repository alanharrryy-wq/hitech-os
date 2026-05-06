import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const casebook = JSON.parse(fs.readFileSync(path.join(root, "tools/fixtures/tablet_payment_sales_returns_casebook_03e_03i.json"), "utf8"));
function assert(ok, msg){ if(!ok){ console.error(`[FAIL] ${msg}`); process.exitCode=1; } else console.log(`[OK] ${msg}`); }
const ids = new Set();
const counts = new Map();
for (const c of casebook.cases){ ids.add(c.id); counts.set(c.group, (counts.get(c.group) ?? 0) + 1); }
assert(ids.size === casebook.cases.length, "casebook ids are unique");
for (const group of ["payment","return","offline-policy","route"]) assert((counts.get(group) ?? 0) > 0, `casebook has ${group} cases`);
function cashCanClose(c){ return c.method !== "cash" || c.cashReceivedCents >= c.totalCents; }
for (const c of casebook.cases.filter(c => c.group === "payment")){
  assert(cashCanClose(c) === c.expectedCanClose, `payment case ${c.id} expected close`);
  const change = c.method === "cash" ? Math.max(0, c.cashReceivedCents - c.totalCents) : 0;
  assert(change === c.expectedChangeCents, `payment case ${c.id} expected change`);
}
function returnCan(c){ return c.ticketStatus === "COMPLETED" && c.requestedQty > 0 && c.requestedQty <= Math.max(0, c.lineQty - c.alreadyReturnedQty); }
for (const c of casebook.cases.filter(c => c.group === "return")){
  assert(returnCan(c) === c.expectedCanReturn, `return case ${c.id} expected returnability`);
}
function offlineCan(c){ return c.hasLocalCatalog && c.hasOpenShift && !(c.connectionState !== "online" && c.cartTotalCents > c.maxOfflineSaleCents); }
for (const c of casebook.cases.filter(c => c.group === "offline-policy")){
  assert(offlineCan(c) === c.expectedCanComplete, `offline case ${c.id} expected completion`);
}
for (const c of casebook.cases.filter(c => c.group === "route")){
  const file = c.route === "/checkout" ? "app/checkout/page.tsx" : c.route === "/returns" ? "app/returns/page.tsx" : c.route === "/sales" ? "app/sales/page.tsx" : c.route === "/inventory" ? "app/inventory/page.tsx" : "app/existencias/page.tsx";
  const text = fs.readFileSync(path.join(root,file), "utf8");
  assert(text.includes(`redirect("${c.expectedRedirect}")`), `route case ${c.id} redirects`);
}
if(process.exitCode) process.exit(process.exitCode);
console.log(`[OK] casebook verified: ${casebook.cases.length} cases`);

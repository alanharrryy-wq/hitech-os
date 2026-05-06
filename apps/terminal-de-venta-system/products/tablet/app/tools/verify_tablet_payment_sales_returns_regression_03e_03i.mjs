import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const fixtures = JSON.parse(fs.readFileSync(path.join(root, "tools/fixtures/tablet_payment_sales_returns_regression_cases_03e_03i.json"), "utf8"));
function assert(ok, msg){ if(!ok){ console.error(`[FAIL] ${msg}`); process.exitCode = 1; } else console.log(`[OK] ${msg}`); }
function reviewPayment(c){
  const total = Math.max(0, c.totalCents);
  if(c.method === "cash"){
    const received = Math.max(0, c.cashReceivedCents ?? 0);
    const change = Math.max(0, received - total);
    return { canClose: received >= total, changeCents: change };
  }
  return { canClose: true, changeCents: 0 };
}
for (const c of fixtures.paymentCases){
  const got = reviewPayment(c);
  assert(got.canClose === c.canClose, `payment ${c.id} canClose`);
  assert(got.changeCents === c.changeCents, `payment ${c.id} change`);
}
function evaluateReturn(c){
  const available = Math.max(0, c.lineQty - c.returnedAlready);
  const qty = Math.max(0, c.requested);
  const canReturn = c.ticketStatus === "COMPLETED" && qty > 0 && qty <= available;
  const amountCents = Math.min(qty, available) * 1200;
  return { canReturn, amountCents };
}
for (const c of fixtures.returnCases){
  const got = evaluateReturn(c);
  assert(got.canReturn === c.canReturn, `return ${c.id} canReturn`);
  assert(got.amountCents === c.amountCents, `return ${c.id} amount`);
}
function offline(c){
  const blockers = [];
  if(!c.hasLocalCatalog) blockers.push("catalog");
  if(!c.hasOpenShift) blockers.push("shift");
  if(c.connectionState !== "online" && c.cartTotalCents > (c.maxOfflineSaleCents ?? 100000)) blockers.push("limit");
  return blockers.length === 0;
}
for (const c of fixtures.offlinePolicyCases){
  assert(offline(c) === c.canComplete, `offline ${c.id}`);
}
if(process.exitCode) process.exit(process.exitCode);
console.log("[OK] regression matrix verified");


import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "components/pos/pos-screen.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "components/pos/pos-payment-panel.tsx",
  "src/lib/pos/payment-flow.ts",
  "src/lib/pos/payment-session.ts",
  "src/lib/pos/cart-engine.ts",
  "src/server/pos-api/validators.ts",
  "src/server/pos-engine/repository.prisma.ts",
  "src/server/pos-engine/event-factory.ts",
  "prisma/schema.prisma",
  "tools/fixtures/tablet_sell_checkout_payment_04a_cases.json"
];

const failures = [];
function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) {
    failures.push(`missing ${rel}`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
}
function must(rel, needle) {
  const text = read(rel);
  if (!text.includes(needle)) failures.push(`${rel} missing ${needle}`);
}
function mustNot(rel, needle) {
  const text = read(rel);
  if (text.includes(needle)) failures.push(`${rel} should not include ${needle}`);
}

for (const rel of required) read(rel);
mustNot("components/pos/pos-ticket-panel.tsx", "href={lines.length ? \"/checkout\"");
must("components/pos/pos-ticket-panel.tsx", "onCheckout");
must("src/lib/pos/payment-state.ts", "Efectivo");
must("src/lib/pos/payment-state.ts", "Tarjeta");
must("src/lib/pos/payment-state.ts", "Transferencia");
must("src/lib/pos/payment-flow.ts", "paymentMethod");
must("src/lib/pos/payment-flow.ts", "cashReceivedCents");
must("src/lib/pos/payment-flow.ts", "changeCents");
must("src/lib/pos/payment-session.ts", "resolvePaymentSessionContext");
must("src/server/pos-api/validators.ts", "INVALID_PAYMENT_METHOD");
must("src/server/pos-engine/repository.prisma.ts", "paymentMethod");
must("src/server/pos-engine/event-factory.ts", "paymentMethod");
must("prisma/schema.prisma", "paymentMethod String");
must("prisma/schema.prisma", "cashReceivedCents Int?");
must("prisma/schema.prisma", "changeCents");

const fixture = JSON.parse(read("tools/fixtures/tablet_sell_checkout_payment_04a_cases.json"));
if (fixture.caseCount < 300 || fixture.cases.length < 300) failures.push("fixture should contain at least 300 payment cases");

if (failures.length) {
  console.error("PRISMA 04A verify failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log("OK PRISMA_TABLET_SELL_CHECKOUT_PAYMENT_FLOW_04A verified");

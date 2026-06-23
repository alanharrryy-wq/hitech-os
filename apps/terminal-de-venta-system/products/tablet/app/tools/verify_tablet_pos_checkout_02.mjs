import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const requiredFiles = [
  "app/pos/page.tsx",
  "app/checkout/page.tsx",
  "components/pos/pos-screen.tsx",
  "components/pos/pos-product-search.tsx",
  "components/pos/pos-product-list.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "components/pos/pos-sale-success.tsx",
  "components/pos/pos-error-banner.tsx",
  "components/pos/pos-shortcuts.tsx",
  "components/pos/pos-payment-panel.tsx",
  "components/pos/pos.module.css",
  "src/lib/pos/cart-state.ts",
  "src/lib/pos/payment-flow.ts",
  "src/lib/pos/payment-state.ts",
  "src/lib/pos/pos-visible-errors.ts",
  "docs/qa/pos-checkout-02/acceptance.md",
  "docs/qa/pos-checkout-02/smoke-tests.md"
];

const failures = [];
const read = (rel) => readFileSync(resolve(root, rel), "utf8");

for (const rel of requiredFiles) {
  if (!existsSync(resolve(root, rel))) failures.push(`Falta ${rel}`);
}

if (!failures.length) {
  const posPage = read("app/pos/page.tsx");
  const checkoutPage = read("app/checkout/page.tsx");
  const posScreen = read("components/pos/pos-screen.tsx");
  const posTicketPanel = read("components/pos/pos-ticket-panel.tsx");
  const posPaymentPanel = read("components/pos/pos-payment-panel.tsx");
  const paymentFlow = read("src/lib/pos/payment-flow.ts");
  const pkg = JSON.parse(read("package.json"));

  if (!posPage.includes("PosScreen")) failures.push("/pos no renderiza PosScreen");
  if (!checkoutPage.includes("PosScreen")) failures.push("/checkout no usa el flujo unificado PosScreen");
  if (posPage.includes("TouchPosApp")) failures.push("/pos todavía depende de TouchPosApp");
  if (checkoutPage.includes("TouchPosApp")) failures.push("/checkout todavía depende de TouchPosApp");
  if (!/["'`]Cobrar["'`]|COBRAR/.test(posTicketPanel)) failures.push("POS no tiene CTA Cobrar");
  if (!posTicketPanel.includes('data-prisma-zone="tablet-pos-cobrar-cta"')) failures.push("COBRAR no tiene marcador gobernado");
  if (!posPaymentPanel.includes('data-prisma-zone="tablet-checkout-root"')) failures.push("Checkout modal no tiene marcador de raíz");
  if (!posPaymentPanel.includes('data-prisma-zone="tablet-checkout-confirm-action"')) failures.push("Checkout no marca la acción final");
  if (!paymentFlow.includes('/api/pos/sales/complete')) failures.push("El flujo de pago no llama al endpoint de cierre de venta");
  if (!pkg.scripts?.["verify:pos-checkout-02"]) failures.push("package.json no contiene verify:pos-checkout-02");
}

if (failures.length) {
  console.error("PRISMA_TABLET_POS_CHECKOUT_02 FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_TABLET_POS_CHECKOUT_02 PASS");

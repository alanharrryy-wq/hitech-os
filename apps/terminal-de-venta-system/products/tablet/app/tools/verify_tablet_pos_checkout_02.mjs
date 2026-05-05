import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const requiredFiles = [
  "components/pos/pos-screen.tsx",
  "components/pos/pos-product-search.tsx",
  "components/pos/pos-product-list.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "components/pos/pos-sale-success.tsx",
  "components/pos/pos-error-banner.tsx",
  "components/pos/pos-shortcuts.tsx",
  "components/pos/pos-payment-panel.tsx",
  "components/pos/pos.module.css",
  "components/checkout/checkout-screen.tsx",
  "components/checkout/checkout-payment-methods.tsx",
  "components/checkout/checkout-cash-calculator.tsx",
  "components/checkout/checkout-summary.tsx",
  "components/checkout/checkout.module.css",
  "src/lib/pos/cart-state.ts",
  "src/lib/pos/payment-state.ts",
  "src/lib/pos/pos-visible-errors.ts",
  "docs/qa/pos-checkout-02/acceptance.md",
  "docs/qa/pos-checkout-02/smoke-tests.md"
];

const failures = [];
for (const rel of requiredFiles) {
  if (!existsSync(resolve(root, rel))) failures.push(`Falta ${rel}`);
}

const posPage = readFileSync(resolve(root, "app/pos/page.tsx"), "utf8");
const checkoutPage = readFileSync(resolve(root, "app/checkout/page.tsx"), "utf8");
const posScreen = readFileSync(resolve(root, "components/pos/pos-screen.tsx"), "utf8");
const posTicketPanel = readFileSync(resolve(root, "components/pos/pos-ticket-panel.tsx"), "utf8");
const checkoutScreen = readFileSync(resolve(root, "components/checkout/checkout-screen.tsx"), "utf8");
const pkg = JSON.parse(readFileSync(resolve(root, "package.json"), "utf8"));

if (!posPage.includes("PosScreen")) failures.push("/pos no renderiza PosScreen");
if (!checkoutPage.includes("CheckoutScreen")) failures.push("/checkout no renderiza CheckoutScreen");
if (posPage.includes("TouchPosApp")) failures.push("/pos todavía depende de TouchPosApp");
if (checkoutPage.includes("TouchPosApp")) failures.push("/checkout todavía depende de TouchPosApp");
if (!(posScreen + posTicketPanel).includes("Ir a cobro")) failures.push("POS no tiene acción clara para ir a cobro");
if (!checkoutScreen.includes("Confirmar cobro")) failures.push("Checkout no tiene confirmación de cobro");
if (!checkoutScreen.includes("/api/pos/sales/complete")) failures.push("Checkout no llama al endpoint de cierre de venta");
if (!pkg.scripts?.["verify:pos-checkout-02"]) failures.push("package.json no contiene verify:pos-checkout-02");

if (failures.length) {
  console.error("PRISMA_TABLET_POS_CHECKOUT_02 FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_TABLET_POS_CHECKOUT_02 PASS");

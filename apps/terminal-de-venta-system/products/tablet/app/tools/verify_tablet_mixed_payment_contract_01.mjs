#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const checks = [];

function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) {
    checks.push({ name: `exists ${rel}`, ok: false });
    return "";
  }
  checks.push({ name: `exists ${rel}`, ok: true });
  return fs.readFileSync(file, "utf8");
}

function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), detail });
}

const types = read("src/server/pos-engine/types.ts");
const repository = read("src/server/pos-engine/repository.prisma.ts");
const eventFactory = read("src/server/pos-engine/event-factory.ts");
const route = read("app/api/pos/sales/complete/route.ts");
const detail = read("src/server/pos-api/sales-detail.prisma.ts");
const paymentFlow = read("src/lib/pos/payment-flow.ts");
const viewModel = read("src/lib/pos/payment-view-model.ts");
const panel = read("components/pos/pos-payment-panel.tsx");

check("server input accepts paymentTenders", types.includes("paymentTenders?: SalePaymentTenderInput[]"));
check("server result returns paymentTenders", types.includes("paymentTenders: SalePaymentTenderResult[]"));
check("repository persists real SalePaymentTender rows", repository.includes("tx.salePaymentTender.create"));
check("repository blocks incomplete payment", repository.includes("PAYMENT_INCOMPLETE"));
check("repository blocks non-cash overpayment", repository.includes("NON_CASH_OVERPAYMENT"));
check("outbox payload preserves tenders", eventFactory.includes("tenders: result.paymentTenders.map"));
check("ticket evidence preserves tenders", route.includes("tenders: sale.paymentTenders.map"));
check("ticket detail reads real tender rows", detail.includes("paymentTenders: true") && detail.includes("source: \"salePaymentTender\""));
check("client posts paymentTenders", paymentFlow.includes("paymentTenders: payloadTenders"));
check("client computes cash-only change", viewModel.includes("nonCashOverpayCents") && viewModel.includes("changeCents = nonCashOverpayCents > 0 ? 0"));
check("payment panel exposes reference inputs", panel.includes("Referencia") && panel.includes("onPaymentTenderChange"));
check("payment panel lets partial payment attempt open recovery dialog", panel.includes("handleConfirmClick") && panel.includes("canExplainIncompletePayment"));
check("payment panel renders insufficient payment alertdialog", panel.includes("role=\"alertdialog\"") && panel.includes("paymentPremiumInsufficientDialog"));
check("payment panel offers incomplete payment recovery actions", panel.includes("Agregar otro método") && panel.includes("Ajustar importe") && panel.includes("Cancelar cobro"));
check("payment copy tells operator how to complete balance", viewModel.includes("El pago todavía no cubre el total") && panel.includes("El pago todavía no cubre el total"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("PRISMA_TABLET_MIXED_PAYMENT_CONTRACT_01 failed");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}

console.log(`PRISMA_TABLET_MIXED_PAYMENT_CONTRACT_01 PASS ${checks.length} checks`);

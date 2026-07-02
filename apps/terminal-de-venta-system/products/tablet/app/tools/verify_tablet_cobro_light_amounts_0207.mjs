#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const appRoot = fs.existsSync(path.join(repoRoot, "components", "pos", "pos-cobro-surface.tsx"))
  ? repoRoot
  : path.join(repoRoot, "apps", "terminal-de-venta-system", "products", "tablet", "app");

const checks = [];

function read(rel) {
  const file = path.join(appRoot, rel);
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

const surface = read("components/pos/pos-cobro-surface.tsx");
const css = read("components/pos/pos-cobro-surface.module.css");
const tender = read("src/lib/pos/payment-tender.ts");

check("cobro surface uses draft tenders for live totals", surface.includes("const draftPaymentTenders = useMemo<PaymentTenderInput[]>") && surface.includes("manualMoneyDraftToCents(amountDrafts[tender.method]"));
check("confirm submits drafted tender amounts", surface.includes("onConfirm(draftPaymentTenders);"));
check("partial payment is recoverable, not silently finalized", surface.includes("canExplainIncompletePayment") && surface.includes("setShowInsufficientDialog(true)"));
check("cash/card/transfer inputs keep decimal keyboard contract", surface.includes('inputMode="decimal"') && surface.includes('pattern="[0-9]*[.,]?[0-9]{0,2}"'));
check("money parser accepts decimal draft sanitization", tender.includes("sanitizeMoneyDraft") && tender.includes("centsFromDecimalString") && tender.includes("lastDot") && tender.includes("lastComma"));
check("overlay uses a pure CSS-module local class", surface.includes("overlayClassName={styles.cobroOverlay}") && css.includes(".cobroOverlay"));
check("overlay avoids impure global-only selector", !css.includes(':global([data-prisma-zone="tablet-pos-cobro-modal"])'));
check("overlay stays in light premium range", css.includes("rgba(236, 244, 255, 0.88)") && css.includes("rgba(196, 216, 240, 0.84)"));
check("panel stays clear instead of dark themed", css.includes("rgba(249, 252, 255, 0.86)") && css.includes("rgba(239, 247, 255, 0.58)"));
check("ready final button is blue", css.includes('.confirmButton[data-payment-state="ready"]') && css.includes("var(--cobro-blue-deep)"));
check("insufficient final button is amber", css.includes('.confirmButton[data-payment-state="short"]') && css.includes("var(--cobro-amber)"));
check("idle/loading final button is muted", css.includes('.confirmButton[data-payment-state="idle"]') && css.includes('.confirmButton[data-payment-state="loading"]'));
check("no priority override token in cobro css", !css.includes("!important"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("PRISMA_TABLET_COBRO_LIGHT_AMOUNTS_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}

console.log(`PRISMA_TABLET_COBRO_LIGHT_AMOUNTS_0207 PASS ${checks.length} checks`);

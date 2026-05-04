"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import type { CartLine, CompletedSale, UiState } from "@/lib/pos/cart-state";
import { cartTotalCents, clearCartStorage, formatMoney, makeClientRequestId, readCartFromStorage, requestJson } from "@/lib/pos/cart-state";
import type { PaymentMethod } from "@/lib/pos/payment-state";
import { paymentMethodLabel } from "@/lib/pos/payment-state";
import { PosErrorBanner } from "@components/pos/pos-error-banner";
import { PosSaleSuccess } from "@components/pos/pos-sale-success";
import { CheckoutPaymentMethods } from "./checkout-payment-methods";
import { CheckoutCashCalculator } from "./checkout-cash-calculator";
import { CheckoutSummary } from "./checkout-summary";
import styles from "./checkout.module.css";

export function CheckoutScreen() {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash");
  const [receivedCents, setReceivedCents] = useState(0);
  const [state, setState] = useState<UiState>("idle");
  const [error, setError] = useState<unknown>(null);
  const [lastSale, setLastSale] = useState<CompletedSale | null>(null);
  const totalCents = useMemo(() => cartTotalCents(lines), [lines]);
  const cashIsShort = paymentMethod === "cash" && receivedCents > 0 && receivedCents < totalCents;

  useEffect(() => {
    setLines(readCartFromStorage());
  }, []);

  async function completeSale() {
    if (!lines.length) {
      setError("EMPTY_CART");
      return;
    }
    if (cashIsShort) {
      setError("El efectivo recibido no alcanza para cubrir el total.");
      return;
    }
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<{ sale: CompletedSale }>("/api/pos/sales/complete", {
        method: "POST",
        body: JSON.stringify({
          clientRequestId: makeClientRequestId(),
          paymentMethod,
          lines: lines.map((line) => ({ productId: line.product.id, qty: line.qty }))
        })
      });
      setLastSale(response.data.sale);
      setLines([]);
      clearCartStorage();
      setState("success");
    } catch (caught) {
      setError(caught);
      setState("error");
    }
  }

  return (
    <PrismaTabletShellUnified
      currentPath="/checkout"
      title="Cobro"
      subtitle="Confirma el pago, cierra el ticket y deja la venta registrada localmente."
      status={<TabletShellStatusPill tone={state === "error" ? "danger" : state === "success" ? "ok" : "neutral"}>{state === "loading" ? "Cerrando ticket" : state === "success" ? "Ticket cerrado" : "Listo para cobrar"}</TabletShellStatusPill>}
      visualSurface="tablet-checkout"
      visualPreset="POS_TOUCH_REFERENCE"
    >
      <div className={styles.checkoutGrid} data-prisma-vos-stage="00F_00I" data-prisma-vsurface="tablet-checkout" data-prisma-layer="surface">
        <CheckoutSummary lines={lines} />
        <section className={styles.paymentCard} aria-label="Cobro del ticket">
          <div className={styles.totalHero}>
            <span>Total a cobrar</span>
            <strong>{formatMoney(totalCents)}</strong>
            <small>{paymentMethodLabel(paymentMethod)}</small>
          </div>
          <CheckoutPaymentMethods value={paymentMethod} onChange={setPaymentMethod} />
          {paymentMethod === "cash" ? <CheckoutCashCalculator totalCents={totalCents} receivedCents={receivedCents} onReceivedCents={setReceivedCents} /> : null}
          <PosErrorBanner error={error} />
          <button className={styles.confirmButton} type="button" onClick={() => void completeSale()} disabled={!lines.length || state === "loading" || cashIsShort} data-prisma-component="CheckoutButton" aria-label="Confirmar cobro">
            <span className={styles.visuallyHidden}>Confirmar cobro</span>
            <span>{state === "loading" ? "Cerrando venta..." : "COBRAR"}</span>
            <PrismaIcon name="receipt" size={20} />
          </button>
          {!lines.length ? <a className={styles.backLink} href="/pos">Agregar productos para cobrar</a> : null}
        </section>
      </div>
      <PosSaleSuccess sale={lastSale} onNewSale={() => { setLastSale(null); setReceivedCents(0); }} />
    </PrismaTabletShellUnified>
  );
}

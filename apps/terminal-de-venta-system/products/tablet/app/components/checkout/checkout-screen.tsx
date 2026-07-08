"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import type { CartLine, CompletedSale, UiState } from "@/lib/pos/cart-state";
import { cartTotalCents, clearCartStorage, formatMoney, makeClientRequestId, readCartFromStorage, requestJson } from "@/lib/pos/cart-state";
import type { PaymentMethod } from "@/lib/pos/payment-state";
import { paymentMethodLabel } from "@/lib/pos/payment-state";
import { PosErrorBanner } from "@components/pos/pos-error-banner";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { PosSaleSuccess } from "@components/pos/pos-sale-success";
import { CheckoutPaymentMethods } from "./checkout-payment-methods";
import { CheckoutCashCalculator } from "./checkout-cash-calculator";
import { CheckoutSummary } from "./checkout-summary";
import styles from "./checkout.module.css";

const PAYMENT_INSUFFICIENT_COPY = "El pago todavía no cubre el total. Agrega otro método de pago, ajusta el importe o completa el saldo pendiente.";

export function CheckoutScreen({ runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT }: { runtimeSnapshot?: TabletRuntimeSnapshot }) {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash");
  const [receivedCents, setReceivedCents] = useState(0);
  const [state, setState] = useState<UiState>("idle");
  const [error, setError] = useState<unknown>(null);
  const [lastSale, setLastSale] = useState<CompletedSale | null>(null);
  const [showInsufficientDialog, setShowInsufficientDialog] = useState(false);
  const totalCents = useMemo(() => cartTotalCents(lines), [lines]);
  const cashIsShort = paymentMethod === "cash" && receivedCents > 0 && receivedCents < totalCents;
  const gate = useMemo(() => decideCanSellFromRuntimeSnapshot(runtimeSnapshot), [runtimeSnapshot]);

  useEffect(() => {
    setLines(readCartFromStorage());
  }, []);

  async function completeSale() {
    if (!lines.length) {
      setError("EMPTY_CART");
      return;
    }
    if (cashIsShort) {
      setError(PAYMENT_INSUFFICIENT_COPY);
      setShowInsufficientDialog(true);
      return;
    }
    if (!gate.canCheckout) {
      setError("Caja cerrada. Abre turno antes de cobrar; PRISMA Tablet no abre caja automáticamente.");
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
      runtimeSnapshot={runtimeSnapshot}
    >
      <div className={styles.checkoutGrid} data-prisma-vos-stage="00F_00I" data-prisma-vsurface="tablet-checkout" data-prisma-layer="surface"
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-screen"
        data-target="checkout-screen-panel-82"
        data-kind="panel"
        data-role="revenue-core"
      >
        <CheckoutSummary lines={lines} />
        <section className={styles.paymentCard} aria-label="Cobro del ticket"
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-screen"
          data-target="checkout-screen-cobro-del-ticket-84"
          data-kind="price"
          data-role="financial-control"
        >
          <div className={styles.totalHero}
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-screen"
            data-target="checkout-screen-price-85"
            data-kind="price"
            data-role="financial-control"
          >
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_screen" data-target="checkout-screen-span-1" data-kind="text" data-role="text">Total a cobrar</span>
            <strong
              data-surface="tablet"
              data-screen="checkout"
              data-zone="checkout"
              data-panel="checkout-screen"
              data-target="checkout-screen-element-87"
              data-kind="element"
              data-role="revenue-core"
            >{formatMoney(totalCents)}</strong>
            <small>{paymentMethodLabel(paymentMethod)}</small>
          </div>
          <CheckoutPaymentMethods value={paymentMethod} onChange={(value) => { setPaymentMethod(value); setShowInsufficientDialog(false); setError(null); }} />
          {paymentMethod === "cash" ? <CheckoutCashCalculator totalCents={totalCents} receivedCents={receivedCents} onReceivedCents={(value) => { setReceivedCents(value); setShowInsufficientDialog(false); }} /> : null}
          <PosErrorBanner error={error} />
          {!gate.canSell ? <PosErrorBanner error="Caja cerrada. Abre turno antes de cobrar." /> : null}
          <button className={styles.confirmButton} type="button" onClick={() =
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-screen"
            data-target="checkout-screen-button-94"
            data-kind="button"
            data-role="action"
          > void completeSale()} disabled={!lines.length || state === "loading" || !gate.canCheckout} data-prisma-component="CheckoutButton" aria-label="Confirmar cobro">
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_screen" data-target="checkout-screen-span-2" data-kind="text" data-role="text" className={styles.visuallyHidden}>Confirmar cobro</span>
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_screen" data-target="checkout-screen-span-3" data-kind="text" data-role="text">{state === "loading" ? "Cerrando venta..." : "COBRAR"}</span>
            <PrismaIcon name="receipt" size={20} />
          </button>
          {!lines.length ? <a className={styles.backLink} href={gate.actionHref}
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-screen"
            data-target="checkout-screen-button-99"
            data-kind="button"
            data-role="action"
          >{gate.canShowSellNavigation ? "Agregar productos para cobrar" : "Abrir turno para cobrar"}</a> : null}
        </section>
      </div>
      {showInsufficientDialog && cashIsShort ? (
        <section className={styles.insufficientOverlay} role="dialog" aria-modal="true" aria-labelledby="checkout-insufficient-title"
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-screen"
          data-target="checkout-screen-panel-103"
          data-kind="panel"
          data-role="revenue-core"
        >
          <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_screen" data-target="checkout-screen-div-4" data-kind="panel" data-role="container" className={styles.insufficientDialog}>
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_screen" data-target="checkout-screen-span-5" data-kind="text" data-role="text">Pago incompleto</span>
            <h2 id="checkout-insufficient-title"
              data-surface="tablet"
              data-screen="checkout"
              data-zone="checkout"
              data-panel="checkout-screen"
              data-target="checkout-screen-text-106"
              data-kind="text"
              data-role="copy"
            >Saldo pendiente: {formatMoney(Math.max(0, totalCents - receivedCents))}</h2>
            <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_screen" data-target="checkout-screen-p-6" data-kind="text" data-role="text">{PAYMENT_INSUFFICIENT_COPY}</p>
            <div className={styles.insufficientActions}
              data-surface="tablet"
              data-screen="checkout"
              data-zone="checkout"
              data-panel="checkout-screen"
              data-target="checkout-screen-button-108"
              data-kind="button"
              data-role="action"
            >
              <button type="button" onClick={() =
                data-surface="tablet"
                data-screen="checkout"
                data-zone="checkout"
                data-panel="checkout-screen"
                data-target="checkout-screen-button-109"
                data-kind="button"
                data-role="action"
              > { setPaymentMethod("card"); setShowInsufficientDialog(false); setError(null); }}>Agregar otro método</button>
              <button type="button" onClick={() =
                data-surface="tablet"
                data-screen="checkout"
                data-zone="checkout"
                data-panel="checkout-screen"
                data-target="checkout-screen-button-110"
                data-kind="button"
                data-role="action"
              > { setShowInsufficientDialog(false); setError(null); }}>Ajustar importe</button>
              <button type="button" onClick={() =
                data-surface="tablet"
                data-screen="checkout"
                data-zone="checkout"
                data-panel="checkout-screen"
                data-target="checkout-screen-button-111"
                data-kind="button"
                data-role="action"
              > { setPaymentMethod(paymentMethod === "cash" ? "card" : "cash"); setShowInsufficientDialog(false); setError(null); }}>Cambiar método</button>
              <a href="/pos"
                data-surface="tablet"
                data-screen="checkout"
                data-zone="checkout"
                data-panel="checkout-screen"
                data-target="checkout-screen-button-112"
                data-kind="button"
                data-role="action"
              >Volver al ticket</a>
              <button type="button" onClick={() =
                data-surface="tablet"
                data-screen="checkout"
                data-zone="checkout"
                data-panel="checkout-screen"
                data-target="checkout-screen-button-113"
                data-kind="button"
                data-role="action"
              > { setReceivedCents(0); setShowInsufficientDialog(false); setError(null); }}>Cancelar cobro</button>
            </div>
          </div>
        </section>
      ) : null}
      <PosSaleSuccess sale={lastSale} onNewSale={() => { setLastSale(null); setReceivedCents(0); }} />
    </PrismaTabletShellUnified>
  );
}

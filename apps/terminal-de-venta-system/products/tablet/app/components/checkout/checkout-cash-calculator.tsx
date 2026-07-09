"use client";

import { formatMoney } from "@/lib/pos/cart-state";
import styles from "./checkout.module.css";

export function CheckoutCashCalculator({ totalCents, receivedCents, onReceivedCents }: { totalCents: number; receivedCents: number; onReceivedCents: (value: number) => void }) {
  const changeCents = Math.max(0, receivedCents - totalCents);
  return (
    <section className={styles.cashBox} aria-label="Cálculo de efectivo"
      data-surface="tablet"
      data-screen="checkout"
      data-zone="checkout"
      data-panel="checkout-cash-calculator"
      data-target="checkout-cash-calculator-c-lculo-de-efectivo-9"
      data-kind="price"
      data-role="financial-control"
    >
      <label
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-cash-calculator"
        data-target="checkout-cash-calculator-price-10"
        data-kind="price"
        data-role="financial-control"
      >
        <span
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-cash-calculator"
          data-target="checkout-cash-calculator-price-11"
          data-kind="price"
          data-role="financial-control"
        >Recibido en efectivo</span>
        <input
          inputMode="decimal"
          type="number"
          min="0"
          step="0.01"
          value={receivedCents ? String(receivedCents / 100) : ""}
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-cash-calculator"
          data-target="checkout-cash-calculator-price-12"
          data-kind="price"
          data-role="financial-control"
            onChange={(event) => onReceivedCents(Math.round(Number(event.target.value || 0) * 100))}
            placeholder="0.00"
        />
      </label>
      <div
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-cash-calculator"
        data-target="checkout-cash-calculator-price-22"
        data-kind="price"
        data-role="financial-control"
      >
        <span
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-cash-calculator"
          data-target="checkout-cash-calculator-price-23"
          data-kind="price"
          data-role="financial-control"
        >Cambio</span>
        <strong
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-cash-calculator"
          data-target="checkout-cash-calculator-price-24"
          data-kind="price"
          data-role="financial-control"
        >{formatMoney(changeCents)}</strong>
      </div>
    </section>
  );
}

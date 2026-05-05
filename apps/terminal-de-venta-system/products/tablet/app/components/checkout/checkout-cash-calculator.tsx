"use client";

import { formatMoney } from "@/lib/pos/cart-state";
import styles from "./checkout.module.css";

export function CheckoutCashCalculator({ totalCents, receivedCents, onReceivedCents }: { totalCents: number; receivedCents: number; onReceivedCents: (value: number) => void }) {
  const changeCents = Math.max(0, receivedCents - totalCents);
  return (
    <section className={styles.cashBox} aria-label="Cálculo de efectivo">
      <label>
        <span>Recibido en efectivo</span>
        <input
          inputMode="decimal"
          type="number"
          min="0"
          step="0.01"
          value={receivedCents ? String(receivedCents / 100) : ""}
          onChange={(event) => onReceivedCents(Math.round(Number(event.target.value || 0) * 100))}
          placeholder="0.00"
        />
      </label>
      <div>
        <span>Cambio</span>
        <strong>{formatMoney(changeCents)}</strong>
      </div>
    </section>
  );
}

"use client";

import { formatMoney } from "@/lib/pos/cart-state";
import { suggestedCashTenderCents } from "@/lib/pos/payment-tender";
import styles from "./checkout.module.css";

export function CheckoutCashCalculator({
  targetCents,
  receivedCents,
  changeCents,
  onReceivedCents,
  disabled = false
}: {
  targetCents: number;
  receivedCents: number;
  changeCents: number;
  onReceivedCents: (value: number) => void;
  disabled?: boolean;
}) {
  const suggestions = suggestedCashTenderCents(Math.max(0, targetCents)).slice(0, 4);
  const calculatedChangeCents = Math.max(0, changeCents);

  return (
    <div className={styles.cashCapture}>
      <label className={styles.field} htmlFor="checkout-cash-amount">
        <span>Importe recibido</span>
        <span className={styles.moneyInput}>
          <i aria-hidden="true">$</i>
          <input
            id="checkout-cash-amount"
            inputMode="decimal"
            type="number"
            min="0"
            step="0.01"
            value={receivedCents ? String(receivedCents / 100) : ""}
            onChange={(event) => onReceivedCents(Math.max(0, Math.round(Number(event.target.value || 0) * 100)))}
            placeholder="0.00"
            disabled={disabled}
            aria-describedby="checkout-cash-help"
          />
        </span>
      </label>
      <div className={styles.quickCash} aria-label="Denominaciones rápidas">
        {suggestions.map((value) => (
          <button key={value} type="button" onClick={() => onReceivedCents(value)} disabled={disabled}>
            {value === targetCents ? "Exacto" : formatMoney(value)}
          </button>
        ))}
      </div>
      <small id="checkout-cash-help" className={styles.fieldHelp}>Selecciona una cantidad o captura el efectivo entregado.</small>
      <div className={styles.cashOutcome} data-tone={calculatedChangeCents > 0 ? "change" : "neutral"} aria-live="polite">
        <span>Cambio calculado</span>
        <strong>{formatMoney(calculatedChangeCents)}</strong>
      </div>
    </div>
  );
}

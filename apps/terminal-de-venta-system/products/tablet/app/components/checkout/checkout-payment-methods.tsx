"use client";

import type { PaymentMethod } from "@/lib/pos/payment-state";
import { PAYMENT_METHODS } from "@/lib/pos/payment-state";
import styles from "./checkout.module.css";

export function CheckoutPaymentMethods({ value, onChange }: { value: PaymentMethod; onChange: (value: PaymentMethod) => void }) {
  return (
    <section className={styles.paymentMethods} aria-label="Método de pago">
      {PAYMENT_METHODS.map((method) => (
        <button key={method.id} className={value === method.id ? styles.paymentActive : styles.paymentButton} type="button" onClick={() => onChange(method.id)}>
          <strong>{method.label}</strong>
          <span>{method.visibleConfirmation}</span>
        </button>
      ))}
    </section>
  );
}

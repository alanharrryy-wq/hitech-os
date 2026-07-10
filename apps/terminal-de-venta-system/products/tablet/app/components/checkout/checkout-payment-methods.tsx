"use client";

import type { PaymentMethod } from "@/lib/pos/payment-state";
import { PAYMENT_METHODS } from "@/lib/pos/payment-state";
import styles from "./checkout.module.css";

export function CheckoutPaymentMethods({ value, onChange }: { value: PaymentMethod; onChange: (value: PaymentMethod) => void }) {
  return (
    <section className={styles.paymentMethods} aria-label="Método de pago"
      data-surface="tablet"
      data-screen="checkout"
      data-zone="checkout"
      data-panel="checkout-payment-methods"
      data-target="checkout-payment-methods-m-todo-de-pago-9"
      data-kind="price"
      data-role="financial-control"
    >
      {PAYMENT_METHODS.map((method) => (
        <button key={method.id} className={value === method.id ? styles.paymentActive : styles.paymentButton} type="button"
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-payment-methods"
          data-target="checkout-payment-methods-price-11"
          data-kind="price"
          data-role="financial-control"
          onClick={() => onChange(method.id)}>
          <strong
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-payment-methods"
            data-target="checkout-payment-methods-price-12"
            data-kind="price"
            data-role="financial-control"
          >{method.label}</strong>
          <span
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-payment-methods"
            data-target="checkout-payment-methods-price-13"
            data-kind="price"
            data-role="financial-control"
          >{method.visibleConfirmation}</span>
        </button>
      ))}
    </section>
  );
}

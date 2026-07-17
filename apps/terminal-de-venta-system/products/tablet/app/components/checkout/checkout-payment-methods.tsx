"use client";

import { Banknote, CreditCard, Landmark, Split } from "lucide-react";
import type { PaymentMethod, PaymentMethodOrMixed } from "@/lib/pos/payment-state";
import styles from "./checkout.module.css";

const METHODS: Array<{ id: PaymentMethodOrMixed; label: string; icon: typeof Banknote }> = [
  { id: "cash", label: "Efectivo", icon: Banknote },
  { id: "card", label: "Tarjeta", icon: CreditCard },
  { id: "transfer", label: "Transferencia", icon: Landmark },
  { id: "mixed", label: "Mixto", icon: Split }
];

export function CheckoutPaymentMethods({
  value,
  onChange,
  disabled = false,
  compact = false
}: {
  value: PaymentMethodOrMixed;
  onChange: (value: PaymentMethodOrMixed) => void;
  disabled?: boolean;
  compact?: boolean;
}) {
  return (
    <div className={compact ? styles.paymentMethodsCompact : styles.paymentMethods} role="tablist" aria-label={compact ? "Método de la aportación" : "Método de pago"}>
      {METHODS.filter((method) => !compact || method.id !== "mixed").map((method) => {
        const Icon = method.icon;
        const active = value === method.id;
        return (
          <button
            key={method.id}
            className={active ? styles.paymentActive : styles.paymentButton}
            type="button"
            role="tab"
            aria-selected={active}
            disabled={disabled}
            onClick={() => onChange(method.id)}
          >
            <Icon aria-hidden="true" size={18} />
            <span>{method.label}</span>
          </button>
        );
      })}
    </div>
  );
}

export function paymentMethodForMixed(value: PaymentMethodOrMixed): PaymentMethod {
  return value === "mixed" ? "cash" : value;
}

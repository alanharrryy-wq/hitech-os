"use client";

import type { CartLine } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { isCheckoutBusy } from "@/lib/pos/payment-contract";
import type { PaymentMethod, PaymentTenderInput } from "@/lib/pos/payment-state";
import { paymentMethodDefinition } from "@/lib/pos/payment-state";
import { buildPaymentReviewViewModel } from "@/lib/pos/payment-view-model";
import { centsFromDecimalString, suggestedCashTenderCents } from "@/lib/pos/payment-tender";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import styles from "./pos.module.css";

function paymentIcon(method: PaymentMethod) {
  if (method === "transfer") return "->";
  if (method === "card") return "[]";
  return "$";
}

function tenderAmountValue(cents: number) {
  return cents > 0 ? String(cents / 100) : "";
}

function tenderDefinition(method: PaymentMethod) {
  return paymentMethodDefinition(method);
}

export function PosPaymentPanel({
  open,
  lines,
  state,
  error,
  paymentTenders,
  clientRequestId,
  onPaymentTenderChange,
  onClose,
  onConfirm
}: {
  open: boolean;
  lines: CartLine[];
  state: CheckoutState;
  error: unknown;
  paymentTenders: PaymentTenderInput[];
  clientRequestId: string;
  onPaymentTenderChange: (method: PaymentMethod, patch: Partial<Pick<PaymentTenderInput, "amountCents" | "reference">>) => void;
  onClose: () => void;
  onConfirm: () => void;
}) {
  if (!open) return null;
  const busy = isCheckoutBusy(state);
  const view = buildPaymentReviewViewModel({ lines, paymentTenders });
  const visibleError = error ? friendlyPosError(error) : view.blockReason;

  return (
    <section
      className={styles.paymentOverlay}
      aria-label="Ventana de método de pago"
      role="dialog"
      aria-modal="true"
      data-prisma-zone="tablet-checkout-root"
      data-prisma-role="operational-summary"
      data-prisma-priority="primary"
      data-prisma-state={busy ? "loading" : visibleError ? "error" : view.canConfirm ? "ready" : "disabled"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-checkout"
      data-prisma-payment-method={view.paymentMethod}
      data-prisma-payment-can-confirm={view.canConfirm ? "true" : "false"}
    >
      <div className={styles.paymentPanelCard}>
        <header className={styles.paymentHeader}>
          <div>
            <span>Paso final de venta</span>
            <h2>Pago del ticket</h2>
            <p>Combina efectivo, tarjeta y transferencia. El cambio solo se calcula desde efectivo.</p>
          </div>
          <button className={styles.paymentCloseButton} type="button" onClick={onClose} disabled={busy}>
            Cancelar cobro
          </button>
        </header>

        <div className={styles.paymentSummary} data-prisma-zone="tablet-checkout-summary" data-prisma-role="sale-total">
          <span>Total a cobrar</span>
          <strong>{formatMoney(view.totalCents)}</strong>
          <small>{view.totalQty} piezas · {view.totalLines} líneas</small>
        </div>

        <div className={styles.paymentTenderList} aria-label="Desglose de pago" data-prisma-zone="tablet-checkout-payment-breakdown">
          {paymentTenders.map((tender) => {
            const definition = tenderDefinition(tender.method);
            const active = tender.amountCents > 0;
            return (
              <div className={styles.paymentTenderRow} key={tender.method} data-active={active ? "true" : "false"}>
                <div>
                  <span aria-hidden="true">{paymentIcon(tender.method)}</span>
                  <strong>{definition.label}</strong>
                  <small>{definition.visibleConfirmation}</small>
                </div>
                <label className={styles.paymentTenderAmount}>
                  <span>Importe</span>
                  <input
                    inputMode="decimal"
                    placeholder="0.00"
                    aria-label={`Importe ${definition.label}`}
                    value={tenderAmountValue(tender.amountCents)}
                    disabled={busy}
                    onChange={(event) => onPaymentTenderChange(tender.method, { amountCents: centsFromDecimalString(event.target.value) })}
                  />
                </label>
                {tender.method !== "cash" ? (
                  <label className={styles.paymentTenderReference}>
                    <span>Referencia</span>
                    <input
                      placeholder="Autorización o folio"
                      aria-label={`Referencia ${definition.label}`}
                      value={tender.reference}
                      disabled={busy}
                      onChange={(event) => onPaymentTenderChange(tender.method, { reference: event.target.value })}
                    />
                  </label>
                ) : null}
              </div>
            );
          })}
        </div>

        <div className={styles.cashBox} data-prisma-zone="tablet-checkout-cash-helper" data-prisma-state={view.canConfirm ? "ready" : "pending"}>
          <span className={styles.cashInputLabel}>Sugerencias de efectivo</span>
          <div className={styles.cashSuggestions} aria-label="Billetes y monedas sugeridas">
            {suggestedCashTenderCents(Math.max(view.remainingCents, view.totalCents)).map((value) => (
              <button key={value} type="button" onClick={() => onPaymentTenderChange("cash", { amountCents: value })} disabled={busy}>
                {value === view.totalCents ? "Exacto" : formatMoney(value)}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.paymentTotalsGrid}>
          <span>Total <strong>{formatMoney(view.totalCents)}</strong></span>
          <span>Pagado <strong>{formatMoney(view.paidCents)}</strong></span>
          <span>Restante <strong>{formatMoney(view.remainingCents)}</strong></span>
          <span>Cambio <strong>{formatMoney(view.changeCents)}</strong></span>
        </div>

        <div className={view.canConfirm ? styles.paymentReviewReady : styles.paymentReview} data-prisma-state={view.canConfirm ? "success" : "pending"} data-prisma-motion={view.canConfirm ? "success-feedback" : "reduced-motion-safe"}>
          <strong>{view.tenderLabel}</strong>
          <span>{view.tenderDetail}</span>
          {clientRequestId ? <small>Folio técnico: {clientRequestId.slice(0, 8)}</small> : null}
        </div>

        {busy ? (
          <div className={styles.paymentBusyNote} role="status" aria-live="polite">
            <strong>Generando ticket local...</strong>
            <span>No cierres esta pantalla. PRISMA está cerrando venta, stock y evento.</span>
          </div>
        ) : null}
        {visibleError ? (
          <div className={styles.paymentError} role="alert" aria-live="assertive" data-prisma-zone="tablet-checkout-error-state" data-prisma-state="error" data-prisma-motion="error-feedback">
            <strong>No se cerró el ticket.</strong>
            <span>{visibleError}</span>
          </div>
        ) : null}

        <footer className={styles.paymentFooter}>
          <button className={styles.paymentCancelButton} type="button" onClick={onClose} disabled={busy}>
            Volver al ticket
          </button>
          <button className={styles.paymentOkButton} type="button" onClick={onConfirm} disabled={!view.canConfirm || busy} data-prisma-checkout-finalize="31" data-prisma-zone="tablet-checkout-confirm-action" data-prisma-role="primary-action" data-prisma-priority={view.canConfirm ? "primary" : "passive"} data-prisma-state={!view.canConfirm || busy ? "disabled" : "ready"} data-prisma-motion="press-feedback" data-prisma-qa={!view.canConfirm || busy ? "tablet-qa-disabled" : "tablet-qa-cobrar"}>
            {busy ? "Generando ticket..." : "OK, generar ticket"}
          </button>
        </footer>
      </div>
    </section>
  );
}

"use client";

import type { CartLine } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { isCheckoutBusy } from "@/lib/pos/payment-contract";
import type { PaymentMethod } from "@/lib/pos/payment-state";
import { PAYMENT_METHODS } from "@/lib/pos/payment-state";
import { buildPaymentReviewViewModel } from "@/lib/pos/payment-view-model";
import { centsFromDecimalString, suggestedCashTenderCents } from "@/lib/pos/payment-tender";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import styles from "./pos.module.css";

function paymentIcon(method: PaymentMethod) {
  if (method === "transfer") return "↗";
  if (method === "card") return "▣";
  return "$";
}

export function PosPaymentPanel({ open, lines, state, error, paymentMethod, cashReceivedCents, clientRequestId, onPaymentMethod, onCashReceivedCents, onClose, onConfirm }: {
  open: boolean; lines: CartLine[]; state: CheckoutState; error: unknown; paymentMethod: PaymentMethod; cashReceivedCents: number; clientRequestId: string; onPaymentMethod: (method: PaymentMethod) => void; onCashReceivedCents: (value: number) => void; onClose: () => void; onConfirm: () => void;
}) {
  if (!open) return null;
  const busy = isCheckoutBusy(state);
  const view = buildPaymentReviewViewModel({ lines, paymentMethod, cashReceivedCents });
  const canShowChange = paymentMethod === "cash" && cashReceivedCents > 0 && view.canConfirm;
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
    >
      <div className={styles.paymentPanelCard}>
        <header className={styles.paymentHeader}>
          <div><span>Paso final de venta</span><h2>Método de pago</h2><p>Elige cómo paga el cliente. Si es efectivo, calcula el cambio antes de generar ticket.</p></div>
          <button className={styles.paymentCloseButton} type="button" onClick={onClose} disabled={busy}>Cancelar cobro</button>
        </header>
        <div className={styles.paymentSummary} data-prisma-zone="tablet-checkout-summary" data-prisma-role="sale-total"><span>Total a cobrar</span><strong>{formatMoney(view.totalCents)}</strong><small>{view.totalQty} piezas · {view.totalLines} líneas</small></div>
        <div data-prisma-zone="tablet-pos-payment-methods">
          <div className={styles.paymentMethods} aria-label="Opciones de método de pago" data-prisma-zone="tablet-checkout-payment-methods" data-prisma-role="payment-selector">
            {PAYMENT_METHODS.map((method) => (
              <button key={method.id} type="button" data-active={method.id === paymentMethod ? "true" : "false"} onClick={() => onPaymentMethod(method.id)} disabled={busy} data-prisma-role="secondary-action" data-prisma-priority={method.id === paymentMethod ? "primary" : "secondary"} data-prisma-state={method.id === paymentMethod ? "selected" : busy ? "disabled" : "ready"} data-prisma-motion="press-feedback">
                <span aria-hidden="true">{paymentIcon(method.id)}</span><strong>{method.label}</strong><small>{method.visibleConfirmation}</small>
              </button>
            ))}
          </div>
        </div>
        {paymentMethod === "cash" ? (
          <div className={styles.cashBox} data-prisma-zone="tablet-checkout-cash-helper" data-prisma-state={view.canConfirm ? "ready" : "pending"}>
            <label className={styles.cashInputLabel}><span>¿Con cuánto paga?</span><input inputMode="decimal" placeholder="Ej. 200, 500, 1000" aria-label="Efectivo recibido" disabled={busy} onChange={(event) => onCashReceivedCents(centsFromDecimalString(event.target.value))} /></label>
            <div className={styles.cashSuggestions} aria-label="Billetes y monedas sugeridas">
              {suggestedCashTenderCents(view.totalCents).map((value) => (
                <button key={value} type="button" data-active={value === cashReceivedCents ? "true" : "false"} onClick={() => onCashReceivedCents(value)} disabled={busy}>{value === view.totalCents ? "Exacto" : formatMoney(value)}</button>
              ))}
            </div>
            <div className={styles.cashTenderLine}><span>Recibido</span><strong>{cashReceivedCents > 0 ? formatMoney(cashReceivedCents) : "Pendiente"}</strong></div>
          </div>
        ) : <div className={styles.paymentNonCashNotice}><strong>{view.paymentLabel}</strong><span>Confirma aprobación o comprobante antes de tocar OK.</span></div>}
        <div className={canShowChange ? styles.paymentReviewReady : styles.paymentReview} data-prisma-state={canShowChange ? "success" : "pending"} data-prisma-motion={canShowChange ? "success-feedback" : "reduced-motion-safe"}>
          <strong>{view.tenderLabel}</strong><span>{view.tenderDetail}</span>{paymentMethod === "cash" ? <b>Cambio a entregar: {view.changeCents > 0 ? formatMoney(view.changeCents) : formatMoney(0)}</b> : null}{clientRequestId ? <small>Folio técnico: {clientRequestId.slice(0, 8)}</small> : null}
        </div>
        {busy ? <div className={styles.paymentBusyNote} role="status" aria-live="polite"><strong>Generando ticket local...</strong><span>No cierres esta pantalla. PRISMA está cerrando venta, stock y evento.</span></div> : null}
        {visibleError ? <div className={styles.paymentError} role="alert" aria-live="assertive" data-prisma-zone="tablet-checkout-error-state" data-prisma-state="error" data-prisma-motion="error-feedback"><strong>No se cerró el ticket.</strong><span>{visibleError}</span></div> : null}
        <footer className={styles.paymentFooter}><button className={styles.paymentCancelButton} type="button" onClick={onClose} disabled={busy}>Volver al ticket</button><button className={styles.paymentOkButton} type="button" onClick={onConfirm} disabled={!view.canConfirm || busy} data-prisma-checkout-finalize="31" data-prisma-zone="tablet-checkout-confirm-action" data-prisma-role="primary-action" data-prisma-priority={view.canConfirm ? "primary" : "passive"} data-prisma-state={!view.canConfirm || busy ? "disabled" : "ready"} data-prisma-motion="press-feedback" data-prisma-qa={!view.canConfirm || busy ? "tablet-qa-disabled" : "tablet-qa-cobrar"}>{busy ? "Generando ticket..." : "OK, generar ticket"}</button></footer>
      </div>
    </section>
  );
}

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
    <section className={styles.paymentOverlay} aria-label="Ventana de método de pago" role="dialog" aria-modal="true">
      <div className={styles.paymentPanelCard}>
        <header className={styles.paymentHeader}>
          <div><span>Paso final de venta</span><h2>Método de pago</h2><p>Elige cómo paga el cliente. Si es efectivo, calcula el cambio antes de generar ticket.</p></div>
          <button className={styles.paymentCloseButton} type="button" onClick={onClose} disabled={busy}>Cancelar cobro</button>
        </header>
        <div className={styles.paymentSummary}><span>Total a cobrar</span><strong>{formatMoney(view.totalCents)}</strong><small>{view.totalQty} piezas · {view.totalLines} líneas</small></div>
        <div className={styles.paymentMethods} aria-label="Opciones de método de pago">
          {PAYMENT_METHODS.map((method) => (
            <button key={method.id} type="button" data-active={method.id === paymentMethod ? "true" : "false"} onClick={() => onPaymentMethod(method.id)} disabled={busy}>
              <span aria-hidden="true">{paymentIcon(method.id)}</span><strong>{method.label}</strong><small>{method.visibleConfirmation}</small>
            </button>
          ))}
        </div>
        {paymentMethod === "cash" ? (
          <div className={styles.cashBox}>
            <label className={styles.cashInputLabel}><span>¿Con cuánto paga?</span><input inputMode="decimal" placeholder="Ej. 200, 500, 1000" aria-label="Efectivo recibido" disabled={busy} onChange={(event) => onCashReceivedCents(centsFromDecimalString(event.target.value))} /></label>
            <div className={styles.cashSuggestions} aria-label="Billetes y monedas sugeridas">
              {suggestedCashTenderCents(view.totalCents).map((value) => (
                <button key={value} type="button" data-active={value === cashReceivedCents ? "true" : "false"} onClick={() => onCashReceivedCents(value)} disabled={busy}>{value === view.totalCents ? "Exacto" : formatMoney(value)}</button>
              ))}
            </div>
            <div className={styles.cashTenderLine}><span>Recibido</span><strong>{cashReceivedCents > 0 ? formatMoney(cashReceivedCents) : "Pendiente"}</strong></div>
          </div>
        ) : <div className={styles.paymentNonCashNotice}><strong>{view.paymentLabel}</strong><span>Confirma aprobación o comprobante antes de tocar OK.</span></div>}
        <div className={canShowChange ? styles.paymentReviewReady : styles.paymentReview}>
          <strong>{view.tenderLabel}</strong><span>{view.tenderDetail}</span>{paymentMethod === "cash" ? <b>Cambio a entregar: {view.changeCents > 0 ? formatMoney(view.changeCents) : formatMoney(0)}</b> : null}{clientRequestId ? <small>Folio tecnico: {clientRequestId.slice(0, 8)}</small> : null}
        </div>
        {busy ? <div className={styles.paymentBusyNote} role="status" aria-live="polite"><strong>Generando ticket local...</strong><span>No cierres esta pantalla. PRISMA esta cerrando venta, stock y evento.</span></div> : null}
        {visibleError ? <div className={styles.paymentError} role="alert" aria-live="assertive"><strong>No se cerro el ticket.</strong><span>{visibleError}</span></div> : null}
        <footer className={styles.paymentFooter}><button className={styles.paymentCancelButton} type="button" onClick={onClose} disabled={busy}>Volver al ticket</button><button className={styles.paymentOkButton} type="button" onClick={onConfirm} disabled={!view.canConfirm || busy} data-prisma-checkout-finalize="31">{busy ? "Generando ticket..." : "OK, generar ticket"}</button></footer>
      </div>
    </section>
  );
}

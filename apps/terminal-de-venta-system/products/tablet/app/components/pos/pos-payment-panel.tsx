"use client";

import { cva } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";
import {
  AlertTriangle,
  ArrowLeft,
  Banknote,
  CheckCircle2,
  CreditCard,
  Landmark,
  Loader2,
  ReceiptText,
  ShieldCheck,
  Sparkles,
  WalletCards,
  X
} from "lucide-react";
import { motion } from "motion/react";
import type { CartLine } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { isCheckoutBusy } from "@/lib/pos/payment-contract";
import type { PaymentMethod, PaymentTenderInput } from "@/lib/pos/payment-state";
import { paymentMethodDefinition } from "@/lib/pos/payment-state";
import { buildPaymentReviewViewModel } from "@/lib/pos/payment-view-model";
import { centsFromDecimalString, suggestedCashTenderCents } from "@/lib/pos/payment-tender";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import { PrismaActionButton, PrismaCheckoutPanel, PrismaStateBanner } from "../../../../shared-ui/prisma/components";
import styles from "./pos.module.css";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(...inputs));
}

const checkoutAction = cva(styles.paymentPremiumAction, {
  variants: {
    intent: {
      primaryCheckout: styles.paymentPremiumActionPrimary,
      secondaryAction: styles.paymentPremiumActionSecondary,
      dangerSoft: styles.paymentPremiumActionDanger,
      ghostGlass: styles.paymentPremiumActionGhost
    }
  },
  defaultVariants: {
    intent: "secondaryAction"
  }
});

const tenderCard = cva(styles.paymentPremiumTenderRow, {
  variants: {
    active: {
      true: styles.paymentPremiumTenderActive,
      false: styles.paymentPremiumTenderIdle
    }
  },
  defaultVariants: {
    active: false
  }
});

function PaymentIcon({ method }: { method: PaymentMethod }) {
  if (method === "transfer") return <Landmark aria-hidden="true" size={18} strokeWidth={2.5} />;
  if (method === "card") return <CreditCard aria-hidden="true" size={18} strokeWidth={2.5} />;
  return <Banknote aria-hidden="true" size={18} strokeWidth={2.5} />;
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
    <motion.section
      className={styles.paymentPremiumOverlay}
      aria-label="Ventana de método de pago"
      role="dialog"
      aria-modal="true"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
      data-prisma-zone="tablet-checkout-root"
      data-prisma-role="operational-summary"
      data-prisma-priority="primary"
      data-prisma-state={busy ? "loading" : visibleError ? "error" : view.canConfirm ? "ready" : "disabled"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-checkout"
      data-prisma-payment-method={view.paymentMethod}
      data-prisma-payment-can-confirm={view.canConfirm ? "true" : "false"}
    >
      <span className={styles.paymentPremiumAtmosphere} aria-hidden="true" />
      <motion.div
        className={styles.paymentPremiumShell}
        initial={{ opacity: 0, y: 18, scale: 0.982 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
      >
        <PrismaCheckoutPanel
          surface="tablet"
          title={<span className={styles.paymentPremiumPanelTitle}>Cobro PRISMA</span>}
          className={styles.paymentPremiumPanel}
          data-prisma-layer="2-glass-payment-panel"
          data-prisma-recipe="tablet-cloudglass-light checkout-panel"
        >
          <header className={styles.paymentPremiumHeader}>
            <div className={styles.paymentPremiumTitleBlock}>
              <span><ShieldCheck aria-hidden="true" size={15} /> Paso final de venta</span>
              <h2>Método de pago</h2>
              <p>Combina efectivo, tarjeta y transferencia. El cambio se calcula sólo desde efectivo.</p>
            </div>
            <PrismaActionButton
              className={cn(checkoutAction({ intent: "ghostGlass" }), styles.paymentPremiumCloseButton)}
              type="button"
              onClick={onClose}
              disabled={busy}
              surface="tablet"
              tone="default"
            >
              <X aria-hidden="true" size={18} />
              Cancelar cobro
            </PrismaActionButton>
          </header>

          <motion.div
            className={styles.paymentPremiumHeroTotal}
            data-prisma-zone="tablet-checkout-summary"
            data-prisma-role="sale-total"
            data-prisma-layer="3-total-block"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22, delay: 0.04, ease: [0.22, 1, 0.36, 1] }}
          >
            <div>
              <span><ReceiptText aria-hidden="true" size={15} /> Total a cobrar</span>
              <strong>{formatMoney(view.totalCents)}</strong>
              <small>{view.totalQty} piezas · {view.totalLines} líneas</small>
            </div>
            <div className={styles.paymentPremiumStatusPill} data-state={view.canConfirm ? "ready" : "pending"}>
              {view.canConfirm ? <CheckCircle2 aria-hidden="true" size={18} /> : <WalletCards aria-hidden="true" size={18} />}
              {view.canConfirm ? "Listo para ticket" : "Completa el pago"}
            </div>
          </motion.div>

          <div className={styles.paymentPremiumBodyGrid}>
            <div className={styles.paymentPremiumTenderList} aria-label="Desglose de pago" data-prisma-zone="tablet-checkout-payment-breakdown" data-prisma-layer="3-payment-methods">
              {paymentTenders.map((tender, index) => {
                const definition = tenderDefinition(tender.method);
                const active = tender.amountCents > 0;
                return (
                  <motion.div
                    className={tenderCard({ active })}
                    key={tender.method}
                    data-active={active ? "true" : "false"}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.18, delay: 0.06 + index * 0.035, ease: [0.22, 1, 0.36, 1] }}
                  >
                    <div className={styles.paymentPremiumTenderMeta}>
                      <span aria-hidden="true"><PaymentIcon method={tender.method} /></span>
                      <strong>{definition.label}</strong>
                      <small>{definition.visibleConfirmation}</small>
                    </div>
                    <label className={styles.paymentPremiumTenderAmount}>
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
                      <label className={styles.paymentPremiumTenderReference}>
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
                  </motion.div>
                );
              })}
            </div>

            <div className={styles.paymentPremiumRightRail}>
              <div className={styles.paymentPremiumCashBox} data-prisma-zone="tablet-checkout-cash-helper" data-prisma-state={view.canConfirm ? "ready" : "pending"}>
                <span className={styles.paymentPremiumSectionLabel}><Sparkles aria-hidden="true" size={15} /> Sugerencias de efectivo</span>
                <div className={styles.paymentPremiumCashSuggestions} aria-label="Billetes y monedas sugeridas">
                  {suggestedCashTenderCents(Math.max(view.remainingCents, view.totalCents)).map((value) => (
                    <motion.button
                      key={value}
                      type="button"
                      onClick={() => onPaymentTenderChange("cash", { amountCents: value })}
                      disabled={busy}
                      whileTap={{ scale: 0.982 }}
                      transition={{ duration: 0.16, ease: [0.22, 1, 0.36, 1] }}
                    >
                      {value === view.totalCents ? "Exacto" : formatMoney(value)}
                    </motion.button>
                  ))}
                </div>
              </div>

              <motion.div
                className={styles.paymentPremiumTotalsGrid}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
              >
                <span>Total <strong>{formatMoney(view.totalCents)}</strong></span>
                <span>Pagado <strong>{formatMoney(view.paidCents)}</strong></span>
                <span>Restante <strong>{formatMoney(view.remainingCents)}</strong></span>
                <span>Cambio a entregar <strong>{formatMoney(view.changeCents)}</strong></span>
              </motion.div>

              <div className={view.canConfirm ? styles.paymentPremiumReviewReady : styles.paymentPremiumReview} data-prisma-state={view.canConfirm ? "success" : "pending"} data-prisma-motion={view.canConfirm ? "success-feedback" : "reduced-motion-safe"}>
                <strong>{view.tenderLabel}</strong>
                <span>{view.tenderDetail}</span>
                {clientRequestId ? <small>Folio técnico: {clientRequestId.slice(0, 8)}</small> : null}
              </div>
            </div>
          </div>

          {busy ? (
            <PrismaStateBanner className={styles.paymentPremiumBusyNote} role="status" aria-live="polite" surface="tablet" tone="info" title="Generando ticket local..." data-prisma-legacy-class="paymentBusyNote">
              <span>No cierres esta pantalla. PRISMA está cerrando venta, stock y evento.</span>
            </PrismaStateBanner>
          ) : null}
          {visibleError ? (
            <PrismaStateBanner className={styles.paymentPremiumError} role="alert" aria-live="assertive" surface="tablet" tone="danger" title="No se cerró el ticket." data-prisma-zone="tablet-checkout-error-state" data-prisma-state="error" data-prisma-motion="error-feedback">
              <span><AlertTriangle aria-hidden="true" size={16} /> {visibleError}</span>
            </PrismaStateBanner>
          ) : null}

          <footer className={styles.paymentPremiumFooter} data-prisma-layer="4-primary-checkout-cta">
            <PrismaActionButton className={checkoutAction({ intent: "secondaryAction" })} type="button" onClick={onClose} disabled={busy} surface="tablet" tone="default">
              <ArrowLeft aria-hidden="true" size={18} />
              Volver al ticket
            </PrismaActionButton>
            <motion.button
              className={checkoutAction({ intent: "primaryCheckout" })}
              type="button"
              onClick={onConfirm}
              disabled={!view.canConfirm || busy}
              whileTap={!view.canConfirm || busy ? undefined : { scale: 0.982 }}
              whileHover={!view.canConfirm || busy ? undefined : { y: -1, boxShadow: "0 26px 62px rgba(22, 91, 238, 0.34)" }}
              transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
              data-prisma-checkout-finalize="31"
              data-prisma-zone="tablet-checkout-confirm-action"
              data-prisma-role="primary-action"
              data-prisma-priority={view.canConfirm ? "primary" : "passive"}
              data-prisma-state={!view.canConfirm || busy ? "disabled" : "ready"}
              data-prisma-motion="press-feedback"
              data-prisma-qa={!view.canConfirm || busy ? "tablet-qa-disabled" : "tablet-qa-cobrar"}
            >
              {busy ? <Loader2 className={styles.paymentPremiumSpinner} aria-hidden="true" size={21} /> : <CheckCircle2 aria-hidden="true" size={22} />}
              <span>{busy ? "Generando ticket..." : "OK, generar ticket"}</span>
            </motion.button>
          </footer>
        </PrismaCheckoutPanel>
      </motion.div>
    </motion.section>
  );
}

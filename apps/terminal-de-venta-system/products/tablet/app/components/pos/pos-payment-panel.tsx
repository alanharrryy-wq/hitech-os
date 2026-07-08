"use client";

import { createPortal } from "react-dom";
import { useEffect, useRef, useState } from "react";
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
import { centsFromDecimalString, sanitizeMoneyDraft, suggestedCashTenderCents } from "@/lib/pos/payment-tender";
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

function decimalTenderValue(cents: number) {
  return (Math.max(0, cents) / 100).toFixed(2);
}

function manualMoneyDraftToCents(value: string) {
  return centsFromDecimalString(value);
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
  const busy = isCheckoutBusy(state);
  const view = buildPaymentReviewViewModel({ lines, paymentTenders });
  const visibleError = error ? friendlyPosError(error) : view.blockReason;
  const focusedTenderRef = useRef<PaymentMethod | null>(null);
  const [showInsufficientDialog, setShowInsufficientDialog] = useState(false);
  const dialogRef = useRef<HTMLElement | null>(null);
  const [amountDrafts, setAmountDrafts] = useState<Record<PaymentMethod, string>>({
    cash: decimalTenderValue(paymentTenders.find((tender) => tender.method === "cash")?.amountCents ?? 0),
    card: decimalTenderValue(paymentTenders.find((tender) => tender.method === "card")?.amountCents ?? 0),
    transfer: decimalTenderValue(paymentTenders.find((tender) => tender.method === "transfer")?.amountCents ?? 0)
  });
  const canExplainIncompletePayment = view.paidCents > 0 && view.paidCents < view.totalCents;
  const confirmDisabled = busy || (!view.canConfirm && !canExplainIncompletePayment);

  function updateTender(method: PaymentMethod, patch: Partial<Pick<PaymentTenderInput, "amountCents" | "reference">>) {
    setShowInsufficientDialog(false);
    onPaymentTenderChange(method, patch);
  }

  function focusTender(method: PaymentMethod) {
    focusedTenderRef.current = method;
  }

  function clearFocusedTender() {
    focusedTenderRef.current = null;
  }

  function updateTenderAmount(method: PaymentMethod, amountCents: number) {
    updateTender(method, { amountCents });
    setAmountDrafts((current) => ({ ...current, [method]: decimalTenderValue(amountCents) }));
  }

  function addRemainingTo(method: PaymentMethod) {
    const current = paymentTenders.find((tender) => tender.method === method)?.amountCents ?? 0;
    updateTenderAmount(method, current + view.remainingCents);
    focusTender(method);
  }

  function clearTenderAmounts() {
    for (const tender of paymentTenders) {
      onPaymentTenderChange(tender.method, { amountCents: 0 });
    }
    setShowInsufficientDialog(false);
  }

  function handleConfirmClick() {
    if (view.canConfirm) {
      onConfirm();
      return;
    }
    if (canExplainIncompletePayment) {
      setShowInsufficientDialog(true);
    }
  }

  useEffect(() => {
    setAmountDrafts((current) => {
      let changed = false;
      const next = { ...current };
      for (const tender of paymentTenders) {
        if (focusedTenderRef.current === tender.method) continue;
        const formatted = decimalTenderValue(tender.amountCents);
        if (manualMoneyDraftToCents(next[tender.method] ?? "") !== tender.amountCents || !next[tender.method]) {
          next[tender.method] = formatted;
          changed = true;
        }
      }
      return changed ? next : current;
    });
  }, [paymentTenders]);

  useEffect(() => {
    if (!open || typeof document === "undefined") return;

    const focusableSelector = 'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])';
    const previousOverflow = document.body.style.overflow;
    const previousOverscrollBehavior = document.body.style.overscrollBehavior;
    const previousTouchAction = document.body.style.touchAction;
    const previousPaymentModalState = document.body.dataset.prismaPaymentModalOpen;
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;

    document.body.style.overflow = "hidden";
    document.body.style.overscrollBehavior = "contain";
    document.body.style.touchAction = "none";
    document.body.dataset.prismaPaymentModalOpen = "true";

    const frame = window.requestAnimationFrame(() => {
      const firstControl = dialogRef.current?.querySelector<HTMLElement>(focusableSelector);
      (firstControl ?? dialogRef.current)?.focus();
    });

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !busy) {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== "Tab") return;

      const focusable = Array.from(dialogRef.current?.querySelectorAll<HTMLElement>(focusableSelector) ?? []).filter((node) => {
        return node.tabIndex !== -1 && !node.hasAttribute("disabled") && node.getClientRects().length > 0;
      });

      if (!focusable.length) {
        event.preventDefault();
        dialogRef.current?.focus();
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
        return;
      }

      if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.cancelAnimationFrame(frame);
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
      document.body.style.overscrollBehavior = previousOverscrollBehavior;
      document.body.style.touchAction = previousTouchAction;
      if (previousPaymentModalState === undefined) {
        delete document.body.dataset.prismaPaymentModalOpen;
      } else {
        document.body.dataset.prismaPaymentModalOpen = previousPaymentModalState;
      }
      previouslyFocused?.focus?.();
    };
  }, [busy, onClose, open]);

  if (!open) return null;
  if (typeof document === "undefined") return null;

  const paymentOverlay = (
    <motion.section
      ref={dialogRef}
      className={styles.paymentPremiumOverlay}
      aria-label="Cobro PRISMA"
      role="dialog"
      aria-modal="true"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
      data-prisma-panel="tablet.pos.payment-overlay"
      data-prisma-overlay-root="document-body"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-zone="tablet-checkout-root"
      data-prisma-role="operational-summary"
      data-prisma-priority="primary"
      data-prisma-state={busy ? "loading" : visibleError ? "error" : view.canConfirm ? "ready" : "disabled"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-checkout"
      data-prisma-payment-method={view.paymentMethod}
      data-prisma-payment-can-confirm={view.canConfirm ? "true" : "false"}
      data-prisma-fix="PRISMA_TABLET_POS_COBRAR_MODAL_CANONICAL_2406"
      aria-labelledby="pos-payment-title"
      aria-describedby="pos-payment-description"
      tabIndex={-1}
      data-prisma-payment-modal="true"

      data-surface="tablet"
      data-screen="pos"
      data-zone="checkout-payment-modal"
      data-panel="pos-payment-panel"
      data-target="pos-payment-panel"
      data-kind="panel"
      data-role="content-container">
      <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-1" data-kind="panel" data-role="panel" className={styles.paymentPremiumAtmosphere} aria-hidden="true" />
      <motion.div
        className={styles.paymentPremiumShell}
        initial={{ opacity: 0, y: 18, scale: 0.982 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
      >
        <PrismaCheckoutPanel
          surface="tablet"
          title={<span className={styles.paymentPremiumPanelTitle}
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout"
            data-panel="pos-payment-panel"
            data-target="pos-payment-panel-price-293"
            data-kind="price"
            data-role="financial-control"
          >Cobro PRISMA</span>}
          className={styles.paymentPremiumPanel}
          data-prisma-layer="2-glass-payment-panel"
          data-prisma-recipe="tablet-cloudglass-light checkout-panel"
        >
          <header className={styles.paymentPremiumHeader}
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout"
            data-panel="pos-payment-panel"
            data-target="pos-payment-panel-price-298"
            data-kind="price"
            data-role="financial-control"
          >
            <div className={styles.paymentPremiumTitleBlock}
              data-surface="tablet"
              data-screen="pos"
              data-zone="checkout"
              data-panel="pos-payment-panel"
              data-target="pos-payment-panel-price-299"
              data-kind="price"
              data-role="financial-control"
            >
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-2" data-kind="panel" data-role="panel"><ShieldCheck aria-hidden="true" size={15} /> Paso final de venta</span>
              <h2 id="pos-payment-title"
                data-surface="tablet"
                data-screen="pos"
                data-zone="checkout"
                data-panel="pos-payment-panel"
                data-target="pos-payment-panel-price-301"
                data-kind="price"
                data-role="financial-control"
              >Cobro PRISMA</h2>
              <p id="pos-payment-description"
                data-surface="tablet"
                data-screen="pos"
                data-zone="checkout"
                data-panel="pos-payment-panel"
                data-target="pos-payment-panel-price-302"
                data-kind="price"
                data-role="financial-control"
              >Total a cobrar, saldo restante y métodos de pago disponibles. Captura importes con punto decimal manual; referencia, autorización o folio son opcionales.</p>
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

            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout-payment-summary"
            data-panel="payment-total-panel"
            data-target="payment-total-display"
            data-kind="price"
            data-role="primary-total">
            <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-3" data-kind="panel" data-role="container">
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-4" data-kind="panel" data-role="panel"><ReceiptText aria-hidden="true" size={15} /> Total a cobrar</span>
              <strong>{formatMoney(view.totalCents)}</strong>
              <small>{view.totalQty} piezas · {view.totalLines} líneas</small>
            </div>
            <div className={styles.paymentPremiumStatusPill} data-state={view.canConfirm ? "ready" : "pending"}
              data-surface="tablet"
              data-screen="pos"
              data-zone="checkout-payment-summary"
              data-panel="payment-status-pill"
              data-target="payment-status-pill"
              data-kind="badge"
              data-role="state-indicator">
              {view.canConfirm ? <CheckCircle2 aria-hidden="true" size={18} /> : <WalletCards aria-hidden="true" size={18} />}
              {view.canConfirm ? "Listo para ticket" : "Completa el pago"}
            </div>
          </motion.div>

          <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-5" data-kind="panel" data-role="container" className={styles.paymentPremiumBodyGrid}>
            <div className={styles.paymentPremiumTenderList} aria-label="Desglose de pago" data-prisma-zone="tablet-checkout-payment-breakdown" data-prisma-layer="3-payment-methods"
              data-surface="tablet"
              data-screen="pos"
              data-zone="checkout-payment-methods"
              data-panel="payment-tender-list"
              data-target="payment-tender-list"
              data-kind="table"
              data-role="audit-surface">
              <span className={styles.paymentPremiumSectionLabel}
                data-surface="tablet"
                data-screen="pos"
                data-zone="checkout"
                data-panel="pos-payment-panel"
                data-target="pos-payment-panel-price-360"
                data-kind="price"
                data-role="financial-control"
              ><WalletCards aria-hidden="true" size={15} /> Métodos de pago disponibles</span>
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
                    <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-6" data-kind="panel" data-role="container" className={styles.paymentPremiumTenderMeta}>
                      <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-7" data-kind="panel" data-role="panel" aria-hidden="true"><PaymentIcon method={tender.method} /></span>
                      <strong>{definition.label}</strong>
                      <small>{definition.visibleConfirmation}</small>
                    </div>
                    <label className={styles.paymentPremiumTenderAmount}>
                      <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-8" data-kind="panel" data-role="panel">Importe</span>
                      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-9" data-kind="price" data-role="container" className={styles.paymentPremiumAmountField} data-prisma-currency="MXN" data-prisma-entry-mode="manual-decimal">
                        <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-10" data-kind="panel" data-role="panel" className={styles.paymentPremiumCurrencyPrefix} aria-hidden="true">$</span>
                        <input
                          type="text"
                          inputMode="decimal"
                          enterKeyHint="done"
                          autoComplete="off"
                          spellCheck={false}
                          pattern="[0-9]*[.,]?[0-9]{0,2}"
                          placeholder="0.00"
                          aria-label={`Importe ${definition.label} en pesos. Escribe el punto decimal manualmente.`}
                          value={amountDrafts[tender.method] ?? "0.00"}
                          disabled={busy}
                          data-surface="tablet"
                          data-screen="pos"
                          data-zone="checkout"
                          data-panel="pos-payment-panel"
                          data-target="pos-payment-panel-price-382"
                          data-kind="price"
                          data-role="financial-control"
                          onFocus={(event) => {
                            focusTender(tender.method);
                            event.currentTarget.select();
                          }}
                          onBlur={(event) => {
                            clearFocusedTender();
                            const amountCents = manualMoneyDraftToCents(event.currentTarget.value);
                            updateTender(tender.method, { amountCents });
                            setAmountDrafts((current) => ({
                              ...current,
                              [tender.method]: decimalTenderValue(amountCents)
                            }));
                          }}
                          onChange={(event) => {
                            focusedTenderRef.current = tender.method;
                            const draft = sanitizeMoneyDraft(event.target.value);
                            setAmountDrafts((current) => ({ ...current, [tender.method]: draft }));
                            updateTender(tender.method, { amountCents: manualMoneyDraftToCents(draft) });
                          }}
                        />
                      </div>
                    </label>
                    {tender.method !== "cash" ? (
                      <label className={styles.paymentPremiumTenderReference} data-optional="true">
                        <span className={styles.paymentPremiumTenderReferenceLabel}
                          data-surface="tablet"
                          data-screen="pos"
                          data-zone="checkout"
                          data-panel="pos-payment-panel"
                          data-target="pos-payment-panel-price-417"
                          data-kind="price"
                          data-role="financial-control"
                        >
                          Referencia
                          <small>Opcional</small>
                        </span>
                        <input
                          placeholder="Opcional: autorización o folio"
                          aria-label={`Referencia opcional ${definition.label}`}
                          value={tender.reference}
                          disabled={busy}
                          data-surface="tablet"
                          data-screen="pos"
                          data-zone="checkout"
                          data-panel="pos-payment-panel"
                          data-target="pos-payment-panel-price-421"
                          data-kind="price"
                          data-role="financial-control"
                          onChange={(event) => updateTender(tender.method, { reference: event.target.value })}
                        />
                      </label>
                    ) : null}
                  </motion.div>
                );
              })}
            </div>

            <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-11" data-kind="panel" data-role="container" className={styles.paymentPremiumRightRail}>
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-12" data-kind="panel" data-role="container" className={styles.paymentPremiumCashBox} data-prisma-zone="tablet-checkout-cash-helper" data-prisma-state={view.canConfirm ? "ready" : "pending"}>
                <span className={styles.paymentPremiumSectionLabel}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="checkout"
                  data-panel="pos-payment-panel"
                  data-target="pos-payment-panel-price-437"
                  data-kind="price"
                  data-role="financial-control"
                ><Sparkles aria-hidden="true" size={15} /> Sugerencias de efectivo</span>
                <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-div-13" data-kind="panel" data-role="container" className={styles.paymentPremiumCashSuggestions} aria-label="Billetes y monedas sugeridas">
                  {suggestedCashTenderCents(Math.max(view.remainingCents, view.totalCents)).map((value) => (
                    <motion.button
                      key={value}
                      type="button"
                      onClick={() => updateTenderAmount("cash", value)}
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
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-14" data-kind="panel" data-role="panel">Total <strong>{formatMoney(view.totalCents)}</strong></span>
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-15" data-kind="panel" data-role="panel">Pagado <strong>{formatMoney(view.paidCents)}</strong></span>
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-16" data-kind="panel" data-role="panel">Restante <strong>{formatMoney(view.remainingCents)}</strong></span>
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-17" data-kind="panel" data-role="panel">Cambio a entregar <strong>{formatMoney(view.changeCents)}</strong></span>
              </motion.div>

              <div className={view.canConfirm ? styles.paymentPremiumReviewReady : styles.paymentPremiumReview} data-prisma-state={view.canConfirm ? "success" : "pending"} data-prisma-motion={view.canConfirm ? "success-feedback" : "reduced-motion-safe"}
                data-surface="tablet"
                data-screen="pos"
                data-zone="checkout"
                data-panel="pos-payment-panel"
                data-target="pos-payment-panel-price-466"
                data-kind="price"
                data-role="financial-control"
              >
                <strong>{view.tenderLabel}</strong>
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_payment_panel" data-target="pos-payment-panel-span-18" data-kind="panel" data-role="panel">{view.tenderDetail}</span>
                {clientRequestId ? <small>Referencia de venta: {clientRequestId.slice(0, 8)}</small> : null}
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
          {showInsufficientDialog && canExplainIncompletePayment ? (
            <section className={styles.paymentPremiumInsufficientLayer} role="alertdialog" aria-modal="true" aria-labelledby="pos-insufficient-title" aria-describedby="pos-insufficient-copy"
              data-surface="tablet"
              data-screen="pos"
              data-zone="checkout"
              data-panel="pos-payment-panel"
              data-target="pos-payment-panel-price-485"
              data-kind="price"
              data-role="financial-control"
            >
              <div className={styles.paymentPremiumInsufficientDialog}>
                <span>Pago incompleto</span>
                <h3 id="pos-insufficient-title">Saldo pendiente: {formatMoney(view.remainingCents)}</h3>
                <p id="pos-insufficient-copy">El pago todavía no cubre el total. Agrega otro método de pago, ajusta el importe o completa el saldo pendiente.</p>
                <div className={styles.paymentPremiumInsufficientActions}>
                  <button type="button"
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="checkout"
                    data-panel="pos-payment-panel"
                    data-target="pos-payment-panel-price-491"
                    data-kind="price"
                    data-role="financial-control"
                    onClick={() => addRemainingTo("card")}>Agregar otro método</button>
                  <button type="button"
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="checkout"
                    data-panel="pos-payment-panel"
                    data-target="pos-payment-panel-price-492"
                    data-kind="price"
                    data-role="financial-control"
                    onClick={() => { setShowInsufficientDialog(false); focusTender("cash"); }}>Ajustar importe</button>
                  <button type="button"
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="checkout"
                    data-panel="pos-payment-panel"
                    data-target="pos-payment-panel-price-493"
                    data-kind="price"
                    data-role="financial-control"
                    onClick={() => addRemainingTo("transfer")}>Cambiar método</button>
                  <button type="button" onClick={onClose}
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="checkout"
                    data-panel="pos-payment-panel"
                    data-target="pos-payment-panel-price-494"
                    data-kind="price"
                    data-role="financial-control"
                  >Volver al ticket</button>
                  <button type="button" onClick={clearTenderAmounts}
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="checkout"
                    data-panel="pos-payment-panel"
                    data-target="pos-payment-panel-price-495"
                    data-kind="price"
                    data-role="financial-control"
                  >Cancelar cobro</button>
                </div>
              </div>
            </section>
          ) : null}

          <footer className={styles.paymentPremiumFooter} data-prisma-layer="4-primary-checkout-cta"
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout"
            data-panel="pos-payment-panel"
            data-target="pos-payment-panel-price-501"
            data-kind="price"
            data-role="financial-control"
          >
            <PrismaActionButton className={checkoutAction({ intent: "secondaryAction" })} type="button" onClick={onClose} disabled={busy} surface="tablet" tone="default">
              <ArrowLeft aria-hidden="true" size={18} />
              Volver al ticket
            </PrismaActionButton>
            <motion.button
              className={checkoutAction({ intent: "primaryCheckout" })}
              type="button"
              onClick={handleConfirmClick}
              disabled={confirmDisabled}
              whileTap={confirmDisabled ? undefined : { scale: 0.982 }}
              whileHover={confirmDisabled ? undefined : { y: -1, boxShadow: "0 26px 62px rgba(78, 94, 118, 0.20), 0 0 34px rgba(255, 255, 255, 0.40)" }}
              transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
              data-prisma-checkout-finalize="31"
              data-prisma-zone="tablet-checkout-confirm-action"
              data-prisma-role="primary-action"
              data-prisma-priority={view.canConfirm ? "primary" : "passive"}
              data-prisma-state={confirmDisabled ? "disabled" : view.canConfirm ? "ready" : "review"}
              data-prisma-motion="press-feedback"
              data-prisma-qa={confirmDisabled ? "tablet-qa-disabled" : view.canConfirm ? "tablet-qa-cobrar" : "tablet-qa-incomplete-payment"}
            >
              {busy ? (
                <Loader2 className={styles.paymentPremiumSpinner} aria-hidden="true" size={21} />
              ) : canExplainIncompletePayment && !view.canConfirm ? (
                <AlertTriangle aria-hidden="true" size={22} />
              ) : (
                <CheckCircle2 aria-hidden="true" size={22} />
              )}
              <span>{busy ? "Generando ticket..." : canExplainIncompletePayment && !view.canConfirm ? "Revisar saldo pendiente" : "Generar ticket"}</span>
            </motion.button>
          </footer>
        </PrismaCheckoutPanel>
      </motion.div>
    </motion.section>
  );

  return createPortal(paymentOverlay, document.body);
}

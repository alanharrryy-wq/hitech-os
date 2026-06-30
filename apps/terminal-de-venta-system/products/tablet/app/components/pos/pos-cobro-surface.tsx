"use client";

import { createPortal } from "react-dom";
import { useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, ArrowLeft, Banknote, CheckCircle2, CreditCard, Landmark, Loader2, X } from "lucide-react";
import { PrismaGlassControl, PrismaLiquidAction, PrismaModalShell, PrismaSoftCard, PrismaStatusChip } from "@components/tablet-visual-v2";
import type { CartLine } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { isCheckoutBusy } from "@/lib/pos/payment-contract";
import type { PaymentMethod, PaymentTenderInput } from "@/lib/pos/payment-state";
import { paymentMethodDefinition } from "@/lib/pos/payment-state";
import { buildPaymentReviewViewModel } from "@/lib/pos/payment-view-model";
import { centsFromDecimalString, suggestedCashTenderCents } from "@/lib/pos/payment-tender";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import styles from "./pos-cobro-surface.module.css";

type CobroSurfaceProps = {
  open: boolean;
  lines: CartLine[];
  state: CheckoutState;
  error: unknown;
  paymentTenders: PaymentTenderInput[];
  clientRequestId: string;
  onPaymentTenderChange: (method: PaymentMethod, patch: Partial<Pick<PaymentTenderInput, "amountCents" | "reference">>) => void;
  onClose: () => void;
  onConfirm: () => void;
};

function decimalTenderValue(cents: number) {
  return (Math.max(0, cents) / 100).toFixed(2);
}

function sanitizeManualMoneyInput(value: string) {
  const compact = value.replace(/,/g, ".").replace(/[^0-9.]/g, "");
  const [whole = "", ...decimalParts] = compact.split(".");
  const decimals = decimalParts.join("").slice(0, 2);
  if (compact.startsWith(".")) return `0.${decimals}`;
  if (decimalParts.length > 0) return `${whole || "0"}.${decimals}`;
  return whole;
}

function manualMoneyDraftToCents(value: string) {
  return centsFromDecimalString(value);
}

function PaymentIcon({ method }: { method: PaymentMethod }) {
  if (method === "transfer") return <Landmark aria-hidden="true" size={20} strokeWidth={2.5} />;
  if (method === "card") return <CreditCard aria-hidden="true" size={20} strokeWidth={2.5} />;
  return <Banknote aria-hidden="true" size={20} strokeWidth={2.5} />;
}

export function PosCobroSurface({
  open,
  lines,
  state,
  error,
  paymentTenders,
  clientRequestId,
  onPaymentTenderChange,
  onClose,
  onConfirm
}: CobroSurfaceProps) {
  const busy = isCheckoutBusy(state);
  const view = buildPaymentReviewViewModel({ lines, paymentTenders });
  const visibleError = error ? friendlyPosError(error) : view.blockReason;
  const [focusedTender, setFocusedTender] = useState<PaymentMethod | null>(null);
  const [mounted, setMounted] = useState(false);
  const [showInsufficientDialog, setShowInsufficientDialog] = useState(false);
  const panelRef = useRef<HTMLElement | null>(null);
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const [amountDrafts, setAmountDrafts] = useState<Record<PaymentMethod, string>>({
    cash: decimalTenderValue(paymentTenders.find((tender) => tender.method === "cash")?.amountCents ?? 0),
    card: decimalTenderValue(paymentTenders.find((tender) => tender.method === "card")?.amountCents ?? 0),
    transfer: decimalTenderValue(paymentTenders.find((tender) => tender.method === "transfer")?.amountCents ?? 0)
  });

  const canExplainIncompletePayment = view.paidCents > 0 && view.paidCents < view.totalCents;
  const confirmDisabled = busy || (!view.canConfirm && !canExplainIncompletePayment);
  const suggestedCash = useMemo(() => suggestedCashTenderCents(Math.max(view.remainingCents, view.totalCents)).slice(0, 5), [view.remainingCents, view.totalCents]);
  const paymentTone = view.canConfirm ? "success" : canExplainIncompletePayment ? "warning" : "neutral";

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (view.canConfirm || !canExplainIncompletePayment || !open) setShowInsufficientDialog(false);
  }, [canExplainIncompletePayment, open, view.canConfirm]);

  useEffect(() => {
    setAmountDrafts((current) => {
      let changed = false;
      const next = { ...current };
      for (const tender of paymentTenders) {
        if (focusedTender === tender.method) continue;
        const formatted = decimalTenderValue(tender.amountCents);
        if (manualMoneyDraftToCents(next[tender.method] ?? "") !== tender.amountCents || !next[tender.method]) {
          next[tender.method] = formatted;
          changed = true;
        }
      }
      return changed ? next : current;
    });
  }, [paymentTenders, focusedTender]);

  useEffect(() => {
    if (!open || !mounted || typeof document === "undefined") return;

    const previousBodyOverflow = document.body.style.overflow;
    const previousBodyOverscroll = document.body.style.overscrollBehavior;
    const previousHtmlOverflow = document.documentElement.style.overflow;
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const changedSiblings: Array<{ element: Element; ariaHidden: string | null; inert: string | null }> = [];

    document.body.style.overflow = "hidden";
    document.body.style.overscrollBehavior = "contain";
    document.documentElement.style.overflow = "hidden";

    const frame = window.requestAnimationFrame(() => {
      const portal = panelRef.current?.closest("[data-prisma-cobro-portal]");
      for (const element of Array.from(document.body.children)) {
        if (portal && element === portal) continue;
        if (portal && element.contains(portal)) continue;
        changedSiblings.push({ element, ariaHidden: element.getAttribute("aria-hidden"), inert: element.getAttribute("inert") });
        element.setAttribute("aria-hidden", "true");
        element.setAttribute("inert", "");
      }
      const firstControl = panelRef.current?.querySelector<HTMLElement>('button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])');
      (firstControl ?? closeRef.current ?? panelRef.current)?.focus();
    });

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !busy) {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const focusables = Array.from(panelRef.current?.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])') ?? []).filter((node) => node.offsetParent !== null || node === document.activeElement);
      if (!focusables.length) {
        event.preventDefault();
        panelRef.current?.focus();
        return;
      }
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.cancelAnimationFrame(frame);
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousBodyOverflow;
      document.body.style.overscrollBehavior = previousBodyOverscroll;
      document.documentElement.style.overflow = previousHtmlOverflow;
      for (const item of changedSiblings) {
        if (item.ariaHidden === null) item.element.removeAttribute("aria-hidden");
        else item.element.setAttribute("aria-hidden", item.ariaHidden);
        if (item.inert === null) item.element.removeAttribute("inert");
        else item.element.setAttribute("inert", item.inert);
      }
      previouslyFocused?.focus?.();
    };
  }, [busy, mounted, onClose, open]);

  if (!open || !mounted || typeof document === "undefined") return null;

  function updateTender(method: PaymentMethod, patch: Partial<Pick<PaymentTenderInput, "amountCents" | "reference">>) {
    onPaymentTenderChange(method, patch);
  }

  function addRemainingTo(method: PaymentMethod) {
    const current = paymentTenders.find((tender) => tender.method === method)?.amountCents ?? 0;
    updateTender(method, { amountCents: current + view.remainingCents });
    setFocusedTender(method);
  }

  function handleConfirmClick() {
    if (view.canConfirm) {
      onConfirm();
      return;
    }
    if (canExplainIncompletePayment) setShowInsufficientDialog(true);
  }

  const surfaceNode = (
    <PrismaModalShell
      panelRef={panelRef}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
      aria-labelledby="pos-cobro-title"
      aria-describedby="pos-cobro-description"
      onOverlayMouseDown={(event: any) => {
        if (event.target === event.currentTarget) event.preventDefault();
      }}
    >
      <header className={styles.topbar}>
        <div className={styles.titleGroup}>
          <PrismaStatusChip tone={paymentTone} icon={view.canConfirm ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}>Cobro PRISMA</PrismaStatusChip>
          <h2 id="pos-cobro-title" className={styles.title}>Cobro PRISMA</h2>
          <p id="pos-cobro-description" className={styles.description}>
            Total a cobrar, saldo restante y métodos de pago disponibles. El cobro vive encima del POS y bloquea productos, ticket y navegación inferior mientras está abierto.
          </p>
        </div>
        <button ref={closeRef} className={styles.closeButton} type="button" onClick={onClose} disabled={busy}>
          <X aria-hidden="true" size={18} />
          Cancelar cobro
        </button>
      </header>

      <section className={styles.contentGrid}>
        <div className={styles.methodsColumn} aria-label="Métodos de pago disponibles">
          <div className={styles.summaryGrid}>
            <PrismaSoftCard className={styles.amountCard} tone="amount" data-prisma-effect="softglass-surface ticket-total-pulse">
              <span className={styles.amountLabel}>Total a cobrar</span>
              <strong className={styles.amountValue}>{formatMoney(view.totalCents)}</strong>
              <span className={styles.amountMeta}>{lines.length} productos en ticket</span>
            </PrismaSoftCard>
            <PrismaSoftCard className={styles.amountCard} tone={view.remainingCents > 0 ? "warning" : "amount"}>
              <span className={styles.amountLabel}>Saldo restante</span>
              <strong className={styles.amountValue}>{formatMoney(view.remainingCents)}</strong>
              <span className={styles.amountMeta}>Pago mixto compatible</span>
            </PrismaSoftCard>
            <PrismaSoftCard className={styles.amountCard}>
              <span className={styles.amountLabel}>Cambio</span>
              <strong className={styles.amountValue}>{formatMoney(view.changeCents)}</strong>
              <span className={styles.amountMeta}>Sólo si aplica</span>
            </PrismaSoftCard>
          </div>

          <div className={styles.methodsHeader}>
            <span className={styles.amountLabel}>Métodos de pago</span>
            <PrismaStatusChip tone={paymentTone}>{view.canConfirm ? "Listo para cobrar" : "Pago por completar"}</PrismaStatusChip>
          </div>

          <div className={styles.methodsList}>
            {paymentTenders.map((tender) => {
              const definition = paymentMethodDefinition(tender.method);
              const active = tender.amountCents > 0;
              return (
                <PrismaSoftCard
                  as="section"
                  key={tender.method}
                  className={styles.methodCard}
                  tone={active ? "selected" : "default"}
                  data-prisma-payment-method={tender.method}
                  data-active={active ? "true" : "false"}
                  data-prisma-effect={active ? "method-selected-aura softglass-surface" : "softglass-surface"}
                >
                  <div className={styles.methodHeader}>
                    <span className={styles.methodIcon}><PaymentIcon method={tender.method} /></span>
                    <div className={styles.methodCopy}>
                      <strong>{definition.label}</strong>
                      <small>{definition.visibleConfirmation}</small>
                    </div>
                  </div>
                  <PrismaGlassControl label="Importe" icon="$">
                    <input
                      type="text"
                      inputMode="decimal"
                      enterKeyHint="done"
                      autoComplete="off"
                      spellCheck={false}
                      pattern="[0-9]*[.,]?[0-9]{0,2}"
                      aria-label={`Importe ${definition.label} en pesos`}
                      value={amountDrafts[tender.method] ?? "0.00"}
                      disabled={busy}
                      onFocus={(event) => {
                        setFocusedTender(tender.method);
                        event.currentTarget.select();
                      }}
                      onBlur={() => {
                        setFocusedTender(null);
                        setAmountDrafts((current) => ({ ...current, [tender.method]: decimalTenderValue(manualMoneyDraftToCents(current[tender.method] ?? "0")) }));
                      }}
                      onChange={(event) => {
                        const draft = sanitizeManualMoneyInput(event.target.value);
                        setAmountDrafts((current) => ({ ...current, [tender.method]: draft }));
                        updateTender(tender.method, { amountCents: manualMoneyDraftToCents(draft) });
                      }}
                    />
                  </PrismaGlassControl>
                  {tender.method !== "cash" ? (
                    <PrismaGlassControl label="Referencia opcional" hint="Autorización o folio">
                      <input
                        placeholder="Autorización o folio"
                        aria-label={`Referencia opcional ${definition.label}`}
                        value={tender.reference ?? ""}
                        disabled={busy}
                        onChange={(event) => updateTender(tender.method, { reference: event.target.value })}
                      />
                    </PrismaGlassControl>
                  ) : (
                    <div className={styles.quickRow} aria-label="Efectivo rápido">
                      {suggestedCash.map((value) => (
                        <button key={value} className={styles.quickButton} type="button" disabled={busy} onClick={() => updateTender("cash", { amountCents: value })}>
                          {value === view.totalCents ? "Exacto" : formatMoney(value)}
                        </button>
                      ))}
                    </div>
                  )}
                </PrismaSoftCard>
              );
            })}
          </div>
        </div>

        <aside className={styles.reviewColumn} aria-live="polite">
          <PrismaSoftCard className={styles.reviewCard} data-prisma-effect="softglass-surface ticket-total-pulse">
            <PrismaStatusChip tone={paymentTone}>Resumen de cobro</PrismaStatusChip>
            <div className={styles.reviewBody}>
              <strong>{view.tenderLabel}</strong>
              <span>{view.tenderDetail}</span>
              {clientRequestId ? <small>Referencia de venta: {clientRequestId.slice(0, 8)}</small> : null}
            </div>
            {view.remainingCents > 0 ? (
              <button className={styles.quickButton} type="button" disabled={busy} onClick={() => addRemainingTo("cash")}>
                Cubrir saldo con efectivo
              </button>
            ) : null}
            {canExplainIncompletePayment || showInsufficientDialog ? (
              <div className={styles.warningCard} role={showInsufficientDialog ? "alert" : "status"}>
                <strong>Pago incompleto</strong>
                <span>El pago todavía no cubre el total. Agrega otro método de pago, ajusta el importe o completa el saldo pendiente.</span>
              </div>
            ) : null}
            {visibleError ? (
              <div className={styles.warningCard} role="alert">
                <strong>No se cerró el ticket</strong>
                <span>{visibleError}</span>
              </div>
            ) : null}
          </PrismaSoftCard>
        </aside>
      </section>

      <footer className={styles.footer}>
        <button className={styles.secondaryButton} type="button" disabled={busy} onClick={onClose}>
          <ArrowLeft aria-hidden="true" size={18} />
          Volver al ticket
        </button>
        <PrismaLiquidAction
          className={styles.confirmButton}
          disabled={confirmDisabled}
          onClick={handleConfirmClick}
          icon={busy ? <Loader2 className={styles.spinner} aria-hidden="true" size={20} /> : view.canConfirm ? <CheckCircle2 aria-hidden="true" size={21} /> : <AlertTriangle aria-hidden="true" size={21} />}
          amount={view.remainingCents > 0 ? `Falta ${formatMoney(view.remainingCents)}` : formatMoney(view.totalCents)}
          status={busy ? "loading" : view.canConfirm ? "success" : confirmDisabled ? "disabled" : "ready"}
          variant={view.canConfirm ? "success" : "primary"}
          data-prisma-checkout-finalize="visual-surface-v2"
          data-prisma-qa={view.canConfirm ? "tablet-qa-cobro-confirm" : "tablet-qa-cobro-incomplete"}
        >
          {busy ? "Completando pago..." : "Completar pago"}
        </PrismaLiquidAction>
      </footer>
    </PrismaModalShell>
  );

  return createPortal(surfaceNode, document.body);
}

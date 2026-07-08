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
import { centsFromDecimalString, sanitizeMoneyDraft, suggestedCashTenderCents } from "@/lib/pos/payment-tender";
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
  onConfirm: (paymentTenders: PaymentTenderInput[]) => void;
};

function decimalTenderValue(cents: number) {
  return (Math.max(0, cents) / 100).toFixed(2);
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
  const visibleError = error ? friendlyPosError(error) : null;
  const focusedTenderRef = useRef<PaymentMethod | null>(null);
  const [mounted, setMounted] = useState(false);
  const [showInsufficientDialog, setShowInsufficientDialog] = useState(false);
  const panelRef = useRef<HTMLElement | null>(null);
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const [amountDrafts, setAmountDrafts] = useState<Record<PaymentMethod, string>>({
    cash: decimalTenderValue(paymentTenders.find((tender) => tender.method === "cash")?.amountCents ?? 0),
    card: decimalTenderValue(paymentTenders.find((tender) => tender.method === "card")?.amountCents ?? 0),
    transfer: decimalTenderValue(paymentTenders.find((tender) => tender.method === "transfer")?.amountCents ?? 0)
  });
  const draftPaymentTenders = useMemo<PaymentTenderInput[]>(
    () =>
      paymentTenders.map((tender) => ({
        ...tender,
        amountCents: manualMoneyDraftToCents(amountDrafts[tender.method] ?? decimalTenderValue(tender.amountCents))
      })),
    [paymentTenders, amountDrafts]
  );
  const view = buildPaymentReviewViewModel({ lines, paymentTenders: draftPaymentTenders });

  const canExplainIncompletePayment = view.paidCents > 0 && view.paidCents < view.totalCents;
  const confirmDisabled = busy || (!view.canConfirm && !canExplainIncompletePayment);
  const suggestedCash = useMemo(() => suggestedCashTenderCents(Math.max(view.remainingCents, view.totalCents)).slice(0, 5), [view.remainingCents, view.totalCents]);
  const paymentTone = view.canConfirm ? "success" : canExplainIncompletePayment ? "warning" : "neutral";
  const checkoutMood = busy ? "loading" : view.canConfirm ? "ready" : canExplainIncompletePayment ? "short" : "idle";
  const statusCopy = view.canConfirm
    ? "Listo para cobrar"
    : canExplainIncompletePayment
      ? `Faltan ${formatMoney(view.remainingCents)}`
      : "Captura el pago";

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (view.canConfirm || !canExplainIncompletePayment || !open) setShowInsufficientDialog(false);
  }, [canExplainIncompletePayment, open, view.canConfirm]);

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
    const current = draftPaymentTenders.find((tender) => tender.method === method)?.amountCents ?? 0;
    updateTenderAmount(method, current + view.remainingCents);
    focusTender(method);
  }

  function handleConfirmClick() {
    if (view.canConfirm) {
      onConfirm(draftPaymentTenders);
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
      overlayClassName={styles.cobroOverlay}
      onOverlayMouseDown={(event: any) => {
        if (event.target === event.currentTarget) event.preventDefault();
      }}
      className={styles.cobroPanel}
      data-prisma-cobro-state={checkoutMood}
    >
      <header className={styles.topbar}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-cobro-surface"
        data-target="pos-cobro-surface-price-225"
        data-kind="price"
        data-role="revenue-core"
      >
        <div className={styles.titleGroup}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-cobro-surface"
          data-target="pos-cobro-surface-price-226"
          data-kind="price"
          data-role="revenue-core"
        >
          <PrismaStatusChip tone={paymentTone} icon={view.canConfirm ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}>{statusCopy}</PrismaStatusChip>
          <h2 id="pos-cobro-title" className={styles.title}
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-cobro-surface"
            data-target="pos-cobro-surface-price-228"
            data-kind="price"
            data-role="revenue-core"
          >Cobro</h2>
          <p id="pos-cobro-description" className={styles.description}
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-cobro-surface"
            data-target="pos-cobro-surface-price-229"
            data-kind="price"
            data-role="revenue-core"
          >Recibe, revisa cambio y genera el ticket.</p>
        </div>
        <button ref={closeRef} className={styles.closeButton} type="button" aria-label="Cancelar cobro" onClick={onClose} disabled={busy}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-cobro-surface"
          data-target="pos-cobro-surface-cancelar-cobro-231"
          data-kind="price"
          data-role="revenue-core"
        >
          <X aria-hidden="true" size={18} />
          Cancelar
        </button>
      </header>

      <section className={styles.contentGrid}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-cobro-surface"
        data-target="pos-cobro-surface-price-237"
        data-kind="price"
        data-role="revenue-core"
      >
        <div className={styles.methodsColumn} aria-label="Métodos de pago disponibles"
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-cobro-surface"
          data-target="pos-cobro-surface-m-todos-de-pago-disponibles-238"
          data-kind="price"
          data-role="financial-control"
        >
          <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-1" data-kind="layout" data-role="container" className={styles.summaryGrid}>
            <PrismaSoftCard className={styles.amountCard} tone="amount" data-prisma-effect="softglass-surface ticket-total-pulse">
              <span className={styles.amountLabel}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-cobro-surface"
                data-target="pos-cobro-surface-price-241"
                data-kind="price"
                data-role="financial-control"
              >Total</span>
              <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-strong-2" data-kind="price" data-role="price" className={styles.amountValue}>{formatMoney(view.totalCents)}</strong>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-3" data-kind="price" data-role="price" className={styles.amountMeta}>{lines.length} producto{lines.length === 1 ? "" : "s"}</span>
            </PrismaSoftCard>
            <PrismaSoftCard className={styles.amountCard} tone={view.remainingCents > 0 ? "warning" : "amount"}>
              <span className={styles.amountLabel}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-cobro-surface"
                data-target="pos-cobro-surface-price-246"
                data-kind="price"
                data-role="financial-control"
              >{view.remainingCents > 0 ? "Falta" : "Recibido"}</span>
              <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-strong-4" data-kind="price" data-role="price" className={styles.amountValue}>{formatMoney(view.remainingCents > 0 ? view.remainingCents : view.paidCents)}</strong>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-5" data-kind="price" data-role="price" className={styles.amountMeta}>{view.remainingCents > 0 ? "Completa el saldo" : "Pago cubierto"}</span>
            </PrismaSoftCard>
            <PrismaSoftCard className={styles.amountCard}>
              <span className={styles.amountLabel}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-cobro-surface"
                data-target="pos-cobro-surface-price-251"
                data-kind="price"
                data-role="financial-control"
              >Cambio</span>
              <strong className={styles.amountValue}>{formatMoney(view.changeCents)}</strong>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-6" data-kind="price" data-role="price" className={styles.amountMeta}>Entrega al cliente</span>
            </PrismaSoftCard>
          </div>

          <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-7" data-kind="panel" data-role="container" className={styles.methodsHeader}>
            <span className={styles.amountLabel}
              data-surface="tablet"
              data-screen="pos"
              data-zone="pos"
              data-panel="pos-cobro-surface"
              data-target="pos-cobro-surface-price-258"
              data-kind="price"
              data-role="financial-control"
            >Pago recibido</span>
          </div>

          <div className={styles.methodsList}
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-cobro-surface"
            data-target="pos-cobro-surface-price-261"
            data-kind="price"
            data-role="revenue-core"
          >
            {draftPaymentTenders.map((tender) => {
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
                  <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-8" data-kind="panel" data-role="container" className={styles.methodHeader}>
                    <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-9" data-kind="text" data-role="text" className={styles.methodIcon}><PaymentIcon method={tender.method} /></span>
                    <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-10" data-kind="panel" data-role="container" className={styles.methodCopy}>
                      <strong>{definition.label}</strong>
                      <small>{tender.method === "cash" ? "Efectivo recibido" : "Importe confirmado"}</small>
                    </div>
                  </div>
                  <PrismaGlassControl className={styles.moneyControl} label="Importe" icon="$">
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
                      data-surface="tablet"
                      data-screen="pos"
                      data-zone="pos"
                      data-panel="pos-cobro-surface"
                      data-target="pos-cobro-surface-price-283"
                      data-kind="price"
                      data-role="financial-control"
                      onFocus={(event) => {
                        focusTender(tender.method);
                        event.currentTarget.select();
                      }}
                      onBlur={(event) => {
                        clearFocusedTender();
                        const amountCents = manualMoneyDraftToCents(event.currentTarget.value);
                        updateTenderAmount(tender.method, amountCents);
                      }}
                      onChange={(event) => {
                        focusedTenderRef.current = tender.method;
                        const draft = sanitizeMoneyDraft(event.target.value);
                        setAmountDrafts((current) => ({ ...current, [tender.method]: draft }));
                      }}
                    />
                  </PrismaGlassControl>
                  {tender.method !== "cash" ? (
                    <PrismaGlassControl className={styles.moneyControl} label="Referencia opcional" hint="Autorización o folio">
                      <input
                        placeholder="Autorización o folio"
                        aria-label={`Referencia opcional ${definition.label}`}
                        value={tender.reference ?? ""}
                        disabled={busy}
                        data-surface="tablet"
                        data-screen="pos"
                        data-zone="pos"
                        data-panel="pos-cobro-surface"
                        data-target="pos-cobro-surface-price-311"
                        data-kind="price"
                        data-role="ticket-context"
                        onChange={(event) => updateTender(tender.method, { reference: event.target.value })}
                      />
                    </PrismaGlassControl>
                  ) : (
                    <div className={styles.quickRow} aria-label="Efectivo rápido"
                      data-surface="tablet"
                      data-screen="pos"
                      data-zone="pos"
                      data-panel="pos-cobro-surface"
                      data-target="pos-cobro-surface-efectivo-r-pido-320"
                      data-kind="price"
                      data-role="revenue-core"
                    >
                      {suggestedCash.map((value) => (
                        <button key={value} className={styles.quickButton} type="button" disabled={busy}
                          data-surface="tablet"
                          data-screen="pos"
                          data-zone="pos"
                          data-panel="pos-cobro-surface"
                          data-target="pos-cobro-surface-price-322"
                          data-kind="price"
                          data-role="revenue-core"
                          onClick={() => updateTenderAmount("cash", value)}
                        >
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

        <aside data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-aside-11" data-kind="panel" data-role="container" className={styles.reviewColumn} aria-live="polite">
          <PrismaSoftCard className={styles.reviewCard} data-prisma-effect="softglass-surface ticket-total-pulse">
            <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-12" data-kind="panel" data-role="container" className={styles.reviewBody}>
              <strong>{view.tenderLabel}</strong>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-13" data-kind="text" data-role="text">{view.canConfirm ? "Todo cubierto. Genera el ticket cuando confirmes el cobro." : canExplainIncompletePayment ? "El importe no cubre el total." : "Captura efectivo, tarjeta o transferencia."}</span>
            </div>
            {view.remainingCents > 0 ? (
              <button className={styles.quickButton} type="button" disabled={busy}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-cobro-surface"
                data-target="pos-cobro-surface-price-341"
                data-kind="price"
                data-role="revenue-core"
                onClick={() => addRemainingTo("cash")}
              >
                Cubrir saldo con efectivo
              </button>
            ) : null}
            {canExplainIncompletePayment || showInsufficientDialog ? (
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-14" data-kind="badge" data-role="container" className={styles.warningCard} role={showInsufficientDialog ? "alert" : "status"}>
                <strong>Importe insuficiente</strong>
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-15" data-kind="text" data-role="text">Faltan {formatMoney(view.remainingCents)} para cerrar.</span>
              </div>
            ) : null}
            {visibleError ? (
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-div-16" data-kind="panel" data-role="container" className={styles.warningCard} role="alert">
                <strong>No se cerró el ticket</strong>
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-span-17" data-kind="text" data-role="text">{visibleError}</span>
              </div>
            ) : null}
          </PrismaSoftCard>
        </aside>
      </section>

      <footer data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_cobro_surface" data-target="pos-cobro-surface-footer-18" data-kind="panel" data-role="container" className={styles.footer}>
        <button className={styles.secondaryButton} type="button" disabled={busy} onClick={onClose}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-cobro-surface"
          data-target="pos-cobro-surface-price-362"
          data-kind="price"
          data-role="revenue-core"
        >
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
          data-payment-state={checkoutMood}
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

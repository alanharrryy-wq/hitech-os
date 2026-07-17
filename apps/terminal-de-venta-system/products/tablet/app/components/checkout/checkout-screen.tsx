"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, ArrowLeft, CheckCircle2, Loader2 } from "lucide-react";
import type { CartLine, CompletedSaleReceipt } from "@/lib/pos/cart-state";
import { clearCartStorage, formatMoney, readCartFromStorage } from "@/lib/pos/cart-state";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { isCheckoutBusy } from "@/lib/pos/payment-contract";
import { completeCartSale } from "@/lib/pos/payment-flow";
import { clearPaymentRequestRecord, getOrCreatePaymentRequestId } from "@/lib/pos/payment-idempotency";
import type { PaymentMethod, PaymentMethodOrMixed, PaymentTenderInput } from "@/lib/pos/payment-state";
import { createDefaultPaymentTenders, normalizePaymentTenders, paymentMethodLabel } from "@/lib/pos/payment-state";
import { centsFromDecimalString, sanitizeMoneyDraft } from "@/lib/pos/payment-tender";
import { buildPaymentReviewViewModel } from "@/lib/pos/payment-view-model";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import { buildTicketSuccessViewModel } from "@/lib/pos/ticket-success-view-model";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { SellingWorkspace } from "@components/pos/pos-screen";
import { CheckoutCashCalculator } from "./checkout-cash-calculator";
import { CheckoutPaymentMethods } from "./checkout-payment-methods";
import { CheckoutSummary } from "./checkout-summary";
import styles from "./checkout.module.css";

const CHECKOUT_DRAFT_KEY = "prisma.tablet.pos.checkoutDraft.v1";
const CHECKOUT_RETURN_FOCUS_KEY = "prisma.tablet.pos.checkoutReturnFocus.v1";

type CheckoutUiDraft = {
  cartSignature: string;
  paymentMode: PaymentMethodOrMixed;
  mixedMethod: PaymentMethod;
  paymentTenders: PaymentTenderInput[];
  amountDrafts: Record<PaymentMethod, string>;
  committedMethods: PaymentMethod[];
};

function decimalTenderValue(cents: number) {
  return cents > 0 ? (cents / 100).toFixed(2) : "";
}

function cartSignature(lines: CartLine[]) {
  return lines.map((line) => `${line.product.id}:${line.qty}:${line.product.priceCents}`).join("|");
}

function validPaymentMode(value: unknown): PaymentMethodOrMixed {
  return value === "cash" || value === "card" || value === "transfer" || value === "mixed" ? value : "cash";
}

function validPaymentMethod(value: unknown): PaymentMethod {
  return value === "card" || value === "transfer" ? value : "cash";
}

function detailHref(sale: CompletedSaleReceipt) {
  const key = sale.ticketEvidence?.canonicalTicketId || sale.saleId;
  return sale.ticketEvidence?.localDetailHref || `/sales/today/${encodeURIComponent(key)}${sale.businessId ? `?businessId=${encodeURIComponent(sale.businessId)}` : ""}`;
}

export function CheckoutScreen({ runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT }: { runtimeSnapshot?: TabletRuntimeSnapshot }) {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [paymentMode, setPaymentMode] = useState<PaymentMethodOrMixed>("cash");
  const [mixedMethod, setMixedMethod] = useState<PaymentMethod>("cash");
  const [paymentTenders, setPaymentTenders] = useState<PaymentTenderInput[]>(() => createDefaultPaymentTenders());
  const [amountDrafts, setAmountDrafts] = useState<Record<PaymentMethod, string>>({ cash: "", card: "", transfer: "" });
  const [committedMethods, setCommittedMethods] = useState<PaymentMethod[]>([]);
  const [draftHydrated, setDraftHydrated] = useState(false);
  const [state, setState] = useState<CheckoutState>("idle");
  const [error, setError] = useState<unknown>(null);
  const [lastSale, setLastSale] = useState<CompletedSaleReceipt | null>(null);
  const [clientRequestId, setClientRequestId] = useState("");
  const submittingRef = useRef(false);
  const busyRef = useRef(false);
  const dialogRef = useRef<HTMLElement | null>(null);
  const posContextRef = useRef<HTMLDivElement | null>(null);
  const gate = useMemo(() => decideCanSellFromRuntimeSnapshot(runtimeSnapshot), [runtimeSnapshot]);
  const busy = isCheckoutBusy(state);

  const effectiveTenders = useMemo(
    () => normalizePaymentTenders(paymentTenders).map((tender) => {
      if (paymentMode === "mixed") return committedMethods.includes(tender.method) ? tender : { ...tender, amountCents: 0 };
      return tender.method === paymentMode ? tender : { ...tender, amountCents: 0 };
    }),
    [committedMethods, paymentMode, paymentTenders]
  );
  const view = useMemo(() => buildPaymentReviewViewModel({ lines, paymentTenders: effectiveTenders }), [effectiveTenders, lines]);
  const captureMethod: PaymentMethod = paymentMode === "mixed" ? mixedMethod : paymentMode;
  const captureTender = paymentTenders.find((tender) => tender.method === captureMethod) ?? createDefaultPaymentTenders().find((tender) => tender.method === captureMethod)!;
  const captureIsCommitted = committedMethods.includes(captureMethod);
  const captureTargetCents = paymentMode === "mixed" ? (captureIsCommitted ? captureTender.amountCents : 0) + view.remainingCents : view.totalCents;
  const activeContributions = paymentMode === "mixed" ? paymentTenders.filter((tender) => committedMethods.includes(tender.method) && tender.amountCents > 0) : [];
  const visibleError = error ? friendlyPosError(error) : "";

  useEffect(() => {
    const storedLines = readCartFromStorage();
    setLines(storedLines);

    if (typeof window !== "undefined" && storedLines.length) {
      const raw = window.sessionStorage.getItem(CHECKOUT_DRAFT_KEY);
      if (raw) {
        try {
          const saved = JSON.parse(raw) as Partial<CheckoutUiDraft>;
          if (saved.cartSignature === cartSignature(storedLines)) {
            const tenders = normalizePaymentTenders(saved.paymentTenders);
            setPaymentMode(validPaymentMode(saved.paymentMode));
            setMixedMethod(validPaymentMethod(saved.mixedMethod));
            setPaymentTenders(tenders);
            setAmountDrafts(saved.amountDrafts ?? {
              cash: decimalTenderValue(tenders.find((tender) => tender.method === "cash")?.amountCents ?? 0),
              card: decimalTenderValue(tenders.find((tender) => tender.method === "card")?.amountCents ?? 0),
              transfer: decimalTenderValue(tenders.find((tender) => tender.method === "transfer")?.amountCents ?? 0)
            });
            setCommittedMethods((saved.committedMethods ?? []).map(validPaymentMethod).filter((method, index, all) => all.indexOf(method) === index));
          }
        } catch {
          window.sessionStorage.removeItem(CHECKOUT_DRAFT_KEY);
        }
      }
      void getOrCreatePaymentRequestId(storedLines)
        .then(setClientRequestId)
        .catch((caught) => { setError(caught); setState("error"); });
    }
    setDraftHydrated(true);
  }, []);

  useEffect(() => {
    if (!draftHydrated || !lines.length || lastSale || typeof window === "undefined") return;
    const draft: CheckoutUiDraft = {
      cartSignature: cartSignature(lines),
      paymentMode,
      mixedMethod,
      paymentTenders,
      amountDrafts,
      committedMethods
    };
    window.sessionStorage.setItem(CHECKOUT_DRAFT_KEY, JSON.stringify(draft));
  }, [amountDrafts, committedMethods, draftHydrated, lastSale, lines, mixedMethod, paymentMode, paymentTenders]);

  useEffect(() => {
    busyRef.current = busy;
  }, [busy]);

  useEffect(() => {
    const context = posContextRef.current;
    context?.setAttribute("inert", "");
    const frame = window.requestAnimationFrame(() => {
      const firstField = dialogRef.current?.querySelector<HTMLElement>('input:not([disabled])')
        ?? dialogRef.current?.querySelector<HTMLElement>('button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])');
      (firstField ?? dialogRef.current)?.focus();
    });

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !busyRef.current) {
        event.preventDefault();
        goBackToTicket();
        return;
      }
      if (event.key !== "Tab") return;
      const focusable = Array.from(dialogRef.current?.querySelectorAll<HTMLElement>('input:not([disabled]), button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])') ?? []).filter((node) => node.offsetParent !== null);
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
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.cancelAnimationFrame(frame);
      document.removeEventListener("keydown", handleKeyDown);
      context?.removeAttribute("inert");
    };
  }, []);

  function persistDraft() {
    if (typeof window === "undefined" || !lines.length) return;
    const draft: CheckoutUiDraft = { cartSignature: cartSignature(lines), paymentMode, mixedMethod, paymentTenders, amountDrafts, committedMethods };
    window.sessionStorage.setItem(CHECKOUT_DRAFT_KEY, JSON.stringify(draft));
  }

  function goBackToTicket() {
    if (submittingRef.current) return;
    persistDraft();
    window.sessionStorage.setItem(CHECKOUT_RETURN_FOCUS_KEY, "1");
    window.location.assign("/pos");
  }

  function cancelCheckout() {
    if (submittingRef.current) return;
    window.sessionStorage.removeItem(CHECKOUT_DRAFT_KEY);
    window.sessionStorage.setItem(CHECKOUT_RETURN_FOCUS_KEY, "1");
    clearPaymentRequestRecord();
    window.location.assign("/pos");
  }

  function updateTender(method: PaymentMethod, patch: Partial<Pick<PaymentTenderInput, "amountCents" | "reference">>) {
    setPaymentTenders((current) => normalizePaymentTenders(current).map((tender) => tender.method === method ? { ...tender, ...patch } : tender));
    setError(null);
    if (state === "error") setState("review");
  }

  function updateAmount(method: PaymentMethod, amountCents: number) {
    const normalized = Math.max(0, Math.round(amountCents));
    setAmountDrafts((current) => ({ ...current, [method]: decimalTenderValue(normalized) }));
    updateTender(method, { amountCents: normalized });
  }

  function updateAmountDraft(method: PaymentMethod, value: string) {
    const draft = sanitizeMoneyDraft(value);
    setAmountDrafts((current) => ({ ...current, [method]: draft }));
    updateTender(method, { amountCents: centsFromDecimalString(draft) });
  }

  function selectPaymentMode(next: PaymentMethodOrMixed) {
    if (next === "mixed" && paymentMode !== "mixed") {
      const previous = paymentTenders.find((tender) => tender.method === paymentMode);
      if (previous && previous.amountCents > 0) setCommittedMethods((current) => current.includes(previous.method) ? current : [...current, previous.method]);
    }
    setPaymentMode(next);
    setError(null);
  }

  function addContribution() {
    if (captureTender.amountCents <= 0) {
      setError("Captura un importe antes de agregar esta aportación.");
      return;
    }
    setCommittedMethods((current) => current.includes(captureMethod) ? current : [...current, captureMethod]);
    setError(null);
  }

  function removeContribution(method: PaymentMethod) {
    setCommittedMethods((current) => current.filter((item) => item !== method));
    updateAmount(method, 0);
  }

  async function confirmPayment() {
    if (submittingRef.current || !view.canConfirm || !gate.canCheckout || !lines.length) return;
    submittingRef.current = true;
    setState("submitting");
    setError(null);
    try {
      const requestId = clientRequestId || await getOrCreatePaymentRequestId(lines);
      setClientRequestId(requestId);
      const sale = await completeCartSale({ lines, paymentTenders: effectiveTenders, clientRequestId: requestId });
      setLastSale(sale);
      setLines([]);
      clearCartStorage();
      clearPaymentRequestRecord();
      window.sessionStorage.removeItem(CHECKOUT_DRAFT_KEY);
      setState("success");
    } catch (caught) {
      setError(caught);
      setState("error");
    } finally {
      submittingRef.current = false;
    }
  }

  const validationCopy = visibleError
    || (!gate.canCheckout ? gate.detail : "")
    || (!lines.length ? "Vuelve al ticket y agrega productos antes de cobrar." : "")
    || (view.canConfirm
      ? `${view.paymentLabel} listo para confirmar.`
      : view.nonCashOverpayCents > 0
        ? view.tenderDetail
        : `Captura ${formatMoney(view.remainingCents)} para completar el pago.`);

  const success = lastSale ? buildTicketSuccessViewModel(lastSale) : null;

  return (
    <main className={styles.modalStage} data-prisma-workspace="CheckoutWorkspace" data-state={success ? "success" : busy ? "submitting" : view.canConfirm ? "ready" : "capture"}>
      <div ref={posContextRef} className={styles.posContext} aria-hidden="true" data-prisma-checkout-context="real-pos-inert">
        <SellingWorkspace runtimeSnapshot={runtimeSnapshot} checkoutBackdrop />
      </div>
      <div className={styles.modalBackdrop} data-prisma-component="CheckoutModalBackdrop">
        <section
          ref={dialogRef}
          className={styles.glassSheet}
          role="dialog"
          aria-modal="true"
          aria-labelledby="checkout-dialog-title"
          aria-describedby="checkout-validation"
          tabIndex={-1}
          data-prisma-component="PremiumGlassPaymentSheet"
        >
          <header className={styles.sheetHeader}>
            <button className={styles.backAction} type="button" onClick={goBackToTicket} disabled={busy}>
              <ArrowLeft aria-hidden="true" size={17} />
              <span>{success ? "Volver a vender" : "Volver al ticket"}</span>
            </button>
            <div className={styles.headerTitle}>
              <span>{success ? "PAGO CONFIRMADO" : "CAPTURA DE PAGO"}</span>
              <h1 id="checkout-dialog-title">{success ? "Cobro completado" : "Cobro"}</h1>
            </div>
            {success && lastSale ? (
              <a className={styles.cancelAction} href={detailHref(lastSale)}>Ver ticket</a>
            ) : (
              <button className={styles.cancelAction} type="button" onClick={cancelCheckout} disabled={busy}>Cancelar cobro</button>
            )}
          </header>

          {success && lastSale ? (
            <section className={styles.successWorkspace} aria-live="polite">
              <CheckCircle2 aria-hidden="true" size={36} />
              <span>{success.title}</span>
              <h2>{success.folio}</h2>
              <strong>{success.totalLabel}</strong>
              <p>{success.lineSummary} · {success.paymentLabel} · {success.paymentDetail}</p>
              <div className={styles.successActions}>
                <a href={detailHref(lastSale)}>Ver detalle</a>
                <a className={styles.successPrimary} href="/pos">Nueva venta</a>
              </div>
            </section>
          ) : (
            <section className={styles.sheetWorkspace}>
              <section className={styles.captureColumn} aria-labelledby="checkout-method-title">
                <div className={styles.columnHeading}><span>Paso 1</span><h2 id="checkout-method-title">Método de pago</h2></div>
                <CheckoutPaymentMethods value={paymentMode} onChange={selectPaymentMode} disabled={busy} />

                {paymentMode === "mixed" ? (
                  <div className={styles.mixedControl}>
                    <span>Contribución actual</span>
                    <CheckoutPaymentMethods value={mixedMethod} onChange={(next) => { if (next !== "mixed") setMixedMethod(next); }} disabled={busy} compact />
                  </div>
                ) : null}

                <div className={styles.captureForm} data-method={captureMethod}>
                  {captureMethod === "cash" ? (
                    <CheckoutCashCalculator
                      targetCents={captureTargetCents}
                      receivedCents={captureTender.amountCents}
                      changeCents={view.changeCents}
                      onReceivedCents={(value) => updateAmount("cash", value)}
                      disabled={busy}
                    />
                  ) : (
                    <>
                      <label className={styles.field} htmlFor={`checkout-${captureMethod}-amount`}>
                        <span>Importe</span>
                        <span className={styles.moneyInput}>
                          <i aria-hidden="true">$</i>
                          <input id={`checkout-${captureMethod}-amount`} type="text" inputMode="decimal" autoComplete="off" value={amountDrafts[captureMethod]} onChange={(event) => updateAmountDraft(captureMethod, event.target.value)} placeholder="0.00" disabled={busy} />
                        </span>
                      </label>
                      <label className={styles.field} htmlFor={`checkout-${captureMethod}-reference`}>
                        <span>{captureMethod === "card" ? "Autorización" : "Referencia o folio"} <small>(opcional)</small></span>
                        <input id={`checkout-${captureMethod}-reference`} value={captureTender.reference} onChange={(event) => updateTender(captureMethod, { reference: event.target.value })} placeholder={captureMethod === "card" ? "Número de autorización" : "Referencia bancaria"} disabled={busy} />
                      </label>
                      <button className={styles.coverButton} type="button" onClick={() => updateAmount(captureMethod, captureTender.amountCents + view.remainingCents)} disabled={busy || view.remainingCents <= 0}>Cubrir saldo</button>
                    </>
                  )}
                </div>

                {paymentMode === "mixed" ? (
                  <>
                    <button className={styles.addContribution} type="button" onClick={addContribution} disabled={busy || captureTender.amountCents <= 0}>Agregar pago</button>
                    <div className={styles.contributions} aria-label="Aportaciones registradas">
                      {activeContributions.length ? activeContributions.map((tender) => (
                        <div className={styles.contributionRow} key={tender.method}>
                          <span><strong>{paymentMethodLabel(tender.method)}</strong><small>{tender.reference || "Sin referencia"}</small></span>
                          <b>{formatMoney(tender.amountCents)}</b>
                          <button type="button" onClick={() => removeContribution(tender.method)} disabled={busy} aria-label={`Eliminar aportación ${paymentMethodLabel(tender.method)}`}>Quitar</button>
                        </div>
                      )) : <p>Agrega la primera aportación.</p>}
                    </div>
                  </>
                ) : null}
              </section>

              <aside className={styles.reviewColumn} aria-labelledby="checkout-review-title">
                <CheckoutSummary lines={lines} />
                <section className={styles.amountSummary}>
                  <div className={styles.totalRow}><span>Total</span><strong id="checkout-review-title">{formatMoney(view.totalCents)}</strong></div>
                  <div><span>Pagado</span><b>{formatMoney(view.paidCents)}</b></div>
                  <div data-tone={view.remainingCents > 0 ? "warning" : "ok"}><span>Falta</span><b>{formatMoney(view.remainingCents)}</b></div>
                  <div data-tone={view.changeCents > 0 ? "ok" : "neutral"}><span>Cambio</span><b>{formatMoney(view.changeCents)}</b></div>
                </section>
                <div className={visibleError ? styles.validationError : view.canConfirm ? styles.validationReady : styles.validationMessage} role={visibleError ? "alert" : "status"}>
                  <AlertCircle aria-hidden="true" size={15} />
                  <span>{validationCopy}</span>
                </div>
                <button className={styles.confirmButton} type="button" onClick={() => void confirmPayment()} disabled={busy || !view.canConfirm || !gate.canCheckout || !lines.length}>
                  {busy ? <Loader2 className={styles.spinner} aria-hidden="true" size={19} /> : <CheckCircle2 aria-hidden="true" size={19} />}
                  <span>{busy ? "Procesando pago…" : "Confirmar pago"}</span>
                  <strong>{formatMoney(view.totalCents)}</strong>
                </button>
                <span id="checkout-validation" className={styles.visuallyHidden}>{validationCopy}</span>
              </aside>
            </section>
          )}
        </section>
      </div>
    </main>
  );
}

export const CheckoutWorkspace = CheckoutScreen;

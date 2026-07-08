"use client";

import { cva } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";
import { AlertTriangle, CheckCircle2, Clock3, Gem, Minus, Plus, ReceiptText, Save, Trash2, Undo2, WalletCards } from "lucide-react";
import { motion } from "motion/react";
import { twMerge } from "tailwind-merge";
import { PrismaLiquidAction } from "@components/tablet-visual-v2";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import type { HeldCart } from "@/lib/pos/held-carts";
import { getCartLineStockSignal, validateCartForCheckout } from "@/lib/pos/cart-engine";
import { resolveNextPackshotSrc, resolveProductPackshot } from "./pos-packshots";
import { usePrismaPackshotSkin } from "./use-prisma-packshot-skin";
import styles from "./pos.module.css";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(...inputs));
}



const ticketPanelChrome = cva(styles.posPremiumTicketPanel, {
  variants: {
    state: {
      ready: styles.posPremiumTicketReady,
      empty: styles.posPremiumTicketEmpty,
      error: styles.posPremiumTicketError
    }
  },
  defaultVariants: {
    state: "empty"
  }
});

function cartThumbClass(name: string) {
  const source = name.toLowerCase();
  if (source.includes("coca") || source.includes("refresco")) return styles.posPremiumCartThumbBottle;
  if (source.includes("agua") || source.includes("ciel")) return styles.posPremiumCartThumbBlue;
  if (source.includes("sabrita") || source.includes("papa")) return styles.posPremiumCartThumbBag;
  if (source.includes("lala") || source.includes("leche")) return styles.posPremiumCartThumbCarton;
  if (source.includes("nesc")) return styles.posPremiumCartThumbJar;
  if (source.includes("bimbo") || source.includes("pan")) return styles.posPremiumCartThumbBread;
  return styles.posPremiumCartThumbGeneric;
}

function heldCartTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sin hora";
  return new Intl.DateTimeFormat("es-MX", { hour: "2-digit", minute: "2-digit" }).format(date);
}

function stockChipClass(tone: "ok" | "warn" | "danger") {
  if (tone === "danger") return `${styles.lineStockChip} ${styles.lineStockDanger}`;
  if (tone === "warn") return `${styles.lineStockChip} ${styles.lineStockWarn}`;
  return `${styles.lineStockChip} ${styles.lineStockOk}`;
}

export function PosTicketPanel({
  lines,
  heldCarts = [],
  checkoutBusy,
  checkoutError,
  checkoutReason,
  canCheckout = true,
  checkoutBlockedReason,
  onIncrement,
  onDecrement,
  onRemove,
  onClear,
  onHold,
  onRestoreHeldCart,
  onDiscardHeldCart,
  onCheckout
}: {
  lines: CartLine[];
  heldCarts?: HeldCart[];
  checkoutBusy?: boolean;
  checkoutError?: unknown;
  checkoutReason?: string;
  canCheckout?: boolean;
  checkoutBlockedReason?: string;
  onIncrement: (productId: string) => void;
  onDecrement: (productId: string) => void;
  onRemove: (productId: string) => void;
  onClear: () => void;
  onHold: () => void;
  onRestoreHeldCart: (heldCartId: string) => void;
  onDiscardHeldCart: (heldCartId: string) => void;
  onCheckout: () => void;
}) {
  const qty = cartTotalQty(lines);
  const total = cartTotalCents(lines);
  const checkoutDisabled = !canCheckout || !lines.length || Boolean(checkoutBusy);
  const readiness = validateCartForCheckout(lines);
  const checkoutReady = canCheckout && readiness.ready;
  const diagnosticCopy = !canCheckout ? checkoutBlockedReason || "Abre turno antes de cobrar." : checkoutError ? "Revisa el cobro antes de continuar." : checkoutReason || readiness.reason;
  const packshotSkin = usePrismaPackshotSkin();
  const ticketState = checkoutError ? "error" : lines.length ? "ready" : "empty";

  return (
    <motion.aside
      className={ticketPanelChrome({ state: ticketState })}
      aria-label="Ticket actual"
      initial={{ opacity: 0, x: 18 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.28, delay: 0.04, ease: [0.22, 1, 0.36, 1] }}
      data-prisma-component="CartPanel"
      data-prisma-panel="tablet.pos.cart-panel"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-zone="tablet-pos-ticket-panel"
      data-prisma-role="sale-ticket"
      data-prisma-priority="primary"
      data-prisma-state={checkoutError ? "error" : lines.length ? "ready" : "empty"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-cart"

      data-surface="tablet"
      data-screen="pos"
      data-zone="checkout-rail"
      data-panel="pos-ticket-panel"
      data-target="pos-ticket-panel"
      data-kind="panel"
      data-role="sale-ticket">
      <header className={styles.posPremiumTicketHeader} data-prisma-component="CartHeader"
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-ticket-panel"
        data-target="pos-ticket-panel-ticket-126"
        data-kind="ticket"
        data-role="ticket-context"
      >
        <div
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-ticket-panel"
          data-target="pos-ticket-panel-ticket-127"
          data-kind="ticket"
          data-role="ticket-context"
        >
          <span
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-ticket-panel"
            data-target="pos-ticket-panel-ticket-128"
            data-kind="ticket"
            data-role="ticket-context"
          ><ReceiptText aria-hidden="true" size={15} /> Ticket actual</span>
          <h2 data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-h2-1" data-kind="panel" data-role="panel">{qty} piezas</h2>
        </div>
        <motion.button
          className={styles.posPremiumTicketUtilityButton}
          type="button"
          onClick={onClear}
          disabled={!lines.length || checkoutBusy}
          whileTap={!lines.length || checkoutBusy ? undefined : { scale: 0.98 }}
          whileHover={!lines.length || checkoutBusy ? undefined : { y: -1 }}
          data-prisma-component="IconButton"
        >
          <Undo2 aria-hidden="true" size={16} />
          Cancelar venta
        </motion.button>
      </header>

      <div className={styles.posPremiumTicketLines}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-ticket-panel"
        data-target="pos-ticket-panel-ticket-145"
        data-kind="ticket"
        data-role="ticket-context"
      >
        {!lines.length ? (
          <div className={styles.posPremiumEmptyTicket} data-prisma-component="EmptyState" data-prisma-zone="tablet-pos-empty-state" data-prisma-state="empty" data-prisma-qa="tablet-qa-disabled"
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout-rail"
            data-panel="empty-ticket-state"
            data-target="empty-ticket-state"
            data-kind="panel"
            data-role="empty-state">
            <WalletCards aria-hidden="true" size={30} />
            <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-strong-2" data-kind="panel" data-role="panel">Agrega productos para cobrar</strong>
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-3" data-kind="panel" data-role="panel">El total y el botón de cobro se activan cuando el ticket tiene productos.</span>
          </div>
        ) : (
          lines.map((line) => {
            const packshot = resolveProductPackshot(line.product.name, line.product.category, line.product.sku, { skin: packshotSkin });
            const stockSignal = getCartLineStockSignal(line);
            return (
              <motion.article
                key={line.product.id}
                className={styles.posPremiumTicketLine}
                data-prisma-component="CartItemRow"
                data-prisma-zone="tablet-pos-ticket-line"
                data-prisma-state="ready"
                data-prisma-motion="hover-lift"
                data-prisma-effect="product-added-echo pressed-depth"
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -2 }}
                transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}

                data-surface="tablet"
                data-screen="pos"
                data-zone="checkout-rail"
                data-panel="cart-line-list"
                data-target="cart-line-row"
                data-kind="table"
                data-role="sale-line">
                <span
                  className={cn(
                    styles.posPremiumCartThumb,
                    packshot ? styles.posPremiumCartThumbPackshot : cartThumbClass(line.product.name),
                    packshot ? styles[`cartThumbPackshot_${packshot.kind}`] : ""
                  )}
                  data-prisma-packshot-host
                  aria-hidden="true"
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-ticket-panel"
                  data-target="pos-ticket-panel-ticket-185"
                  data-kind="ticket"
                  data-role="ticket-context"
                >
                  {packshot ? (
                    <>
                      <img
                        src={packshot.src}
                        alt=""
                        loading="lazy"
                        draggable={false}
                        onError={(event: { currentTarget: HTMLImageElement }) => {
                          const nextSrc = resolveNextPackshotSrc(event.currentTarget.src, packshot.fallbackSrcs);
                          if (nextSrc) {
                            event.currentTarget.src = nextSrc;
                            return;
                          }
                          event.currentTarget.closest("[data-prisma-packshot-host]")?.setAttribute("data-packshot-error", "true");
                        }}
                        onLoad={(event: { currentTarget: HTMLImageElement }) => {
                          event.currentTarget.closest("[data-prisma-packshot-host]")?.removeAttribute("data-packshot-error");
                        }}
                      />
                      <span className={styles.posPremiumCartThumbFallback}
                        data-surface="tablet"
                        data-screen="pos"
                        data-zone="pos"
                        data-panel="pos-ticket-panel"
                        data-target="pos-ticket-panel-ticket-213"
                        data-kind="ticket"
                        data-role="ticket-context"
                      />
                    </>
                  ) : (
                    <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-4" data-kind="panel" data-role="panel" />
                  )}
                </span>
                <div className={styles.posPremiumTicketLineText}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-ticket-panel"
                  data-target="pos-ticket-panel-ticket-219"
                  data-kind="ticket"
                  data-role="ticket-context"
                >
                  <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-strong-5" data-kind="panel" data-role="panel">{line.product.name}</strong>
                  <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-6" data-kind="panel" data-role="panel">
                    {line.product.sku} · {formatMoney(line.product.priceCents)}
                  </span>
                  <small className={stockChipClass(stockSignal.tone)}>{stockSignal.label}</small>
                </div>
                <div className={styles.posPremiumStepper} data-prisma-component="QuantityStepper" data-prisma-role="secondary-action" data-prisma-motion="press-feedback"
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="checkout-rail"
                  data-panel="quantity-stepper"
                  data-target="quantity-stepper"
                  data-kind="button"
                  data-role="quantity-control">
                  <button type="button" aria-label={`Restar ${line.product.name}`}
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="pos"
                    data-panel="pos-ticket-panel"
                    data-target="pos-ticket-panel-button-234"
                    data-kind="button"
                    data-role="ticket-context"
                    onClick={() => onDecrement(line.product.id)} disabled={!canCheckout || checkoutBusy}
                  >
                    <Minus aria-hidden="true" size={15} />
                  </button>
                  <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-strong-7" data-kind="panel" data-role="panel">{line.qty}</strong>
                  <button type="button" aria-label={`Sumar ${line.product.name}`}
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="pos"
                    data-panel="pos-ticket-panel"
                    data-target="pos-ticket-panel-button-238"
                    data-kind="button"
                    data-role="ticket-context"
                    onClick={() => onIncrement(line.product.id)} disabled={!canCheckout || checkoutBusy}
                  >
                    <Plus aria-hidden="true" size={15} />
                  </button>
                </div>
                <strong className={styles.posPremiumLineTotal}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="checkout-rail"
                  data-panel="cart-line-list"
                  data-target="line-total"
                  data-kind="price"
                  data-role="line-total">{formatMoney(line.product.priceCents * line.qty)}</strong>
                <button className={styles.posPremiumRemoveButton} type="button" aria-label={`Quitar ${line.product.name}`}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-ticket-panel"
                  data-target="pos-ticket-panel-button-250"
                  data-kind="button"
                  data-role="ticket-context"
                  onClick={() => onRemove(line.product.id)} disabled={!canCheckout || checkoutBusy}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="checkout-rail"
                  data-panel="cart-line-list"
                  data-target="remove-line-button"
                  data-kind="button"
                  data-role="secondary-action">
                  <Trash2 aria-hidden="true" size={16} />
                </button>
              </motion.article>
            );
          })
        )}
      </div>

      <div className={checkoutReady ? styles.posPremiumDiagnosticOk : styles.posPremiumDiagnosticWarn} aria-live="polite" data-prisma-component="CheckoutDiagnostic" data-prisma-panel="tablet.pos.checkout-diagnostic" data-prisma-surface="tablet" data-prisma-route="/pos" data-prisma-role="status-surface" data-prisma-state={checkoutReady ? "ready" : "disabled"}
        data-surface="tablet"
        data-screen="pos"
        data-zone="checkout-rail"
        data-panel="checkout-diagnostic"
        data-target="checkout-diagnostic"
        data-kind="badge"
        data-role="state-indicator">
        <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-strong-8" data-kind="panel" data-role="panel">{checkoutReady ? <CheckCircle2 aria-hidden="true" size={16} /> : <Clock3 aria-hidden="true" size={16} />} {checkoutReady ? "Listo para cobrar" : "Prepara el cobro"}</strong>
        <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-9" data-kind="panel" data-role="panel">{diagnosticCopy}</span>
      </div>

      <section className={styles.posPremiumCheckoutStack} aria-label="Checkout" data-prisma-zone="tablet-pos-checkout-stack" data-prisma-role="sale-total"
        data-surface="tablet"
        data-screen="pos"
        data-zone="checkout-rail"
        data-panel="checkout-stack"
        data-target="checkout-stack"
        data-kind="panel"
        data-role="checkout-summary">
        <div className={styles.posPremiumTotalsBreakdown} aria-label="Resumen del ticket" data-prisma-zone="tablet-pos-total-area" data-prisma-role="sale-total"
          data-surface="tablet"
          data-screen="pos"
          data-zone="checkout-rail"
          data-panel="totals-breakdown"
          data-target="totals-breakdown"
          data-kind="table"
          data-role="audit-surface">
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-10" data-kind="panel" data-role="panel">Subtotal</span>
          <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-strong-11" data-kind="panel" data-role="panel">{formatMoney(total)}</strong>
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-12" data-kind="panel" data-role="panel">Impuestos</span>
          <strong>Incluidos</strong>
        </div>

        <div className={styles.posPremiumTicketTotal} data-prisma-component="TotalsSummary" data-prisma-zone="tablet-pos-total-area" data-prisma-role="sale-total" data-prisma-priority="primary" data-prisma-state={lines.length ? "ready" : "empty"}
          data-surface="tablet"
          data-screen="pos"
          data-zone="checkout-rail"
          data-panel="ticket-total-panel"
          data-target="ticket-total-display"
          data-kind="price"
          data-role="primary-total">
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-13" data-kind="panel" data-role="panel">Total a cobrar</span>
          <strong data-total-value="true"
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-ticket-panel"
            data-target="pos-ticket-panel-price-309"
            data-kind="price"
            data-role="financial-control"
          >{formatMoney(total)}</strong>
        </div>

        {checkoutError ? <div className={styles.posPremiumInlineError} data-prisma-zone="tablet-pos-error-state" data-prisma-state="error" data-prisma-motion="error-feedback"
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout-rail"
            data-panel="checkout-inline-error"
            data-target="checkout-inline-error"
            data-kind="badge"
            data-role="status-alert"><AlertTriangle aria-hidden="true" size={16} /> Revisa el cobro antes de continuar.</div> : null}

        <PrismaLiquidAction
          className={styles.cobrarReferenceButton}
          type="button"
          id="prisma-cobrar-prismplate-button"
          disabled={checkoutDisabled}
          aria-disabled={checkoutDisabled}
          aria-label={!canCheckout ? "Abrir turno antes de cobrar" : checkoutBusy ? "Cobro en proceso" : "Abrir cobro"}
          icon={<Gem aria-hidden="true" size={24} strokeWidth={2.15} />}
          amount={formatMoney(total)}
          status={checkoutDisabled ? "disabled" : checkoutBusy ? "loading" : "ready"}
          sublabel={checkoutReady ? "Listo para cerrar" : "Revisar ticket"}
          fullWidth
          data-prisma-component="CheckoutButton"
          data-prisma-effect="liquid-glow pressed-depth ticket-total-pulse focus-halo"
          data-prisma-zone="tablet-pos-cobrar-cta"
          data-prisma-role="primary-action"
          data-prisma-material="visual-surface-v2-liquid"
          data-prisma-priority={checkoutDisabled ? "passive" : "primary"}
          data-prisma-motion={checkoutDisabled ? "reduced-motion-safe" : "press-feedback"}
          data-prisma-state={checkoutDisabled ? "disabled" : checkoutBusy ? "loading" : "ready"}
          data-prisma-qa={checkoutDisabled ? "tablet-qa-disabled" : "tablet-qa-cobrar"}
          data-prisma-visual-v2="PRISMA_SOFTGLASS_TERMINAL_V2"
          onClick={onCheckout}
        >
          {!canCheckout ? "Abrir turno" : checkoutBusy ? "Cobrando" : "Cobrar"}
        </PrismaLiquidAction>
      </section>
      <details className={styles.posPremiumTicketOptions} data-prisma-role="secondary-action"
        data-surface="tablet"
        data-screen="pos"
        data-zone="checkout-rail"
        data-panel="ticket-options"
        data-target="ticket-options"
        data-kind="panel"
        data-role="secondary-actions">
        <summary>Opciones de ticket</summary>
        <div className={styles.posPremiumSecondaryCheckoutActions} aria-label="Acciones secundarias"
          data-surface="tablet"
          data-screen="pos"
          data-zone="checkout"
          data-panel="pos-ticket-panel"
          data-target="pos-ticket-panel-acciones-secundarias-357"
          data-kind="button"
          data-role="ticket-context"
        >
          <button type="button" onClick={onHold} disabled={!canCheckout || !lines.length || checkoutBusy} data-prisma-component="HoldCartButton"
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout"
            data-panel="pos-ticket-panel"
            data-target="pos-ticket-panel-button-358"
            data-kind="button"
            data-role="ticket-context"
          >
            <Save aria-hidden="true" size={18} />
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-14" data-kind="panel" data-role="panel">Guardar ticket</span>
          </button>
          <button type="button" onClick={onClear} disabled={!lines.length || checkoutBusy} data-prisma-component="SecondaryActionCard"
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout"
            data-panel="pos-ticket-panel"
            data-target="pos-ticket-panel-button-362"
            data-kind="button"
            data-role="ticket-context"
          >
            <Undo2 aria-hidden="true" size={18} />
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-15" data-kind="panel" data-role="panel">Cancelar venta</span>
          </button>
        </div>
      </details>

      {heldCarts.length ? (
        <details className={styles.heldCartShelf} aria-label="Tickets en espera" data-prisma-component="HeldCartShelf"
          data-surface="tablet"
          data-screen="pos"
          data-zone="checkout-rail"
          data-panel="held-cart-shelf"
          data-target="held-cart-shelf"
          data-kind="panel"
          data-role="hold-cart-shelf">
          <summary>
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-16" data-kind="panel" data-role="panel">Tickets en espera</span>
            <strong>{heldCarts.length}</strong>
          </summary>
          <div className={styles.heldCartList}
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-ticket-panel"
            data-target="pos-ticket-panel-ticket-382"
            data-kind="ticket"
            data-role="ticket-context"
          >
            {heldCarts.slice(0, 4).map((heldCart, index) => (
              <article key={heldCart.id} className={styles.heldCartCard} data-prisma-component="HeldCartCard"
                data-surface="tablet"
                data-screen="pos"
                data-zone="checkout-rail"
                data-panel="held-cart-shelf"
                data-target="held-cart-card"
                data-kind="panel"
                data-role="held-cart-item">
                <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-div-17" data-kind="panel" data-role="container">
                  <strong>{heldCart.label}</strong>
                  <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_ticket_panel" data-target="pos-ticket-panel-span-18" data-kind="panel" data-role="panel">{heldCartTime(heldCart.createdAt)} · {heldCart.totalQty} pzas · {formatMoney(heldCart.totalCents)}</span>
                </div>
                <div className={styles.heldCartActions}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-ticket-panel"
                  data-target="pos-ticket-panel-button-396"
                  data-kind="button"
                  data-role="ticket-context"
                >
                  <button type="button"
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="pos"
                    data-panel="pos-ticket-panel"
                    data-target="pos-ticket-panel-button-397"
                    data-kind="button"
                    data-role="ticket-context"
                    onClick={() => onRestoreHeldCart(heldCart.id)} disabled={!canCheckout || checkoutBusy || lines.length > 0} aria-label={`Recuperar ${heldCart.label}`}
                  >
                    Usar
                  </button>
                  <button type="button"
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="pos"
                    data-panel="pos-ticket-panel"
                    data-target="pos-ticket-panel-button-400"
                    data-kind="button"
                    data-role="ticket-context"
                    onClick={() => onDiscardHeldCart(heldCart.id)} disabled={checkoutBusy} aria-label={`Descartar ${heldCart.label}`}
                  >
                    Descartar
                  </button>
                </div>
              </article>
            ))}
          </div>
        </details>
      ) : null}
    </motion.aside>
  );
}

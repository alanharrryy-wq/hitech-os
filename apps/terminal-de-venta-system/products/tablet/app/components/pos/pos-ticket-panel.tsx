"use client";

import { AlertTriangle, CheckCircle2, Clock3, Gem, Minus, Plus, ReceiptText, Save, Trash2, Undo2, WalletCards } from "lucide-react";
import { motion } from "motion/react";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import type { HeldCart } from "@/lib/pos/held-carts";
import { getCartLineStockSignal, validateCartForCheckout } from "@/lib/pos/cart-engine";
import { resolveNextPackshotSrc, resolveProductPackshot } from "./pos-packshots";
import { usePrismaPackshotSkin } from "./use-prisma-packshot-skin";
import styles from "./pos.module.css";

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
  const diagnosticCopy = !canCheckout
    ? checkoutBlockedReason || "Abre turno antes de cobrar."
    : checkoutError
      ? "Revisa el cobro antes de continuar."
      : checkoutReason || readiness.reason;
  const packshotSkin = usePrismaPackshotSkin();
  const ticketStateClass = checkoutError
    ? styles.posPremiumTicketError
    : lines.length
      ? styles.posPremiumTicketReady
      : styles.posPremiumTicketEmpty;

  return (
    <motion.aside
      className={`${styles.posPremiumTicketPanel} ${ticketStateClass}`}
      aria-label="Ticket actual"
      initial={{ opacity: 0, x: 10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
      data-prisma-component="CartPanel"
      data-prisma-panel="tablet.pos.cart-panel"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-zone="tablet-pos-ticket-panel"
      data-prisma-role="sale-ticket"
      data-prisma-priority="primary"
      data-prisma-state={checkoutError ? "error" : lines.length ? "ready" : "empty"}
      data-prisma-qa="tablet-qa-cart"
      data-surface="tablet"
      data-screen="pos"
      data-zone="checkout-rail"
      data-panel="pos-ticket-panel"
      data-target="pos-ticket-panel"
      data-kind="panel"
      data-role="sale-ticket"
    >
      <header className={styles.posPremiumTicketHeader} data-prisma-component="CartHeader">
        <div>
          <span><ReceiptText aria-hidden="true" size={17} /> Ticket</span>
          <h2>{qty ? `${qty} ${qty === 1 ? "pieza" : "piezas"}` : "Sin productos"}</h2>
        </div>
        <button
          className={styles.posPremiumTicketUtilityButton}
          type="button"
          onClick={onClear}
          disabled={!lines.length || checkoutBusy}
          data-prisma-component="IconButton"
        >
          <Undo2 aria-hidden="true" size={17} />
          <span>Cancelar</span>
        </button>
      </header>

      <div className={styles.posPremiumTicketLines} data-target="cart-line-list" data-role="ticket-context">
        {!lines.length ? (
          <div className={styles.posPremiumEmptyTicket} data-prisma-component="EmptyState" data-prisma-state="empty" data-prisma-qa="tablet-qa-disabled">
            <WalletCards aria-hidden="true" size={30} />
            <strong>Tu ticket está vacío</strong>
            <span>Agrega productos desde el catálogo.</span>
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
                data-target="cart-line-row"
                data-role="sale-line"
                layout
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.16 }}
              >
                <span
                  className={`${styles.posPremiumCartThumb} ${packshot ? styles.posPremiumCartThumbPackshot : cartThumbClass(line.product.name)} ${packshot ? styles[`cartThumbPackshot_${packshot.kind}`] : ""}`}
                  data-prisma-packshot-host
                  aria-hidden="true"
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
                      <span className={styles.posPremiumCartThumbFallback} />
                    </>
                  ) : (
                    <span />
                  )}
                </span>

                <div className={styles.posPremiumTicketLineText}>
                  <strong>{line.product.name}</strong>
                  <span>{formatMoney(line.product.priceCents)} c/u</span>
                  <small className={stockChipClass(stockSignal.tone)}>{stockSignal.label}</small>
                </div>

                <button
                  className={styles.posPremiumRemoveButton}
                  type="button"
                  aria-label={`Quitar ${line.product.name}`}
                  onClick={() => onRemove(line.product.id)}
                  disabled={!canCheckout || checkoutBusy}
                  data-target="remove-line-button"
                  data-role="secondary-action"
                >
                  <Trash2 aria-hidden="true" size={16} />
                </button>

                <div className={styles.posPremiumLineActions}>
                  <div className={styles.posPremiumStepper} data-prisma-component="QuantityStepper" data-role="quantity-control">
                    <button type="button" aria-label={`Restar ${line.product.name}`} onClick={() => onDecrement(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                      <Minus aria-hidden="true" size={15} />
                    </button>
                    <strong>{line.qty}</strong>
                    <button type="button" aria-label={`Sumar ${line.product.name}`} onClick={() => onIncrement(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                      <Plus aria-hidden="true" size={15} />
                    </button>
                  </div>
                  <strong className={styles.posPremiumLineTotal} data-target="line-total" data-role="line-total">
                    {formatMoney(line.product.priceCents * line.qty)}
                  </strong>
                </div>
              </motion.article>
            );
          })
        )}
      </div>

      <section className={styles.posPremiumCheckoutStack} aria-label="Checkout" data-prisma-zone="tablet-pos-checkout-stack" data-prisma-role="sale-total">
        <div
          className={checkoutReady ? styles.posPremiumDiagnosticOk : styles.posPremiumDiagnosticWarn}
          aria-live="polite"
          data-prisma-component="CheckoutDiagnostic"
          data-prisma-state={checkoutReady ? "ready" : "disabled"}
        >
          {checkoutReady ? <CheckCircle2 aria-hidden="true" size={15} /> : <Clock3 aria-hidden="true" size={15} />}
          <span>{diagnosticCopy}</span>
        </div>

        <div className={styles.posPremiumTotalsBreakdown} aria-label="Resumen del ticket">
          <span>Subtotal</span>
          <strong>{formatMoney(total)}</strong>
          <span>Impuestos</span>
          <strong>Incluidos</strong>
        </div>

        <div className={styles.posPremiumTicketTotal} data-prisma-component="TotalsSummary" data-prisma-state={lines.length ? "ready" : "empty"}>
          <span>Total</span>
          <strong data-total-value="true">{formatMoney(total)}</strong>
        </div>

        {checkoutError ? (
          <div className={styles.posPremiumInlineError} data-prisma-state="error">
            <AlertTriangle aria-hidden="true" size={16} /> Revisa el cobro antes de continuar.
          </div>
        ) : null}

        <button
          className={styles.cobrarReferenceButton}
          type="button"
          id="prisma-cobrar-prismplate-button"
          disabled={checkoutDisabled}
          aria-disabled={checkoutDisabled}
          aria-label={!canCheckout ? "Abrir turno antes de cobrar" : checkoutBusy ? "Cobro en proceso" : "Abrir cobro"}
          data-prisma-component="CheckoutButton"
          data-prisma-zone="tablet-pos-cobrar-cta"
          data-prisma-role="primary-action"
          data-prisma-priority={checkoutDisabled ? "passive" : "primary"}
          data-prisma-state={checkoutDisabled ? "disabled" : checkoutBusy ? "loading" : "ready"}
          data-prisma-qa={checkoutDisabled ? "tablet-qa-disabled" : "tablet-qa-cobrar"}
          onClick={onCheckout}
        >
          <span className={styles.cobrarIcon}><Gem aria-hidden="true" size={21} /></span>
          <span className={styles.cobrarCopy}>
            <strong>{!canCheckout ? "Abrir turno" : checkoutBusy ? "Cobrando" : "Cobrar"}</strong>
            <small>{checkoutReady ? "Listo para cerrar" : "Revisar ticket"}</small>
          </span>
          <strong className={styles.cobrarAmount}>{formatMoney(total)}</strong>
        </button>

        <details className={styles.posPremiumTicketOptions} data-prisma-role="secondary-action">
          <summary>Opciones de ticket</summary>
          <div className={styles.posPremiumSecondaryCheckoutActions} aria-label="Acciones secundarias">
            <button type="button" onClick={onHold} disabled={!canCheckout || !lines.length || checkoutBusy} data-prisma-component="HoldCartButton">
              <Save aria-hidden="true" size={17} /> Suspender
            </button>
            <button type="button" onClick={onClear} disabled={!lines.length || checkoutBusy}>
              <Undo2 aria-hidden="true" size={17} /> Vaciar carrito
            </button>
          </div>
        </details>

        {heldCarts.length ? (
          <details className={styles.heldCartShelf} aria-label="Tickets en espera" data-prisma-component="HeldCartShelf">
            <summary>Tickets en espera <strong>{heldCarts.length}</strong></summary>
            <div className={styles.heldCartList}>
              {heldCarts.slice(0, 4).map((heldCart) => (
                <article key={heldCart.id} className={styles.heldCartCard} data-prisma-component="HeldCartCard">
                  <div>
                    <strong>{heldCart.label}</strong>
                    <span>{heldCartTime(heldCart.createdAt)} · {heldCart.totalQty} pzas · {formatMoney(heldCart.totalCents)}</span>
                  </div>
                  <div className={styles.heldCartActions}>
                    <button type="button" onClick={() => onRestoreHeldCart(heldCart.id)} disabled={Boolean(checkoutBusy)}>Reanudar</button>
                    <button type="button" onClick={() => onDiscardHeldCart(heldCart.id)} disabled={Boolean(checkoutBusy)} aria-label={`Eliminar ${heldCart.label}`}>
                      <Trash2 aria-hidden="true" size={15} />
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </details>
        ) : null}
      </section>
    </motion.aside>
  );
}

"use client";

import { cva } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";
import { AlertTriangle, CheckCircle2, Clock3, Minus, Plus, ReceiptText, Save, Trash2, Undo2, WalletCards } from "lucide-react";
import { motion } from "motion/react";
import { twMerge } from "tailwind-merge";
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

const checkoutCtaChrome = cva(styles.posPremiumCheckoutCta, {
  variants: {
    disabled: {
      true: styles.posPremiumCheckoutCtaDisabled,
      false: styles.posPremiumCheckoutCtaReady
    },
    busy: {
      true: styles.posPremiumCheckoutCtaBusy,
      false: null
    }
  },
  defaultVariants: {
    disabled: false,
    busy: false
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
      data-prisma-zone="tablet-pos-ticket-panel"
      data-prisma-role="sale-ticket"
      data-prisma-priority="primary"
      data-prisma-state={checkoutError ? "error" : lines.length ? "ready" : "empty"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-cart"
    >
      <header className={styles.posPremiumTicketHeader} data-prisma-component="CartHeader">
        <div>
          <span><ReceiptText aria-hidden="true" size={15} /> Ticket activo</span>
          <h2>{qty} piezas</h2>
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

      <div className={styles.posPremiumTicketLines}>
        {!lines.length ? (
          <div className={styles.posPremiumEmptyTicket} data-prisma-component="EmptyState" data-prisma-zone="tablet-pos-empty-state" data-prisma-state="empty" data-prisma-qa="tablet-qa-disabled">
            <WalletCards aria-hidden="true" size={30} />
            <strong>Agrega productos para cobrar</strong>
            <span>El total y el botón de cobro se activan cuando el ticket tiene productos.</span>
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
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -2 }}
                transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
              >
                <span
                  className={cn(
                    styles.posPremiumCartThumb,
                    packshot ? styles.posPremiumCartThumbPackshot : cartThumbClass(line.product.name),
                    packshot ? styles[`cartThumbPackshot_${packshot.kind}`] : ""
                  )}
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
                  <span>
                    {line.product.sku} · {formatMoney(line.product.priceCents)}
                  </span>
                  <small className={stockChipClass(stockSignal.tone)}>{stockSignal.label}</small>
                </div>
                <div className={styles.posPremiumStepper} data-prisma-component="QuantityStepper" data-prisma-role="secondary-action" data-prisma-motion="press-feedback">
                  <button type="button" aria-label={`Restar ${line.product.name}`} onClick={() => onDecrement(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                    <Minus aria-hidden="true" size={15} />
                  </button>
                  <strong>{line.qty}</strong>
                  <button type="button" aria-label={`Sumar ${line.product.name}`} onClick={() => onIncrement(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                    <Plus aria-hidden="true" size={15} />
                  </button>
                </div>
                <strong className={styles.posPremiumLineTotal}>{formatMoney(line.product.priceCents * line.qty)}</strong>
                <button className={styles.posPremiumRemoveButton} type="button" aria-label={`Quitar ${line.product.name}`} onClick={() => onRemove(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                  <Trash2 aria-hidden="true" size={16} />
                </button>
              </motion.article>
            );
          })
        )}
      </div>

      <div className={checkoutReady ? styles.posPremiumDiagnosticOk : styles.posPremiumDiagnosticWarn} aria-live="polite" data-prisma-component="CheckoutDiagnostic" data-prisma-role="status-surface" data-prisma-state={checkoutReady ? "ready" : "disabled"}>
        <strong>{checkoutReady ? <CheckCircle2 aria-hidden="true" size={16} /> : <Clock3 aria-hidden="true" size={16} />} {checkoutReady ? "Listo para cobrar" : "Prepara el cobro"}</strong>
        <span>{diagnosticCopy}</span>
      </div>

      <div className={styles.posPremiumTotalsBreakdown} aria-label="Resumen del ticket" data-prisma-zone="tablet-pos-total-area" data-prisma-role="sale-total">
        <span>Subtotal</span>
        <strong>{formatMoney(total)}</strong>
        <span>Impuestos</span>
        <strong>Incluidos</strong>
      </div>

      <div className={styles.posPremiumTicketTotal} data-prisma-component="TotalsSummary" data-prisma-zone="tablet-pos-total-area" data-prisma-role="sale-total" data-prisma-priority="primary" data-prisma-state={lines.length ? "ready" : "empty"}>
        <span>Total a cobrar</span>
        <strong data-total-value="true">{formatMoney(total)}</strong>
      </div>

      {checkoutError ? <div className={styles.posPremiumInlineError} data-prisma-zone="tablet-pos-error-state" data-prisma-state="error" data-prisma-motion="error-feedback"><AlertTriangle aria-hidden="true" size={16} /> Revisa el cobro antes de continuar.</div> : null}

      <motion.button
        className={checkoutCtaChrome({ disabled: checkoutDisabled, busy: Boolean(checkoutBusy) })}
        type="button"
        disabled={checkoutDisabled}
        aria-disabled={checkoutDisabled}
        whileTap={checkoutDisabled ? undefined : { scale: 0.982 }}
        whileHover={checkoutDisabled ? undefined : { y: -2, boxShadow: "0 30px 64px rgba(8, 122, 62, 0.36), 0 0 44px rgba(58, 237, 154, 0.30)" }}
        data-prisma-component="CheckoutButton"
        data-prisma-zone="tablet-pos-cobrar-cta"
        data-prisma-role="primary-action"
        data-prisma-priority={checkoutDisabled ? "passive" : "primary"}
        data-prisma-motion={checkoutDisabled ? "reduced-motion-safe" : "press-feedback"}
        data-prisma-state={checkoutDisabled ? "disabled" : checkoutBusy ? "loading" : "ready"}
        data-prisma-qa={checkoutDisabled ? "tablet-qa-disabled" : "tablet-qa-cobrar"}
        data-prisma-legacy-class={checkoutDisabled ? "checkoutLinkDisabled" : "checkoutLink"}
        onClick={onCheckout}
      >
        <span className={styles.visuallyHidden}>Abrir cobro</span>
        <span>{!canCheckout ? "ABRIR TURNO" : checkoutBusy ? "COBRANDO" : "COBRAR"}</span>
        <strong>Tocar</strong>
      </motion.button>
      <div className={styles.posPremiumSecondaryCheckoutActions} aria-label="Acciones secundarias" data-prisma-role="secondary-action">
        <button type="button" disabled data-prisma-component="SecondaryActionCard">
          <ReceiptText aria-hidden="true" size={18} />
          <span>Reembolso</span>
          <small>Pronto</small>
        </button>
        <button type="button" onClick={onHold} disabled={!canCheckout || !lines.length || checkoutBusy} data-prisma-component="HoldCartButton">
          <Save aria-hidden="true" size={18} />
          <span>Guardar</span>
          <small>Guardar</small>
        </button>
        <button type="button" onClick={onClear} disabled={!lines.length || checkoutBusy} data-prisma-component="SecondaryActionCard">
          <Undo2 aria-hidden="true" size={18} />
          <span>Cancelar venta</span>
          <small>Limpiar</small>
        </button>
      </div>

      {heldCarts.length ? (
        <section className={styles.heldCartShelf} aria-label="Tickets en espera" data-prisma-component="HeldCartShelf">
          <header>
            <span>Tickets guardados</span>
            <strong>{heldCarts.length}</strong>
          </header>
          <div className={styles.heldCartList}>
            {heldCarts.slice(0, 4).map((heldCart, index) => (
              <article key={heldCart.id} className={styles.heldCartCard} data-prisma-component="HeldCartCard">
                <div>
                  <strong>{heldCart.label}</strong>
                  <span>{heldCartTime(heldCart.createdAt)} · {heldCart.totalQty} pzas · {formatMoney(heldCart.totalCents)}</span>
                </div>
                <div className={styles.heldCartActions}>
                  <button type="button" onClick={() => onRestoreHeldCart(heldCart.id)} disabled={!canCheckout || checkoutBusy || lines.length > 0} aria-label={`Recuperar ${heldCart.label}`}>
                    Usar
                  </button>
                  <button type="button" onClick={() => onDiscardHeldCart(heldCart.id)} disabled={checkoutBusy} aria-label={`Descartar ${heldCart.label}`}>
                    Descartar
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </motion.aside>
  );
}

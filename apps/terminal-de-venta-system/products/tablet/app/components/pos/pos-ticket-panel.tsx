"use client";

import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import type { HeldCart } from "@/lib/pos/held-carts";
import { getCartLineStockSignal, validateCartForCheckout } from "@/lib/pos/cart-engine";
import { resolveNextPackshotSrc, resolveProductPackshot } from "./pos-packshots";
import { usePrismaPackshotSkin } from "./use-prisma-packshot-skin";
import styles from "./pos.module.css";

function cartThumbClass(name: string) {
  const source = name.toLowerCase();
  if (source.includes("coca") || source.includes("refresco")) return styles.cartThumbBottle;
  if (source.includes("agua") || source.includes("ciel")) return styles.cartThumbBlue;
  if (source.includes("sabrita") || source.includes("papa")) return styles.cartThumbBag;
  if (source.includes("lala") || source.includes("leche")) return styles.cartThumbCarton;
  if (source.includes("nesc")) return styles.cartThumbJar;
  if (source.includes("bimbo") || source.includes("pan")) return styles.cartThumbBread;
  return styles.cartThumbGeneric;
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

  return (
    <aside
      className={styles.ticketPanel}
      aria-label="Ticket actual"
      data-prisma-component="CartPanel"
      data-prisma-zone="tablet-pos-ticket-panel"
      data-prisma-role="sale-ticket"
      data-prisma-priority="primary"
      data-prisma-state={checkoutError ? "error" : lines.length ? "ready" : "empty"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-cart"
    >
      <header className={styles.ticketHeader} data-prisma-component="CartHeader">
        <div>
          <span>Ticket activo</span>
          <h2>{qty} piezas</h2>
        </div>
        <button className={styles.ghostButton} type="button" onClick={onClear} disabled={!lines.length || checkoutBusy} data-prisma-component="IconButton">
          Limpiar
        </button>
      </header>

      <div className={styles.ticketLines}>
        {!lines.length ? (
          <div className={styles.emptyTicket} data-prisma-component="EmptyState" data-prisma-zone="tablet-pos-empty-state" data-prisma-state="empty" data-prisma-qa="tablet-qa-disabled">
            <PrismaIcon name="cart" size={26} />
            <strong>Agrega productos para cobrar</strong>
            <span>El total y el botón de cobro se activan cuando el ticket tiene productos.</span>
          </div>
        ) : (
          lines.map((line) => {
            const packshot = resolveProductPackshot(line.product.name, line.product.category, line.product.sku, { skin: packshotSkin });
            const stockSignal = getCartLineStockSignal(line);
            return (
              <article key={line.product.id} className={styles.ticketLine} data-prisma-component="CartItemRow" data-prisma-zone="tablet-pos-ticket-line" data-prisma-state="ready" data-prisma-motion="hover-lift">
                <span
                  className={[
                    styles.cartThumb,
                    packshot ? styles.cartThumbPackshot : cartThumbClass(line.product.name),
                    packshot ? styles[`cartThumbPackshot_${packshot.kind}`] : ""
                  ]
                    .filter(Boolean)
                    .join(" ")}
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
                      <span className={styles.cartThumbFallback} />
                    </>
                  ) : (
                    <span />
                  )}
                </span>
                <div className={styles.ticketLineText}>
                  <strong>{line.product.name}</strong>
                  <span>
                    {line.product.sku} · {formatMoney(line.product.priceCents)}
                  </span>
                  <small className={stockChipClass(stockSignal.tone)}>{stockSignal.label}</small>
                </div>
                <div className={styles.stepper} data-prisma-component="QuantityStepper" data-prisma-role="secondary-action" data-prisma-motion="press-feedback">
                  <button type="button" aria-label={`Restar ${line.product.name}`} onClick={() => onDecrement(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                    <PrismaIcon name="minus" size={15} />
                  </button>
                  <strong>{line.qty}</strong>
                  <button type="button" aria-label={`Sumar ${line.product.name}`} onClick={() => onIncrement(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                    <PrismaIcon name="plus" size={15} />
                  </button>
                </div>
                <strong className={styles.lineTotal}>{formatMoney(line.product.priceCents * line.qty)}</strong>
                <button className={styles.removeButton} type="button" aria-label={`Quitar ${line.product.name}`} onClick={() => onRemove(line.product.id)} disabled={!canCheckout || checkoutBusy}>
                  <PrismaIcon name="trash" size={16} />
                </button>
              </article>
            );
          })
        )}
      </div>

      <div className={checkoutReady ? styles.checkoutDiagnosticOk : styles.checkoutDiagnosticWarn} aria-live="polite" data-prisma-component="CheckoutDiagnostic" data-prisma-role="status-surface" data-prisma-state={checkoutReady ? "ready" : "disabled"}>
        <strong>{checkoutReady ? "Listo para cobrar" : "Prepara el cobro"}</strong>
        <span>{diagnosticCopy}</span>
      </div>

      <div className={styles.ticketTotalsBreakdown} aria-label="Resumen del ticket" data-prisma-zone="tablet-pos-total-area" data-prisma-role="sale-total">
        <span>Subtotal</span>
        <strong>{formatMoney(total)}</strong>
        <span>Impuestos</span>
        <strong>Incluidos</strong>
      </div>

      <div className={styles.ticketTotal} data-prisma-component="TotalsSummary" data-prisma-zone="tablet-pos-total-area" data-prisma-role="sale-total" data-prisma-priority="primary" data-prisma-state={lines.length ? "ready" : "empty"}>
        <span>Total a cobrar</span>
        <strong data-total-value="true">{formatMoney(total)}</strong>
      </div>

      {checkoutError ? <div className={styles.paymentError} data-prisma-zone="tablet-pos-error-state" data-prisma-state="error" data-prisma-motion="error-feedback">Revisa el cobro antes de continuar.</div> : null}

      <button
        className={lines.length && canCheckout ? styles.checkoutLink : styles.checkoutLinkDisabled}
        type="button"
        disabled={checkoutDisabled}
        aria-disabled={checkoutDisabled}
        data-prisma-component="CheckoutButton"
        data-prisma-zone="tablet-pos-cobrar-cta"
        data-prisma-role="primary-action"
        data-prisma-priority={checkoutDisabled ? "passive" : "primary"}
        data-prisma-motion={checkoutDisabled ? "reduced-motion-safe" : "press-feedback"}
        data-prisma-state={checkoutDisabled ? "disabled" : checkoutBusy ? "loading" : "ready"}
        data-prisma-qa={checkoutDisabled ? "tablet-qa-disabled" : "tablet-qa-cobrar"}
        onClick={onCheckout}
      >
        <span className={styles.visuallyHidden}>Abrir cobro</span>
        <span>{!canCheckout ? "ABRIR TURNO" : checkoutBusy ? "COBRANDO" : "COBRAR"}</span>
        <strong>Tocar</strong>
      </button>
      <div className={styles.secondaryCheckoutActions} aria-label="Acciones secundarias" data-prisma-role="secondary-action">
        <button type="button" disabled data-prisma-component="SecondaryActionCard">
          <PrismaIcon name="receipt" size={18} />
          <span>Cotización</span>
          <small>Pronto</small>
        </button>
        <button type="button" onClick={onHold} disabled={!canCheckout || !lines.length || checkoutBusy} data-prisma-component="HoldCartButton">
          <PrismaIcon name="save" size={18} />
          <span>Guardar</span>
          <small>Guardar</small>
        </button>
        <button type="button" onClick={onClear} disabled={!lines.length || checkoutBusy} data-prisma-component="SecondaryActionCard">
          <PrismaIcon name="broom" size={18} />
          <span>Limpiar</span>
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
    </aside>
  );
}

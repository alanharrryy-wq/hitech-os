"use client";

import Link from "next/link";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import type { HeldCart } from "@/lib/pos/held-carts";
import { getCartLineStockSignal, validateCartForCheckout } from "@/lib/pos/cart-engine";
import { resolveProductPackshot } from "./pos-packshots";
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
  const checkoutDisabled = !lines.length || Boolean(checkoutBusy);
  const readiness = validateCartForCheckout(lines);
  const diagnosticCopy = checkoutError ? "Revisa el cobro antes de continuar." : checkoutReason || readiness.reason;

  return (
    <aside className={styles.ticketPanel} aria-label="Ticket actual" data-prisma-component="CartPanel">
      <header className={styles.ticketHeader} data-prisma-component="CartHeader">
        <div>
          <span>Ticket activo</span>
          <h2>{qty} piezas</h2>
        </div>
        <button className={styles.ghostButton} type="button" onClick={onClear} disabled={!lines.length || checkoutBusy} data-prisma-component="IconButton">
          Cancelar venta
        </button>
      </header>

      <div className={styles.ticketLines}>
        {!lines.length ? (
          <div className={styles.emptyTicket} data-prisma-component="EmptyState">
            <PrismaIcon name="cart" size={26} />
            <strong>Agrega productos para cobrar</strong>
            <span>El total y el botón de cobro se activan cuando el ticket tiene productos.</span>
          </div>
        ) : (
          lines.map((line) => {
            const packshot = resolveProductPackshot(line.product.name, line.product.category, line.product.sku);
            const stockSignal = getCartLineStockSignal(line);
            return (
              <article key={line.product.id} className={styles.ticketLine} data-prisma-component="CartItemRow">
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
                        onError={(event) => {
                          event.currentTarget.closest("[data-prisma-packshot-host]")?.setAttribute("data-packshot-error", "true");
                        }}
                        onLoad={(event) => {
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
                <div className={styles.stepper} data-prisma-component="QuantityStepper">
                  <button type="button" aria-label={`Restar ${line.product.name}`} onClick={() => onDecrement(line.product.id)} disabled={checkoutBusy}>
                    <PrismaIcon name="minus" size={15} />
                  </button>
                  <strong>{line.qty}</strong>
                  <button type="button" aria-label={`Sumar ${line.product.name}`} onClick={() => onIncrement(line.product.id)} disabled={checkoutBusy}>
                    <PrismaIcon name="plus" size={15} />
                  </button>
                </div>
                <strong className={styles.lineTotal}>{formatMoney(line.product.priceCents * line.qty)}</strong>
                <button className={styles.removeButton} type="button" aria-label={`Quitar ${line.product.name}`} onClick={() => onRemove(line.product.id)} disabled={checkoutBusy}>
                  <PrismaIcon name="trash" size={16} />
                </button>
              </article>
            );
          })
        )}
      </div>

      <div className={readiness.ready ? styles.checkoutDiagnosticOk : styles.checkoutDiagnosticWarn} aria-live="polite" data-prisma-component="CheckoutDiagnostic">
        <strong>{readiness.ready ? "Listo para cobrar" : "Aduana del ticket"}</strong>
        <span>{diagnosticCopy}</span>
      </div>

      <div className={styles.ticketTotalsBreakdown} aria-label="Resumen del ticket">
        <span>Subtotal</span>
        <strong>{formatMoney(total)}</strong>
        <span>Impuestos</span>
        <strong>Incluidos</strong>
      </div>

      <div className={styles.ticketTotal} data-prisma-component="TotalsSummary">
        <span>Total a cobrar</span>
        <strong data-total-value="true">{formatMoney(total)}</strong>
      </div>

      {checkoutError ? <div className={styles.paymentError}>Revisa el cobro antes de continuar.</div> : null}

      <button
        className={lines.length ? styles.checkoutLink : styles.checkoutLinkDisabled}
        type="button"
        disabled={checkoutDisabled}
        aria-disabled={checkoutDisabled}
        data-prisma-component="CheckoutButton"
        data-prisma-touch-only-actions="checkout-cta-04h"
        onClick={onCheckout}
      >
        <span className={styles.visuallyHidden}>Abrir cobro</span>
        <span>{checkoutBusy ? "COBRANDO" : "COBRAR"}</span>
        <strong>Tocar</strong>
      </button>
      <div className={styles.secondaryCheckoutActions} aria-label="Acciones secundarias">
        <Link href="/returns" aria-disabled={checkoutBusy} data-prisma-component="RefundActionCard">
          <PrismaIcon name="receipt" size={18} />
          <span>Reembolso</span>
          <small>Buscar ticket</small>
        </Link>
        <button type="button" onClick={onHold} disabled={!lines.length || checkoutBusy} data-prisma-component="HoldCartButton">
          <PrismaIcon name="save" size={18} />
          <span>Guardar</span>
          <small>Guardar</small>
        </button>
        <button type="button" onClick={onClear} disabled={!lines.length || checkoutBusy} data-prisma-component="SecondaryActionCard">
          <PrismaIcon name="broom" size={18} />
          <span>Cancelar</span>
          <small>Venta</small>
        </button>
      </div>

      {heldCarts.length ? (
        <section className={styles.heldCartShelf} aria-label="Tickets guardados" data-prisma-component="HeldCartShelf">
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
                  <button type="button" onClick={() => onRestoreHeldCart(heldCart.id)} disabled={checkoutBusy || lines.length > 0} aria-label={`Recuperar ${heldCart.label}`}>
                    Recuperar
                  </button>
                  <button type="button" onClick={() => onDiscardHeldCart(heldCart.id)} disabled={checkoutBusy} aria-label={`Descartar ${heldCart.label}`}>
                    Quitar
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

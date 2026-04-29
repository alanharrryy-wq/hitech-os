"use client";

import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import styles from "./pos.module.css";

export function PosTicketPanel({
  lines,
  onIncrement,
  onDecrement,
  onRemove,
  onClear
}: {
  lines: CartLine[];
  onIncrement: (productId: string) => void;
  onDecrement: (productId: string) => void;
  onRemove: (productId: string) => void;
  onClear: () => void;
}) {
  const qty = cartTotalQty(lines);
  const total = cartTotalCents(lines);

  return (
    <aside className={styles.ticketPanel} aria-label="Ticket actual">
      <header className={styles.ticketHeader}>
        <div>
          <span>Ticket activo</span>
          <h2>{qty} piezas</h2>
        </div>
        <button className={styles.ghostButton} type="button" onClick={onClear} disabled={!lines.length}>Limpiar</button>
      </header>

      <div className={styles.ticketLines}>
        {!lines.length ? (
          <div className={styles.emptyTicket}>
            <PrismaIcon name="cart" size={26} />
            <strong>Agrega productos para cobrar</strong>
            <span>El total y el botón de cobro se activan cuando el ticket tiene productos.</span>
          </div>
        ) : (
          lines.map((line) => (
            <article key={line.product.id} className={styles.ticketLine}>
              <div className={styles.ticketLineText}>
                <strong>{line.product.name}</strong>
                <span>{line.product.sku} · {formatMoney(line.product.priceCents)}</span>
              </div>
              <div className={styles.stepper}>
                <button type="button" aria-label={`Restar ${line.product.name}`} onClick={() => onDecrement(line.product.id)}>
                  <PrismaIcon name="minus" size={15} />
                </button>
                <strong>{line.qty}</strong>
                <button type="button" aria-label={`Sumar ${line.product.name}`} onClick={() => onIncrement(line.product.id)}>
                  <PrismaIcon name="plus" size={15} />
                </button>
              </div>
              <strong className={styles.lineTotal}>{formatMoney(line.product.priceCents * line.qty)}</strong>
              <button className={styles.removeButton} type="button" aria-label={`Quitar ${line.product.name}`} onClick={() => onRemove(line.product.id)}>
                <PrismaIcon name="trash" size={16} />
              </button>
            </article>
          ))
        )}
      </div>

      <div className={styles.ticketTotal}>
        <span>Total a cobrar</span>
        <strong>{formatMoney(total)}</strong>
      </div>

      <a className={lines.length ? styles.checkoutLink : styles.checkoutLinkDisabled} href={lines.length ? "/checkout" : undefined} aria-disabled={!lines.length}>
        <span>Ir a cobro</span>
        <strong>F2</strong>
      </a>
    </aside>
  );
}

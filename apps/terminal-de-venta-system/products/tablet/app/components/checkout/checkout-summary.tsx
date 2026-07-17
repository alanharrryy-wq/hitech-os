"use client";

import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import styles from "./checkout.module.css";

export function CheckoutSummary({ lines }: { lines: CartLine[] }) {
  const visibleLines = lines.slice(0, 2);
  const hiddenCount = Math.max(0, lines.length - visibleLines.length);

  return (
    <section className={styles.ticketSummary} aria-labelledby="checkout-ticket-summary">
      <div className={styles.ticketHeading}>
        <div>
          <span>Ticket actual</span>
          <h2 id="checkout-ticket-summary">{cartTotalQty(lines)} pieza(s)</h2>
        </div>
        <a href="/pos">Editar</a>
      </div>
      <div className={styles.ticketLines}>
        {visibleLines.map((line) => (
          <div className={styles.ticketLine} key={line.product.id}>
            <span><strong>{line.product.name}</strong><small>{line.qty} × {formatMoney(line.product.priceCents)}</small></span>
            <b>{formatMoney(line.qty * line.product.priceCents)}</b>
          </div>
        ))}
        {hiddenCount > 0 ? <div className={styles.moreLines}>+ {hiddenCount} producto(s) en el ticket</div> : null}
        {!lines.length ? <div className={styles.emptyTicket}>No hay productos para cobrar.</div> : null}
      </div>
    </section>
  );
}

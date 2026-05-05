"use client";

import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import styles from "./checkout.module.css";

export function CheckoutSummary({ lines }: { lines: CartLine[] }) {
  const qty = cartTotalQty(lines);
  const total = cartTotalCents(lines);
  return (
    <section className={styles.summaryCard} aria-label="Resumen de ticket">
      <header>
        <div>
          <span>Resumen del ticket</span>
          <h2>{qty} piezas</h2>
        </div>
        <a href="/pos">Editar ticket</a>
      </header>
      <div className={styles.summaryLines}>
        {lines.map((line) => (
          <article key={line.product.id}>
            <div>
              <strong>{line.product.name}</strong>
              <span>{line.qty} × {formatMoney(line.product.priceCents)}</span>
            </div>
            <strong>{formatMoney(line.qty * line.product.priceCents)}</strong>
          </article>
        ))}
      </div>
      <footer>
        <span>Total</span>
        <strong>{formatMoney(total)}</strong>
      </footer>
      {!lines.length ? <div className={styles.emptyCheckout}><PrismaIcon name="cart" size={24} /><span>No hay productos para cobrar.</span></div> : null}
    </section>
  );
}

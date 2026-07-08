"use client";

import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { CartLine } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, formatMoney } from "@/lib/pos/cart-state";
import styles from "./checkout.module.css";

export function CheckoutSummary({ lines }: { lines: CartLine[] }) {
  const qty = cartTotalQty(lines);
  const total = cartTotalCents(lines);
  return (
    <section className={styles.summaryCard} aria-label="Resumen de ticket"
      data-surface="tablet"
      data-screen="checkout"
      data-zone="checkout"
      data-panel="checkout-summary"
      data-target="checkout-summary-resumen-de-ticket-12"
      data-kind="ticket"
      data-role="ticket-context"
    >
      <header
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-summary"
        data-target="checkout-summary-panel-13"
        data-kind="panel"
        data-role="revenue-core"
      >
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_summary" data-target="checkout-summary-div-1" data-kind="panel" data-role="container">
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_summary" data-target="checkout-summary-span-2" data-kind="text" data-role="text">Resumen del ticket</span>
          <h2
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-summary"
            data-target="checkout-summary-text-16"
            data-kind="text"
            data-role="copy"
          >{qty} piezas</h2>
        </div>
        <a href="/shift"
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-summary"
          data-target="checkout-summary-button-18"
          data-kind="button"
          data-role="action"
        >Ver turno antes de editar</a>
      </header>
      <div className={styles.summaryLines}
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-summary"
        data-target="checkout-summary-cart-20"
        data-kind="cart"
        data-role="revenue-core"
      >
        {lines.map((line) => (
          <article key={line.product.id}
            data-surface="tablet"
            data-screen="checkout"
            data-zone="checkout"
            data-panel="checkout-summary"
            data-target="checkout-summary-cart-22"
            data-kind="cart"
            data-role="revenue-core"
          >
            <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_summary" data-target="checkout-summary-div-3" data-kind="panel" data-role="container">
              <strong
                data-surface="tablet"
                data-screen="checkout"
                data-zone="checkout"
                data-panel="checkout-summary"
                data-target="checkout-summary-element-24"
                data-kind="element"
                data-role="revenue-core"
              >{line.product.name}</strong>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_summary" data-target="checkout-summary-span-4" data-kind="text" data-role="text">{line.qty} × {formatMoney(line.product.priceCents)}</span>
            </div>
            <strong
              data-surface="tablet"
              data-screen="checkout"
              data-zone="checkout"
              data-panel="checkout-summary"
              data-target="checkout-summary-element-27"
              data-kind="element"
              data-role="revenue-core"
            >{formatMoney(line.qty * line.product.priceCents)}</strong>
          </article>
        ))}
      </div>
      <footer
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-summary"
        data-target="checkout-summary-panel-31"
        data-kind="panel"
        data-role="revenue-core"
      >
        <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_summary" data-target="checkout-summary-span-5" data-kind="text" data-role="text">Total</span>
        <strong
          data-surface="tablet"
          data-screen="checkout"
          data-zone="checkout"
          data-panel="checkout-summary"
          data-target="checkout-summary-element-33"
          data-kind="element"
          data-role="revenue-core"
        >{formatMoney(total)}</strong>
      </footer>
      {!lines.length ? <div className={styles.emptyCheckout}
        data-surface="tablet"
        data-screen="checkout"
        data-zone="checkout"
        data-panel="checkout-summary"
        data-target="checkout-summary-text-35"
        data-kind="text"
        data-role="copy"
      ><PrismaIcon name="cart" size={24} /><span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="checkout_summary" data-target="checkout-summary-span-6" data-kind="text" data-role="text">No hay productos para cobrar.</span></div> : null}
    </section>
  );
}

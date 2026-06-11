"use client";

import { cartItems, products } from "./prisma-dark-pos-data";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import { ProductFigure } from "./prisma-product-card";
import styles from "./prisma-dark-pos.module.css";

type PosCartActionDetail = {
  action: "clear-cart" | "remove-line" | "decrement-line" | "increment-line" | "charge" | "quote" | "save-ticket" | "clear-current";
  productId?: string;
  productName?: string;
  source: "prisma-dark-pos-cart";
  ts: string;
};

function emitCartAction(action: PosCartActionDetail["action"], detail: Omit<Partial<PosCartActionDetail>, "action" | "source" | "ts"> = {}) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<PosCartActionDetail>("prisma:pos-cart-action", {
    detail: { action, source: "prisma-dark-pos-cart", ts: new Date().toISOString(), ...detail }
  }));
}

export function PrismaCartPanel() {
  return (
    <aside className={styles.cartPanel} aria-label="Carrito de venta" data-prisma-hardening="cart-actions-260611">
      <header className={styles.cartHeader}>
        <div>
          <h2>Carrito de venta</h2>
          <span>Ticket actual</span>
        </div>
        <div className={styles.cartHeaderActions}>
          <span className={styles.itemCount}>{cartItems.length} artículos</span>
          <button className={styles.trashButton} type="button" aria-label="Vaciar carrito" onClick={() => emitCartAction("clear-cart")}>
            <PrismaIcon name="trash" size={18} />
          </button>
        </div>
      </header>

      <div className={styles.cartItems}>
        {cartItems.map((item) => {
          const product = products.find((entry) => entry.id === item.productId);

          return (
            <article key={item.productId} className={styles.cartItem}>
              <div className={styles.cartItemIndex}>{item.index}</div>
              {product ? (
                <ProductFigure product={product} compact />
              ) : (
                <span className={styles.cartThumbFallback} />
              )}
              <div className={styles.cartItemMain}>
                <div className={styles.cartItemTitle}>
                  <strong>{item.name}</strong>
                  <button type="button" aria-label={`Quitar ${item.name}`} onClick={() => emitCartAction("remove-line", { productId: item.productId, productName: item.name })}>
                    <PrismaIcon name="x" size={15} />
                  </button>
                </div>
                <span className={styles.unitPrice}>{item.unitPrice}</span>
                <div className={styles.cartItemBottom}>
                  <div className={styles.quantityStepper} aria-label={`Cantidad ${item.quantity}`}>
                    <button type="button" aria-label={`Restar ${item.name}`} onClick={() => emitCartAction("decrement-line", { productId: item.productId, productName: item.name })}>
                      <PrismaIcon name="minus" size={13} />
                    </button>
                    <span>{item.quantity}</span>
                    <button type="button" aria-label={`Sumar ${item.name}`} onClick={() => emitCartAction("increment-line", { productId: item.productId, productName: item.name })}>
                      <PrismaIcon name="plus" size={13} />
                    </button>
                  </div>
                  <strong className={styles.lineTotal}>{item.total}</strong>
                </div>
              </div>
            </article>
          );
        })}
      </div>

      <section className={styles.totals} aria-label="Totales">
        <div className={styles.totalRow}>
          <span>Subtotal</span>
          <strong>$113.50</strong>
        </div>
        <div className={styles.totalRow}>
          <span>Impuestos (IVA 16%)</span>
          <strong>$18.16</strong>
        </div>
        <div className={styles.totalGrand}>
          <span>Total</span>
          <strong>$131.66</strong>
        </div>
      </section>

      <button className={styles.chargeButton} type="button" onClick={() => emitCartAction("charge")}>
        <span>COBRAR</span>
        <strong>Tocar</strong>
      </button>

      <footer className={styles.secondaryActions}>
        <button type="button" onClick={() => emitCartAction("quote")}>
          <PrismaIcon name="receipt" size={20} />
          <span>COTIZACIÓN</span>
          <strong>Pronto</strong>
        </button>
        <button type="button" onClick={() => emitCartAction("save-ticket")}>
          <PrismaIcon name="save" size={20} />
          <span>GUARDAR</span>
          <strong>Ticket</strong>
        </button>
        <button type="button" onClick={() => emitCartAction("clear-current")}>
          <PrismaIcon name="trash" size={20} />
          <span>LIMPIAR</span>
          <strong>Actual</strong>
        </button>
      </footer>
    </aside>
  );
}

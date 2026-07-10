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
    <aside className={styles.cartPanel} aria-label="Carrito de venta" data-prisma-hardening="cart-actions-260611"
      data-surface="tablet"
      data-screen="pos"
      data-zone="pos"
      data-panel="prisma-cart-panel"
      data-target="prisma-cart-panel-carrito-de-venta-25"
      data-kind="button"
      data-role="action"
    >
      <header className={styles.cartHeader}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-cart-panel"
        data-target="prisma-cart-panel-cart-26"
        data-kind="cart"
        data-role="revenue-core"
      >
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-1" data-kind="panel" data-role="container">
          <h2>Carrito de venta</h2>
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-2" data-kind="panel" data-role="panel">Ticket actual</span>
        </div>
        <div className={styles.cartHeaderActions}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-cart-panel"
          data-target="prisma-cart-panel-button-31"
          data-kind="button"
          data-role="action"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-3" data-kind="panel" data-role="panel" className={styles.itemCount}>{cartItems.length} artículos</span>
<button className={styles.trashButton} type="button" aria-label="Vaciar carrito"
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="prisma-cart-panel"
            data-target="prisma-cart-panel-vaciar-carrito-33"
            data-kind="button"
            data-role="action"
            onClick={() => emitCartAction("clear-cart")}>
            <PrismaIcon name="trash" size={18} />
          </button>
        </div>
      </header>

      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-4" data-kind="panel" data-role="container" className={styles.cartItems}>
        {cartItems.map((item) => {
          const product = products.find((entry) => entry.id === item.productId);

          return (
            <article key={item.productId} className={styles.cartItem}
              data-surface="tablet"
              data-screen="pos"
              data-zone="pos"
              data-panel="prisma-cart-panel"
              data-target="prisma-cart-panel-cart-44"
              data-kind="cart"
              data-role="revenue-core"
            >
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-5" data-kind="panel" data-role="container" className={styles.cartItemIndex}>{item.index}</div>
              {product ? (
                <ProductFigure product={product} compact />
              ) : (
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-6" data-kind="panel" data-role="panel" className={styles.cartThumbFallback} />
              )}
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-7" data-kind="panel" data-role="container" className={styles.cartItemMain}>
                <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-8" data-kind="panel" data-role="container" className={styles.cartItemTitle}>
                  <strong>{item.name}</strong>
<button type="button" aria-label={`Quitar ${item.name}`}
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="pos"
                    data-panel="prisma-cart-panel"
                    data-target="prisma-cart-panel-button-54"
                    data-kind="button"
                    data-role="action"
                    onClick={() => emitCartAction("remove-line", { productId: item.productId, productName: item.name})}>
                    <PrismaIcon name="x" size={15} />
                  </button>
                </div>
                <span className={styles.unitPrice}
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="prisma-cart-panel"
                  data-target="prisma-cart-panel-price-58"
                  data-kind="price"
                  data-role="financial-control"
                >{item.unitPrice}</span>
                <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-9" data-kind="panel" data-role="container" className={styles.cartItemBottom}>
                  <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-10" data-kind="panel" data-role="container" className={styles.quantityStepper} aria-label={`Cantidad ${item.quantity}`}>
<button type="button" aria-label={`Restar ${item.name}`}
                      data-surface="tablet"
                      data-screen="pos"
                      data-zone="pos"
                      data-panel="prisma-cart-panel"
                      data-target="prisma-cart-panel-button-61"
                      data-kind="button"
                      data-role="action"
                      onClick={() => emitCartAction("decrement-line", { productId: item.productId, productName: item.name})}>
                      <PrismaIcon name="minus" size={13} />
                    </button>
                    <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-11" data-kind="panel" data-role="panel">{item.quantity}</span>
<button type="button" aria-label={`Sumar ${item.name}`}
                      data-surface="tablet"
                      data-screen="pos"
                      data-zone="pos"
                      data-panel="prisma-cart-panel"
                      data-target="prisma-cart-panel-button-65"
                      data-kind="button"
                      data-role="action"
                      onClick={() => emitCartAction("increment-line", { productId: item.productId, productName: item.name})}>
                      <PrismaIcon name="plus" size={13} />
                    </button>
                  </div>
                  <strong className={styles.lineTotal}
                    data-surface="tablet"
                    data-screen="pos"
                    data-zone="pos"
                    data-panel="prisma-cart-panel"
                    data-target="prisma-cart-panel-price-69"
                    data-kind="price"
                    data-role="financial-control"
                  >{item.total}</strong>
                </div>
              </div>
            </article>
          );
        })}
      </div>

      <section className={styles.totals} aria-label="Totales"
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-cart-panel"
        data-target="prisma-cart-panel-totales-77"
        data-kind="price"
        data-role="financial-control"
      >
        <div className={styles.totalRow}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-cart-panel"
          data-target="prisma-cart-panel-price-78"
          data-kind="price"
          data-role="financial-control"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-12" data-kind="panel" data-role="panel">Subtotal</span>
          <strong>$113.50</strong>
        </div>
        <div className={styles.totalRow}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-cart-panel"
          data-target="prisma-cart-panel-price-82"
          data-kind="price"
          data-role="financial-control"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-13" data-kind="panel" data-role="panel">Impuestos (IVA 16%)</span>
          <strong>$18.16</strong>
        </div>
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-div-14" data-kind="price" data-role="container" className={styles.totalGrand}>
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-15" data-kind="panel" data-role="panel">Total</span>
          <strong>$131.66</strong>
        </div>
      </section>

<button className={styles.chargeButton} type="button"
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-cart-panel"
        data-target="prisma-cart-panel-button-92"
        data-kind="button"
        data-role="action"
        onClick={() => emitCartAction("charge")}>
        <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-16" data-kind="panel" data-role="panel">COBRAR</span>
        <strong>Tocar</strong>
      </button>

      <footer className={styles.secondaryActions}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-cart-panel"
        data-target="prisma-cart-panel-button-97"
        data-kind="button"
        data-role="action"
      >
<button type="button"
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-cart-panel"
          data-target="prisma-cart-panel-button-98"
          data-kind="button"
          data-role="action"
          onClick={() => emitCartAction("quote")}>
          <PrismaIcon name="receipt" size={20} />
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-17" data-kind="panel" data-role="panel">COTIZACIÓN</span>
          <strong>Pronto</strong>
        </button>
<button type="button"
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-cart-panel"
          data-target="prisma-cart-panel-button-103"
          data-kind="button"
          data-role="action"
          onClick={() => emitCartAction("save-ticket")}>
          <PrismaIcon name="save" size={20} />
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_cart_panel" data-target="prisma-cart-panel-span-18" data-kind="panel" data-role="panel">GUARDAR</span>
          <strong>Ticket</strong>
        </button>
<button type="button"
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-cart-panel"
          data-target="prisma-cart-panel-button-108"
          data-kind="button"
          data-role="action"
          onClick={() => emitCartAction("clear-current")}>
          <PrismaIcon name="trash" size={20} />
          <span>LIMPIAR</span>
          <strong>Actual</strong>
        </button>
      </footer>
    </aside>
  );
}

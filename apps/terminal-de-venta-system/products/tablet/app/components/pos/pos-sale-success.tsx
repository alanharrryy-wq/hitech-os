"use client";

import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { CompletedSale } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import styles from "./pos.module.css";

export function PosSaleSuccess({ sale, onNewSale }: { sale: CompletedSale | null; onNewSale: () => void }) {
  if (!sale) return null;
  return (
    <section className={styles.successCard} aria-label="Venta cerrada">
      <PrismaIcon name="receipt" size={26} />
      <div>
        <span>Ticket cerrado</span>
        <h2>{sale.folio}</h2>
        <p>{sale.lines.length} líneas · {sale.events.length} eventos locales</p>
      </div>
      <strong>{formatMoney(sale.totalCents)}</strong>
      <button className={styles.secondaryButton} type="button" onClick={onNewSale}>Nueva venta</button>
    </section>
  );
}

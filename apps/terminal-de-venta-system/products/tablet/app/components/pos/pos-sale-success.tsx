"use client";

import Link from "next/link";
import type { CompletedSaleReceipt } from "@/lib/pos/cart-state";
import { buildTicketSuccessViewModel } from "@/lib/pos/ticket-success-view-model";
import styles from "./pos.module.css";

export function PosSaleSuccess({ sale, onNewSale }: { sale: CompletedSaleReceipt | null; onNewSale: () => void }) {
  if (!sale) return null;
  const view = buildTicketSuccessViewModel(sale);
  const detailHref = `/sales/today/${encodeURIComponent(sale.saleId || sale.folio)}`;

  return (
    <section className={styles.successCard} aria-label="Ticket cerrado">
      <div className={styles.successMainCopy}>
        <span>Ticket cerrado</span>
        <h2>{view.folio}</h2>
        <p>
          {view.lineSummary} · {view.paymentLabel}
        </p>
      </div>
      <div className={styles.successTotals}>
        <span>Total cobrado</span>
        <strong>{view.totalLabel}</strong>
        <small>{view.paymentDetail}</small>
      </div>
      <div className={styles.successSyncBadge}>
        <strong>{view.syncLabel}</strong>
        <small>{view.syncDetail}</small>
      </div>
      <div className={styles.successActions}>
        <Link className={styles.secondaryButton} href={detailHref} prefetch={false}>
          Ver detalle
        </Link>
        <button className={styles.primaryButton} type="button" onClick={onNewSale}>
          Nueva venta
        </button>
      </div>
    </section>
  );
}

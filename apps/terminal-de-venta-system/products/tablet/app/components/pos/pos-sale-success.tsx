"use client";

import Link from "next/link";
import type { CompletedSaleReceipt } from "@/lib/pos/cart-state";
import { buildTicketSuccessViewModel } from "@/lib/pos/ticket-success-view-model";
import styles from "./pos.module.css";

export function PosSaleSuccess({ sale, onNewSale }: { sale: CompletedSaleReceipt | null; onNewSale: () => void }) {
  if (!sale) return null;
  const view = buildTicketSuccessViewModel(sale);
  const detailKey = sale.ticketEvidence?.canonicalTicketId || sale.saleId;
  const detailHref = sale.ticketEvidence?.localDetailHref || `/sales/today/${encodeURIComponent(detailKey)}${sale.businessId ? `?businessId=${encodeURIComponent(sale.businessId)}` : ""}`;

  return (
    <section className={styles.successCard} aria-label="Ticket cerrado" data-prisma-zone="tablet-pos-success-state" data-prisma-role="status-surface" data-prisma-state="success" data-prisma-motion="success-feedback">
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

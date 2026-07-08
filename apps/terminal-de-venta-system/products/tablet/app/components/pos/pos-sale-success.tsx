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
    <section className={styles.successCard} aria-label="Venta registrada" data-prisma-zone="tablet-pos-success-state" data-prisma-role="status-surface" data-prisma-state="success" data-prisma-motion="success-feedback"
      data-surface="tablet"
      data-screen="pos"
      data-zone="pos"
      data-panel="pos-sale-success"
      data-target="pos-sale-success-venta-registrada-15"
      data-kind="badge"
      data-role="state-feedback"
    >
      <div className={styles.successMainCopy}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-sale-success"
        data-target="pos-sale-success-badge-16"
        data-kind="badge"
        data-role="state-feedback"
      >
        <span
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-badge-17"
          data-kind="badge"
          data-role="state-feedback"
        >Venta registrada</span>
        <h2
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-badge-18"
          data-kind="badge"
          data-role="state-feedback"
        >{view.folio}</h2>
        <p
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-badge-19"
          data-kind="badge"
          data-role="state-feedback"
        >
          {view.lineSummary} · {view.paymentLabel}
        </p>
      </div>
      <div className={styles.successTotals}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-sale-success"
        data-target="pos-sale-success-price-23"
        data-kind="price"
        data-role="financial-control"
      >
        <span
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-badge-24"
          data-kind="badge"
          data-role="state-feedback"
        >Total cobrado</span>
        <strong
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-badge-25"
          data-kind="badge"
          data-role="state-feedback"
        >{view.totalLabel}</strong>
        <small>{view.paymentDetail}</small>
      </div>
      <div className={styles.successSyncBadge}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-sale-success"
        data-target="pos-sale-success-badge-28"
        data-kind="badge"
        data-role="state-feedback"
      >
        <strong
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-badge-29"
          data-kind="badge"
          data-role="state-feedback"
        >{view.syncLabel}</strong>
        <small>{view.syncDetail}</small>
      </div>
      <div className={styles.successActions}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-sale-success"
        data-target="pos-sale-success-button-32"
        data-kind="button"
        data-role="state-feedback"
      >
        <Link className={styles.secondaryButton} href={detailHref} prefetch={false}>
          Ver detalle
        </Link>
        <button className={styles.primaryButton} type="button" onClick={onNewSale}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-sale-success"
          data-target="pos-sale-success-button-36"
          data-kind="button"
          data-role="state-feedback"
        >
          Nueva venta
        </button>
      </div>
    </section>
  );
}

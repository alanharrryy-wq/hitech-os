"use client";

import Link from "next/link";
import { formatMoney } from "@/lib/pos/cart-state";
import type { SalesTodayTicket } from "@/lib/sales-today/types";
import { formatTicketTime } from "@/lib/sales-today/view-model";
import styles from "./sales.module.css";

export function SalesTicketList({ tickets }: { tickets: SalesTodayTicket[] }) {
  if (!tickets.length) return <div className={styles.empty}>Aún no hay tickets cerrados para mostrar.</div>;

  return (
    <section className={styles.ticketList} aria-label="Tickets cerrados del día">
      {tickets.map((ticket) => {
        const detailHref = `/sales/today/${encodeURIComponent(ticket.saleId || ticket.folio)}`;
        return (
          <Link
            className={styles.ticketRow}
            href={detailHref}
            key={ticket.saleId || ticket.folio}
            aria-label={`Ver detalle del ticket ${ticket.folio}`}
            prefetch={false}
          >
            <div className={styles.ticketMain}>
              <strong>{ticket.folio}</strong>
              <span>
                {formatTicketTime(ticket.createdAt)} · {ticket.cashier} · {ticket.lineCount} líneas
              </span>
            </div>
            <strong>{formatMoney(ticket.totalCents)}</strong>
            <span className={styles.detailCta}>Ver detalle</span>
          </Link>
        );
      })}
    </section>
  );
}

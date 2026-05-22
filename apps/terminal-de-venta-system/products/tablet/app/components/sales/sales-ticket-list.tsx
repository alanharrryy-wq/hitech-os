"use client";

import Link from "next/link";
import { formatMoney } from "@/lib/pos/cart-state";
import type { SalesTodayTicket } from "@/lib/sales-today/types";
import { formatTicketTime } from "@/lib/sales-today/view-model";
import styles from "./sales.module.css";

export function SalesTicketList({
  tickets,
  basePath = "/sales/today",
  emptyMessage = "Aún no hay tickets cerrados para mostrar."
}: {
  tickets: SalesTodayTicket[];
  basePath?: "/sales/today" | "/sales/history";
  emptyMessage?: string;
}) {
  const validTickets = tickets.filter((ticket) => ticket.saleId && ticket.saleId !== "undefined");
  if (!validTickets.length) return <div className={styles.empty}>{emptyMessage}</div>;

  return (
    <section className={styles.ticketList} aria-label="Tickets cerrados del día">
      {validTickets.map((ticket) => {
        const detailHref = `${basePath}/${encodeURIComponent(ticket.saleId)}?businessId=${encodeURIComponent(ticket.businessId)}`;
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

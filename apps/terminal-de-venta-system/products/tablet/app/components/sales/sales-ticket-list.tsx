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
  if (!validTickets.length) return <div className={styles.empty}
    data-surface="tablet"
    data-screen="sales"
    data-zone="pos"
    data-panel="sales-ticket-list"
    data-target="sales-ticket-list-ticket-19"
    data-kind="ticket"
    data-role="ticket-context"
  >{emptyMessage}</div>;

  return (
    <section className={styles.ticketList} aria-label="Tickets cerrados del día"
      data-surface="tablet"
      data-screen="sales"
      data-zone="pos"
      data-panel="sales-ticket-list"
      data-target="sales-ticket-list-tickets-cerrados-del-d-a-22"
      data-kind="ticket"
      data-role="ticket-context"
    >
      {validTickets.map((ticket) => {
        const detailHref = `${basePath}/${encodeURIComponent(ticket.saleId)}?businessId=${encodeURIComponent(ticket.businessId)}`;
        const returnLabel = ticket.returnSummary
          ? ticket.returnSummary.status === "fully_returned"
            ? "Devuelto"
            : "Devolución parcial"
          : null;
        return (
          <Link
            className={styles.ticketRow}
            href={detailHref}
            key={ticket.saleId || ticket.folio}
            aria-label={`Ver detalle del ticket ${ticket.folio}`}
            prefetch={false}
          >
            <div className={styles.ticketMain}
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-ticket-list"
              data-target="sales-ticket-list-ticket-38"
              data-kind="ticket"
              data-role="ticket-context"
            >
              <strong
                data-surface="tablet"
                data-screen="sales"
                data-zone="pos"
                data-panel="sales-ticket-list"
                data-target="sales-ticket-list-ticket-39"
                data-kind="ticket"
                data-role="ticket-context"
              >{ticket.folio}</strong>
              <span
                data-surface="tablet"
                data-screen="sales"
                data-zone="pos"
                data-panel="sales-ticket-list"
                data-target="sales-ticket-list-ticket-40"
                data-kind="ticket"
                data-role="ticket-context"
              >
                {formatTicketTime(ticket.createdAt)} · {ticket.cashier} · {ticket.lineCount} líneas
              </span>
              {ticket.returnSummary ? (
                <small className={styles.ticketReturnHint}>
                  {returnLabel}: {formatMoney(ticket.returnSummary.returnedCents)} · {ticket.returnSummary.latestReason ?? "Devolución registrada"}
                </small>
              ) : null}
            </div>
            <strong
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-ticket-list"
              data-target="sales-ticket-list-ticket-49"
              data-kind="ticket"
              data-role="ticket-context"
            >{formatMoney(ticket.totalCents)}</strong>
            {returnLabel ? <span className={styles.returnBadge}
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-ticket-list"
              data-target="sales-ticket-list-badge-50"
              data-kind="badge"
              data-role="ticket-context"
            >{returnLabel}</span> : null}
            <span className={styles.detailCta}
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-ticket-list"
              data-target="sales-ticket-list-button-51"
              data-kind="button"
              data-role="ticket-context"
            >Ver detalle</span>
          </Link>
        );
      })}
    </section>
  );
}

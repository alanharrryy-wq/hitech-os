import type { SalesTodayTicket } from "./types";

export type SalesExportFormat = "json" | "csv";

function csvCell(value: unknown) {
  const raw = String(value ?? "");
  return /[",\n]/.test(raw) ? `"${raw.replace(/"/g, '""')}"` : raw;
}

export function buildSalesTodayExport(tickets: SalesTodayTicket[], format: SalesExportFormat) {
  if (format === "json") {
    return JSON.stringify({ exportedAt: new Date().toISOString(), tickets }, null, 2);
  }
  const rows = [["folio", "saleId", "fecha", "operador", "estado", "totalCents", "lineas", "unidades"]];
  for (const ticket of tickets) {
    rows.push([
      ticket.folio,
      ticket.saleId,
      ticket.createdAt,
      ticket.cashier,
      ticket.status,
      String(ticket.totalCents),
      String(ticket.lineCount),
      String(ticket.unitsSold),
    ]);
  }
  return rows.map(row => row.map(csvCell).join(",")).join("\n");
}

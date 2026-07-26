import { getTabletRuntimeMeta } from "../pos-runtime";
import { getOperationalDayRange, getRecentInventoryMovements } from "../pos-reports";
import { listRecentEvents } from "../pos-outbox";
import { getTodaySalesSummary } from "../pos-api/sales-summary.prisma";
import type { PosExportInput } from "../pos-api/validators";

type CsvValue = string | number | boolean | null | undefined;

function csvEscape(value: CsvValue) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  if (/[",\r\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

export function toCsv(headers: string[], rows: Record<string, CsvValue>[]) {
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => csvEscape(row[header])).join(","));
  }
  return `${lines.join("\r\n")}\r\n`;
}

export function csvResponse(filename: string, csv: string, extraHeaders: Record<string, string> = {}) {
  return new Response(csv, {
    status: 200,
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": `attachment; filename="${filename}"`,
      ...extraHeaders
    }
  });
}

/* PRISMA_TABLET_SALES_EXPORT_CANONICAL_READMODEL_2607
 * Reuse the same proven read model used by /sales/today.
 * This removes the divergent direct sale query and keeps PAID/COMPLETED semantics aligned.
 */
export async function buildSalesTodayExport(input: PosExportInput) {
  const range = getOperationalDayRange(input.date);
  const summary = await getTodaySalesSummary({
    businessId: input.businessId,
    terminalId: input.terminalId,
    date: input.date
  });
  const sales = summary.tickets.slice(0, input.limit);

  const rows = sales.flatMap((sale: any) =>
    sale.lines.map((line: any) => ({
      saleId: sale.saleId,
      folio: sale.folio,
      businessId: sale.businessId,
      terminalId: sale.terminalId,
      cashier: sale.cashier,
      status: sale.status,
      saleTotalCents: sale.totalCents,
      createdAt: sale.createdAt,
      lineId: line.id,
      productId: line.productId,
      sku: line.sku,
      productName: line.productName,
      qty: line.qty,
      priceCents: line.priceCents,
      lineTotalCents: line.totalCents
    }))
  );

  const headers = [
    "saleId", "folio", "businessId", "terminalId", "cashier", "status",
    "saleTotalCents", "createdAt", "lineId", "productId", "sku",
    "productName", "qty", "priceCents", "lineTotalCents"
  ];

  return {
    filename: `tablet-sales-${range.date}.csv`,
    data: {
      date: range.date,
      range: { from: range.from.toISOString(), to: range.to.toISOString() },
      summary,
      sales,
      rows,
      source: "canonical-sales-today-summary",
      runtime: getTabletRuntimeMeta()
    },
    csv: toCsv(headers, rows)
  };
}

export async function buildEventsExport(input: PosExportInput) {
  const events = await listRecentEvents(input);
  const headers = ["id", "eventId", "businessId", "topic", "aggregateId", "status", "attempts", "createdAt", "sentAt", "lastError"];
  const rows = events.map((event: any) => ({
    id: event.id,
    eventId: event.eventId,
    businessId: event.businessId,
    topic: event.topic,
    aggregateId: event.aggregateId,
    status: event.status,
    attempts: event.attempts,
    createdAt: event.createdAt,
    sentAt: event.sentAt,
    lastError: event.lastError
  }));

  return {
    filename: "tablet-events.csv",
    data: { events, count: events.length, runtime: getTabletRuntimeMeta() },
    csv: toCsv(headers, rows)
  };
}

export async function buildInventoryMovementsExport(input: PosExportInput) {
  const movements = await getRecentInventoryMovements(input);
  const headers = ["id", "businessId", "productId", "sku", "productName", "movement", "quantityDelta", "reason", "location", "createdAt"];
  const rows = movements.map((movement: any) => ({
    id: movement.id,
    businessId: movement.businessId,
    productId: movement.productId,
    sku: movement.sku,
    productName: movement.productName,
    movement: movement.movement,
    quantityDelta: movement.quantityDelta,
    reason: movement.reason,
    location: movement.location,
    createdAt: movement.createdAt
  }));

  return {
    filename: "tablet-inventory-movements.csv",
    data: { movements, count: movements.length, runtime: getTabletRuntimeMeta() },
    csv: toCsv(headers, rows)
  };
}

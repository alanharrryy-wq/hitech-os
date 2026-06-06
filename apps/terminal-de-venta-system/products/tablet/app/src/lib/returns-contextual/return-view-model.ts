import type { SalesTodayTicket } from "@/lib/sales-today/types";
import type { ReturnSelection } from "./types";
import { returnReasonLabel } from "./return-reasons";

function clampReturnQty(value: unknown, maxQty: number) {
  const numeric = Number(value ?? 0);
  if (!Number.isFinite(numeric)) return 0;
  return Math.max(0, Math.min(Math.trunc(numeric), Math.max(0, maxQty)));
}

export function lineReturnAlreadyReturnedQty(line: SalesTodayTicket["lines"][number]) {
  const returned = Number(line.returnedQty ?? 0);
  return Number.isFinite(returned) ? Math.max(0, Math.min(Math.trunc(returned), line.qty)) : 0;
}

export function lineReturnAvailableQty(line: SalesTodayTicket["lines"][number]) {
  const explicit = Number(line.returnAvailableQty);
  if (Number.isFinite(explicit)) return Math.max(0, Math.min(Math.trunc(explicit), line.qty));
  return Math.max(0, line.qty - lineReturnAlreadyReturnedQty(line));
}

export function selectedReturnLines(ticket: SalesTodayTicket, selection: ReturnSelection) {
  return ticket.lines
    .map((line) => ({ ...line, qty: clampReturnQty(selection[line.id], lineReturnAvailableQty(line)) }))
    .filter((line) => line.qty > 0);
}

export function returnAmountCents(ticket: SalesTodayTicket, selection: ReturnSelection) {
  return selectedReturnLines(ticket, selection).reduce((sum, line) => sum + line.qty * line.priceCents, 0);
}

export function buildReturnPayload(ticket: SalesTodayTicket, selection: ReturnSelection, reason: string, notes: string) {
  const lines = selectedReturnLines(ticket, selection);
  return {
    businessId: ticket.businessId,
    terminalId: ticket.terminalId,
    cashSessionId: ticket.cashSessionId,
    saleId: ticket.saleId,
    saleFolio: ticket.folio,
    reason,
    reasonLabel: returnReasonLabel(reason),
    notes,
    amountCents: returnAmountCents(ticket, selection),
    cashier: ticket.cashier,
    lines: lines.map((line) => ({
      saleLineId: line.id,
      productId: line.productId,
      sku: line.sku,
      productName: line.productName,
      name: line.productName,
      qty: line.qty,
      unitPriceCents: line.priceCents,
      amountCents: line.qty * line.priceCents
    }))
  };
}

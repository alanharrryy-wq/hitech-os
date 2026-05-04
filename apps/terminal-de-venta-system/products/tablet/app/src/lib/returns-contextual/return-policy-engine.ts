import type { SalesTodayTicket } from "../sales-today/types";
import type { ReturnSelection } from "./types";

export type ReturnPolicyDecision = {
  canReturn: boolean;
  amountCents: number;
  totalQty: number;
  blockingReasons: string[];
  warnings: string[];
};

export function evaluateReturnPolicy(ticket: SalesTodayTicket, selection: ReturnSelection, previousReturnedLineQty: Record<string, number> = {}): ReturnPolicyDecision {
  const blockingReasons: string[] = [];
  const warnings: string[] = [];
  let amountCents = 0;
  let totalQty = 0;
  for (const line of ticket.lines) {
    const requestedQty = Math.max(0, Math.floor(selection[line.id] ?? 0));
    if (!requestedQty) continue;
    const alreadyReturned = Math.max(0, previousReturnedLineQty[line.id] ?? 0);
    const available = Math.max(0, line.qty - alreadyReturned);
    if (requestedQty > available) blockingReasons.push(`${line.productName}: sólo se pueden devolver ${available} piezas.`);
    amountCents += Math.min(requestedQty, available) * line.priceCents;
    totalQty += Math.min(requestedQty, available);
    if (alreadyReturned > 0) warnings.push(`${line.productName} ya tiene ${alreadyReturned} piezas devueltas.`);
  }
  if (totalQty <= 0) blockingReasons.push("Selecciona al menos una pieza para devolver.");
  if (ticket.status !== "COMPLETED") blockingReasons.push("Sólo se pueden devolver tickets cerrados.");
  return { canReturn: blockingReasons.length === 0, amountCents, totalQty, blockingReasons, warnings };
}

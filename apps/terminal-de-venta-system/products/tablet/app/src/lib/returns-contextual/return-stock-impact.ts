import type { SalesTodayTicket } from "../sales-today/types";
import type { ReturnSelection } from "./types";

export type ReturnStockImpactLine = {
  productId: string;
  sku: string;
  productName: string;
  qtyToRestore: number;
  reason: "customer_return" | "damaged" | "manual_review";
  visibleCopy: string;
};

export function buildReturnStockImpact(ticket: SalesTodayTicket, selection: ReturnSelection, reasonId: string): ReturnStockImpactLine[] {
  const damaged = reasonId.includes("damaged") || reasonId.includes("damage") || reasonId.includes("defect");
  return ticket.lines.flatMap(line => {
    const qty = Math.max(0, Math.floor(selection[line.id] ?? 0));
    if (!qty) return [];
    const reason = damaged ? "damaged" : "customer_return";
    return [{
      productId: line.productId,
      sku: line.sku,
      productName: line.productName,
      qtyToRestore: damaged ? 0 : qty,
      reason,
      visibleCopy: damaged ? "No se devuelve a existencia; revisar merma." : "Se devuelve a existencia local.",
    } satisfies ReturnStockImpactLine];
  });
}

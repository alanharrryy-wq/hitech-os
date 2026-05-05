
import type { CompletedSaleReceipt } from "./cart-state";
import { formatMoney } from "./cart-state";
import { paymentMethodLabel } from "./payment-state";

export function buildTicketSuccessViewModel(sale: CompletedSaleReceipt) {
  const qty = sale.lines.reduce((sum, line) => sum + line.qty, 0);
  const changeCents = sale.changeCents ?? 0;
  return {
    title: "Ticket cerrado",
    folio: sale.folio,
    totalLabel: formatMoney(sale.totalCents),
    lineSummary: `${sale.lines.length} líneas · ${qty} piezas`,
    paymentLabel: paymentMethodLabel(sale.paymentMethod),
    paymentDetail: changeCents > 0 ? `Cambio: ${formatMoney(changeCents)}` : "Venta guardada",
    syncLabel: "Pendiente registrado",
    syncDetail: "La venta dejó evento operativo para sincronizar o exportar.",
    syncTone: "warn"
  };
}

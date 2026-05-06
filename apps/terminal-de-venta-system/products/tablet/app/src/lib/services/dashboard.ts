import { formatMoney, formatInt } from "@/lib/utils";
import { tabletMessages } from "@/lib/i18n/messages/es";
import { getSalesConsole } from "@/lib/services/sales";
import { getShiftConsole } from "@/lib/services/shift";
import { getReturnsConsole } from "@/lib/services/returns";
import { getSyncConsole } from "@/lib/services/sync";
import { getStockConsole } from "@/lib/services/stock";

export async function getTabletDashboard() {
  const [sales, shift, returns, sync, stock] = await Promise.all([
    getSalesConsole(),
    getShiftConsole(),
    getReturnsConsole(),
    getSyncConsole(),
    getStockConsole()
  ]);

  const stockPressure = stock.watchlist.filter((row) => row.tone !== "ok").length;
  const riskLane = sync.channels.find((row) => row.tone === "danger") ?? sync.channels[0];
  const shiftAlert = shift.alerts[0];
  const syncAlert = sync.alerts[0];
  const stockAlert = stock.barcodeAlerts[0] ?? {
    title: "Barcodes canónicos completos",
    level: "ok",
    description: "Los productos activos tienen Barcode asociado al mismo negocio.",
    action: "Mantener validación de escaneo.",
    tone: "ok" as const
  };
  const returnsAlert = returns.guardrails[1] ?? returns.guardrails[0];

  return {
    hero: {
      title: tabletMessages.home.title,
      subtitle: tabletMessages.home.subtitle,
      branch: shift.activeShift.store,
      window: `corte ${shift.activeShift.openedAt} a 18:00 · operador ${shift.activeShift.cashier}`,
      healthLabel: riskLane.status,
      healthNote: `${formatInt(sync.kpis.pending)} pendientes · ${formatInt(stock.kpis.stockouts)} quiebres activos · ${formatInt(returns.kpis.returnCount)} devoluciones hoy`
    },
    kpis: [
      { label: "Ventas netas", value: formatMoney(sales.kpis.netSales), note: "turno actual" },
      { label: "Tickets", value: formatInt(sales.kpis.tickets), note: "cerrados hoy" },
      { label: "Ticket promedio", value: formatMoney(sales.kpis.avgTicket), note: "cesta media" },
      { label: "Quiebres vivos", value: formatInt(stock.kpis.stockouts), note: "SKUs en riesgo" }
    ],
    executivePulse: [
      { label: "Devoluciones", value: formatInt(returns.kpis.returnCount), note: "movimientos del día", signal: "vigilar", tone: "warn" as const },
      { label: "Tiempo medio de venta", value: "01:48", note: "promedio de caja", signal: "estable", tone: "ok" as const },
      { label: "Eventos offline", value: `${sync.kpis.offlineShare}%`, note: "captura sin red", signal: "controlado", tone: sync.kpis.offlineShare > 40 ? "warn" as const : "ok" as const },
      { label: "Presión de stock", value: formatInt(stockPressure), note: "SKUs con cobertura baja", signal: stockPressure > 3 ? "alto" : "estable", tone: stockPressure > 3 ? "danger" as const : "ok" as const }
    ],
    topSkus: sales.topProducts.map((row) => {
      const stockRow = stock.watchlist.find((item) => item.sku === row.sku);
      return {
        ...row,
        signal: stockRow?.signal ?? "estable",
        tone: stockRow?.tone ?? ("ok" as const)
      };
    }),
    risks: [
      {
        title: shiftAlert.title,
        level: shiftAlert.level,
        description: shiftAlert.description,
        action: shiftAlert.action,
        tone: shiftAlert.tone
      },
      {
        title: syncAlert.title,
        level: syncAlert.level,
        description: syncAlert.description,
        action: syncAlert.action,
        tone: syncAlert.tone
      },
      {
        title: stockAlert.title,
        level: stockAlert.level,
        description: stockAlert.description,
        action: stockAlert.action,
        tone: stockAlert.tone
      },
      {
        title: returnsAlert.title,
        level: returnsAlert.level,
        description: returnsAlert.description,
        action: returnsAlert.action,
        tone: returnsAlert.tone
      }
    ],
    shiftTable: shift.recentShifts,
    syncTable: sync.channels,
    stockTable: stock.watchlist
  };
}

import type { CanonicalPcDashboard } from "./types";
import { asRecord, readCents, readNonNegativeInt, readNumber, readString, unwrapOkData } from "./extractors";

function centsFromMoneyLabel(value: unknown): number | null {
  const text = String(value ?? "").trim();
  if (!text) return null;
  const numeric = Number(text.replace(/[^\d.-]/g, ""));
  if (!Number.isFinite(numeric)) return null;
  return Math.round(numeric * 100);
}

export function normalizePcDashboard(payload: unknown): CanonicalPcDashboard {
  const data = asRecord(unwrapOkData(payload));
  const salesControl = asRecord(data.salesControl);
  if (Object.keys(salesControl).length > 0) {
    const recentActivity = asRecord(salesControl.recentActivity);
    const salesCents = centsFromMoneyLabel(salesControl.netLabel ?? salesControl.totalLabel ?? recentActivity.netLabel ?? recentActivity.totalLabel);
    return {
      ok: true,
      branchName: readString(salesControl, ["branchCountLabel"], "PC Sales Control"),
      branchStatus: "sano",
      consolidatedSalesCents: salesCents,
      consolidatedTickets: readNonNegativeInt(salesControl, ["ticketsLabel"], readNonNegativeInt(recentActivity, ["ticketsLabel"], 0)),
      syncLagMs: null,
      activeAlerts: 0
    };
  }

  const branch = asRecord(data.branch ?? data.store ?? data.location);
  const sync = asRecord(data.sync ?? data.syncStatus);
  const sales = asRecord(data.sales ?? data.today ?? data.kpis);
  const status = readString(branch, ["status", "health"], readString(data, ["status", "health"], "revisar"));
  const normalizedStatus = status === "sano" || status === "revisar" || status === "urgente" || status === "offline" ? status : "revisar";
  const syncLagMsRaw = readNumber(sync, ["lagMs", "syncLagMs", "latencyMs"], Number.NaN);
  return {
    ok: true,
    branchName: readString(branch, ["name", "branchName", "storeName"], readString(data, ["branchName", "name"], "Sucursal sin consolidado PC")),
    branchStatus: normalizedStatus,
    consolidatedSalesCents: readCents(sales, ["totalSalesCents", "netSalesCents", "salesTodayCents"], readCents(data, ["salesTodayCents"], 0)),
    consolidatedTickets: readNonNegativeInt(sales, ["tickets", "ticketCount"], readNonNegativeInt(data, ["tickets"], 0)),
    syncLagMs: Number.isFinite(syncLagMsRaw) ? syncLagMsRaw : null,
    activeAlerts: readNonNegativeInt(data, ["activeAlerts", "alerts"], readNonNegativeInt(branch, ["alerts"], 0))
  };
}

export function offlinePcDashboard(): CanonicalPcDashboard {
  return { ok: false, branchName: "Sucursal sin consolidado PC", branchStatus: "offline", consolidatedSalesCents: null, consolidatedTickets: null, syncLagMs: null, activeAlerts: 0 };
}

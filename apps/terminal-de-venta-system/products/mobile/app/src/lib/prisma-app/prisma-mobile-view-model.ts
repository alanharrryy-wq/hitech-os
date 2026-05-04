import type { PrismaMobileSnapshotPayload } from "./prisma-mobile-snapshot-contract";
import type { PrismaMobileDataReadiness } from "./prisma-app-api-contracts";
import { formatInteger, formatSignedMxnFromCents } from "./prisma-mobile-formatters";

export type PrismaMobileHealthTone = "sano" | "revisar" | "urgente" | "offline";

export type PrismaMobileHeroViewModel = {
  businessName: string;
  health: PrismaMobileHealthTone;
  healthLabel: string;
  headline: string;
  subline: string;
  salesDelta: string;
  urgentAlerts: number;
  branchesToReview: number;
  cashDifferenceLabel: string;
  inventoryCriticalCount: number;
};

const healthLabels: Record<PrismaMobileHealthTone, string> = {
  sano: "Operación sana",
  revisar: "Revisar hoy",
  urgente: "Atención urgente",
  offline: "Datos sin conexión"
};

export const PRISMA_MOBILE_DATA_READINESS_FALLBACK: PrismaMobileDataReadiness = {
  level: "partial",
  label: "Lectura pendiente",
  headline: "La app está esperando datos operativos.",
  detail: "La lectura actual no trae todavía el contrato de madurez de datos. Refresca la app o limpia caché para reconstruirla desde fuentes reales.",
  sourceSummary: "snapshot anterior sin dataReadiness",
  salesState: "unavailable",
  inventoryState: "unavailable",
  pcState: "unavailable",
  syncState: "unknown",
  facts: ["Snapshot compatible sin contrato 28", "UI protegida contra lecturas antiguas"],
  actions: [
    {
      title: "Actualizar lectura",
      detail: "Pulsa actualizar o limpia caché para pedir el snapshot nuevo.",
      owner: "PRISMA App",
      priority: "media"
    }
  ]
};

export function getPrismaMobileDataReadiness(snapshot: PrismaMobileSnapshotPayload): PrismaMobileDataReadiness {
  const summary = snapshot.summary as PrismaMobileSnapshotPayload["summary"] & {
    dataReadiness?: PrismaMobileDataReadiness;
  };

  return summary.dataReadiness ?? PRISMA_MOBILE_DATA_READINESS_FALLBACK;
}

export function derivePrismaMobileHero(snapshot: PrismaMobileSnapshotPayload): PrismaMobileHeroViewModel {
  const urgentAlerts = snapshot.alerts.counts.critical + snapshot.alerts.counts.high;
  const branchesToReview = snapshot.branches.counts.review + snapshot.branches.counts.urgent + snapshot.branches.counts.offline;
  const inventoryCriticalCount = snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder;
  const dataReadiness = getPrismaMobileDataReadiness(snapshot);
  const health: PrismaMobileHealthTone = snapshot.branches.counts.offline > 0
    ? "offline"
    : urgentAlerts > 2
      ? "urgente"
      : urgentAlerts > 0 || branchesToReview > 0
        ? "revisar"
        : snapshot.summary.health;

  return {
    businessName: snapshot.summary.businessName,
    health,
    healthLabel: healthLabels[health],
    headline: dataReadiness.headline,
    subline: `${snapshot.salesToday.totalSalesLabel} · ${formatInteger(snapshot.salesToday.tickets)} tickets · ${dataReadiness.label}`,
    salesDelta: snapshot.salesToday.deltaAgainstYesterday,
    urgentAlerts,
    branchesToReview,
    cashDifferenceLabel: formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents),
    inventoryCriticalCount
  };
}

export function buildPrismaMobileOperationsList(snapshot: PrismaMobileSnapshotPayload) {
  return [
    { label: "Caja", value: snapshot.cashCurrent.status, detail: snapshot.cashCurrent.differenceCents === 0 ? "Sin diferencia registrada" : `Diferencia ${formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents)}`, tone: snapshot.cashCurrent.differenceCents === 0 ? "sano" : "revisar" },
    { label: "Inventario", value: `${snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder} señales`, detail: snapshot.inventoryWatchlist.items.length > 0 ? "Productos que pueden pegarle a venta hoy" : "Watchlist esperando SKUs reales", tone: snapshot.inventoryWatchlist.counts.critical > 0 ? "urgente" : snapshot.inventoryWatchlist.items.length === 0 ? "revisar" : "sano" },
    { label: "Alertas", value: `${snapshot.alerts.counts.total} activas`, detail: `${snapshot.alerts.counts.critical} críticas · ${snapshot.alerts.counts.high} altas`, tone: snapshot.alerts.counts.critical > 0 ? "urgente" : snapshot.alerts.counts.total > 0 ? "revisar" : "sano" },
    { label: "Sucursales", value: `${snapshot.branches.counts.total} registradas`, detail: `${snapshot.branches.counts.offline} offline · ${snapshot.branches.counts.review} por revisar`, tone: snapshot.branches.counts.offline > 0 ? "offline" : "sano" }
  ] as const;
}

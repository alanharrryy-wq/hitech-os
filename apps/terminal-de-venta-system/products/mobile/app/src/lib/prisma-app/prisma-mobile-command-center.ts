import type { PrismaMobileAlert, PrismaMobileBranch, PrismaMobileInventoryItem } from "./prisma-app-api-contracts";
import type { PrismaMobileClientSnapshot, PrismaMobileSnapshotPayload } from "./prisma-mobile-snapshot-contract";
import { formatSignedMxnFromCents } from "./prisma-mobile-formatters";

export const PRISMA_MOBILE_COMMAND_CENTER_CONTRACT_ID = "PRISMA_APP_MOBILE_20_COMMAND_CENTER";

export type PrismaMobileCommandTone = "sano" | "revisar" | "urgente" | "offline";
export type PrismaMobileDecisionKind = "cash" | "inventory" | "sync" | "sales" | "branch" | "data";

export type PrismaMobileCommandDecision = {
  id: string;
  kind: PrismaMobileDecisionKind;
  title: string;
  value: string;
  detail: string;
  action: string;
  owner: string;
  tone: PrismaMobileCommandTone;
  score: number;
};

export type PrismaMobileCommandBrief = {
  title: string;
  detail: string;
  tone: PrismaMobileCommandTone;
};

export type PrismaMobileCommandSignal = {
  label: string;
  value: string;
  detail: string;
  tone: PrismaMobileCommandTone;
  progress: number;
};

export type PrismaMobileCommandCenter = {
  contractId: typeof PRISMA_MOBILE_COMMAND_CENTER_CONTRACT_ID;
  readinessScore: number;
  riskScore: number;
  riskLabel: string;
  riskTone: PrismaMobileCommandTone;
  primaryBrief: PrismaMobileCommandBrief;
  ownerBriefs: PrismaMobileCommandBrief[];
  decisionQueue: PrismaMobileCommandDecision[];
  signals: PrismaMobileCommandSignal[];
  dataQuality: {
    label: string;
    detail: string;
    tone: PrismaMobileCommandTone;
    upstreamOk: number;
    upstreamTotal: number;
  };
  followUp: {
    title: string;
    detail: string;
    items: string[];
  };
};

function clamp(value: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, Math.round(value)));
}

function absoluteCashExposure(snapshot: PrismaMobileSnapshotPayload): number {
  return Math.abs(snapshot.cashCurrent.differenceCents);
}

function cashRisk(snapshot: PrismaMobileSnapshotPayload): number {
  const exposure = absoluteCashExposure(snapshot);
  if (exposure >= 20000) return 25;
  if (exposure >= 5000) return 14;
  if (exposure > 0) return 6;
  return 0;
}

function alertRisk(snapshot: PrismaMobileSnapshotPayload): number {
  return clamp(snapshot.alerts.counts.critical * 18 + snapshot.alerts.counts.high * 9 + snapshot.alerts.counts.medium * 4, 0, 35);
}

function inventoryRisk(snapshot: PrismaMobileSnapshotPayload): number {
  return clamp(snapshot.inventoryWatchlist.counts.critical * 12 + snapshot.inventoryWatchlist.counts.reorder * 5 + snapshot.inventoryWatchlist.counts.overstock * 2, 0, 30);
}

function syncRisk(snapshot: PrismaMobileSnapshotPayload): number {
  const syncKpi = snapshot.summary.kpis.find((kpi) => kpi.key === "sync");
  const pending = typeof syncKpi?.numericValue === "number" ? syncKpi.numericValue : 0;
  const failed = snapshot.cashCurrent.status.toLowerCase().includes("fall") ? 1 : 0;
  return clamp(pending * 5 + failed * 12 + snapshot.branches.counts.offline * 18 + snapshot.branches.counts.review * 6, 0, 28);
}

function salesRisk(snapshot: PrismaMobileSnapshotPayload): number {
  if (snapshot.salesToday.tickets === 0) return 12;
  if (snapshot.salesToday.averageTicketCents === 0) return 10;
  return snapshot.salesToday.deltaAgainstYesterday.trim().startsWith("-") ? 8 : 0;
}

function riskTone(score: number, snapshot: PrismaMobileSnapshotPayload): PrismaMobileCommandTone {
  if (snapshot.branches.counts.offline > 0) return "offline";
  if (score >= 70) return "urgente";
  if (score >= 34) return "revisar";
  return "sano";
}

function riskLabel(tone: PrismaMobileCommandTone, score: number): string {
  if (tone === "offline") return "Operación con zonas offline";
  if (tone === "urgente") return `Riesgo alto ${score}/100`;
  if (tone === "revisar") return `Riesgo moderado ${score}/100`;
  return `Operación controlada ${score}/100`;
}

function decisionTone(score: number, offline = false): PrismaMobileCommandTone {
  if (offline) return "offline";
  if (score >= 24) return "urgente";
  if (score >= 9) return "revisar";
  return "sano";
}

function topInventory(snapshot: PrismaMobileSnapshotPayload): PrismaMobileInventoryItem | null {
  const items = [...snapshot.inventoryWatchlist.items];
  items.sort((a, b) => {
    const stateWeight = (item: PrismaMobileInventoryItem) => item.state === "critico" ? 4 : item.state === "reponer" ? 3 : item.state === "sobrestock" ? 2 : 1;
    return stateWeight(b) - stateWeight(a) || b.weeklyUnitsSold - a.weeklyUnitsSold || a.stockQty - b.stockQty;
  });
  return items[0] ?? null;
}

function topAlert(snapshot: PrismaMobileSnapshotPayload): PrismaMobileAlert | null {
  const alerts = [...snapshot.alerts.alerts];
  const severityWeight: Record<PrismaMobileAlert["severity"], number> = { critica: 4, alta: 3, media: 2, info: 1 };
  alerts.sort((a, b) => severityWeight[b.severity] - severityWeight[a.severity]);
  return alerts[0] ?? null;
}

function topBranch(snapshot: PrismaMobileSnapshotPayload): PrismaMobileBranch | null {
  const branches = [...snapshot.branches.branches];
  const statusWeight: Record<PrismaMobileBranch["status"], number> = { offline: 4, urgente: 3, revisar: 2, sano: 1 };
  branches.sort((a, b) => statusWeight[b.status] - statusWeight[a.status] || b.alerts - a.alerts);
  return branches[0] ?? null;
}

function buildDecisionQueue(snapshot: PrismaMobileSnapshotPayload, client: PrismaMobileClientSnapshot): PrismaMobileCommandDecision[] {
  const cashScore = cashRisk(snapshot);
  const inventoryScore = inventoryRisk(snapshot);
  const alertsScore = alertRisk(snapshot);
  const syncScore = syncRisk(snapshot);
  const salesScore = salesRisk(snapshot);
  const inventory = topInventory(snapshot);
  const alert = topAlert(snapshot);
  const branch = topBranch(snapshot);

  const decisions: PrismaMobileCommandDecision[] = [
    {
      id: "cash-control",
      kind: "cash",
      title: "Caja y corte",
      value: formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents),
      detail: snapshot.cashCurrent.differenceCents === 0 ? "La caja no reporta diferencia contra esperado." : `Diferencia contra esperado con corte ${snapshot.cashCurrent.lastCut}.`,
      action: snapshot.cashCurrent.differenceCents === 0 ? "Mantener vigilancia normal." : "Pedir conteo rápido antes del siguiente cierre.",
      owner: "Encargado de turno",
      tone: decisionTone(cashScore),
      score: cashScore
    },
    {
      id: "inventory-pressure",
      kind: "inventory",
      title: "Inventario que puede frenar venta",
      value: `${snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder} SKUs`,
      detail: inventory ? `${inventory.name} · ${inventory.stock} · ${inventory.movement}` : "Sin productos en lista de vigilancia.",
      action: inventory ? "Revisar existencia física y preparar reabasto." : "Mantener monitoreo operativo.",
      owner: "Inventario",
      tone: decisionTone(inventoryScore),
      score: inventoryScore
    },
    {
      id: "alert-priority",
      kind: "branch",
      title: "Alerta más importante",
      value: `${snapshot.alerts.counts.total} activas`,
      detail: alert ? `${alert.area}: ${alert.title}` : "No hay alertas activas.",
      action: alert ? alert.action : "Sin acción urgente.",
      owner: "Dueño / supervisor",
      tone: decisionTone(alertsScore),
      score: alertsScore
    },
    {
      id: "sync-readiness",
      kind: "sync",
      title: "Estado de sincronización",
      value: client.stale ? "respaldo local" : "datos frescos",
      detail: client.errors.length > 0 ? client.errors.slice(0, 2).join(" · ") : `Fuente activa: ${client.source}`,
      action: client.stale ? "Actualizar conexión antes de decisiones sensibles." : "Usar datos para seguimiento normal.",
      owner: "Operación",
      tone: decisionTone(syncScore, snapshot.branches.counts.offline > 0),
      score: syncScore
    },
    {
      id: "sales-rhythm",
      kind: "sales",
      title: "Ritmo de venta",
      value: snapshot.salesToday.totalSalesLabel,
      detail: `${snapshot.salesToday.tickets} tickets · categoría fuerte: ${snapshot.salesToday.strongCategory}`,
      action: snapshot.salesToday.tickets === 0 ? "Confirmar que Tablet esté registrando ventas." : "Comparar contra cierre y ticket promedio.",
      owner: "Dueño",
      tone: decisionTone(salesScore),
      score: salesScore
    },
    {
      id: "branch-status",
      kind: "branch",
      title: "Sucursal que pide mirada",
      value: branch ? branch.name : "Sin sucursal",
      detail: branch ? `${branch.cashState} · ${branch.alerts} alertas · sync ${branch.syncLag}` : "No hay sucursales registradas.",
      action: branch && branch.status !== "sano" ? "Contactar responsable y validar operación." : "Sin intervención de sucursal.",
      owner: "Supervisor",
      tone: branch ? branch.status : "sano",
      score: branch ? (branch.status === "offline" ? 28 : branch.status === "urgente" ? 24 : branch.status === "revisar" ? 10 : 0) : 0
    }
  ];

  return decisions.sort((a, b) => b.score - a.score).slice(0, 6);
}

function buildOwnerBriefs(decisions: PrismaMobileCommandDecision[]): PrismaMobileCommandBrief[] {
  const top = decisions.slice(0, 3);
  if (top.length === 0) {
    return [{ title: "Sin frentes abiertos", detail: "La app no encontró focos operativos fuertes.", tone: "sano" }];
  }
  return top.map((decision, index) => ({
    title: index === 0 ? "Primero" : index === 1 ? "Después" : "Luego",
    detail: `${decision.title}: ${decision.action}`,
    tone: decision.tone
  }));
}

function buildSignals(snapshot: PrismaMobileSnapshotPayload, client: PrismaMobileClientSnapshot): PrismaMobileCommandSignal[] {
  const totalInventory = snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder + snapshot.inventoryWatchlist.counts.normal + snapshot.inventoryWatchlist.counts.overstock;
  const pressuredInventory = snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder;
  const inventoryProgress = totalInventory > 0 ? (pressuredInventory / totalInventory) * 100 : 0;
  const upstreamTotal = snapshot.health.upstreams.length;
  const upstreamOk = snapshot.health.upstreams.filter((upstream) => upstream.ok).length;
  const dataProgress = upstreamTotal > 0 ? (upstreamOk / upstreamTotal) * 100 : client.stale ? 35 : 100;

  return [
    {
      label: "Presión de inventario",
      value: `${pressuredInventory}/${Math.max(totalInventory, pressuredInventory)}`,
      detail: "SKUs críticos o por reponer contra watchlist total.",
      tone: pressuredInventory > 0 ? "revisar" : "sano",
      progress: clamp(inventoryProgress)
    },
    {
      label: "Caja",
      value: formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents),
      detail: "Diferencia operativa visible desde móvil.",
      tone: decisionTone(cashRisk(snapshot)),
      progress: clamp(Math.min(100, absoluteCashExposure(snapshot) / 250))
    },
    {
      label: "Datos conectados",
      value: upstreamTotal === 0 ? (client.stale ? "respaldo" : "sin probes") : `${upstreamOk}/${upstreamTotal}`,
      detail: client.stale ? "La app está apoyándose en caché local." : "Lecturas activas de Tablet/PC disponibles.",
      tone: client.stale ? "offline" : upstreamTotal > 0 && upstreamOk < upstreamTotal ? "revisar" : "sano",
      progress: clamp(dataProgress)
    },
    {
      label: "Ritmo comercial",
      value: snapshot.salesToday.deltaAgainstYesterday,
      detail: `${snapshot.salesToday.tickets} tickets registrados hoy.`,
      tone: snapshot.salesToday.deltaAgainstYesterday.trim().startsWith("-") ? "revisar" : "sano",
      progress: clamp(snapshot.salesToday.tickets > 0 ? 72 : 12)
    }
  ];
}

function buildDataQuality(snapshot: PrismaMobileSnapshotPayload, client: PrismaMobileClientSnapshot) {
  const upstreamTotal = snapshot.health.upstreams.length;
  const upstreamOk = snapshot.health.upstreams.filter((upstream) => upstream.ok).length;
  if (client.stale) {
    return { label: "Respaldo local", detail: "Hay datos visibles, pero requieren refresco antes de decisiones pesadas.", tone: "offline" as const, upstreamOk, upstreamTotal };
  }
  if (upstreamTotal > 0 && upstreamOk < upstreamTotal) {
    return { label: "Lectura parcial", detail: "Algunas fuentes respondieron y otras no. Sirve para operar, no para auditoría fina.", tone: "revisar" as const, upstreamOk, upstreamTotal };
  }
  return { label: "Datos listos", detail: "Snapshot móvil con fuentes conectadas y sin degradación visible.", tone: "sano" as const, upstreamOk, upstreamTotal };
}

function buildFollowUp(decisions: PrismaMobileCommandDecision[]) {
  const items = decisions.slice(0, 4).map((decision) => `${decision.owner}: ${decision.action}`);
  return {
    title: "Siguiente ronda recomendada",
    detail: "Orden de intervención para que el dueño no revise todo como quien busca llaves en una feria.",
    items: items.length > 0 ? items : ["Mantener monitoreo normal y revisar cierre operativo."]
  };
}

export function buildPrismaMobileCommandCenter(client: PrismaMobileClientSnapshot): PrismaMobileCommandCenter {
  const snapshot = client.snapshot;
  const riskScore = clamp(alertRisk(snapshot) + inventoryRisk(snapshot) + cashRisk(snapshot) + syncRisk(snapshot) + salesRisk(snapshot));
  const readinessScore = clamp(100 - riskScore + (client.stale ? -12 : 0));
  const tone = riskTone(riskScore, snapshot);
  const decisionQueue = buildDecisionQueue(snapshot, client);
  const primary = decisionQueue[0];

  return {
    contractId: PRISMA_MOBILE_COMMAND_CENTER_CONTRACT_ID,
    readinessScore,
    riskScore,
    riskLabel: riskLabel(tone, riskScore),
    riskTone: tone,
    primaryBrief: primary
      ? { title: "Mandato inmediato", detail: `${primary.title}: ${primary.action}`, tone: primary.tone }
      : { title: "Mandato inmediato", detail: "Sin intervención urgente detectada.", tone: "sano" },
    ownerBriefs: buildOwnerBriefs(decisionQueue),
    decisionQueue,
    signals: buildSignals(snapshot, client),
    dataQuality: buildDataQuality(snapshot, client),
    followUp: buildFollowUp(decisionQueue)
  };
}

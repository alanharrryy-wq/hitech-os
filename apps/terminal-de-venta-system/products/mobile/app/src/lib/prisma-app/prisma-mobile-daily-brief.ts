import type { PrismaMobileSnapshotPayload } from "./prisma-mobile-snapshot-contract";
import type { PrismaMobileCommandTone } from "./prisma-mobile-command-center";
import { buildPrismaMobileCommandCenter } from "./prisma-mobile-command-center";
import { buildPrismaMobileActionInbox, type PrismaMobileOwnerAction } from "./prisma-mobile-action-inbox";
import type { PrismaMobileClientSnapshot } from "./prisma-mobile-snapshot-contract";
import { formatInteger, formatSignedMxnFromCents } from "./prisma-mobile-formatters";

export const PRISMA_MOBILE_DAILY_BRIEF_CONTRACT_ID = "PRISMA_APP_MOBILE_22_DAILY_BRIEF";

export type PrismaMobileDailyBriefCard = {
  label: string;
  value: string;
  detail: string;
  tone: PrismaMobileCommandTone;
};

export type PrismaMobileDailyBriefSection = {
  id: string;
  title: string;
  subtitle: string;
  tone: PrismaMobileCommandTone;
  bullets: string[];
};

export type PrismaMobileDailyBrief = {
  contractId: typeof PRISMA_MOBILE_DAILY_BRIEF_CONTRACT_ID;
  generatedLabel: string;
  headline: string;
  subheadline: string;
  readinessLabel: string;
  shareTitle: string;
  whatsappText: string;
  emailSubject: string;
  emailBody: string;
  exportText: string;
  copyHint: string;
  cards: PrismaMobileDailyBriefCard[];
  sections: PrismaMobileDailyBriefSection[];
  closingChecklist: string[];
  riskTone: PrismaMobileCommandTone;
};

const toneLabel: Record<PrismaMobileCommandTone, string> = {
  sano: "Sano",
  revisar: "Revisar",
  urgente: "Urgente",
  offline: "Sin conexión"
};

function topActions(actions: PrismaMobileOwnerAction[], count: number): PrismaMobileOwnerAction[] {
  return actions.filter((action) => !action.id.startsWith("empty-")).slice(0, count);
}

function buildCashLine(snapshot: PrismaMobileSnapshotPayload): string {
  if (snapshot.cashCurrent.differenceCents === 0) return `Caja sin diferencia registrada en corte ${snapshot.cashCurrent.lastCut}.`;
  return `Caja con diferencia ${formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents)} en corte ${snapshot.cashCurrent.lastCut}.`;
}

function buildInventoryLine(snapshot: PrismaMobileSnapshotPayload): string {
  const risk = snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder;
  if (risk === 0) return "Inventario sin señales críticas para venta inmediata.";
  const names = snapshot.inventoryWatchlist.items
    .filter((item) => item.state === "critico" || item.state === "reponer")
    .slice(0, 3)
    .map((item) => item.name)
    .join(", ");
  return `${risk} señales de inventario por atender${names ? `: ${names}` : ""}.`;
}

function buildBranchLine(snapshot: PrismaMobileSnapshotPayload): string {
  const flagged = snapshot.branches.counts.offline + snapshot.branches.counts.urgent + snapshot.branches.counts.review;
  if (flagged === 0) return `${snapshot.branches.counts.total} sucursales sin bloqueo operativo visible.`;
  return `${flagged} sucursales requieren revisión; ${snapshot.branches.counts.offline} offline.`;
}

function buildActionLine(action: PrismaMobileOwnerAction): string {
  return `${action.owner}: ${action.title} - ${action.recommendedAction}.`;
}

function sectionTone(actions: PrismaMobileOwnerAction[], fallback: PrismaMobileCommandTone): PrismaMobileCommandTone {
  if (actions.some((action) => action.tone === "offline")) return "offline";
  if (actions.some((action) => action.tone === "urgente")) return "urgente";
  if (actions.some((action) => action.tone === "revisar")) return "revisar";
  return fallback;
}

function joinLines(lines: string[]): string {
  return lines.filter(Boolean).join("\n");
}

export function buildPrismaMobileDailyBrief(client: PrismaMobileClientSnapshot): PrismaMobileDailyBrief {
  const snapshot = client.snapshot;
  const command = buildPrismaMobileCommandCenter(client);
  const inbox = buildPrismaMobileActionInbox(client);
  const actions = topActions(inbox.lanes.flatMap((lane) => lane.actions), 6);
  const immediateActions = actions.filter((action) => action.lane === "ahora").slice(0, 3);
  const todayActions = actions.filter((action) => action.lane !== "ahora").slice(0, 3);
  const inventoryRisk = snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder;
  const branchRisk = snapshot.branches.counts.offline + snapshot.branches.counts.urgent + snapshot.branches.counts.review;
  const alertRisk = snapshot.alerts.counts.critical + snapshot.alerts.counts.high;
  const cashLine = buildCashLine(snapshot);
  const inventoryLine = buildInventoryLine(snapshot);
  const branchLine = buildBranchLine(snapshot);
  const headline = `${snapshot.summary.businessName}: ${snapshot.salesToday.totalSalesLabel} hoy`;
  const subheadline = `${formatInteger(snapshot.salesToday.tickets)} tickets, ticket promedio ${snapshot.salesToday.averageTicketLabel}, ${toneLabel[command.riskTone].toLowerCase()} para decidir.`;
  const generatedLabel = snapshot.summary.generatedLabel || `Fuente ${client.source}`;
  const readinessLabel = `${command.readinessScore}% listo - riesgo ${command.riskLabel}`;
  const opening = `${headline}. ${subheadline}`;
  const actionLines = actions.length > 0 ? actions.slice(0, 5).map(buildActionLine) : ["Sin acciones urgentes detectadas; mantener seguimiento y revisar corte."];
  const whatsappLines = [
    `PRISMA - Resumen operativo`,
    opening,
    cashLine,
    inventoryLine,
    branchLine,
    "Acciones:",
    ...actionLines.map((line, index) => `${index + 1}. ${line}`),
    `Dato: ${client.stale ? "respaldo local / revisar conexión" : "fuente conectada"}.`
  ];
  const emailBody = joinLines([
    `Resumen PRISMA para ${snapshot.summary.businessName}`,
    "",
    opening,
    cashLine,
    inventoryLine,
    branchLine,
    "",
    "Acciones sugeridas:",
    ...actionLines.map((line, index) => `${index + 1}. ${line}`),
    "",
    `Calidad del dato: ${command.dataQuality.label}. ${command.dataQuality.detail}`
  ]);
  const sections: PrismaMobileDailyBriefSection[] = [
    {
      id: "lectura-dueno",
      title: "Lectura del dueño",
      subtitle: command.primaryBrief.title,
      tone: command.primaryBrief.tone,
      bullets: [command.primaryBrief.detail, cashLine, branchLine]
    },
    {
      id: "acciones-ahora",
      title: "Resolver ahora",
      subtitle: `${immediateActions.length} acciones inmediatas`,
      tone: sectionTone(immediateActions, command.riskTone),
      bullets: immediateActions.length > 0 ? immediateActions.map(buildActionLine) : ["No hay incendio inmediato; revisar señales de hoy antes del corte."]
    },
    {
      id: "seguimiento-hoy",
      title: "Seguimiento hoy",
      subtitle: `${todayActions.length} acciones antes del cierre`,
      tone: sectionTone(todayActions, "revisar"),
      bullets: todayActions.length > 0 ? todayActions.map(buildActionLine) : ["Mantener monitoreo; sin pendientes fuertes de seguimiento."]
    },
    {
      id: "inventario-ventas",
      title: "Inventario y venta",
      subtitle: `${inventoryRisk} señales de producto, ${alertRisk} alertas altas/críticas`,
      tone: inventoryRisk > 0 || alertRisk > 0 ? "revisar" : "sano",
      bullets: [inventoryLine, `Categoría fuerte: ${snapshot.salesToday.strongCategory}.`, `${snapshot.alerts.counts.total} alertas activas en total.`]
    }
  ];
  const closingChecklist = [
    "Confirmar caja y diferencia antes del corte.",
    "Validar productos críticos o sin stock antes de reabasto.",
    "Revisar sucursales offline o con alerta antes de cerrar el día.",
    "Compartir resumen operativo al encargado si hay acciones abiertas."
  ];
  const exportText = joinLines([
    `# PRISMA Daily Brief`,
    `Negocio: ${snapshot.summary.businessName}`,
    `Generado: ${generatedLabel}`,
    `Fuente: ${client.source}${client.stale ? " (respaldo local)" : ""}`,
    "",
    opening,
    cashLine,
    inventoryLine,
    branchLine,
    "",
    "## Acciones",
    ...actionLines.map((line) => `- ${line}`),
    "",
    "## Checklist de cierre",
    ...closingChecklist.map((line) => `- ${line}`)
  ]);
  return {
    contractId: PRISMA_MOBILE_DAILY_BRIEF_CONTRACT_ID,
    generatedLabel,
    headline,
    subheadline,
    readinessLabel,
    shareTitle: "Resumen listo para compartir",
    whatsappText: whatsappLines.join("\n"),
    emailSubject: `PRISMA - Resumen operativo ${snapshot.summary.businessName}`,
    emailBody,
    exportText,
    copyHint: "Copia este resumen para WhatsApp, correo o cierre de turno.",
    cards: [
      { label: "Venta", value: snapshot.salesToday.totalSalesLabel, detail: `${snapshot.salesToday.tickets} tickets`, tone: "sano" },
      { label: "Caja", value: formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents), detail: snapshot.cashCurrent.status, tone: snapshot.cashCurrent.differenceCents === 0 ? "sano" : "revisar" },
      { label: "Inventario", value: `${inventoryRisk}`, detail: "señales a revisar", tone: inventoryRisk > 0 ? "revisar" : "sano" },
      { label: "Sucursales", value: `${branchRisk}`, detail: "requieren atención", tone: branchRisk > 0 ? "urgente" : "sano" }
    ],
    sections,
    closingChecklist,
    riskTone: command.riskTone
  };
}

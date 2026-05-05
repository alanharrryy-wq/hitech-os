import type { PrismaMobileAlert, PrismaMobileBranch, PrismaMobileInventoryItem, PrismaMobileSalesPoint } from "./prisma-app-api-contracts";
import type { PrismaMobileClientSnapshot } from "./prisma-mobile-snapshot-contract";
import type { PrismaMobileCommandTone } from "./prisma-mobile-command-center";
import { buildPrismaMobileCommandCenter } from "./prisma-mobile-command-center";
import { buildPrismaMobileActionInbox } from "./prisma-mobile-action-inbox";
import { buildPrismaMobileDecisionLedger } from "./prisma-mobile-decision-ledger";
import { formatInteger, formatMxnFromCents, formatSignedMxnFromCents } from "./prisma-mobile-formatters";

export const PRISMA_MOBILE_PULSE_TIMELINE_CONTRACT_ID = "PRISMA_APP_MOBILE_24_PULSE_TIMELINE";

export type PrismaMobilePulsePhase = "apertura" | "operacion" | "pico" | "cierre" | "seguimiento";
export type PrismaMobilePulseSource = "ventas" | "caja" | "inventario" | "alertas" | "sucursal" | "decision" | "datos";

export type PrismaMobilePulseTimelineEvent = {
  id: string;
  sequence: number;
  phase: PrismaMobilePulsePhase;
  source: PrismaMobilePulseSource;
  timeLabel: string;
  title: string;
  detail: string;
  owner: string;
  tone: PrismaMobileCommandTone;
  priorityScore: number;
  evidence: string[];
  nextCheck: string;
};

export type PrismaMobilePulseTimelineCard = {
  label: string;
  value: string;
  detail: string;
  tone: PrismaMobileCommandTone;
};

export type PrismaMobilePulseTimelineCheckpoint = {
  label: string;
  title: string;
  detail: string;
  tone: PrismaMobileCommandTone;
  checklist: string[];
};

export type PrismaMobilePulseTimeline = {
  contractId: typeof PRISMA_MOBILE_PULSE_TIMELINE_CONTRACT_ID;
  headline: string;
  subheadline: string;
  generatedLabel: string;
  pulseLabel: string;
  nowCheckpoint: PrismaMobilePulseTimelineCheckpoint;
  cards: PrismaMobilePulseTimelineCard[];
  events: PrismaMobilePulseTimelineEvent[];
  ownerNarrative: string[];
  exportText: string;
};

function normalizeId(value: string): string {
  return value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 80) || "pulse";
}

function toneRank(tone: PrismaMobileCommandTone): number {
  return tone === "offline" ? 4 : tone === "urgente" ? 3 : tone === "revisar" ? 2 : 1;
}

function phaseRank(phase: PrismaMobilePulsePhase): number {
  return phase === "apertura" ? 1 : phase === "operacion" ? 2 : phase === "pico" ? 3 : phase === "seguimiento" ? 4 : 5;
}

function eventToneFromScore(score: number, fallback: PrismaMobileCommandTone = "sano"): PrismaMobileCommandTone {
  if (fallback === "offline") return "offline";
  if (score >= 75) return "urgente";
  if (score >= 38) return "revisar";
  return fallback;
}

function sortEvents(events: PrismaMobilePulseTimelineEvent[]): PrismaMobilePulseTimelineEvent[] {
  return [...events]
    .sort((a, b) => phaseRank(a.phase) - phaseRank(b.phase) || toneRank(b.tone) - toneRank(a.tone) || b.priorityScore - a.priorityScore || a.sequence - b.sequence)
    .map((event, index) => ({ ...event, sequence: index + 1 }));
}

function dedupeEvents(events: PrismaMobilePulseTimelineEvent[]): PrismaMobilePulseTimelineEvent[] {
  const seen = new Set<string>();
  const kept: PrismaMobilePulseTimelineEvent[] = [];
  for (const event of events) {
    const key = `${event.phase}|${event.title}|${event.owner}`.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    kept.push(event);
  }
  return kept;
}

function salesEvents(points: PrismaMobileSalesPoint[]): PrismaMobilePulseTimelineEvent[] {
  if (points.length === 0) return [];
  const ranked = [...points].sort((a, b) => b.amountCents - a.amountCents);
  const peak = ranked[0];
  const last = points[points.length - 1];
  const first = points[0];
  const peakScore = Math.min(90, Math.round(peak.amountCents / 1200));
  return [
    {
      id: `ventas-apertura-${normalizeId(first.hour)}`,
      sequence: 0,
      phase: "apertura",
      source: "ventas",
      timeLabel: first.hour,
      title: "Arranque comercial registrado",
      detail: `${first.label} reportó ${first.amount}; sirve como base para comparar el ritmo del día.`,
      owner: "Dueño",
      tone: "sano",
      priorityScore: Math.min(35, Math.round(first.amountCents / 1800)),
      evidence: [`Monto: ${first.amount}`, `Etiqueta: ${first.label}`, `Lectura: línea de ventas`],
      nextCheck: "comparar contra el primer pico de venta"
    },
    {
      id: `ventas-pico-${normalizeId(peak.hour)}`,
      sequence: 0,
      phase: "pico",
      source: "ventas",
      timeLabel: peak.hour,
      title: "Pico de venta detectado",
      detail: `${peak.label} concentra ${peak.amount}; conviene validar surtido y caja después del pico.`,
      owner: "Encargado de turno",
      tone: eventToneFromScore(peakScore, "sano"),
      priorityScore: peakScore,
      evidence: [`Venta pico: ${peak.amount}`, `Hora: ${peak.hour}`, `Altura visual: ${peak.height}`],
      nextCheck: "validar stock y diferencia de caja al bajar el flujo"
    },
    {
      id: `ventas-cierre-${normalizeId(last.hour)}`,
      sequence: 0,
      phase: "cierre",
      source: "ventas",
      timeLabel: last.hour,
      title: "Último corte comercial del día",
      detail: `${last.label} cerró con ${last.amount}; usarlo para preparar brief y caja.`,
      owner: "Encargado de turno",
      tone: "sano",
      priorityScore: Math.min(45, Math.round(last.amountCents / 1500)),
      evidence: [`Última lectura: ${last.amount}`, `Tickets del día visibles en snapshot`, `Brief diario disponible`],
      nextCheck: "comparar con brief diario antes de compartir"
    }
  ];
}

function cashEvent(client: PrismaMobileClientSnapshot): PrismaMobilePulseTimelineEvent | null {
  const cash = client.snapshot.cashCurrent;
  const exposure = Math.abs(cash.differenceCents);
  if (exposure === 0) {
    return {
      id: "caja-sin-diferencia",
      sequence: 0,
      phase: "cierre",
      source: "caja",
      timeLabel: cash.lastCut,
      title: "Caja sin diferencia visible",
      detail: `Corte ${cash.lastCut} coincide con lo esperado.`,
      owner: "Encargado de turno",
      tone: "sano",
      priorityScore: 8,
      evidence: [`Esperado: ${cash.expectedLabel}`, `Contado: ${cash.countedLabel}`, "Diferencia: $0"],
      nextCheck: "guardar cierre normal"
    };
  }
  const score = exposure >= 20000 ? 92 : exposure >= 5000 ? 64 : 38;
  return {
    id: "caja-diferencia-pulso",
    sequence: 0,
    phase: "cierre",
    source: "caja",
    timeLabel: cash.lastCut,
    title: "Diferencia de caja cambia el cierre",
    detail: `Hay ${formatSignedMxnFromCents(cash.differenceCents)} contra lo esperado; debe quedar explicado antes de cerrar.`,
    owner: "Encargado de turno",
    tone: eventToneFromScore(score, "revisar"),
    priorityScore: score,
    evidence: [`Esperado: ${cash.expectedLabel}`, `Contado: ${cash.countedLabel}`, `Diferencia: ${formatSignedMxnFromCents(cash.differenceCents)}`],
    nextCheck: "pedir reconteo y registrar motivo"
  };
}

function inventoryEvents(items: PrismaMobileInventoryItem[]): PrismaMobilePulseTimelineEvent[] {
  return items
    .filter((item) => item.state === "critico" || item.state === "reponer" || item.state === "sobrestock")
    .slice(0, 5)
    .map((item, index) => {
      const score = item.state === "critico" ? 88 : item.state === "reponer" ? 58 : 36;
      const title = item.state === "critico" ? "Riesgo de quiebre en inventario" : item.state === "reponer" ? "Reabasto pendiente antes del siguiente pico" : "Sobrestock para revisar";
      const action = item.state === "critico" ? "confirmar existencia física y surtir" : item.state === "reponer" ? "preparar reposición" : "validar rotación y espacio";
      return {
        id: `inventario-${normalizeId(item.sku)}-${index}`,
        sequence: 0,
        phase: item.state === "sobrestock" ? "seguimiento" : "operacion",
        source: "inventario",
        timeLabel: "durante venta",
        title,
        detail: `${item.name} (${item.sku}) tiene ${item.stock}; movimiento ${item.movement}.`,
        owner: "Encargado de piso",
        tone: eventToneFromScore(score, "revisar"),
        priorityScore: score,
        evidence: [`Stock: ${item.stock}`, `Venta semanal: ${formatInteger(item.weeklyUnitsSold)} uds`, `Categoría: ${item.category}`],
        nextCheck: action
      };
    });
}

function alertEvents(alerts: PrismaMobileAlert[]): PrismaMobilePulseTimelineEvent[] {
  return alerts.slice(0, 5).map((alert, index) => {
    const score = alert.severity === "critica" ? 96 : alert.severity === "alta" ? 76 : alert.severity === "media" ? 48 : 22;
    return {
      id: `alerta-${normalizeId(alert.id)}-${index}`,
      sequence: 0,
      phase: alert.severity === "critica" || alert.severity === "alta" ? "operacion" : "seguimiento",
      source: "alertas",
      timeLabel: alert.time,
      title: alert.title,
      detail: alert.detail,
      owner: alert.area,
      tone: alert.severity === "critica" ? "urgente" : eventToneFromScore(score, "revisar"),
      priorityScore: score,
      evidence: [`Área: ${alert.area}`, `Severidad: ${alert.severity}`, `Acción: ${alert.action}`],
      nextCheck: alert.action
    };
  });
}

function branchEvents(branches: PrismaMobileBranch[]): PrismaMobilePulseTimelineEvent[] {
  return branches
    .filter((branch) => branch.status !== "sano")
    .slice(0, 4)
    .map((branch, index) => {
      const score = branch.status === "offline" ? 94 : branch.status === "urgente" ? 82 : 52;
      return {
        id: `sucursal-${normalizeId(branch.name)}-${index}`,
        sequence: 0,
        phase: branch.status === "offline" ? "operacion" : "seguimiento",
        source: "sucursal",
        timeLabel: branch.syncLag,
        title: `Sucursal ${branch.name} requiere seguimiento`,
        detail: `${branch.salesToday} · ${branch.cashState} · ${branch.alerts} alertas.`,
        owner: "Supervisor",
        tone: branch.status,
        priorityScore: score,
        evidence: [`Tickets: ${formatInteger(branch.tickets)}`, `Variación: ${branch.salesDelta}`, `Sync: ${branch.syncLag}`],
        nextCheck: branch.status === "offline" ? "recuperar conexión y confirmar operación sensible" : "contactar encargado"
      };
    });
}

function decisionEvents(client: PrismaMobileClientSnapshot): PrismaMobilePulseTimelineEvent[] {
  const ledger = buildPrismaMobileDecisionLedger(client);
  return ledger.entries.slice(0, 4).map((entry, index) => ({
    id: `decision-${normalizeId(entry.id)}-${index}`,
    sequence: 0,
    phase: entry.tone === "urgente" || entry.tone === "offline" ? "operacion" : "seguimiento",
    source: "decision",
    timeLabel: entry.dueLabel,
    title: entry.title,
    detail: entry.summary,
    owner: entry.owner,
    tone: entry.tone,
    priorityScore: entry.priorityScore,
    evidence: entry.evidence.slice(0, 3),
    nextCheck: entry.nextStep
  }));
}

function dataQualityEvent(client: PrismaMobileClientSnapshot): PrismaMobilePulseTimelineEvent | null {
  if (!client.stale && client.errors.length === 0) return null;
  return {
    id: "datos-fuente-pulso",
    sequence: 0,
    phase: "apertura",
    source: "datos",
    timeLabel: "lectura móvil",
    title: "Fuente de datos requiere confirmación",
    detail: client.errors.length > 0 ? client.errors.slice(0, 2).join(" · ") : "La app conserva lectura con respaldo local.",
    owner: "Operación",
    tone: client.source === "unavailable" ? "offline" : "revisar",
    priorityScore: client.source === "unavailable" ? 90 : 44,
    evidence: [`Fuente: ${client.source}`, `Respaldo: ${client.stale ? "sí" : "no"}`, `Errores: ${formatInteger(client.errors.length)}`],
    nextCheck: "refrescar datos antes de autorizar decisiones sensibles"
  };
}

function buildCards(client: PrismaMobileClientSnapshot, events: PrismaMobilePulseTimelineEvent[]): PrismaMobilePulseTimelineCard[] {
  const urgent = events.filter((event) => event.tone === "urgente" || event.tone === "offline").length;
  const review = events.filter((event) => event.tone === "revisar").length;
  const cash = client.snapshot.cashCurrent.differenceCents;
  const peak = Math.max(0, ...client.snapshot.salesToday.timeline.map((point) => point.amountCents));
  return [
    { label: "Eventos", value: formatInteger(events.length), detail: "pulso del día", tone: urgent > 0 ? "urgente" : review > 0 ? "revisar" : "sano" },
    { label: "Críticos", value: formatInteger(urgent), detail: "resolver primero", tone: urgent > 0 ? "urgente" : "sano" },
    { label: "Pico", value: formatMxnFromCents(peak), detail: "máxima lectura de venta", tone: "sano" },
    { label: "Caja", value: formatSignedMxnFromCents(cash), detail: client.snapshot.cashCurrent.status, tone: cash === 0 ? "sano" : "revisar" }
  ];
}

function buildCheckpoint(client: PrismaMobileClientSnapshot, events: PrismaMobilePulseTimelineEvent[]): PrismaMobilePulseTimelineCheckpoint {
  const active = events.filter((event) => event.priorityScore >= 50).slice(0, 3);
  const tone: PrismaMobileCommandTone = events.some((event) => event.tone === "offline") ? "offline" : events.some((event) => event.tone === "urgente") ? "urgente" : active.length > 0 ? "revisar" : "sano";
  if (active.length === 0) {
    return {
      label: "Pulso estable",
      title: "Operación sin incendio visible",
      detail: `${client.snapshot.summary.businessName} puede seguir con revisión normal y brief de cierre.`,
      tone,
      checklist: ["mantener ventas observadas", "guardar brief diario", "cerrar caja con evidencia"]
    };
  }
  return {
    label: tone === "offline" ? "Pulso sin señal completa" : tone === "urgente" ? "Pulso caliente" : "Pulso en revisión",
    title: active[0].title,
    detail: `${active.length} puntos requieren seguimiento antes del cierre operativo.`,
    tone,
    checklist: active.map((event) => `${event.owner}: ${event.nextCheck}`)
  };
}

function buildNarrative(events: PrismaMobilePulseTimelineEvent[], checkpoint: PrismaMobilePulseTimelineCheckpoint): string[] {
  const byPhase = new Map<PrismaMobilePulsePhase, number>();
  for (const event of events) byPhase.set(event.phase, (byPhase.get(event.phase) ?? 0) + 1);
  const urgent = events.filter((event) => event.tone === "urgente" || event.tone === "offline").length;
  return [
    `${checkpoint.label}: ${checkpoint.detail}`,
    `Secuencia: apertura ${byPhase.get("apertura") ?? 0}, operación ${byPhase.get("operacion") ?? 0}, pico ${byPhase.get("pico") ?? 0}, seguimiento ${byPhase.get("seguimiento") ?? 0}, cierre ${byPhase.get("cierre") ?? 0}.`,
    urgent > 0 ? `Hay ${formatInteger(urgent)} eventos críticos que deben quedar atendidos o documentados.` : "No hay eventos críticos visibles en el pulso móvil."
  ];
}

function buildExportText(client: PrismaMobileClientSnapshot, events: PrismaMobilePulseTimelineEvent[], checkpoint: PrismaMobilePulseTimelineCheckpoint): string {
  const lines = [
    "# PRISMA Pulse Timeline",
    `Negocio: ${client.snapshot.summary.businessName}`,
    `Generado: ${client.snapshot.summary.generatedLabel}`,
    `Pulso: ${checkpoint.label}`,
    `Fuente: ${client.source}${client.stale ? " (respaldo local)" : ""}`,
    "",
    "## Secuencia operativa"
  ];
  for (const event of events) {
    lines.push(`- ${event.sequence}. [${event.phase}] ${event.timeLabel} · ${event.title} · ${event.owner} · ${event.nextCheck}`);
  }
  lines.push("", "## Checklist inmediato");
  for (const item of checkpoint.checklist) lines.push(`- ${item}`);
  lines.push("", "## Nota", "Timeline móvil derivado de snapshot, centro de mando, bandeja del dueño y bitácora de decisiones.");
  return lines.join("\n");
}

export function buildPrismaMobilePulseTimeline(client: PrismaMobileClientSnapshot): PrismaMobilePulseTimeline {
  const command = buildPrismaMobileCommandCenter(client);
  const inbox = buildPrismaMobileActionInbox(client);
  const rawEvents = [
    ...salesEvents(client.snapshot.salesToday.timeline),
    cashEvent(client),
    ...inventoryEvents(client.snapshot.inventoryWatchlist.items),
    ...alertEvents(client.snapshot.alerts.alerts),
    ...branchEvents(client.snapshot.branches.branches),
    ...decisionEvents(client),
    dataQualityEvent(client)
  ].filter((event): event is PrismaMobilePulseTimelineEvent => Boolean(event));
  const events = sortEvents(dedupeEvents(rawEvents)).slice(0, 18);
  const checkpoint = buildCheckpoint(client, events);
  const urgentCount = events.filter((event) => event.tone === "urgente" || event.tone === "offline").length;
  const headline = urgentCount > 0 ? "Timeline con focos rojos del día" : events.some((event) => event.tone === "revisar") ? "Timeline con seguimiento operativo" : "Timeline estable para cierre";
  const openActions = inbox.lanes.reduce((total, lane) => total + lane.actions.filter((action) => !action.id.startsWith("empty-")).length, 0);
  return {
    contractId: PRISMA_MOBILE_PULSE_TIMELINE_CONTRACT_ID,
    headline,
    subheadline: `${formatInteger(events.length)} eventos ordenados por fase; ${formatInteger(openActions)} acciones abiertas; riesgo ${command.riskLabel}.`,
    generatedLabel: client.snapshot.summary.generatedLabel,
    pulseLabel: checkpoint.label,
    nowCheckpoint: checkpoint,
    cards: buildCards(client, events),
    events,
    ownerNarrative: buildNarrative(events, checkpoint),
    exportText: buildExportText(client, events, checkpoint)
  };
}

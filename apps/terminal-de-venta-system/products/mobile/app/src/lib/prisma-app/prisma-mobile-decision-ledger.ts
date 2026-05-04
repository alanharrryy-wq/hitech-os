import type { PrismaMobileClientSnapshot } from "./prisma-mobile-snapshot-contract";
import type { PrismaMobileCommandTone } from "./prisma-mobile-command-center";
import { buildPrismaMobileCommandCenter } from "./prisma-mobile-command-center";
import { buildPrismaMobileActionInbox, type PrismaMobileOwnerAction } from "./prisma-mobile-action-inbox";
import { buildPrismaMobileDailyBrief } from "./prisma-mobile-daily-brief";
import { formatInteger, formatSignedMxnFromCents } from "./prisma-mobile-formatters";

export const PRISMA_MOBILE_DECISION_LEDGER_CONTRACT_ID = "PRISMA_APP_MOBILE_23_DECISION_LEDGER";

export type PrismaMobileDecisionLedgerSource = "command-center" | "action-inbox" | "daily-brief" | "data-quality" | "cash";

export type PrismaMobileDecisionLedgerEntry = {
  id: string;
  sequence: number;
  source: PrismaMobileDecisionLedgerSource;
  sourceLabel: string;
  title: string;
  summary: string;
  owner: string;
  tone: PrismaMobileCommandTone;
  priorityScore: number;
  auditLabel: string;
  dueLabel: string;
  evidence: string[];
  nextStep: string;
  shareLine: string;
};

export type PrismaMobileDecisionLedgerProofCard = {
  label: string;
  value: string;
  detail: string;
  tone: PrismaMobileCommandTone;
};

export type PrismaMobileDecisionLedger = {
  contractId: typeof PRISMA_MOBILE_DECISION_LEDGER_CONTRACT_ID;
  generatedLabel: string;
  headline: string;
  subheadline: string;
  trustLabel: string;
  ownerDigest: string[];
  proofCards: PrismaMobileDecisionLedgerProofCard[];
  entries: PrismaMobileDecisionLedgerEntry[];
  exportText: string;
};

function toneRank(tone: PrismaMobileCommandTone): number {
  return tone === "offline" ? 4 : tone === "urgente" ? 3 : tone === "revisar" ? 2 : 1;
}

function entryTone(actions: PrismaMobileOwnerAction[]): PrismaMobileCommandTone {
  if (actions.some((action) => action.tone === "offline")) return "offline";
  if (actions.some((action) => action.tone === "urgente")) return "urgente";
  if (actions.some((action) => action.tone === "revisar")) return "revisar";
  return "sano";
}

function normalizeEntryId(value: string): string {
  return value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 80) || "decision";
}

function actionSourceLabel(action: PrismaMobileOwnerAction): string {
  if (action.lane === "ahora") return "Resolver ahora";
  if (action.lane === "hoy") return "Seguimiento hoy";
  return "Cierre operativo";
}

function entryFromAction(action: PrismaMobileOwnerAction, index: number): PrismaMobileDecisionLedgerEntry {
  return {
    id: `accion-${normalizeEntryId(action.id)}-${index + 1}`,
    sequence: index + 1,
    source: "action-inbox",
    sourceLabel: actionSourceLabel(action),
    title: action.title,
    summary: action.summary,
    owner: action.owner,
    tone: action.tone,
    priorityScore: action.priorityScore,
    auditLabel: `${action.area} · ${action.dueLabel}`,
    dueLabel: action.dueLabel,
    evidence: action.evidence.slice(0, 3),
    nextStep: action.recommendedAction,
    shareLine: action.shareLine
  };
}

function uniqueEntries(entries: PrismaMobileDecisionLedgerEntry[]): PrismaMobileDecisionLedgerEntry[] {
  const seen = new Set<string>();
  const kept: PrismaMobileDecisionLedgerEntry[] = [];
  for (const entry of entries) {
    const key = `${entry.title}|${entry.owner}|${entry.nextStep}`.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    kept.push(entry);
  }
  return kept;
}

function sortEntries(entries: PrismaMobileDecisionLedgerEntry[]): PrismaMobileDecisionLedgerEntry[] {
  return [...entries].sort((a, b) => toneRank(b.tone) - toneRank(a.tone) || b.priorityScore - a.priorityScore || a.sequence - b.sequence).map((entry, index) => ({ ...entry, sequence: index + 1 }));
}

function cashEntry(client: PrismaMobileClientSnapshot): PrismaMobileDecisionLedgerEntry | null {
  const cash = client.snapshot.cashCurrent;
  if (cash.differenceCents === 0) return null;
  const score = Math.min(100, Math.round(Math.abs(cash.differenceCents) / 600));
  return {
    id: "caja-diferencia-auditable",
    sequence: 0,
    source: "cash",
    sourceLabel: "Caja auditable",
    title: "Diferencia de caja documentada",
    summary: `Corte ${cash.lastCut} con diferencia ${formatSignedMxnFromCents(cash.differenceCents)}.` ,
    owner: "Encargado de turno",
    tone: Math.abs(cash.differenceCents) >= 20000 ? "urgente" : "revisar",
    priorityScore: score,
    auditLabel: "caja · evidencia de corte",
    dueLabel: "antes de cerrar turno",
    evidence: [`Esperado: ${cash.expectedLabel}`, `Contado: ${cash.countedLabel}`, `Diferencia: ${formatSignedMxnFromCents(cash.differenceCents)}`],
    nextStep: "Confirmar conteo y registrar explicación antes del cierre.",
    shareLine: `Encargado de turno: confirmar diferencia ${formatSignedMxnFromCents(cash.differenceCents)} antes del cierre.`
  };
}

function dataQualityEntry(client: PrismaMobileClientSnapshot): PrismaMobileDecisionLedgerEntry | null {
  if (!client.stale && client.errors.length === 0) return null;
  return {
    id: "calidad-dato-movil",
    sequence: 0,
    source: "data-quality",
    sourceLabel: "Calidad de dato",
    title: "Datos con respaldo o lectura parcial",
    summary: client.errors.length > 0 ? client.errors.slice(0, 2).join(" · ") : "La app está usando respaldo local para mantener lectura operativa.",
    owner: "Operación",
    tone: client.source === "unavailable" ? "offline" : "revisar",
    priorityScore: client.source === "unavailable" ? 88 : 42,
    auditLabel: `datos · fuente ${client.source}`,
    dueLabel: "antes de tomar decisiones sensibles",
    evidence: [`Fuente: ${client.source}`, `Lectura: ${client.stale ? "respaldo" : "conectada"}`, `Errores: ${client.errors.length}`],
    nextStep: "Actualizar conexión y repetir lectura antes de autorizar acciones sensibles.",
    shareLine: "Operación: validar fuente de datos antes de decisiones sensibles."
  };
}

function buildOwnerDigest(entries: PrismaMobileDecisionLedgerEntry[]): string[] {
  const active = entries.filter((entry) => entry.priorityScore > 0).slice(0, 4);
  if (active.length === 0) return ["Sin decisiones críticas abiertas.", "Mantener cierre normal y revisar el brief diario."];
  return active.map((entry, index) => `${index + 1}. ${entry.owner}: ${entry.nextStep}`);
}

function buildExportText(client: PrismaMobileClientSnapshot, entries: PrismaMobileDecisionLedgerEntry[], trustLabel: string): string {
  const lines = [
    "# PRISMA Decision Ledger",
    `Negocio: ${client.snapshot.summary.businessName}`,
    `Generado: ${client.snapshot.summary.generatedLabel}`,
    `Fuente: ${client.source}${client.stale ? " (respaldo local)" : ""}`,
    `Confianza: ${trustLabel}`,
    "",
    "## Decisiones auditables"
  ];
  for (const entry of entries) {
    lines.push(`- ${entry.sequence}. ${entry.title} | ${entry.owner} | ${entry.nextStep} | evidencia: ${entry.evidence.join("; ")}`);
  }
  lines.push("", "## Nota", "Esta bitácora resume decisiones derivadas de señales móviles conectadas; no sustituye auditoría contable ni permisos administrativos.");
  return lines.join("\n");
}

export function buildPrismaMobileDecisionLedger(client: PrismaMobileClientSnapshot): PrismaMobileDecisionLedger {
  const snapshot = client.snapshot;
  const command = buildPrismaMobileCommandCenter(client);
  const inbox = buildPrismaMobileActionInbox(client);
  const brief = buildPrismaMobileDailyBrief(client);
  const inboxActions = inbox.lanes.flatMap((lane) => lane.actions).filter((action) => !action.id.startsWith("empty-")).map(entryFromAction);
  const extraEntries = [cashEntry(client), dataQualityEntry(client)].filter((entry): entry is PrismaMobileDecisionLedgerEntry => Boolean(entry));
  const entries = sortEntries(uniqueEntries([...extraEntries, ...inboxActions])).slice(0, 12);
  const activeEntries = entries.filter((entry) => entry.priorityScore > 0);
  const urgentEntries = entries.filter((entry) => entry.tone === "urgente" || entry.tone === "offline");
  const overallTone = urgentEntries.length > 0 ? entryTone(urgentEntries.map((entry) => ({ tone: entry.tone } as PrismaMobileOwnerAction))) : command.riskTone;
  const trustScore = Math.max(0, Math.min(100, command.readinessScore - (client.stale ? 18 : 0) - client.errors.length * 7));
  const trustLabel = `${trustScore}% confianza operativa · ${client.stale ? "revisar respaldo" : "fuente conectada"}`;
  const headline = urgentEntries.length > 0 ? "Bitácora con decisiones calientes" : activeEntries.length > 0 ? "Bitácora de decisiones del día" : "Bitácora limpia para cierre";
  const subheadline = `${formatInteger(entries.length)} entradas ordenadas por prioridad; ${brief.readinessLabel}.`;
  const proofCards: PrismaMobileDecisionLedgerProofCard[] = [
    { label: "Entradas", value: formatInteger(entries.length), detail: "decisiones trazables", tone: overallTone },
    { label: "Urgentes", value: formatInteger(urgentEntries.length), detail: "requieren seguimiento", tone: urgentEntries.length > 0 ? "urgente" : "sano" },
    { label: "Confianza", value: `${trustScore}%`, detail: client.stale ? "usa respaldo" : "conectada", tone: trustScore < 70 ? "revisar" : "sano" },
    { label: "Caja", value: formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents), detail: snapshot.cashCurrent.status, tone: snapshot.cashCurrent.differenceCents === 0 ? "sano" : "revisar" }
  ];
  return {
    contractId: PRISMA_MOBILE_DECISION_LEDGER_CONTRACT_ID,
    generatedLabel: snapshot.summary.generatedLabel,
    headline,
    subheadline,
    trustLabel,
    ownerDigest: buildOwnerDigest(entries),
    proofCards,
    entries,
    exportText: buildExportText(client, entries, trustLabel)
  };
}

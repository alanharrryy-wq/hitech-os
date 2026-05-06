import type {
  PrismaOperationalScreenModel,
  PrismaScreenAction,
  PrismaScreenMetric,
  PrismaScreenSection,
  PrismaScreenStatus,
  PrismaScreenTone
} from "./prisma-operational-screen-contract";

const PLACEHOLDER_WORDS = ["placeholder", "provisional", "segun el plan activo", "pendiente de integrar"];

export function prismaTone(input: unknown, fallback: PrismaScreenTone = "neutral"): PrismaScreenTone {
  if (input === "ok" || input === "warn" || input === "danger" || input === "neutral") return input;
  return fallback;
}

export function moneyMXN(value: number | null | undefined, options: { compact?: boolean } = {}) {
  const amount = value ?? 0;
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: options.compact ? 0 : 2
  }).format(amount);
}

export function numberMX(value: number | null | undefined) {
  return new Intl.NumberFormat("es-MX").format(value ?? 0);
}

export function percentMX(value: number | null | undefined) {
  return `${new Intl.NumberFormat("es-MX", { maximumFractionDigits: 1 }).format(value ?? 0)}%`;
}

export function operationalStatus(label: string, tone: PrismaScreenTone = "neutral"): PrismaScreenStatus {
  return { label, tone: prismaTone(tone) };
}

export function operationalMetric(metric: PrismaScreenMetric): PrismaScreenMetric {
  return {
    ...metric,
    tone: prismaTone(metric.tone, "neutral"),
    note: metric.note ?? "sin nota operativa"
  };
}

export function operationalAction(action: PrismaScreenAction): PrismaScreenAction {
  return {
    ...action,
    tone: prismaTone(action.tone, action.disabled ? "neutral" : "ok")
  };
}

export function operationalSection(section: PrismaScreenSection): PrismaScreenSection {
  const rows = section.table?.rows ?? [];
  const items = section.items ?? [];
  const empty = rows.length === 0 && items.length === 0;
  return {
    ...section,
    tone: prismaTone(section.tone, "neutral"),
    emptyTitle: section.emptyTitle ?? (empty ? "Sin datos operativos todavia" : undefined),
    emptyDescription: section.emptyDescription ?? (empty ? "La pantalla esta lista para pintar datos reales cuando el servicio responda." : undefined)
  };
}

export function createOperationalScreenModel(model: PrismaOperationalScreenModel): PrismaOperationalScreenModel {
  return {
    ...model,
    density: model.density ?? "standard",
    kicker: model.kicker ?? "Tablet operativa",
    status: model.status ? operationalStatus(model.status.label, model.status.tone) : undefined,
    actions: (model.actions ?? []).map(operationalAction),
    metrics: model.metrics.map(operationalMetric),
    sections: model.sections.map(operationalSection)
  };
}

export function assertNoPlaceholderCopy(model: PrismaOperationalScreenModel) {
  const haystack = JSON.stringify(model).toLowerCase();
  const hit = PLACEHOLDER_WORDS.find((word) => haystack.includes(word));
  if (hit) {
    throw new Error(`PRISMA screen standard blocked placeholder copy: ${hit}`);
  }
  return model;
}

export function readyOperationalScreen(model: PrismaOperationalScreenModel) {
  return assertNoPlaceholderCopy(createOperationalScreenModel(model));
}

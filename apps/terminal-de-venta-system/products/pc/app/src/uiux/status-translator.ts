// PRISMA PC UIUX V02 status translator.

import { translatePcStatus, translatePcTerm } from "./copy-dictionary";

export type HumanizedStatus = {
  label: string;
  severity: "info" | "attention" | "critical" | "blocking" | "demo" | "technical";
};

export function humanizePcStatus(status: string): HumanizedStatus {
  const normalized = status.toLowerCase().trim();

  if (["blocking", "blocked"].includes(normalized)) {
    return { label: translatePcStatus(status), severity: "blocking" };
  }

  if (["critical", "failed", "error", "danger"].includes(normalized)) {
    return { label: translatePcStatus(status), severity: "critical" };
  }

  if (["warning", "stale", "degraded", "partial", "medium", "low", "missing", "proxy"].includes(normalized)) {
    return { label: translatePcStatus(status), severity: "attention" };
  }

  if (["mock", "demo", "static"].includes(normalized)) {
    return { label: translatePcStatus(status), severity: "demo" };
  }

  if (["runtime", "raw", "debug", "adapter", "registry", "manifest", "canonical", "sqlite"].includes(normalized)) {
    return { label: translatePcTerm(status), severity: "technical" };
  }

  return { label: translatePcStatus(status), severity: "info" };
}

export function humanizePcConfidence(confidence: string): HumanizedStatus {
  const normalized = confidence.toLowerCase().trim();
  if (["real", "high", "healthy", "ok"].includes(normalized)) return { label: translatePcStatus(confidence), severity: "info" };
  if (["partial", "hybrid", "medium", "proxy"].includes(normalized)) return { label: translatePcStatus(confidence), severity: "attention" };
  if (["mock", "demo", "static"].includes(normalized)) return { label: translatePcStatus(confidence), severity: "demo" };
  if (["blocked", "missing", "failed"].includes(normalized)) return { label: translatePcStatus(confidence), severity: "critical" };
  return humanizePcStatus(confidence);
}

export function humanizePcFreshness(value: string): string {
  if (!value) return "Actualización no disponible";
  const parsed = new Date(value);
  if (!Number.isNaN(parsed.getTime())) {
    return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(parsed);
  }
  return translatePcStatus(value);
}

export function humanizePcTechnicalTerm(term: string): string {
  return translatePcTerm(term);
}

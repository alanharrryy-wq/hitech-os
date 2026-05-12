import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { AlertCenter, DataQualityReport, HealthRadar, HealthRadarDimension, OperationalValueStatus } from "./contracts";
import { HealthRadarSchema } from "./contracts";
import { evidence } from "./evidence";

function clampScore(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)));
}

function statusForScore(score: number | null, availability: OperationalValueStatus = "ok"): HealthRadarDimension["status"] {
  if (availability === "unknown" || availability === "unavailable") return "unknown";
  if (availability === "offline") return "blocked";
  if (score === null) return "unknown";
  if (score >= 82) return "healthy";
  if (score >= 62) return "watch";
  if (score >= 36) return "degraded";
  return "blocked";
}

function dimension(input: Omit<HealthRadarDimension, "status"> & { availability?: OperationalValueStatus }): HealthRadarDimension {
  return { ...input, status: statusForScore(input.score, input.availability) };
}

export function buildIntelligenceHealthRadar(state: MobileDataPlaneState, report: DataQualityReport, alerts: AlertCenter): HealthRadar {
  const tabletSource = report.sources.find((source) => source.id === "tablet");
  const pcSource = report.sources.find((source) => source.id === "pc");
  const controlSource = report.sources.find((source) => source.id === "control");
  const tabletAvailability: OperationalValueStatus = tabletSource?.status === "ok" ? "ok" : tabletSource?.status === "unknown" ? "unknown" : "offline";
  const pcAvailability: OperationalValueStatus = pcSource?.status === "ok" ? "ok" : pcSource?.status === "unknown" ? "unknown" : "partial";
  const controlAvailability: OperationalValueStatus = controlSource?.status === "ok" ? "ok" : controlSource?.status === "unknown" ? "unknown" : "partial";

  const pendingSync = state.outbox.pending + state.outbox.failed;
  const inventoryRisk = state.inventory.critical * 22 + state.inventory.reorder * 9;
  const alertRisk = alerts.counts.critical * 22 + alerts.counts.high * 12 + alerts.counts.medium * 5;
  const salesScore = tabletAvailability === "ok" ? clampScore(100 - (state.salesToday.tickets === 0 ? 28 : 0)) : null;
  const cashScore = state.cash.countedCents === null ? null : clampScore(100 - Math.min(68, Math.abs(state.cash.differenceCents) / 350));

  const dimensions: HealthRadarDimension[] = [
    dimension({
      key: "tablet",
      label: "Tablet",
      score: tabletAvailability === "ok" ? 92 : null,
      confidence: tabletAvailability === "ok" ? report.confidence : 0.35,
      explanation: tabletAvailability === "ok" ? "Tablet respondió y alimenta operación local." : "Tablet no está disponible para Mobile; POS local no queda bloqueado.",
      evidence: [evidence("radar-tablet", "Estado Tablet", "DataQuality", tabletSource?.status ?? "unknown")],
      availability: tabletAvailability
    }),
    dimension({
      key: "pc",
      label: "PC",
      score: pcAvailability === "ok" ? 86 : null,
      confidence: pcAvailability === "ok" ? report.confidence : 0.4,
      explanation: pcAvailability === "ok" ? "PC aporta gobierno y consolidado." : "PC no respondió; Mobile mantiene supervisión parcial sin convertirse en POS.",
      evidence: [evidence("radar-pc", "Estado PC", "DataQuality", pcSource?.status ?? "unknown")],
      availability: pcAvailability
    }),
    dimension({
      key: "mobile",
      label: "Mobile/Web",
      score: clampScore(report.confidence * 100),
      confidence: report.confidence,
      explanation: "Mobile traduce fuentes en supervisión y acciones, sin operar caja.",
      evidence: [evidence("radar-mobile", "Confianza Mobile", "DataQuality", report.confidence)]
    }),
    dimension({
      key: "sync",
      label: "Sync",
      score: tabletAvailability === "ok" ? clampScore(100 - state.outbox.failed * 24 - state.outbox.pending * 7) : null,
      confidence: report.confidence,
      explanation: pendingSync > 0 ? "Hay eventos pendientes o fallidos que limitan auditoría." : "No hay presión visible de outbox.",
      evidence: [evidence("radar-sync", "Outbox", "Tablet POS", `${state.outbox.pending} pendientes, ${state.outbox.failed} fallidos`)],
      availability: tabletAvailability
    }),
    dimension({
      key: "inventory",
      label: "Inventario",
      score: tabletAvailability === "ok" ? clampScore(100 - inventoryRisk) : null,
      confidence: report.confidence,
      explanation: inventoryRisk > 0 ? "Stock bajo puede pegarle a venta hoy." : "Watchlist sin presión crítica visible.",
      evidence: [evidence("radar-inventory", "Inventario", "Tablet POS", `${state.inventory.critical} críticos, ${state.inventory.reorder} reponer`)],
      availability: tabletAvailability
    }),
    dimension({
      key: "sales",
      label: "Ventas",
      score: salesScore,
      confidence: tabletAvailability === "ok" ? report.confidence : 0.3,
      explanation: state.salesToday.tickets > 0 ? "Ventas reales presentes en el snapshot." : "Sin tickets reales o fuente no disponible.",
      evidence: [evidence("radar-sales", "Ventas", "Tablet POS", `${state.salesToday.tickets} tickets`)],
      availability: tabletAvailability
    }),
    dimension({
      key: "cash",
      label: "Caja",
      score: cashScore,
      confidence: state.cash.countedCents === null ? 0.42 : report.confidence,
      explanation: state.cash.countedCents === null ? "No hay conteo real de caja; no se inventa diferencia." : "Caja cuenta con esperado y contado.",
      evidence: [evidence("radar-cash", "Caja", "Tablet POS", state.cash.countedCents === null ? "sin conteo" : state.cash.differenceCents)]
    }),
    dimension({
      key: "alerts",
      label: "Alertas",
      score: clampScore(100 - alertRisk),
      confidence: report.confidence,
      explanation: alerts.counts.total > 0 ? "Hay excepciones priorizadas con evidencia." : "Sin alertas activas relevantes.",
      evidence: [evidence("radar-alerts", "Alertas", "AlertEngine", `${alerts.counts.total} activas`)]
    }),
    dimension({
      key: "core",
      label: "Core",
      score: pcAvailability === "ok" || tabletAvailability === "ok" ? clampScore(report.completeness * 100) : null,
      confidence: report.confidence,
      explanation: "Core se infiere desde fuentes disponibles; si faltan fuentes, baja confianza.",
      evidence: [evidence("radar-core", "Completitud", "DataQuality", report.completeness)],
      availability: pcAvailability === "ok" || tabletAvailability === "ok" ? "ok" : "unknown"
    }),
    dimension({
      key: "control",
      label: "Control",
      score: controlAvailability === "ok" ? 86 : null,
      confidence: controlAvailability === "ok" ? report.confidence : 0.35,
      explanation: controlAvailability === "ok" ? "Control puede auditar incidentes." : "Control no está configurado o no respondió; auditoría queda parcial.",
      evidence: [evidence("radar-control", "Control", "DataQuality", controlSource?.status ?? "unknown")],
      availability: controlAvailability
    })
  ];

  const scorable = dimensions.filter((item) => typeof item.score === "number");
  const globalScore = scorable.length > 0 ? clampScore(scorable.reduce((sum, item) => sum + (item.score ?? 0), 0) / scorable.length) : null;
  const status = globalScore === null ? "unknown" : dimensions.some((item) => item.status === "blocked") ? "blocked" : globalScore >= 82 ? "healthy" : globalScore >= 62 ? "watch" : "degraded";
  return HealthRadarSchema.parse({ globalScore, status, confidence: report.confidence, dimensions });
}


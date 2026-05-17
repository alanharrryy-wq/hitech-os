import type { ActionInbox, AlertCenter, DataQualityReport, HealthRadar, ReportSummary } from "./contracts";
import { ReportSummarySchema } from "./contracts";
import { evidence } from "./evidence";

export function buildIntelligenceDailyBrief(input: {
  businessName: string;
  generatedAt: string;
  alertCenter: AlertCenter;
  actionInbox: ActionInbox;
  dataQuality: DataQualityReport;
  healthRadar: HealthRadar;
}): ReportSummary {
  const primary = input.actionInbox.primaryAction;
  const strongest = [...input.healthRadar.dimensions]
    .filter((dimension) => typeof dimension.score === "number")
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))[0];
  const weakest = [...input.healthRadar.dimensions]
    .filter((dimension) => typeof dimension.score === "number")
    .sort((a, b) => (a.score ?? 0) - (b.score ?? 0))[0];
  const risks = [
    ...(weakest ? [`${weakest.label}: ${weakest.explanation}`] : []),
    ...input.alertCenter.alerts.filter((alert) => alert.severity === "critical" || alert.severity === "high").slice(0, 3).map((alert) => alert.summary)
  ];
  const recommendedActions = primary
    ? [primary.recommendedAction, ...input.actionInbox.items.slice(1, 4).map((action) => action.recommendedAction)]
    : ["Mantener supervisión normal y revisar cierre cuando existan datos nuevos."];

  return ReportSummarySchema.parse({
    dailyStatus: input.dataQuality.runtimeMode === "live" ? "ok" : input.dataQuality.runtimeMode === "unknown" ? "unknown" : "partial",
    generatedAt: input.generatedAt,
    highlights: [
      `${input.businessName}: modo ${input.dataQuality.runtimeMode}, confianza ${Math.round(input.dataQuality.confidence * 100)}%.`,
      strongest ? `Punto fuerte: ${strongest.label}.` : "Sin dimensión fuerte calculable."
    ],
    risks: risks.length > 0 ? risks : ["Sin riesgos altos visibles en el snapshot."],
    opportunities: [
      input.dataQuality.missingSources.length > 0 ? "Conectar fuentes faltantes eleva confianza de supervisión." : "Fuentes principales disponibles para supervisión.",
      "Usar Action Inbox para cerrar decisiones con evidencia antes del corte."
    ],
    recommendedActions,
    evidence: [
      evidence("daily-quality", "Calidad del dato", "DataQuality", input.dataQuality.runtimeMode),
      ...(primary?.evidence ?? []).slice(0, 2)
    ]
  });
}


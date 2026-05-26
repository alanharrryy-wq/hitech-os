import { DecisionScreen } from "@components/uiux/decision-screen";
import { buildEvidenceDrawerItems } from "@/uiux/decision-model";
import { getOperationWorkspace } from "@/server/services/operation-control.service";
import type { OperationAlert, OperationWorkspace, Severity } from "@/modules/operations/types";

export const dynamic = "force-dynamic";

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: 0
  }).format(Math.round(cents / 100));
}

function freshnessLabel(value: string) {
  if (!value) return "Actualización no disponible";
  const date = new Date(value);
  if (!Number.isNaN(date.getTime())) {
    return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
  }
  return value;
}

function severityTone(severity: Severity): "danger" | "warn" | "ok" | "info" {
  if (severity === "CRITICO") return "danger";
  if (severity === "ALTO" || severity === "MEDIO") return "warn";
  return "ok";
}

function severityLabel(severity: Severity) {
  if (severity === "CRITICO") return "Crítico";
  if (severity === "ALTO") return "Atención";
  if (severity === "MEDIO") return "Revisar";
  return "Bajo";
}

function actionText(alert: OperationAlert) {
  const moduleName = alert.module.toLowerCase();
  if (moduleName.includes("sync")) return "Sincronizar";
  if (moduleName.includes("reabasto")) return "Ver reabasto";
  if (moduleName.includes("compra")) return "Ver compra";
  if (moduleName.includes("recepción") || moduleName.includes("recepcion")) return "Ver recepción";
  return "Revisar";
}

function rowsFromWorkspace(workspace: OperationWorkspace) {
  const alertRows = workspace.alerts.slice(0, 5).map((alert) => ({
    Pendiente: alert.title,
    Estado: severityLabel(alert.severity),
    Motivo: alert.detail,
    "Qué hacer": actionText(alert)
  }));

  if (alertRows.length > 0) return alertRows;

  return [
    {
      Pendiente: "Operación",
      Estado: "Bien",
      Motivo: "No hay pendientes críticos detectados en la lectura actual.",
      "Qué hacer": "Ver ventas"
    }
  ];
}

function recommendedAction(workspace: OperationWorkspace) {
  const critical = workspace.alerts.find((alert) => alert.severity === "CRITICO" || alert.severity === "ALTO");
  if (critical) {
    return {
      title: critical.title,
      motive: critical.detail,
      actions: [
        { label: actionText(critical), href: critical.href, primary: true },
        { label: "Ver reabasto", href: "/replenishment" },
        { label: "Ver ventas", href: "/sales-control" }
      ]
    };
  }

  return {
    title: "La operación no muestra bloqueos principales",
    motive: "La lectura actual no detecta pendientes críticos; puedes revisar ventas o descargar resumen.",
    actions: [
      { label: "Ver ventas", href: "/sales-control", primary: true },
      { label: "Ver reabasto", href: "/replenishment" },
      { label: "Ver evidencia", href: "/detalle-registros" }
    ]
  };
}

function confidenceText(workspace: OperationWorkspace) {
  if (workspace.meta.confidence === "real") return "Datos reales";
  if (workspace.meta.confidence === "partial") return "Datos incompletos";
  if (workspace.meta.confidence === "proxy") return "Estimación operativa";
  if (workspace.meta.confidence === "missing") return "Sin lectura suficiente";
  return "Lectura bloqueada";
}

export default async function HoyPage() {
  const workspace = await getOperationWorkspace("dashboard");
  const urgentCount = workspace.alerts.filter((alert) => alert.severity === "CRITICO" || alert.severity === "ALTO").length;
  const reviewCount = workspace.alerts.filter((alert) => alert.severity === "MEDIO").length + workspace.summary.openOrders + workspace.summary.receiptsWithDiscrepancy;
  const okSignals = workspace.kpis.filter((kpi) => kpi.status === "ok").length;
  const updated = freshnessLabel(workspace.meta.generatedAt);

  return (
    <DecisionScreen
      currentPath="/dashboard"
      title="Hoy"
      subtitle="Resumen de lo que necesita atención antes de vender, comprar o cerrar caja."
      status={urgentCount > 0 ? "warning" : "healthy"}
      lastUpdated={updated}
      summaryCards={[
        { title: String(urgentCount), eyebrow: "urgente", tone: urgentCount > 0 ? "danger" : "ok", lines: [`${workspace.summary.highPrioritySignals} señales altas de reabasto`, `${workspace.summary.receiptsWithDiscrepancy} recepciones con diferencia`] },
        { title: String(reviewCount), eyebrow: "revisar", tone: reviewCount > 0 ? "warn" : "ok", lines: [`${workspace.summary.openOrders} pedidos abiertos`, `${workspace.summary.replenishmentSignals} productos con señal de reabasto`] },
        { title: String(okSignals), eyebrow: "bien", tone: "ok", lines: [`Venta neta: ${money(workspace.summary.netSalesCents)}`, confidenceText(workspace)] }
      ]}
      recommendedAction={recommendedAction(workspace)}
      tableTitle="Pendientes principales"
      tableSubtitle="Ordenado por gravedad y convertido a acciones claras."
      columns={["Pendiente", "Estado", "Motivo", "Qué hacer"]}
      rows={rowsFromWorkspace(workspace)}
      evidence={[
        ...buildEvidenceDrawerItems("/dashboard"),
        { label: "Persistencia", value: workspace.meta.persistence === "available" ? "Disponible" : "No disponible", kind: "technical" },
        { label: "Confianza de datos", value: confidenceText(workspace), kind: "technical" },
        { label: "Última lectura", value: updated, kind: "technical" },
        ...(workspace.meta.warnings.length > 0
          ? workspace.meta.warnings.map((warning) => ({ label: "Advertencia", value: warning, kind: "technical" as const }))
          : [{ label: "Advertencias", value: "No hay advertencias técnicas en la lectura actual.", kind: "technical" as const }])
      ]}
    />
  );
}

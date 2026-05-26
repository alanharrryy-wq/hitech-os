import type { ReactNode } from "react";
import { AppShell } from "@components/layout/app-shell";
import { buildEvidenceDrawerItems, getHumanRouteStatus, getPcRouteContract, getPrimaryRouteActions } from "@/uiux/decision-model";
import { ActionableTable } from "./actionable-table";
import { AttentionSummary } from "./attention-summary";
import { ChartInsightCard } from "./chart-insight-card";
import { DecisionHeader } from "./decision-header";
import { EvidenceDrawer } from "./evidence-drawer";
import { NextBestAction } from "./next-best-action";
import { PcModuleShell } from "./pc-module-shell";
import type { ChartInsight, EvidenceItem, RecommendedAction, SummaryCard } from "./decision-types";

function defaultSummaryCards(title: string): SummaryCard[] {
  return [
    { title: "Atención", eyebrow: "lectura rápida", tone: "info", lines: [`${title} tiene contrato humano activo.`, "Revisa los pendientes antes del detalle técnico."] },
    { title: "Acción", eyebrow: "siguiente paso", tone: "ok", lines: ["La pantalla declara una acción recomendada.", "La evidencia permanece colapsada por defecto."] },
    { title: "Evidencia", eyebrow: "trazabilidad", tone: "info", lines: ["Fuente, confianza y actualización viven en el drawer."] }
  ];
}

export function DecisionScreen({
  currentPath,
  title,
  subtitle,
  status,
  lastUpdated = "Lectura actual",
  summaryCards,
  recommendedAction,
  tableTitle,
  tableSubtitle,
  columns,
  rows,
  evidence,
  children,
  insight
}: {
  currentPath: string;
  title?: string;
  subtitle?: string;
  status?: string;
  lastUpdated?: string;
  summaryCards?: SummaryCard[];
  recommendedAction?: RecommendedAction;
  tableTitle?: string;
  tableSubtitle?: string;
  columns?: string[];
  rows?: Array<Record<string, string | number>>;
  evidence?: EvidenceItem[];
  children?: ReactNode;
  insight?: ChartInsight;
}) {
  const contract = getPcRouteContract(currentPath);
  const routeStatus = getHumanRouteStatus(currentPath);
  const actions = getPrimaryRouteActions(currentPath);
  const resolvedTitle = title ?? contract.humanName;
  const resolvedSubtitle = subtitle ?? contract.subtitle;
  const resolvedSummary = summaryCards ?? defaultSummaryCards(resolvedTitle);
  const resolvedAction = recommendedAction ?? {
    title: contract.primaryAction,
    motive: contract.primaryQuestion,
    actions
  };
  const resolvedRows = rows ?? [{ Pendiente: resolvedTitle, Estado: routeStatus.label, "Qué hacer": contract.primaryAction }];

  return (
    <AppShell currentPath={currentPath}>
      <DecisionHeader
        title={resolvedTitle}
        subtitle={resolvedSubtitle}
        status={status ?? routeStatus.label}
        lastUpdated={lastUpdated}
        currentPath={currentPath}
        actions={actions}
      />
      <PcModuleShell currentPath={currentPath}>
        <AttentionSummary cards={resolvedSummary} />
        <NextBestAction action={resolvedAction} />
        {children}
        <ActionableTable
          title={tableTitle ?? "Pendientes y detalle operativo"}
          subtitle={tableSubtitle ?? "Cada fila debe explicar qué hacer, no sólo mostrar datos."}
          columns={columns ?? ["Pendiente", "Estado", "Qué hacer"]}
          rows={resolvedRows}
        />
        {insight ? <ChartInsightCard insight={insight} /> : null}
        <EvidenceDrawer items={evidence ?? buildEvidenceDrawerItems(currentPath)} />
      </PcModuleShell>
    </AppShell>
  );
}

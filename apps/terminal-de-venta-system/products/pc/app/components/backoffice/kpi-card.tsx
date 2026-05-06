import type { BackofficeKpi } from "@/lib/backoffice/dashboard";
import { StatusBadge } from "./status-badge";

export function KpiCard({ kpi }: { kpi: BackofficeKpi }) {
  const statusText =
    kpi.status === "supported" ? "soportado" : kpi.status === "partial" ? "parcial" : "sin fuente";
  return (
    <article className="card metric-card">
      <div className="card-title-row">
        <div>
          <div className="kicker">KPI</div>
          <div className="card-title">{kpi.label}</div>
        </div>
        <StatusBadge value={statusText} />
      </div>
      <div className="metric">{kpi.value}</div>
      <div className="metric-note">{kpi.note}</div>
      <div className="metric-note">Fuente: {kpi.source}</div>
    </article>
  );
}

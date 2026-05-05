import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI06DashboardData } from "@/lib/i06/dashboard-data";

export default function Page() {
  return (
    <AppShell currentPath="/metricas-dia">
      <section className="hero">
        <div className="kicker">capa i06</div>
        <h1 style={{ margin: 0 }}>Métricas del día</h1>
        <div className="subtle">Lectura por categoría para backoffice y seguimiento operativo.</div>
      </section>
      <SectionCard title="Salud por categoría" subtitle="Valor de stock, quiebres y días de cobertura.">
        <div className="list">
          {pcI06DashboardData.categoryHealth.map((item) => (
            <div key={item.category} className="list-item">{item.category} · valor ${item.stockValueMx} · quiebres {item.stockoutSlots} · cobertura {item.avgDaysCover} días</div>
          ))}
        </div>
      </SectionCard>
      <SectionCard title="Exactitud por ubicación" subtitle="Conteos exactos y varianza media.">
        <div className="list">
          {pcI06DashboardData.auditAccuracy.map((item) => (
            <div key={item.location} className="list-item">{item.location} · exactitud {item.exactPct}% · varianza media {item.avgAbsVariance}</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}

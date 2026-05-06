import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI06DashboardData } from "@/lib/i06/dashboard-data";
import { confidenceLabel, formatKpiValue } from "@/lib/i06/dashboard-helpers";

export default function Page() {
  return (
    <AppShell currentPath="/tablero-kpi">
      <section className="hero">
        <div className="kicker">capa i06</div>
        <h1 style={{ margin: 0 }}>Tablero KPI inicial</h1>
        <div className="subtle">Primera lectura ejecutiva para inventario, control operativo y señales comerciales demo.</div>
      </section>
      <SectionCard title="KPI visibles hoy" subtitle="Mezcla de métricas reales y contratos demo honestos.">
        <div className="list">
          {pcI06DashboardData.cards.map((card) => (
            <div key={card.id} className="list-item">
              <strong>{card.label}:</strong> {formatKpiValue(card)} · base {confidenceLabel(card.confidence)}
            </div>
          ))}
        </div>
      </SectionCard>
      <SectionCard title="Top SKUs por salida de venta demo" subtitle="Sirve para diseño del tablero y priorización inicial.">
        <div className="list">
          {pcI06DashboardData.topSkus.slice(0, 8).map((item) => (
            <div key={item.sku} className="list-item">{item.sku} · {item.name} · {item.unitsSold} uds · ${item.grossSalesMx}</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}

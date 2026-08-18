import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { getBackofficeDashboard } from "@/lib/backoffice/dashboard";

export const dynamic = "force-dynamic";

function formatGeneratedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sin hora disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

export default async function MetricasDiaPage() {
  const dashboard = await getBackofficeDashboard();
  const primary = dashboard.kpis.filter((item) => item.status !== "unavailable").slice(0, 4);
  const kpiRows = dashboard.kpis.map((item) => ({
    Indicador: item.label,
    Valor: item.value,
    Estado: item.status === "supported" ? "Disponible" : item.status === "partial" ? "Parcial" : "No disponible",
    Fuente: item.source,
    Nota: item.note
  }));
  const topSkuRows = dashboard.topSkus.map((item) => ({
    SKU: item.sku,
    Producto: item.productName,
    Unidades: item.qty,
    Venta: money(item.totalCents)
  }));

  return (
    <AppShell currentPath="/metricas-dia">
      <section className="hero" data-prisma-surface="pc-daily-finance-readout">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">lectura financiera diaria</div>
            <h1 className="hero-title">Métricas del día</h1>
            <p>Indicadores calculados desde persistencia canónica. Sin cifras simuladas ni filtros globales.</p>
          </div>
          <div className="inline-list">
            <span className="chip">Actualizado: {formatGeneratedAt(dashboard.meta.generatedAt)}</span>
            <a className="btn btn-primary" href="/sales-control">Abrir ventas y caja</a>
            <a className="btn" href="/cash-sessions">Revisar sesiones</a>
          </div>
        </div>
      </section>

      {dashboard.meta.warnings.length ? (
        <div className="alert-strip">
          <strong>Limitación visible</strong>
          <span className="subtle">{dashboard.meta.warnings.join(" · ")}</span>
        </div>
      ) : null}

      <section className="dashboard-grid" aria-label="Indicadores reales del día">
        {primary.map((item) => (
          <article className="card metric-card" key={item.key}>
            <div className="kicker">{item.status === "supported" ? "dato canónico" : "lectura parcial"}</div>
            <div className="card-title">{item.label}</div>
            <div className="metric">{item.value}</div>
            <div className="metric-note">{item.note}</div>
          </article>
        ))}
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">tabla operativa</div><h2 className="section-title">Indicadores y fuentes</h2><div className="section-copy">Cada fila declara el estado y la fuente que realmente sostiene el valor.</div></div></div>
        <DataTable columns={["Indicador", "Valor", "Estado", "Fuente", "Nota"]} rows={kpiRows} emptyMessage="No hay indicadores disponibles en esta lectura." />
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">venta por producto</div><h2 className="section-title">Top SKUs del día</h2><div className="section-copy">Ranking derivado de las líneas de venta consolidadas.</div></div></div>
        <DataTable columns={["SKU", "Producto", "Unidades", "Venta"]} rows={topSkuRows} emptyMessage="No hay líneas de venta consolidadas para el día actual." />
      </section>
    </AppShell>
  );
}

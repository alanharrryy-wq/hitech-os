import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { getBackofficeDashboard } from "@/lib/backoffice/dashboard";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const dynamic = "force-dynamic";

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

export default async function PrismaInsightsPage() {
  const [dashboard, stock, replenishment] = await Promise.all([
    getBackofficeDashboard(),
    getBackofficeModuleOverview("stock"),
    getBackofficeModuleOverview("replenishment")
  ]);

  const kpiRows = dashboard.kpis.map((item) => ({
    Indicador: item.label,
    Valor: item.value,
    Estado: item.status === "supported" ? "Disponible" : item.status === "partial" ? "Parcial" : "No disponible",
    Fuente: item.source,
    Lectura: item.note
  }));
  const topSkuRows = dashboard.topSkus.map((item) => ({
    SKU: item.sku,
    Producto: item.productName,
    Unidades: item.qty,
    Venta: money(item.totalCents)
  }));

  return (
    <AppShell currentPath="/prisma-insights">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">análisis operativo</div>
            <h1 className="hero-title">Análisis</h1>
            <p>Lecturas derivadas de KPIs, ventas, existencias y reabasto reales. Cada valor declara su fuente y su nivel de soporte.</p>
          </div>
          <div className="inline-list">
            <a className="btn btn-primary" href="/sales-control">Abrir ventas</a>
            <a className="btn" href="/stock">Abrir inventario</a>
            <a className="btn" href="/replenishment">Abrir reabasto</a>
          </div>
        </div>
      </section>

      {dashboard.meta.warnings.length ? <div className="alert-strip"><strong>Lectura parcial</strong><span className="subtle">{dashboard.meta.warnings.join(" · ")}</span></div> : null}

      <section className="card">
        <div className="section-head"><div><div className="kicker">indicadores</div><h2 className="section-title">KPIs con procedencia</h2><div className="section-copy">“Parcial” y “No disponible” permanecen visibles; no se rellenan con ejemplos.</div></div></div>
        <DataTable columns={["Indicador", "Valor", "Estado", "Fuente", "Lectura"]} rows={kpiRows} emptyMessage="No hay KPIs calculables en esta lectura." />
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">ventas</div><h2 className="section-title">Productos con actividad</h2></div></div>
        <DataTable columns={["SKU", "Producto", "Unidades", "Venta"]} rows={topSkuRows} emptyMessage="No hay líneas de venta consolidadas para el periodo actual." />
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">inventario</div><h2 className="section-title">{stock.table.title}</h2></div></div>
        <DataTable columns={stock.table.columns} rows={stock.table.rows} emptyMessage={stock.table.emptyMessage} />
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">reabasto</div><h2 className="section-title">{replenishment.table.title}</h2></div></div>
        <DataTable columns={replenishment.table.columns} rows={replenishment.table.rows} emptyMessage={replenishment.table.emptyMessage} />
      </section>
    </AppShell>
  );
}

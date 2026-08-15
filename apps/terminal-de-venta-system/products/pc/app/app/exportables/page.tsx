import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { getBackofficeDashboard } from "@/lib/backoffice/dashboard";

export const dynamic = "force-dynamic";

export default async function ExportablesPage() {
  const dashboard = await getBackofficeDashboard();
  const sales = dashboard.kpis.find((item) => item.key === "netSalesTodayCents");
  const tickets = dashboard.kpis.find((item) => item.key === "ticketCountToday");
  const rows = [
    {
      Reporte: "Ventas y caja",
      Fuente: "Sale / SaleLine / PaymentTender",
      Formato: "CSV",
      Estado: "Disponible",
      __rowDetailTitle: "Exportación conectada al ledger real de ventas.",
      __rowDetailItems: ["Respeta el gate de licencia export.sales.basic.", "El archivo se genera desde GET /api/backoffice/sales-control?format=csv."],
      __rowActionHref: "/api/backoffice/sales-control?format=csv",
      __rowActionLabel: "Descargar CSV"
    }
  ];

  return (
    <AppShell currentPath="/exportables">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">descargas</div>
            <h1 className="hero-title">Exportables conectados</h1>
            <p>Sólo se anuncian formatos que tienen endpoint real y gate de licencia. Nada de PDF imaginario con corbata.</p>
          </div>
          <div className="inline-list">
            <span className="chip">Venta hoy: {sales?.value ?? "No disponible"}</span>
            <span className="chip">Tickets: {tickets?.value ?? "0"}</span>
          </div>
        </div>
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">exportadores activos</div><h2 className="section-title">Descargas disponibles</h2><div className="section-copy">La acción de descarga sólo aparece cuando existe un productor real.</div></div></div>
        <DataTable columns={["Reporte", "Fuente", "Formato", "Estado"]} rows={rows} emptyMessage="No hay exportadores conectados." />
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">alcance</div><h2 className="section-title">Lo que todavía no se anuncia</h2></div></div>
        <div className="list">
          <div className="list-item">Inventario, compras y auditoría no se ofrecen aquí como CSV/PDF hasta contar con exportador certificado.</div>
          <div className="list-item">La ausencia de un exportador no se disfraza como “reporte listo”.</div>
        </div>
      </section>
    </AppShell>
  );
}

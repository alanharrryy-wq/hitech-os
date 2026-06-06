import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { TableSimple } from "@components/ui/table-simple";
import { getCriticalStockRows } from "@/lib/services/catalog";

export const dynamic = "force-dynamic";

export default async function Page() {
  const { rows: criticalStockRows, notice } = await getCriticalStockRows();

  return (
    <AppShell currentPath="/existencias-criticas">
      <section className="hero">
        <div className="kicker">inventario</div>
        <h1 style={{ margin: 0 }}>Existencias críticas</h1>
        <div className="subtle">Prioridad de quiebres y cobertura baja sin romper la pantalla si la base local no abre.</div>
      </section>

      {notice ? (
        <div className="alert-strip" role="status">
          <strong>{notice.title}</strong>
          <span className="subtle">{notice.detail}</span>
        </div>
      ) : null}

      <SectionCard title="Prioridad de atención" subtitle="Filas para quiebre, cobertura baja y seguimiento de reabasto.">
        <TableSimple
          columns={["SKU", "Producto", "Ubicación", "Disponible", "Días", "Estado"]}
          rows={criticalStockRows.map((row) => ({
            "SKU": row.sku,
            "Producto": row.producto,
            "Ubicación": row.ubicacion,
            "Disponible": row.disponible,
            "Días": row.diasCobertura,
            "Estado": row.estado
          }))}
          emptyMessage="No hay existencias críticas disponibles en esta lectura."
        />
      </SectionCard>
    </AppShell>
  );
}

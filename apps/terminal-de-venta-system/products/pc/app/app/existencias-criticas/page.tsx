import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { TableSimple } from "@components/ui/table-simple";
import { criticalStockRows } from "@/lib/i02/catalog-stock-data";

export default function Page() {
  return (
    <AppShell currentPath="/existencias-criticas">
      <section className="hero">
        <div className="kicker">inyección 02</div>
        <h1 style={{ margin: 0 }}>Existencias críticas</h1>
        <div className="subtle">Overlay operativo para quiebres y riesgo sin modificar el módulo base de existencias.</div>
      </section>

      <SectionCard title="Prioridad de atención" subtitle="Filas de ejemplo para quiebre, cobertura baja y seguimiento de reabasto.">
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
        />
      </SectionCard>
    </AppShell>
  );
}

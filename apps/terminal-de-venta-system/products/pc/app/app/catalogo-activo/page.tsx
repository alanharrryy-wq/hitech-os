import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { TableSimple } from "@components/ui/table-simple";
import { getCatalogActiveSnapshot } from "@/lib/services/catalog";

export const dynamic = "force-dynamic";

export default async function Page() {
  const { snapshot, categorySummary, notice } = await getCatalogActiveSnapshot();
  return (
    <AppShell currentPath="/catalogo-activo">
      <section className="hero">
        <div className="kicker">inventario</div>
        <h1 style={{ margin: 0 }}>Catálogo activo</h1>
        <div className="subtle">Lectura de productos activos con estado vacío honesto si la base local no está disponible.</div>
      </section>

      {notice ? (
        <div className="alert-strip" role="status">
          <strong>{notice.title}</strong>
          <span className="subtle">{notice.detail}</span>
        </div>
      ) : null}

      <div className="grid cols-4">
        <StatCard label="Categorías" value={String(snapshot.categorias)} note="familias visibles en Prisma" />
        <StatCard label="SKUs activos" value={String(snapshot.skusActivos)} note="conteo base para capa administrativa" />
        <StatCard label="Filas críticas" value={String(snapshot.filasCriticas)} note="existencias con cobertura baja" />
        <StatCard label="Barcodes por SKU" value={String(snapshot.promedioBarcodes)} note="promedio simple por categoría" />
      </div>

      <SectionCard title="Resumen por categoría" subtitle="Base útil para decisiones de catálogo, surtido y tablero posterior.">
        <TableSimple
          columns={["Categoría", "SKUs", "Activos", "Precio promedio", "Costo promedio"]}
          rows={categorySummary.map((row) => ({
            "Categoría": row.categoria,
            "SKUs": row.skus,
            "Activos": row.activos,
            "Precio promedio": row.precioPromedio,
            "Costo promedio": row.costoPromedio
          }))}
          emptyMessage="No hay categorías consolidadas disponibles en esta lectura."
        />
      </SectionCard>
    </AppShell>
  );
}

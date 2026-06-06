import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { TableSimple } from "@components/ui/table-simple";
import { getBarcodeHealthRows } from "@/lib/services/catalog";

export const dynamic = "force-dynamic";

export default async function Page() {
  const { rows: barcodeHealthRows, notice } = await getBarcodeHealthRows();

  return (
    <AppShell currentPath="/salud-barcodes">
      <section className="hero">
        <div className="kicker">inventario</div>
        <h1 style={{ margin: 0 }}>Salud de códigos de barras</h1>
        <div className="subtle">Cobertura de códigos por categoría con protección contra error de base local.</div>
      </section>

      {notice ? (
        <div className="alert-strip" role="status">
          <strong>{notice.title}</strong>
          <span className="subtle">{notice.detail}</span>
        </div>
      ) : null}

      <SectionCard title="Cobertura de códigos" subtitle="Sirve para detectar huecos de código antes de abrir auditorías más pesadas.">
        <TableSimple
          columns={["Categoría", "Productos", "Códigos", "Promedio", "Activos"]}
          rows={barcodeHealthRows.map((row) => ({
            "Categoría": row.categoria,
            "Productos": row.productos,
            "Códigos": row.barcodes,
            "Promedio": row.promedio,
            "Activos": row.activos
          }))}
          emptyMessage="No hay códigos de barras consolidados disponibles en esta lectura."
        />
      </SectionCard>
    </AppShell>
  );
}

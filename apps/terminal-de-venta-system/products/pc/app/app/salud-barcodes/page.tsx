import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { TableSimple } from "@components/ui/table-simple";
import { barcodeHealthRows } from "@/lib/i02/catalog-stock-data";

export default function Page() {
  return (
    <AppShell currentPath="/salud-barcodes">
      <section className="hero">
        <div className="kicker">inyección 02</div>
        <h1 style={{ margin: 0 }}>Salud de barcodes</h1>
        <div className="subtle">Vista auxiliar por categoría para endurecer calidad de captura y gobierno de producto.</div>
      </section>

      <SectionCard title="Cobertura de códigos" subtitle="Sirve para detectar huecos de barcode antes de abrir auditorías más pesadas.">
        <TableSimple
          columns={["Categoría", "Productos", "Barcodes", "Promedio", "Activos"]}
          rows={barcodeHealthRows.map((row) => ({
            "Categoría": row.categoria,
            "Productos": row.productos,
            "Barcodes": row.barcodes,
            "Promedio": row.promedio,
            "Activos": row.activos
          }))}
        />
      </SectionCard>
    </AppShell>
  );
}
